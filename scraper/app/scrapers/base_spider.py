"""
基础爬虫类
"""
import logging
from typing import Dict, List, Optional, Any, Union

import scrapy
from scrapy.http import Request, Response
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from app.models.site import SiteConfig


class BaseSpider(CrawlSpider):
    """
    基础爬虫类，所有爬虫都应该继承此类
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
        初始化爬虫
        
        Args:
            site_config: 站点配置
            job_id: 任务ID
        """
        self.site_config = site_config
        self.job_id = job_id
        
        # 设置爬虫参数
        self.allowed_domains = site_config.allowed_domains
        self.start_urls = site_config.start_urls
        
        # 设置XPath选择器
        self.list_page_xpath = site_config.list_page_xpath
        self.next_page_xpath = site_config.next_page_xpath
        self.detail_page_xpath = site_config.detail_page_xpath
        self.field_mappings = site_config.field_mappings or {}
        
        # 设置自定义配置
        self.config = site_config.config or {}
        
        # 调用父类初始化
        super().__init__(*args, **kwargs)
        
        # 设置规则
        self._set_rules()
        
        # 设置日志
        self.logger = logging.getLogger(f"{self.name}_{self.job_id}")
    
    def _set_rules(self):
        """
        设置爬虫规则
        """
        if self.detail_page_xpath:
            self.rules = (
                # 提取详情页链接并跟随
                Rule(
                    LinkExtractor(restrict_xpaths=self.detail_page_xpath),
                    callback='parse_item',
                    follow=False
                ),
                # 提取下一页链接并跟随
                Rule(
                    LinkExtractor(restrict_xpaths=self.next_page_xpath),
                    follow=True
                ),
            )
    
    def start_requests(self):
        """
        开始请求
        
        Returns:
            Iterator[Request]: 请求迭代器
        """
        # 设置请求头
        headers = {
            'User-Agent': self.config.get('user_agent', 'Scrapy/2.5.0'),
        }
        
        # 如果需要登录，先执行登录
        if self.site_config.requires_login:
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
            # 否则直接开始爬取
            for url in self.start_urls:
                yield scrapy.Request(url=url, headers=headers)
    
    def _after_login(self, response):
        """
        登录后的回调函数
        
        Args:
            response: 登录响应
            
        Returns:
            Iterator[Request]: 请求迭代器
        """
        # 检查登录是否成功
        # 注意：实际实现应该根据具体站点检查登录状态
        self.logger.info("登录完成，开始爬取")
        
        # 开始爬取
        for url in self.start_urls:
            yield scrapy.Request(url=url)
    
    def parse_item(self, response):
        """
        解析详情页
        
        Args:
            response: 响应对象
            
        Returns:
            Dict[str, Any]: 解析结果
        """
        item = {}
        
        # 使用字段映射提取数据
        for field, xpath in self.field_mappings.items():
            value = response.xpath(xpath).get()
            if value:
                item[field] = value.strip()
        
        # 添加元数据
        item['url'] = response.url
        item['site_id'] = self.site_config.id
        item['job_id'] = self.job_id
        item['tenant_id'] = self.site_config.tenant_id
        
        return item 