"""
爬取数据项服务模块
"""
from typing import List, Optional, Dict, Any

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app import models


def get(db: Session, item_id: int) -> Optional[models.ScrapedItem]:
    """
    通过ID获取爬取的数据项
    
    Args:
        db: 数据库会话
        item_id: 数据项ID
        
    Returns:
        Optional[models.ScrapedItem]: 数据项对象，如果不存在则返回None
    """
    return db.query(models.ScrapedItem).filter(models.ScrapedItem.id == item_id).first()


def get_by_url(db: Session, url: str, tenant_id: str) -> Optional[models.ScrapedItem]:
    """
    通过URL获取爬取的数据项
    
    Args:
        db: 数据库会话
        url: 数据项URL
        tenant_id: 租户ID
        
    Returns:
        Optional[models.ScrapedItem]: 数据项对象，如果不存在则返回None
    """
    return db.query(models.ScrapedItem).filter(
        and_(
            models.ScrapedItem.url == url,
            models.ScrapedItem.tenant_id == tenant_id
        )
    ).first()


def get_multi(
    db: Session, 
    *, 
    skip: int = 0, 
    limit: int = 100, 
    tenant_id: Optional[str] = None,
    job_id: Optional[int] = None,
    site_config_id: Optional[int] = None,
    page_type: Optional[str] = None
) -> List[models.ScrapedItem]:
    """
    获取多个爬取的数据项
    
    Args:
        db: 数据库会话
        skip: 跳过的记录数
        limit: 返回的最大记录数
        tenant_id: 租户ID，如果提供则过滤特定租户的数据项
        job_id: 任务ID，如果提供则过滤特定任务的数据项
        site_config_id: 站点配置ID，如果提供则过滤特定站点的数据项
        page_type: 页面类型，如果提供则过滤特定类型的数据项
        
    Returns:
        List[models.ScrapedItem]: 数据项对象列表
    """
    query = db.query(models.ScrapedItem)
    
    # 应用过滤条件
    if tenant_id:
        query = query.filter(models.ScrapedItem.tenant_id == tenant_id)
    if job_id:
        query = query.filter(models.ScrapedItem.job_id == job_id)
    if site_config_id:
        query = query.filter(models.ScrapedItem.site_config_id == site_config_id)
    if page_type:
        query = query.filter(models.ScrapedItem.page_type == page_type)
    
    return query.order_by(models.ScrapedItem.created_at.desc()).offset(skip).limit(limit).all()


def create(
    db: Session, 
    *, 
    url: str,
    page_type: str,
    title: Optional[str] = None,
    content: Optional[str] = None,
    data: Dict[str, Any] = None,
    job_id: int,
    site_config_id: int,
    tenant_id: str
) -> models.ScrapedItem:
    """
    创建爬取的数据项
    
    Args:
        db: 数据库会话
        url: 数据项URL
        page_type: 页面类型
        title: 标题
        content: 内容
        data: 爬取的数据
        job_id: 任务ID
        site_config_id: 站点配置ID
        tenant_id: 租户ID
        
    Returns:
        models.ScrapedItem: 创建的数据项对象
    """
    db_obj = models.ScrapedItem(
        url=url,
        page_type=page_type,
        title=title,
        content=content,
        data=data or {},
        job_id=job_id,
        site_config_id=site_config_id,
        tenant_id=tenant_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(
    db: Session, 
    *, 
    db_obj: models.ScrapedItem, 
    data: Dict[str, Any]
) -> models.ScrapedItem:
    """
    更新爬取的数据项
    
    Args:
        db: 数据库会话
        db_obj: 要更新的数据项对象
        data: 更新数据
        
    Returns:
        models.ScrapedItem: 更新后的数据项对象
    """
    # 更新对象属性
    for field, value in data.items():
        setattr(db_obj, field, value)
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete(db: Session, *, item_id: int) -> models.ScrapedItem:
    """
    删除爬取的数据项
    
    Args:
        db: 数据库会话
        item_id: 数据项ID
        
    Returns:
        models.ScrapedItem: 删除的数据项对象
    """
    obj = db.query(models.ScrapedItem).get(item_id)
    db.delete(obj)
    db.commit()
    return obj


def create_or_update(
    db: Session, 
    *, 
    url: str,
    page_type: str,
    title: Optional[str] = None,
    content: Optional[str] = None,
    data: Dict[str, Any] = None,
    job_id: int,
    site_config_id: int,
    tenant_id: str
) -> models.ScrapedItem:
    """
    创建或更新爬取的数据项
    
    Args:
        db: 数据库会话
        url: 数据项URL
        page_type: 页面类型
        title: 标题
        content: 内容
        data: 爬取的数据
        job_id: 任务ID
        site_config_id: 站点配置ID
        tenant_id: 租户ID
        
    Returns:
        models.ScrapedItem: 创建或更新的数据项对象
    """
    # 查找是否已存在
    db_obj = get_by_url(db, url=url, tenant_id=tenant_id)
    
    if db_obj:
        # 更新
        update_data = {
            "page_type": page_type,
            "title": title,
            "content": content,
            "data": data or {},
            "job_id": job_id,
            "site_config_id": site_config_id
        }
        return update(db, db_obj=db_obj, data=update_data)
    else:
        # 创建
        return create(
            db,
            url=url,
            page_type=page_type,
            title=title,
            content=content,
            data=data or {},
            job_id=job_id,
            site_config_id=site_config_id,
            tenant_id=tenant_id
        ) 