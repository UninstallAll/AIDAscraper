"""
站点配置服务模块
"""
from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session

from app import models, schemas


def get(db: Session, site_id: int) -> Optional[models.SiteConfig]:
    """
    通过ID获取站点配置
    
    Args:
        db: 数据库会话
        site_id: 站点配置ID
        
    Returns:
        Optional[models.SiteConfig]: 站点配置对象，如果不存在则返回None
    """
    return db.query(models.SiteConfig).filter(models.SiteConfig.id == site_id).first()


def get_by_name(db: Session, name: str, tenant_id: str) -> Optional[models.SiteConfig]:
    """
    通过名称和租户ID获取站点配置
    
    Args:
        db: 数据库会话
        name: 站点名称
        tenant_id: 租户ID
        
    Returns:
        Optional[models.SiteConfig]: 站点配置对象，如果不存在则返回None
    """
    return db.query(models.SiteConfig).filter(
        models.SiteConfig.name == name,
        models.SiteConfig.tenant_id == tenant_id
    ).first()


def get_multi(
    db: Session, *, skip: int = 0, limit: int = 100, tenant_id: Optional[str] = None
) -> List[models.SiteConfig]:
    """
    获取多个站点配置
    
    Args:
        db: 数据库会话
        skip: 跳过的记录数
        limit: 返回的最大记录数
        tenant_id: 租户ID，如果提供则过滤特定租户的站点配置
        
    Returns:
        List[models.SiteConfig]: 站点配置对象列表
    """
    query = db.query(models.SiteConfig)
    if tenant_id:
        query = query.filter(models.SiteConfig.tenant_id == tenant_id)
    return query.offset(skip).limit(limit).all()


def create(db: Session, *, obj_in: schemas.SiteConfigCreate) -> models.SiteConfig:
    """
    创建站点配置
    
    Args:
        db: 数据库会话
        obj_in: 站点配置创建请求数据
        
    Returns:
        models.SiteConfig: 创建的站点配置对象
    """
    # 从URL推断allowed_domains，如果没有提供
    if not obj_in.allowed_domains and obj_in.url:
        from urllib.parse import urlparse
        domain = urlparse(obj_in.url).netloc
        allowed_domains = [domain]
    else:
        allowed_domains = obj_in.allowed_domains or []
    
    # 如果没有提供start_urls，使用主URL
    start_urls = obj_in.start_urls or [obj_in.url]
    
    db_obj = models.SiteConfig(
        name=obj_in.name,
        url=obj_in.url,
        description=obj_in.description,
        config=obj_in.config,
        requires_login=obj_in.requires_login,
        login_url=obj_in.login_url,
        login_username_field=obj_in.login_username_field,
        login_password_field=obj_in.login_password_field,
        login_username=obj_in.login_username,
        login_password=obj_in.login_password,
        start_urls=start_urls,
        allowed_domains=allowed_domains,
        list_page_xpath=obj_in.list_page_xpath,
        next_page_xpath=obj_in.next_page_xpath,
        detail_page_xpath=obj_in.detail_page_xpath,
        field_mappings=obj_in.field_mappings or {},
        use_playwright=obj_in.use_playwright,
        tenant_id=obj_in.tenant_id,
        is_active=True,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(
    db: Session, *, db_obj: models.SiteConfig, obj_in: schemas.SiteConfigUpdate
) -> models.SiteConfig:
    """
    更新站点配置
    
    Args:
        db: 数据库会话
        db_obj: 要更新的站点配置对象
        obj_in: 站点配置更新请求数据
        
    Returns:
        models.SiteConfig: 更新后的站点配置对象
    """
    update_data = obj_in.dict(exclude_unset=True)
    
    # 处理特殊字段
    if "url" in update_data and not update_data.get("allowed_domains"):
        from urllib.parse import urlparse
        domain = urlparse(update_data["url"]).netloc
        update_data["allowed_domains"] = [domain]
    
    if "url" in update_data and not update_data.get("start_urls"):
        update_data["start_urls"] = [update_data["url"]]
    
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete(db: Session, *, site_id: int) -> models.SiteConfig:
    """
    删除站点配置
    
    Args:
        db: 数据库会话
        site_id: 站点配置ID
        
    Returns:
        models.SiteConfig: 删除的站点配置对象
    """
    obj = db.query(models.SiteConfig).get(site_id)
    db.delete(obj)
    db.commit()
    return obj 