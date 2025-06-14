"""
数据库连接模块
"""
import logging
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建SQLAlchemy引擎
# 如果是SQLite，需要添加connect_args={"check_same_thread": False}
database_url = str(settings.DATABASE_URL)
if database_url.startswith("sqlite"):
    engine = create_engine(
        database_url, 
        connect_args={"check_same_thread": False},
        pool_pre_ping=True
    )
else:
    engine = create_engine(database_url, pool_pre_ping=True)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


def get_db() -> Generator:
    """
    获取数据库会话
    
    Yields:
        Generator: 数据库会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 