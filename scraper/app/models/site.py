"""
站点配置模型
"""
from sqlalchemy import Boolean, Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func

from app.db.database import Base


class SiteConfig(Base):
    """站点配置模型"""
    __tablename__ = "site_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    url = Column(String)
    description = Column(String, nullable=True)
    requires_login = Column(Boolean, default=False)
    login_url = Column(String, nullable=True)
    login_username_field = Column(String, nullable=True)
    login_password_field = Column(String, nullable=True)
    login_username = Column(String, nullable=True)
    login_password = Column(String, nullable=True)
    start_urls = Column(JSON, default=list)
    allowed_domains = Column(JSON, default=list)
    list_page_xpath = Column(String, nullable=True)
    next_page_xpath = Column(String, nullable=True)
    detail_page_xpath = Column(String, nullable=True)
    field_mappings = Column(JSON, default=dict)
    use_playwright = Column(Boolean, default=False)
    config = Column(JSON, default=dict)
    tenant_id = Column(String, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<SiteConfig {self.name}>" 