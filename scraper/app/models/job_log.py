"""
爬虫任务日志模型
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class JobLog(Base):
    """
    爬虫任务日志模型
    """
    __tablename__ = "job_logs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    level = Column(String(10), nullable=False, index=True)  # INFO, WARNING, ERROR, DEBUG
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.now, nullable=False, index=True)
    
    # 关系
    job = relationship("Job", back_populates="logs")
    
    def __repr__(self):
        return f"<JobLog(id={self.id}, job_id={self.job_id}, level={self.level})>" 