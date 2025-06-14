"""
Scrapy Pipeline模块
"""
import json
import logging
import os
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app import services
from app.utils.logger import get_job_logger


class JsonWriterPipeline:
    """
    将爬取的数据写入JSON文件的Pipeline
    """
    
    def __init__(self, output_dir: str = "output"):
        """
        初始化Pipeline
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = output_dir
        self.items = []
        self.logger = logging.getLogger(__name__)
        self.job_logger = None
    
    @classmethod
    def from_crawler(cls, crawler):
        """
        从爬虫创建Pipeline
        
        Args:
            crawler: 爬虫
            
        Returns:
            JsonWriterPipeline: Pipeline实例
        """
        # 获取设置
        output_dir = crawler.settings.get("OUTPUT_DIR", "output")
        return cls(output_dir=output_dir)
    
    def open_spider(self, spider):
        """
        爬虫开始时调用
        
        Args:
            spider: 爬虫
        """
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 获取任务日志记录器
        job_id = getattr(spider, "job_id", None)
        if job_id:
            self.job_logger = get_job_logger(job_id)
            self.job_logger.info(f"JsonWriterPipeline启动，输出目录: {self.output_dir}")
        else:
            self.logger.info(f"JsonWriterPipeline启动，输出目录: {self.output_dir}")
    
    def process_item(self, item: Dict[str, Any], spider):
        """
        处理爬取的数据项
        
        Args:
            item: 数据项
            spider: 爬虫
            
        Returns:
            Dict[str, Any]: 处理后的数据项
        """
        self.items.append(dict(item))
        
        # 记录处理项目日志
        if self.job_logger and len(self.items) % 10 == 0:  # 每10条记录一次
            self.job_logger.debug(f"已处理 {len(self.items)} 条数据")
        
        return item
    
    def close_spider(self, spider):
        """
        爬虫结束时调用
        
        Args:
            spider: 爬虫
        """
        # 写入JSON文件
        output_file = os.path.join(self.output_dir, f"{spider.name}_items.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.items, f, ensure_ascii=False, indent=2)
        
        # 记录完成日志
        if self.job_logger:
            self.job_logger.info(f"爬取完成，共写入 {len(self.items)} 条数据到 {output_file}")
        else:
            self.logger.info(f"爬取完成，共写入 {len(self.items)} 条数据到 {output_file}")


class DatabasePipeline:
    """
    将爬取的数据写入数据库的Pipeline
    """
    
    def __init__(self):
        """
        初始化Pipeline
        """
        self.db = None
        self.job_id = None
        self.site_config_id = None
        self.tenant_id = None
        self.items_count = 0
        self.items_failed = 0
        self.logger = logging.getLogger(__name__)
        self.job_logger = None
    
    @classmethod
    def from_crawler(cls, crawler):
        """
        从爬虫创建Pipeline
        
        Args:
            crawler: 爬虫
            
        Returns:
            DatabasePipeline: Pipeline实例
        """
        return cls()
    
    def open_spider(self, spider):
        """
        爬虫开始时调用
        
        Args:
            spider: 爬虫
        """
        # 获取数据库会话
        self.db = SessionLocal()
        
        # 获取爬虫的任务ID和站点配置ID
        self.job_id = getattr(spider, "job_id", None)
        self.site_config_id = getattr(spider, "site_config", None).id
        self.tenant_id = getattr(spider, "site_config", None).tenant_id
        
        # 获取任务日志记录器
        if self.job_id:
            self.job_logger = get_job_logger(self.job_id)
        
        if not self.job_id or not self.site_config_id or not self.tenant_id:
            if self.job_logger:
                self.job_logger.error("缺少必要的任务ID、站点配置ID或租户ID，无法写入数据库")
            else:
                self.logger.error("缺少必要的任务ID、站点配置ID或租户ID，无法写入数据库")
            return
        
        if self.job_logger:
            self.job_logger.info(f"DatabasePipeline启动，任务ID: {self.job_id}, 站点配置ID: {self.site_config_id}")
        else:
            self.logger.info(f"DatabasePipeline启动，任务ID: {self.job_id}, 站点配置ID: {self.site_config_id}")
    
    def process_item(self, item: Dict[str, Any], spider):
        """
        处理爬取的数据项
        
        Args:
            item: 数据项
            spider: 爬虫
            
        Returns:
            Dict[str, Any]: 处理后的数据项
        """
        if not self.db or not self.job_id or not self.site_config_id or not self.tenant_id:
            return item
        
        try:
            # 提取必要字段
            url = item.get("url")
            page_type = item.get("page_type", "unknown")
            title = item.get("title") or item.get("name")
            
            # 提取内容
            content = None
            if "description" in item:
                content = item["description"]
            elif "biography" in item:
                content = item["biography"]
            
            # 记录处理日志
            if self.job_logger:
                self.job_logger.debug(f"处理数据项: {title or url}, 类型: {page_type}")
            
            # 创建或更新数据项
            db_item = services.scraped_item.create_or_update(
                db=self.db,
                url=url,
                page_type=page_type,
                title=title,
                content=content,
                data=dict(item),
                job_id=self.job_id,
                site_config_id=self.site_config_id,
                tenant_id=self.tenant_id
            )
            
            self.items_count += 1
            
            # 更新任务进度
            if self.items_count % 10 == 0:  # 每10条更新一次
                services.job.update_status(
                    db=self.db,
                    job_id=self.job_id,
                    status_update={
                        "items_scraped": self.items_count,
                        "items_saved": self.items_count,
                        "items_failed": self.items_failed
                    }
                )
                
                if self.job_logger:
                    self.job_logger.info(f"进度更新: 已处理 {self.items_count} 条数据，失败 {self.items_failed} 条")
            
            return item
        except Exception as e:
            self.items_failed += 1
            
            error_msg = f"写入数据库失败: {e}"
            if self.job_logger:
                self.job_logger.error(error_msg)
            else:
                self.logger.exception(error_msg)
            
            return item
    
    def close_spider(self, spider):
        """
        爬虫结束时调用
        
        Args:
            spider: 爬虫
        """
        if self.db and self.job_id:
            try:
                # 更新任务状态
                services.job.update_status(
                    db=self.db,
                    job_id=self.job_id,
                    status_update={
                        "items_scraped": self.items_count,
                        "items_saved": self.items_count,
                        "items_failed": self.items_failed
                    }
                )
                
                completion_msg = f"爬取完成，共写入 {self.items_count} 条数据到数据库，失败 {self.items_failed} 条"
                if self.job_logger:
                    self.job_logger.info(completion_msg)
                else:
                    self.logger.info(completion_msg)
            except Exception as e:
                error_msg = f"更新任务状态失败: {e}"
                if self.job_logger:
                    self.job_logger.error(error_msg)
                else:
                    self.logger.exception(error_msg)
            finally:
                self.db.close() 