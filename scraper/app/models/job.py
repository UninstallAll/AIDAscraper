"""
爬虫任务模型
"""
from sqlalchemy import Boolean, Column, Integer, String, DateTime, JSON, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.database import Base


class Job(Base):
    """爬虫任务模型"""
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    site_config_id = Column(Integer, ForeignKey("site_configs.id"))
    status = Column(String, default="pending")  # pending, running, completed, failed, cancelled
    progress = Column(Integer, default=0)  # 0-100
    error_message = Column(Text, nullable=True)
    config = Column(JSON, default=dict)
    celery_task_id = Column(String, nullable=True)
    items_scraped = Column(Integer, default=0)
    items_saved = Column(Integer, default=0)
    schedule_type = Column(String, default="once")  # once, daily, weekly, monthly, cron
    cron_expression = Column(String, nullable=True)
    tenant_id = Column(String, nullable=False, index=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # 关系
    site_config = relationship("SiteConfig", backref="jobs")
    created_by = relationship("User", backref="jobs")

    def __repr__(self):
        return f"<Job {self.name} ({self.status})>" 