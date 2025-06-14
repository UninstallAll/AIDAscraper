"""
爬取的数据项模型
"""
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.database import Base


class ScrapedItem(Base):
    """爬取的数据项模型"""
    __tablename__ = "scraped_items"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)
    page_type = Column(String, index=True)  # artist, exhibition, artwork
    title = Column(String, nullable=True, index=True)
    content = Column(Text, nullable=True)
    data = Column(JSON, default=dict)  # 存储所有爬取的数据
    job_id = Column(Integer, ForeignKey("jobs.id"), index=True)
    site_config_id = Column(Integer, ForeignKey("site_configs.id"), index=True)
    tenant_id = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    job = relationship("Job", backref="scraped_items")
    site_config = relationship("SiteConfig", backref="scraped_items")

    def __repr__(self):
        return f"<ScrapedItem {self.page_type}: {self.title}>" 