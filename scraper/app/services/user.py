"""
用户服务模块
"""
from typing import Optional

from sqlalchemy.orm import Session

from app import models, schemas
from app.core.security import get_password_hash, verify_password


def get_by_email(db: Session, email: str) -> Optional[models.User]:
    """
    通过邮箱获取用户
    
    Args:
        db: 数据库会话
        email: 用户邮箱
        
    Returns:
        Optional[models.User]: 用户对象，如果不存在则返回None
    """
    return db.query(models.User).filter(models.User.email == email).first()


def get_by_username(db: Session, username: str) -> Optional[models.User]:
    """
    通过用户名获取用户
    
    Args:
        db: 数据库会话
        username: 用户名
        
    Returns:
        Optional[models.User]: 用户对象，如果不存在则返回None
    """
    return db.query(models.User).filter(models.User.username == username).first()


def get(db: Session, user_id: int) -> Optional[models.User]:
    """
    通过ID获取用户
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        
    Returns:
        Optional[models.User]: 用户对象，如果不存在则返回None
    """
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_multi(
    db: Session, *, skip: int = 0, limit: int = 100, tenant_id: Optional[str] = None
):
    """
    获取多个用户
    
    Args:
        db: 数据库会话
        skip: 跳过的记录数
        limit: 返回的最大记录数
        tenant_id: 租户ID，如果提供则过滤特定租户的用户
        
    Returns:
        List[models.User]: 用户对象列表
    """
    query = db.query(models.User)
    if tenant_id:
        query = query.filter(models.User.tenant_id == tenant_id)
    return query.offset(skip).limit(limit).all()


def create(db: Session, *, obj_in: schemas.UserCreate) -> models.User:
    """
    创建用户
    
    Args:
        db: 数据库会话
        obj_in: 用户创建请求数据
        
    Returns:
        models.User: 创建的用户对象
    """
    db_obj = models.User(
        email=obj_in.email,
        username=obj_in.username,
        hashed_password=get_password_hash(obj_in.password),
        full_name=obj_in.full_name,
        is_superuser=False,
        is_active=True,
        tenant_id=obj_in.tenant_id,
        role=obj_in.role or "viewer",
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(
    db: Session, *, db_obj: models.User, obj_in: schemas.UserUpdate
) -> models.User:
    """
    更新用户
    
    Args:
        db: 数据库会话
        db_obj: 要更新的用户对象
        obj_in: 用户更新请求数据
        
    Returns:
        models.User: 更新后的用户对象
    """
    update_data = obj_in.dict(exclude_unset=True)
    if update_data.get("password"):
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password
    
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def authenticate(
    db: Session, *, username: str, password: str
) -> Optional[models.User]:
    """
    认证用户
    
    Args:
        db: 数据库会话
        username: 用户名
        password: 密码
        
    Returns:
        Optional[models.User]: 认证成功的用户对象，如果认证失败则返回None
    """
    user = get_by_username(db, username=username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def is_active(user: models.User) -> bool:
    """
    检查用户是否激活
    
    Args:
        user: 用户对象
        
    Returns:
        bool: 用户是否激活
    """
    return user.is_active


def is_superuser(user: models.User) -> bool:
    """
    检查用户是否是超级用户
    
    Args:
        user: 用户对象
        
    Returns:
        bool: 用户是否是超级用户
    """
    return user.is_superuser 