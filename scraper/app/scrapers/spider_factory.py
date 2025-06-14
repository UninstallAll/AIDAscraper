"""
爬虫工厂类
"""
from typing import Optional

from app.models.site import SiteConfig
from app.scrapers.base_spider import BaseSpider
from app.scrapers.playwright_spider import PlaywrightSpider


class SpiderFactory:
    """
    爬虫工厂类，用于根据配置创建不同类型的爬虫
    """
    
    @staticmethod
    def create_spider(site_config: SiteConfig, job_id: Optional[int] = None) -> BaseSpider:
        """
        创建爬虫
        
        Args:
            site_config: 站点配置
            job_id: 任务ID
            
        Returns:
            BaseSpider: 爬虫实例
        """
        if site_config.use_playwright:
            return PlaywrightSpider(site_config=site_config, job_id=job_id)
        else:
            return BaseSpider(site_config=site_config, job_id=job_id) 