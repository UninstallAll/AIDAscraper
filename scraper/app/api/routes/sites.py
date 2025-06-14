"""
站点配置相关的API路由
"""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.db.database import get_db

router = APIRouter()


@router.get("/sites", response_model=List[schemas.SiteConfig])
def read_sites(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取站点配置列表
    """
    # 获取当前用户所属租户的站点配置
    sites = services.site.get_multi(
        db, skip=skip, limit=limit, tenant_id=current_user.tenant_id
    )
    return sites


@router.post("/sites", response_model=schemas.SiteConfig)
def create_site(
    *,
    db: Session = Depends(get_db),
    site_in: schemas.SiteConfigCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    创建新的站点配置
    """
    # 检查名称是否已被使用
    site = services.site.get_by_name(
        db, name=site_in.name, tenant_id=current_user.tenant_id
    )
    if site:
        raise HTTPException(
            status_code=400,
            detail="该站点名称已被使用",
        )
    
    # 确保使用当前用户的租户ID
    site_in.tenant_id = current_user.tenant_id
    
    # 创建站点
    site = services.site.create(db, obj_in=site_in)
    return site


@router.get("/sites/{site_id}", response_model=schemas.SiteConfig)
def read_site(
    *,
    db: Session = Depends(get_db),
    site_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取特定站点配置
    """
    site = services.site.get(db, site_id=site_id)
    if not site:
        raise HTTPException(status_code=404, detail="站点配置不存在")
    
    # 检查租户权限
    if site.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="没有访问权限")
    
    return site


@router.put("/sites/{site_id}", response_model=schemas.SiteConfig)
def update_site(
    *,
    db: Session = Depends(get_db),
    site_id: int,
    site_in: schemas.SiteConfigUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    更新站点配置
    """
    site = services.site.get(db, site_id=site_id)
    if not site:
        raise HTTPException(status_code=404, detail="站点配置不存在")
    
    # 检查租户权限
    if site.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="没有访问权限")
    
    # 更新站点
    site = services.site.update(db, db_obj=site, obj_in=site_in)
    return site


@router.delete("/sites/{site_id}", response_model=schemas.SiteConfig)
def delete_site(
    *,
    db: Session = Depends(get_db),
    site_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    删除站点配置
    """
    site = services.site.get(db, site_id=site_id)
    if not site:
        raise HTTPException(status_code=404, detail="站点配置不存在")
    
    # 检查租户权限
    if site.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="没有访问权限")
    
    # 检查是否有超级用户权限或编辑权限
    if not current_user.is_superuser and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="没有删除权限")
    
    # 删除站点
    site = services.site.delete(db, site_id=site_id)
    return site 