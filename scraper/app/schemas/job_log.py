"""
任务日志的Pydantic模型
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class JobLogBase(BaseModel):
    """任务日志基础模型"""
    job_id: int
    level: str
    message: str


class JobLogCreate(JobLogBase):
    """创建任务日志模型"""
    timestamp: Optional[datetime] = None


class JobLogUpdate(BaseModel):
    """更新任务日志模型"""
    level: Optional[str] = None
    message: Optional[str] = None


class JobLog(JobLogBase):
    """任务日志模型"""
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True 