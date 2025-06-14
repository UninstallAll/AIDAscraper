"""
Base spider class
"""
import logging
from typing import Dict, List, Optional, Any, Union

import scrapy
from scrapy.http import Request, Response
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from app.models.site import SiteConfig
from app.scrapers.log_handler import setup_job_logger


class BaseSpider(CrawlSpider):
    """
    Base spider class that all spiders should inherit from
    """
    name = 'base_spider'
    
    def __init__(
        self, 
        site_config: SiteConfig, 
        job_id: int = None, 
        *args, 
        **kwargs
    ):
        """
        Initialize the spider
        
        Args:
            site_config: Site configuration
            job_id: Job ID
        """
        self.site_config = site_config
        self.job_id = job_id
        
        # Set spider parameters
        self.allowed_domains = site_config.allowed_domains
        self.start_urls = site_config.start_urls
        
        # Set XPath selectors
        self.list_page_xpath = site_config.list_page_xpath
        self.next_page_xpath = site_config.next_page_xpath
        self.detail_page_xpath = site_config.detail_page_xpath
        self.field_mappings = site_config.field_mappings or {}
        
        # Set custom configuration
        self.config = site_config.config or {}
        
        # Call parent initialization
        super().__init__(*args, **kwargs)
        
        # Set rules
        self._set_rules()
        
        # Set up logger (changed from property to regular attribute)
        self._setup_logger()
    
    def _setup_logger(self):
        """
        Set up the logger for this spider
        """
        self.logger = logging.getLogger(f"{self.name}_{self.job_id}")
        
        # Set up job logger handler
        if self.job_id:
            # Set log level based on configuration
            log_level_str = self.config.get('log_level', 'INFO')
            log_level = getattr(logging, log_level_str, logging.INFO)
            setup_job_logger(self.job_id, level=log_level)
            self.logger.info(f"Spider {self.name} initialized, Job ID: {self.job_id}")
    
    def _set_rules(self):
        """
        Set spider rules
        """
        if self.detail_page_xpath:
            self.rules = (
                # Extract detail page links and follow
                Rule(
                    LinkExtractor(restrict_xpaths=self.detail_page_xpath),
                    callback='parse_item',
                    follow=False
                ),
                # Extract next page links and follow
                Rule(
                    LinkExtractor(restrict_xpaths=self.next_page_xpath),
                    follow=True
                ),
            )
    
    def start_requests(self):
        """
        Start requests
        
        Returns:
            Iterator[Request]: Request iterator
        """
        # Set request headers
        headers = {
            'User-Agent': self.config.get('user_agent', 'Scrapy/2.5.0'),
        }
        
        self.logger.info(f"Starting crawl, start URLs: {self.start_urls}")
        
        # If login is required, execute login first
        if self.site_config.requires_login:
            self.logger.info(f"Site requires login, login URL: {self.site_config.login_url}")
            yield scrapy.FormRequest(
                url=self.site_config.login_url,
                method='POST',
                formdata={
                    self.site_config.login_username_field: self.site_config.login_username,
                    self.site_config.login_password_field: self.site_config.login_password,
                },
                headers=headers,
                callback=self._after_login
            )
        else:
            # Otherwise start crawling directly
            for url in self.start_urls:
                self.logger.info(f"Request URL: {url}")
                yield scrapy.Request(url=url, headers=headers)
    
    def _after_login(self, response):
        """
        Callback after login
        
        Args:
            response: Login response
            
        Returns:
            Iterator[Request]: Request iterator
        """
        # Check if login was successful
        # Note: Actual implementation should check login status based on the specific site
        self.logger.info(f"Login completed, status code: {response.status}, starting crawl")
        
        # Start crawling
        for url in self.start_urls:
            self.logger.info(f"Request URL: {url}")
            yield scrapy.Request(url=url)
    
    def parse_item(self, response):
        """
        Parse detail page
        
        Args:
            response: Response object
            
        Returns:
            Dict[str, Any]: Parse result
        """
        self.logger.info(f"Parsing detail page: {response.url}")
        
        item = {}
        
        # Extract data using field mappings
        for field, xpath in self.field_mappings.items():
            value = response.xpath(xpath).get()
            if value:
                item[field] = value.strip()
                self.logger.debug(f"Extracted field {field}: {value[:50]}...")
            else:
                self.logger.warning(f"Field {field} not found, XPath: {xpath}")
        
        # Add metadata
        item['url'] = response.url
        item['site_id'] = self.site_config.id
        item['job_id'] = self.job_id
        item['tenant_id'] = self.site_config.tenant_id
        
        self.logger.info(f"Parsing completed, extracted {len(item) - 4} fields")
        return item 