"""
用户相关的Pydantic模式
"""
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """用户基础模式"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = True
    full_name: Optional[str] = None
    role: Optional[str] = "viewer"


class UserCreate(UserBase):
    """创建用户的请求模式"""
    email: EmailStr
    username: str
    password: str
    tenant_id: str


class UserUpdate(UserBase):
    """更新用户的请求模式"""
    password: Optional[str] = None


class UserInDBBase(UserBase):
    """数据库中的用户模式基类"""
    id: Optional[int] = None
    tenant_id: str
    
    class Config:
        orm_mode = True


class User(UserInDBBase):
    """API响应中的用户模式"""
    pass


class UserInDB(UserInDBBase):
    """数据库中的用户模式，包含哈希密码"""
    hashed_password: str


class Token(BaseModel):
    """令牌响应模式"""
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """令牌载荷模式"""
    sub: Optional[int] = None 