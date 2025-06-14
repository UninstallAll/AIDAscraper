"""
任务日志服务
"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app import models, schemas


def get(db: Session, log_id: int) -> Optional[models.JobLog]:
    """
    获取单个日志记录
    
    Args:
        db: 数据库会话
        log_id: 日志ID
    
    Returns:
        Optional[models.JobLog]: 日志记录
    """
    return db.query(models.JobLog).filter(models.JobLog.id == log_id).first()


def get_multi(
    db: Session, 
    job_id: int, 
    skip: int = 0, 
    limit: int = 100,
    level: Optional[str] = None
) -> List[models.JobLog]:
    """
    获取任务的多个日志记录
    
    Args:
        db: 数据库会话
        job_id: 任务ID
        skip: 跳过的记录数
        limit: 返回的记录数
        level: 日志级别过滤
    
    Returns:
        List[models.JobLog]: 日志记录列表
    """
    query = db.query(models.JobLog).filter(models.JobLog.job_id == job_id)
    
    if level:
        query = query.filter(models.JobLog.level == level)
    
    return query.order_by(models.JobLog.timestamp.desc()).offset(skip).limit(limit).all()


def create(db: Session, obj_in: schemas.JobLogCreate) -> models.JobLog:
    """
    创建日志记录
    
    Args:
        db: 数据库会话
        obj_in: 日志创建模型
    
    Returns:
        models.JobLog: 创建的日志记录
    """
    db_obj = models.JobLog(
        job_id=obj_in.job_id,
        level=obj_in.level,
        message=obj_in.message,
        timestamp=obj_in.timestamp or datetime.now()
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(
    db: Session, 
    db_obj: models.JobLog, 
    obj_in: schemas.JobLogUpdate
) -> models.JobLog:
    """
    更新日志记录
    
    Args:
        db: 数据库会话
        db_obj: 数据库对象
        obj_in: 更新模型
    
    Returns:
        models.JobLog: 更新后的日志记录
    """
    update_data = obj_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete(db: Session, log_id: int) -> models.JobLog:
    """
    删除日志记录
    
    Args:
        db: 数据库会话
        log_id: 日志ID
    
    Returns:
        models.JobLog: 删除的日志记录
    """
    obj = db.query(models.JobLog).get(log_id)
    db.delete(obj)
    db.commit()
    return obj


def delete_by_job(db: Session, job_id: int) -> int:
    """
    删除任务的所有日志记录
    
    Args:
        db: 数据库会话
        job_id: 任务ID
    
    Returns:
        int: 删除的记录数
    """
    result = db.query(models.JobLog).filter(models.JobLog.job_id == job_id).delete()
    db.commit()
    return result 