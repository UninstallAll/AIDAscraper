"""
爬虫任务模块
"""
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import time

from celery.exceptions import MaxRetriesExceededError
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.core.celery_app import celery_app
from app.db.database import SessionLocal
from app.scrapers.spider_factory import SpiderFactory
from app.utils.logger import get_job_logger

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def run_spider_task(self, job_id: int) -> Dict[str, Any]:
    """
    运行爬虫任务
    
    Args:
        self: Celery任务实例
        job_id: 任务ID
        
    Returns:
        Dict[str, Any]: 任务结果
    """
    # 获取数据库会话
    db = SessionLocal()
    # 获取任务日志记录器
    job_logger = get_job_logger(job_id)
    
    try:
        # 获取任务
        job = services.job.get(db, job_id=job_id)
        if not job:
            logger.error(f"任务不存在: {job_id}")
            return {"status": "failed", "error": "任务不存在"}
        
        # 获取站点配置
        site_config = services.site.get(db, site_id=job.site_config_id)
        if not site_config:
            error_msg = f"站点配置不存在: {job.site_config_id}"
            job_logger.error(error_msg, db)
            services.job.update_status(
                db, 
                job_id=job_id, 
                status_update=schemas.JobStatusUpdate(
                    status="failed",
                    error_message=error_msg
                )
            )
            return {"status": "failed", "error": error_msg}
        
        # 更新任务状态为运行中
        job = services.job.update_status(
            db, 
            job_id=job_id, 
            status_update=schemas.JobStatusUpdate(
                status="running",
                progress=0,
                started_at=datetime.now()
            )
        )
        
        # 保存Celery任务ID
        job = services.job.update(
            db,
            db_obj=job,
            obj_in=schemas.JobUpdate(celery_task_id=self.request.id)
        )
        
        # 记录任务开始日志
        job_logger.info(f"任务 {job.name} 开始执行", db)
        
        try:
            # 创建爬虫
            job_logger.info(f"正在创建爬虫实例，站点: {site_config.name}", db)
            spider = SpiderFactory.create_spider(site_config=site_config, job_id=job_id)
            
            # 创建爬虫进程
            job_logger.info("正在配置爬虫进程", db)
            process = CrawlerProcess(get_project_settings())
            
            # 配置爬虫进程
            process.crawl(spider)
            
            # 运行爬虫
            job_logger.info("爬虫开始运行", db)
            process.start()
            
            # 记录完成日志
            job_logger.info("爬虫任务完成", db)
            
            # 更新任务状态为完成
            job = services.job.update_status(
                db, 
                job_id=job_id, 
                status_update=schemas.JobStatusUpdate(
                    status="completed",
                    progress=100,
                    completed_at=datetime.now()
                )
            )
            
            return {
                "status": "success",
                "job_id": job_id,
                "site_id": site_config.id,
                "items_scraped": job.items_scraped,
                "items_saved": job.items_saved,
            }
        except Exception as e:
            # 记录异常
            error_msg = f"爬虫任务执行异常: {e}"
            job_logger.error(error_msg, db)
            
            # 尝试重试任务
            try:
                # 更新任务状态为重试中
                services.job.update_status(
                    db, 
                    job_id=job_id, 
                    status_update=schemas.JobStatusUpdate(
                        status="retrying",
                        error_message=f"任务执行异常，准备重试: {str(e)}"
                    )
                )
                
                job_logger.warning(f"任务执行失败，准备重试: {str(e)}", db)
                
                # 重试任务
                raise self.retry(exc=e, countdown=60)
            except MaxRetriesExceededError:
                # 超过最大重试次数
                error_msg = f"任务 {job_id} 超过最大重试次数"
                job_logger.error(error_msg, db)
                services.job.update_status(
                    db, 
                    job_id=job_id, 
                    status_update=schemas.JobStatusUpdate(
                        status="failed",
                        error_message=f"超过最大重试次数: {str(e)}"
                    )
                )
                return {"status": "failed", "error": f"超过最大重试次数: {str(e)}"}
    except Exception as e:
        error_msg = f"爬虫任务失败: {e}"
        logger.exception(error_msg)
        job_logger.error(error_msg, db)
        
        # 更新任务状态为失败
        services.job.update_status(
            db, 
            job_id=job_id, 
            status_update=schemas.JobStatusUpdate(
                status="failed",
                error_message=str(e)
            )
        )
        
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def update_job_progress(self, job_id: int, progress: int, items_scraped: int, items_saved: int) -> None:
    """
    更新任务进度
    
    Args:
        self: Celery任务实例
        job_id: 任务ID
        progress: 进度百分比
        items_scraped: 已抓取的项目数
        items_saved: 已保存的项目数
    """
    db = SessionLocal()
    job_logger = get_job_logger(job_id)
    
    try:
        services.job.update_status(
            db, 
            job_id=job_id, 
            status_update=schemas.JobStatusUpdate(
                status="running",
                progress=progress,
                items_scraped=items_scraped,
                items_saved=items_saved
            )
        )
        
        # 记录进度日志
        job_logger.info(f"进度更新: {progress}%, 已抓取: {items_scraped}, 已保存: {items_saved}", db)
    except Exception as e:
        error_msg = f"更新任务进度失败: {e}"
        logger.exception(error_msg)
        job_logger.error(error_msg, db)
        
        try:
            # 重试任务
            raise self.retry(exc=e, countdown=30)
        except MaxRetriesExceededError:
            error_msg = f"更新任务进度 {job_id} 超过最大重试次数"
            logger.error(error_msg)
            job_logger.error(error_msg, db)
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3)
def cleanup_stalled_jobs(self) -> Dict[str, Any]:
    """
    清理卡住的任务
    
    Returns:
        Dict[str, Any]: 清理结果
    """
    db = SessionLocal()
    try:
        # 查找状态为running但长时间未更新的任务
        stalled_jobs = services.job.find_stalled_jobs(db, minutes=30)
        
        count = 0
        for job in stalled_jobs:
            # 更新任务状态为失败
            services.job.update_status(
                db, 
                job_id=job.id, 
                status_update=schemas.JobStatusUpdate(
                    status="failed",
                    error_message="任务执行超时"
                )
            )
            
            # 记录日志
            job_logger = get_job_logger(job.id)
            job_logger.error("任务执行超时，已自动取消", db)
            
            count += 1
        
        return {"status": "success", "cleaned_jobs": count}
    except Exception as e:
        logger.exception(f"清理卡住任务失败: {e}")
        try:
            # 重试任务
            raise self.retry(exc=e)
        except MaxRetriesExceededError:
            logger.error("清理卡住任务超过最大重试次数")
            return {"status": "failed", "error": str(e)}
    finally:
        db.close() 