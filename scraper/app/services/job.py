"""
爬虫任务服务模块
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app import models, schemas


def get(db: Session, job_id: int) -> Optional[models.Job]:
    """
    通过ID获取任务
    
    Args:
        db: 数据库会话
        job_id: 任务ID
        
    Returns:
        Optional[models.Job]: 任务对象，如果不存在则返回None
    """
    return db.query(models.Job).filter(models.Job.id == job_id).first()


def get_by_celery_id(db: Session, celery_task_id: str) -> Optional[models.Job]:
    """
    通过Celery任务ID获取任务
    
    Args:
        db: 数据库会话
        celery_task_id: Celery任务ID
        
    Returns:
        Optional[models.Job]: 任务对象，如果不存在则返回None
    """
    return db.query(models.Job).filter(models.Job.celery_task_id == celery_task_id).first()


def get_multi(
    db: Session, *, skip: int = 0, limit: int = 100, tenant_id: Optional[str] = None
) -> List[models.Job]:
    """
    获取多个任务
    
    Args:
        db: 数据库会话
        skip: 跳过的记录数
        limit: 返回的最大记录数
        tenant_id: 租户ID，如果提供则过滤特定租户的任务
        
    Returns:
        List[models.Job]: 任务对象列表
    """
    query = db.query(models.Job)
    if tenant_id:
        query = query.filter(models.Job.tenant_id == tenant_id)
    return query.order_by(models.Job.created_at.desc()).offset(skip).limit(limit).all()


def create(db: Session, *, obj_in: schemas.JobCreate, user_id: int) -> models.Job:
    """
    创建任务
    
    Args:
        db: 数据库会话
        obj_in: 任务创建请求数据
        user_id: 创建者用户ID
        
    Returns:
        models.Job: 创建的任务对象
    """
    db_obj = models.Job(
        name=obj_in.name,
        site_config_id=obj_in.site_config_id,
        config=obj_in.config or {},
        status="pending",
        progress=0,
        items_scraped=0,
        items_saved=0,
        schedule_type=obj_in.schedule_type,
        cron_expression=obj_in.cron_expression,
        tenant_id=obj_in.tenant_id,
        created_by_id=user_id,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(
    db: Session, *, db_obj: models.Job, obj_in: Union[schemas.JobUpdate, Dict[str, Any]]
) -> models.Job:
    """
    更新任务
    
    Args:
        db: 数据库会话
        db_obj: 要更新的任务对象
        obj_in: 任务更新请求数据
        
    Returns:
        models.Job: 更新后的任务对象
    """
    update_data = obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_status(
    db: Session, *, job_id: int, status_update: schemas.JobStatusUpdate
) -> models.Job:
    """
    更新任务状态
    
    Args:
        db: 数据库会话
        job_id: 任务ID
        status_update: 状态更新数据
        
    Returns:
        models.Job: 更新后的任务对象
    """
    job = get(db, job_id=job_id)
    if not job:
        raise ValueError(f"任务不存在: {job_id}")
    
    # 更新状态
    if status_update.status:
        job.status = status_update.status
    
    # 更新进度
    if status_update.progress is not None:
        job.progress = status_update.progress
    
    # 更新错误信息
    if status_update.error_message:
        job.error_message = status_update.error_message
    
    # 更新抓取和保存的项目数
    if status_update.items_scraped is not None:
        job.items_scraped = status_update.items_scraped
    
    if status_update.items_saved is not None:
        job.items_saved = status_update.items_saved
    
    # 更新开始和完成时间
    if status_update.started_at:
        job.started_at = status_update.started_at
    
    if status_update.completed_at:
        job.completed_at = status_update.completed_at
    
    # 如果状态是completed或failed，自动设置完成时间
    if status_update.status in ["completed", "failed"] and not job.completed_at:
        job.completed_at = datetime.now()
    
    # 保存更新
    job.updated_at = datetime.now()
    db.add(job)
    db.commit()
    db.refresh(job)
    
    return job


def delete(db: Session, *, job_id: int) -> models.Job:
    """
    删除任务
    
    Args:
        db: 数据库会话
        job_id: 任务ID
        
    Returns:
        models.Job: 删除的任务对象
    """
    obj = db.query(models.Job).get(job_id)
    db.delete(obj)
    db.commit()
    return obj


def find_stalled_jobs(db: Session, minutes: int = 30) -> List[models.Job]:
    """
    查找卡住的任务
    
    Args:
        db: 数据库会话
        minutes: 多少分钟未更新视为卡住
        
    Returns:
        List[models.Job]: 卡住的任务列表
    """
    # 计算截止时间
    cutoff_time = datetime.now() - timedelta(minutes=minutes)
    
    # 查找状态为running但长时间未更新的任务
    stalled_jobs = db.query(models.Job).filter(
        and_(
            models.Job.status == "running",
            or_(
                models.Job.updated_at < cutoff_time,
                models.Job.updated_at.is_(None)
            ),
            models.Job.completed_at.is_(None)
        )
    ).all()
    
    return stalled_jobs 