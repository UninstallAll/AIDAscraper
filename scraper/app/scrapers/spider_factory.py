"""
Spider factory module
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

# Configure logging
logger = logging.getLogger(__name__)


class SpiderFactory:
    """
    Spider factory class for creating spider instances
    """
    
    @staticmethod
    def create_spider(site_config: SiteConfig, job_id: int) -> Spider:
        """
        Create a spider instance
        
        Args:
            site_config: Site configuration
            job_id: Job ID
            
        Returns:
            Spider: Spider instance
        """
        # Get job logger
        job_logger = get_job_logger(job_id)
        job_logger.info(f"Creating spider instance, site: {site_config.name}, job ID: {job_id}")
        
        # Select spider class based on URL or name
        spider_class = SpiderFactory._get_spider_class(site_config, job_id)
        
        # Log spider configuration
        job_logger.info(f"Spider type: {spider_class.__name__}")
        job_logger.info(f"Start URLs: {site_config.start_urls}")
        job_logger.info(f"Allowed domains: {site_config.allowed_domains}")
        
        if site_config.config:
            job_logger.info(f"Spider configuration: {site_config.config}")
        
        # Create spider instance with custom kwargs to avoid logger property issue
        spider_kwargs = {
            'site_config': site_config,
            'job_id': job_id,
            '_job_logger': job_logger  # Pass logger as a separate parameter
        }
        
        # Create spider instance
        spider = spider_class(**spider_kwargs)
        
        job_logger.info(f"Spider instance created successfully: {spider.name}")
        return spider
    
    @staticmethod
    def _get_spider_class(site_config: SiteConfig, job_id: int = None) -> Type[Spider]:
        """
        Get spider class based on site configuration
        
        Args:
            site_config: Site configuration
            job_id: Job ID
            
        Returns:
            Type[Spider]: Spider class
        """
        # Get job logger (if job ID is provided)
        log_func = logger.info
        if job_id:
            job_logger = get_job_logger(job_id)
            log_func = job_logger.info
        
        # Select specific spider class based on site URL or name
        site_url = site_config.url.lower()
        site_name = site_config.name.lower()
        
        if 'artsy.net' in site_url or 'artsy' in site_name:
            log_func(f"Selected ArtsySpider for site {site_config.name}")
            return ArtsySpider
        elif 'wikiart.org' in site_url or 'wikiart' in site_name:
            log_func(f"Selected WikiArtSpider for site {site_config.name}")
            return WikiArtSpider
        elif 'gallery' in site_url or 'gallery' in site_name:
            log_func(f"Selected ArtGallerySpider for site {site_config.name}")
            return ArtGallerySpider
        elif 'saatchiart.com' in site_url or 'saatchi' in site_name:
            log_func(f"Selected SaatchiArtSpider for site {site_config.name}")
            return SaatchiArtSpider
        elif site_config.use_playwright:
            log_func(f"Selected generic PlaywrightSpider for site {site_config.name}")
            return PlaywrightSpider
        else:
            log_func(f"Selected generic BaseSpider for site {site_config.name}")
            return BaseSpider 