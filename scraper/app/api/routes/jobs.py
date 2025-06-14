"""
爬虫任务相关的API路由
"""
from typing import Any, List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.db.database import get_db

router = APIRouter()


@router.get("/jobs", response_model=List[schemas.Job])
def read_jobs(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取任务列表
    """
    # 获取当前用户所属租户的任务
    jobs = services.job.get_multi(
        db, skip=skip, limit=limit, tenant_id=current_user.tenant_id
    )
    return jobs


@router.post("/jobs", response_model=schemas.Job)
def create_job(
    *,
    db: Session = Depends(get_db),
    job_in: schemas.JobCreate,
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    创建新的爬虫任务
    """
    # 检查站点配置是否存在
    site = services.site.get(db, site_id=job_in.site_config_id)
    if not site:
        raise HTTPException(
            status_code=404,
            detail="站点配置不存在",
        )
    
    # 检查租户权限
    if site.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="没有访问权限")
    
    # 确保使用当前用户的租户ID
    job_in.tenant_id = current_user.tenant_id
    
    # 创建任务
    job = services.job.create(db, obj_in=job_in, user_id=current_user.id)
    
    # 在后台启动爬虫任务
    # 注意：实际实现需要通过Celery Worker执行
    # background_tasks.add_task(run_spider_task, job.id)
    
    return job


@router.get("/jobs/{job_id}", response_model=schemas.Job)
def read_job(
    *,
    db: Session = Depends(get_db),
    job_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取特定任务
    """
    job = services.job.get(db, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 检查租户权限
    if job.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="没有访问权限")
    
    return job


@router.put("/jobs/{job_id}/status", response_model=schemas.Job)
def update_job_status(
    *,
    db: Session = Depends(get_db),
    job_id: int,
    status_update: schemas.JobStatusUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    更新任务状态
    """
    job = services.job.get(db, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 检查租户权限
    if job.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="没有访问权限")
    
    # 更新任务状态
    job = services.job.update_status(db, job_id=job_id, status_update=status_update)
    return job


@router.delete("/jobs/{job_id}", response_model=schemas.Job)
def delete_job(
    *,
    db: Session = Depends(get_db),
    job_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    删除任务
    """
    job = services.job.get(db, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 检查租户权限
    if job.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="没有访问权限")
    
    # 检查是否有超级用户权限或编辑权限
    if not current_user.is_superuser and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="没有删除权限")
    
    # 如果任务正在运行，先取消任务
    if job.status == "running" and job.celery_task_id:
        # 实际实现需要通过Celery取消任务
        # celery_app.control.revoke(job.celery_task_id, terminate=True)
        pass
    
    # 删除任务
    job = services.job.delete(db, job_id=job_id)
    return job 