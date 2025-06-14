"""
站点配置相关的Pydantic模式
"""
from typing import Dict, List, Optional, Any, Union

from pydantic import BaseModel, HttpUrl, Field


class SiteConfigBase(BaseModel):
    """站点配置基础模式"""
    name: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    requires_login: Optional[bool] = False
    login_url: Optional[str] = None
    login_username_field: Optional[str] = None
    login_password_field: Optional[str] = None
    login_username: Optional[str] = None
    login_password: Optional[str] = None
    start_urls: Optional[List[str]] = None
    allowed_domains: Optional[List[str]] = None
    list_page_xpath: Optional[str] = None
    next_page_xpath: Optional[str] = None
    detail_page_xpath: Optional[str] = None
    field_mappings: Optional[Dict[str, str]] = None
    use_playwright: Optional[bool] = False
    config: Optional[Dict[str, Any]] = Field(default_factory=dict)


class SiteConfigCreate(SiteConfigBase):
    """创建站点配置的请求模式"""
    name: str
    url: str
    tenant_id: str
    config: Dict[str, Any]


class SiteConfigUpdate(SiteConfigBase):
    """更新站点配置的请求模式"""
    pass


class SiteConfigInDBBase(SiteConfigBase):
    """数据库中的站点配置模式基类"""
    id: int
    tenant_id: str
    is_active: bool
    
    class Config:
        orm_mode = True


class SiteConfig(SiteConfigInDBBase):
    """API响应中的站点配置模式"""
    pass


class SiteConfigInDB(SiteConfigInDBBase):
    """数据库中的站点配置模式"""
    pass 