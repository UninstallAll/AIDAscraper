"""
E2E演示：抓取艺术网站并将数据写入数据库
"""
import argparse
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy.orm import Session

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.db.database import SessionLocal, engine
from app.models.scraped_item import ScrapedItem
from app import models, services
from app.scrapers.run_spider import run_spider

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def ensure_database_tables():
    """
    确保数据库表已创建
    """
    # 创建表
    models.Base.metadata.create_all(bind=engine)
    logger.info("数据库表已创建")


def create_test_site_config(db: Session, config_file: str) -> models.SiteConfig:
    """
    创建测试站点配置
    
    Args:
        db: 数据库会话
        config_file: 配置文件路径
        
    Returns:
        models.SiteConfig: 站点配置对象
    """
    # 加载配置
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 查找是否已存在
    site = db.query(models.SiteConfig).filter(
        models.SiteConfig.name == config['name'],
        models.SiteConfig.tenant_id == 'test'
    ).first()
    
    if site:
        logger.info(f"站点配置已存在: {site.name}")
        return site
    
    # 创建站点配置
    site = models.SiteConfig(
        name=config['name'],
        url=config['url'],
        description=config.get('description', ''),
        requires_login=config.get('requires_login', False),
        login_url=config.get('login_url', ''),
        login_username_field=config.get('login_username_field', ''),
        login_password_field=config.get('login_password_field', ''),
        login_username=config.get('login_username', ''),
        login_password=config.get('login_password', ''),
        start_urls=config.get('start_urls', [config['url']]),
        allowed_domains=config.get('allowed_domains', []),
        list_page_xpath=config.get('list_page_xpath', ''),
        next_page_xpath=config.get('next_page_xpath', ''),
        detail_page_xpath=config.get('detail_page_xpath', ''),
        field_mappings=config.get('field_mappings', {}),
        use_playwright=config.get('use_playwright', False),
        config=config.get('config', {}),
        tenant_id='test',
        is_active=True
    )
    
    db.add(site)
    db.commit()
    db.refresh(site)
    
    logger.info(f"站点配置已创建: {site.name}")
    return site


def create_test_job(db: Session, site_config: models.SiteConfig) -> models.Job:
    """
    创建测试任务
    
    Args:
        db: 数据库会话
        site_config: 站点配置对象
        
    Returns:
        models.Job: 任务对象
    """
    # 创建任务
    job = models.Job(
        name=f"{site_config.name} Demo Job",
        site_config_id=site_config.id,
        config={},
        status="pending",
        progress=0,
        items_scraped=0,
        items_saved=0,
        schedule_type="once",
        tenant_id='test'
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    logger.info(f"任务已创建: {job.name}")
    return job


def check_scraped_items(db: Session, job_id: int) -> int:
    """
    检查爬取的数据项
    
    Args:
        db: 数据库会话
        job_id: 任务ID
        
    Returns:
        int: 数据项数量
    """
    # 查询数据项
    items = db.query(ScrapedItem).filter(ScrapedItem.job_id == job_id).all()
    
    # 按类型统计
    types = {}
    for item in items:
        if item.page_type not in types:
            types[item.page_type] = 0
        types[item.page_type] += 1
    
    # 输出统计信息
    logger.info(f"共爬取 {len(items)} 条数据:")
    for page_type, count in types.items():
        logger.info(f"  - {page_type}: {count} 条")
    
    return len(items)


def run_e2e_demo(config_file: str, output_dir: str = 'output'):
    """
    运行E2E演示
    
    Args:
        config_file: 配置文件路径
        output_dir: 输出目录
    """
    # 确保数据库表已创建
    ensure_database_tables()
    
    # 获取数据库会话
    db = SessionLocal()
    
    try:
        # 创建测试站点配置
        site_config = create_test_site_config(db, config_file)
        
        # 创建测试任务
        job = create_test_job(db, site_config)
        
        # 更新任务状态为运行中
        job = services.job.update_status(
            db, 
            job_id=job.id, 
            status_update={
                "status": "running",
                "started_at": datetime.now()
            }
        )
        
        # 运行爬虫
        logger.info(f"开始运行爬虫: {site_config.name}")
        run_spider(config_file, output_dir)
        
        # 检查爬取的数据项
        item_count = check_scraped_items(db, job.id)
        
        # 更新任务状态为完成
        job = services.job.update_status(
            db, 
            job_id=job.id, 
            status_update={
                "status": "completed",
                "progress": 100,
                "completed_at": datetime.now()
            }
        )
        
        # 判断是否成功
        if item_count >= 50:
            logger.info("E2E演示成功！爬取数据超过50条")
        else:
            logger.warning(f"E2E演示完成，但爬取数据不足50条 (实际: {item_count})")
    
    except Exception as e:
        logger.exception(f"E2E演示失败: {e}")
    finally:
        db.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='E2E演示：抓取艺术网站并将数据写入数据库')
    parser.add_argument('--config', '-c', default='scraper/app/scrapers/spiders/example_config.json', help='配置文件路径')
    parser.add_argument('--output', '-o', default='output', help='输出目录')
    
    args = parser.parse_args()
    
    run_e2e_demo(args.config, args.output) 