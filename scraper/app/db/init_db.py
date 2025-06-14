"""
数据库初始化脚本
"""
import logging
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.core.config import settings
from app.db.database import Base, engine

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db(db: Session) -> None:
    """
    初始化数据库
    
    Args:
        db: 数据库会话
    """
    # 创建超级用户
    user = services.user.get_by_username(db, username="admin")
    if not user:
        user_in = schemas.UserCreate(
            email="admin@example.com",
            username="admin",
            password="admin",
            full_name="Administrator",
            tenant_id="default",
            role="admin",
        )
        user = services.user.create(db, obj_in=user_in)
        logger.info(f"已创建超级用户: {user.username}")
    
    # 创建示例站点配置
    site = services.site.get_by_name(db, name="Example Site", tenant_id="default")
    if not site:
        site_in = schemas.SiteConfigCreate(
            name="Example Site",
            url="https://example.com",
            description="示例站点配置",
            tenant_id="default",
            config={
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "delay": 1.0,
            },
            start_urls=["https://example.com"],
            allowed_domains=["example.com"],
            list_page_xpath="//div[@class='list-item']",
            next_page_xpath="//a[@class='next-page']/@href",
            detail_page_xpath="//a[@class='item-title']/@href",
            field_mappings={
                "title": "//h1[@class='title']/text()",
                "content": "//div[@class='content']/text()",
                "date": "//span[@class='date']/text()",
            },
        )
        site = services.site.create(db, obj_in=site_in)
        logger.info(f"已创建示例站点配置: {site.name}")


def create_tables() -> None:
    """
    创建数据库表
    """
    logger.info("创建数据库表")
    Base.metadata.create_all(bind=engine)


def main() -> None:
    """
    主函数
    """
    logger.info("初始化数据库")
    create_tables()
    
    from app.db.database import SessionLocal
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()
    
    logger.info("数据库初始化完成")


if __name__ == "__main__":
    main() 