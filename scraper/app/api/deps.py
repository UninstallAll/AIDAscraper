"""
API依赖函数
"""
from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import models, schemas
from app.core import security
from app.core.config import settings
from app.db.database import get_db

# OAuth2密码流的令牌URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> models.User:
    """
    获取当前用户
    
    Args:
        db: 数据库会话
        token: JWT令牌
        
    Returns:
        models.User: 当前用户对象
        
    Raises:
        HTTPException: 如果令牌无效或用户不存在
    """
    try:
        # 解码令牌
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无法验证凭据",
        )
    # 获取用户
    user = db.query(models.User).filter(models.User.id == token_data.sub).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="用户未激活")
    return user


def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    获取当前激活的用户
    
    Args:
        current_user: 当前用户对象
        
    Returns:
        models.User: 当前激活的用户对象
        
    Raises:
        HTTPException: 如果用户未激活
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="用户未激活")
    return current_user


def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    获取当前激活的超级用户
    
    Args:
        current_user: 当前用户对象
        
    Returns:
        models.User: 当前激活的超级用户对象
        
    Raises:
        HTTPException: 如果用户不是超级用户
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="用户权限不足，需要超级管理员权限"
        )
    return current_user


def get_tenant_id_from_user(
    current_user: models.User = Depends(get_current_active_user),
) -> str:
    """
    从当前用户获取租户ID
    
    Args:
        current_user: 当前用户对象
        
    Returns:
        str: 租户ID
    """
    return current_user.tenant_id 