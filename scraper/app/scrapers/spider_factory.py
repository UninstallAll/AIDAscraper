"""
爬虫工厂模块
"""
import logging
from typing import Type

from scrapy import Spider

from app.models.site import SiteConfig
from app.scrapers.base_spider import BaseSpider
from app.scrapers.playwright_spider import PlaywrightSpider
from app.scrapers.spiders.art_gallery_spider import ArtGallerySpider
from app.scrapers.spiders.artsy_spider import ArtsySpider
from app.scrapers.spiders.wikiart_spider import WikiArtSpider
from app.scrapers.spiders.saatchi_art_spider import SaatchiArtSpider
from app.utils.logger import get_job_logger

# 设置日志
logger = logging.getLogger(__name__)


class SpiderFactory:
    """
    爬虫工厂类，用于创建爬虫实例
    """
    
    @staticmethod
    def create_spider(site_config: SiteConfig, job_id: int) -> Spider:
        """
        创建爬虫实例
        
        Args:
            site_config: 站点配置
            job_id: 任务ID
            
        Returns:
            Spider: 爬虫实例
        """
        # 获取任务日志记录器
        job_logger = get_job_logger(job_id)
        job_logger.info(f"开始创建爬虫实例，站点: {site_config.name}，任务ID: {job_id}")
        
        # 根据URL或名称选择爬虫类
        spider_class = SpiderFactory._get_spider_class(site_config, job_id)
        
        # 记录爬虫配置
        job_logger.info(f"爬虫类型: {spider_class.__name__}")
        job_logger.info(f"起始URL: {site_config.start_urls}")
        job_logger.info(f"允许的域名: {site_config.allowed_domains}")
        
        if site_config.config:
            job_logger.info(f"爬虫配置: {site_config.config}")
        
        # 创建爬虫实例
        spider = spider_class(
            site_config=site_config,
            job_id=job_id
        )
        
        job_logger.info(f"爬虫实例创建成功: {spider.name}")
        return spider
    
    @staticmethod
    def _get_spider_class(site_config: SiteConfig, job_id: int = None) -> Type[Spider]:
        """
        根据站点配置获取爬虫类
        
        Args:
            site_config: 站点配置
            job_id: 任务ID
            
        Returns:
            Type[Spider]: 爬虫类
        """
        # 获取任务日志记录器（如果有任务ID）
        log_func = logger.info
        if job_id:
            job_logger = get_job_logger(job_id)
            log_func = job_logger.info
        
        # 根据站点URL或名称选择特定的爬虫类
        site_url = site_config.url.lower()
        site_name = site_config.name.lower()
        
        if 'artsy.net' in site_url or 'artsy' in site_name:
            log_func(f"为站点 {site_config.name} 选择 ArtsySpider")
            return ArtsySpider
        elif 'wikiart.org' in site_url or 'wikiart' in site_name:
            log_func(f"为站点 {site_config.name} 选择 WikiArtSpider")
            return WikiArtSpider
        elif 'gallery' in site_url or 'gallery' in site_name:
            log_func(f"为站点 {site_config.name} 选择 ArtGallerySpider")
            return ArtGallerySpider
        elif 'saatchiart.com' in site_url or 'saatchi' in site_name:
            log_func(f"为站点 {site_config.name} 选择 SaatchiArtSpider")
            return SaatchiArtSpider
        elif site_config.use_playwright:
            log_func(f"为站点 {site_config.name} 选择通用 PlaywrightSpider")
            return PlaywrightSpider
        else:
            log_func(f"为站点 {site_config.name} 选择通用 BaseSpider")
            return BaseSpider 