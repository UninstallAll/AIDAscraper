"""
爬虫任务相关的Pydantic模式
"""
from datetime import datetime
from typing import Dict, Optional, Any, List

from pydantic import BaseModel, Field

from app.schemas.site import SiteConfig


class JobBase(BaseModel):
    """任务基础模式"""
    name: Optional[str] = None
    site_config_id: Optional[int] = None
    config: Optional[Dict[str, Any]] = Field(default_factory=dict)
    schedule_type: Optional[str] = "once"
    cron_expression: Optional[str] = None


class JobCreate(JobBase):
    """创建任务的请求模式"""
    name: str
    site_config_id: int
    tenant_id: str


class JobUpdate(JobBase):
    """更新任务的请求模式"""
    celery_task_id: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[int] = None
    error_message: Optional[str] = None
    items_scraped: Optional[int] = None
    items_saved: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class JobStatusUpdate(BaseModel):
    """任务状态更新的请求模式"""
    status: Optional[str] = None
    progress: Optional[int] = None
    error_message: Optional[str] = None
    items_scraped: Optional[int] = None
    items_saved: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class JobInDBBase(JobBase):
    """数据库中的任务模式基类"""
    id: int
    status: str
    progress: int
    error_message: Optional[str] = None
    config: Dict[str, Any]
    celery_task_id: Optional[str] = None
    items_scraped: int
    items_saved: int
    tenant_id: str
    created_by_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True


class Job(JobInDBBase):
    """API响应中的任务模式"""
    site_config: Optional[SiteConfig] = None


class JobInDB(JobInDBBase):
    """数据库中的任务模式"""
    pass


class JobWithSiteConfig(Job):
    """包含站点配置的任务模式"""
    site_config: Any  # 避免循环导入


class JobStats(BaseModel):
    """任务统计信息"""
    total: int
    pending: int
    running: int
    completed: int
    failed: int
    cancelled: int 