"""
爬虫任务相关的API路由
"""
from typing import Any, List, Optional
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.db.database import get_db
from app.core.websocket_manager import manager

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


@router.get("/jobs/{job_id}/logs", response_model=List[schemas.JobLog])
def read_job_logs(
    *,
    db: Session = Depends(get_db),
    job_id: int,
    skip: int = 0,
    limit: int = 100,
    level: Optional[str] = None,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取任务日志
    """
    # 检查任务是否存在
    job = services.job.get(db, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 检查租户权限
    if job.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="没有访问权限")
    
    # 获取日志
    logs = services.job_log.get_multi(
        db, job_id=job_id, skip=skip, limit=limit, level=level
    )
    return logs


@router.websocket("/ws/jobs/{job_id}/logs")
async def websocket_job_logs(
    websocket: WebSocket,
    job_id: int,
    token: str = None,
):
    """
    WebSocket端点，用于实时获取任务日志
    """
    # 这里可以添加认证逻辑，但为了简单起见，我们暂时不做认证
    # 在实际生产环境中，应该验证token并检查用户权限
    
    # 生成客户端ID
    client_id = str(uuid.uuid4())
    
    # 接受WebSocket连接
    await manager.connect(websocket, job_id, client_id)
    
    try:
        # 发送初始消息
        await websocket.send_json({
            "type": "connection_established",
            "message": "已连接到任务日志WebSocket",
            "job_id": job_id
        })
        
        # 等待消息
        while True:
            # 接收客户端消息（心跳检测等）
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        # 客户端断开连接
        manager.disconnect(job_id, client_id)
    except Exception as e:
        # 其他异常
        manager.disconnect(job_id, client_id)


@router.post("/jobs/{job_id}/start", response_model=schemas.Job)
def start_job(
    *,
    db: Session = Depends(get_db),
    job_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    启动任务
    """
    job = services.job.get(db, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 检查租户权限
    if job.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="没有访问权限")
    
    # 检查任务状态
    if job.status not in ["pending", "failed", "cancelled"]:
        raise HTTPException(status_code=400, detail=f"任务状态为 {job.status}，无法启动")
    
    # 启动任务
    job = services.job.start_job(db, job_id=job_id)
    return job


@router.post("/jobs/{job_id}/cancel", response_model=schemas.Job)
def cancel_job(
    *,
    db: Session = Depends(get_db),
    job_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    取消任务
    """
    job = services.job.get(db, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 检查租户权限
    if job.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="没有访问权限")
    
    # 检查任务状态
    if job.status not in ["pending", "running"]:
        raise HTTPException(status_code=400, detail=f"任务状态为 {job.status}，无法取消")
    
    # 取消任务
    job = services.job.cancel_job(db, job_id=job_id)
    return job 