"""
数据库模型
"""
from app.db.base_class import Base
from app.models.user import User
from app.models.site import SiteConfig
from app.models.job_log import JobLog
from app.models.job import Job
from app.models.scraped_item import ScrapedItem 