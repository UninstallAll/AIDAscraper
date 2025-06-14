"""
数据库基础模块 - 导入所有模型以解决循环依赖
"""
# 导入基类
from app.db.base_class import Base

# 导入所有模型，以便Alembic可以自动检测它们
from app.models.user import User
from app.models.site import SiteConfig
from app.models.job import Job
from app.models.job_log import JobLog
from app.models.scraped_item import ScrapedItem 