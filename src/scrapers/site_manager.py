"""
网站管理器模块 - 用于管理各个艺术数据网站及其专用爬虫
"""
import os
import logging
import json
from typing import Dict, List, Any, Optional, Type
from pathlib import Path
import importlib

from .registry import ScraperRegistry
from .base import BaseScraper

logger = logging.getLogger(__name__)

class WebsiteManager:
    """
    网站管理器 - 用于管理艺术数据网站和对应的爬虫
    提供网站添加、删除、配置和爬虫调用等功能
    """
    
    def __init__(self, registry: ScraperRegistry = None, sites_dir: str = None):
        """
        初始化网站管理器
        
        Args:
            registry: 爬虫注册表实例，如果不提供则创建新的
            sites_dir: 网站爬虫目录路径
        """
        self.registry = registry or ScraperRegistry()
        
        # 设置网站爬虫目录
        module_path = os.path.dirname(os.path.abspath(__file__))
        self.sites_dir = sites_dir or os.path.join(module_path, 'sites')
        
        # 确保sites目录存在
        os.makedirs(self.sites_dir, exist_ok=True)
        
        # 网站模板目录
        self.template_dir = os.path.join(module_path, 'templates')
        os.makedirs(self.template_dir, exist_ok=True)
        
        logger.info(f"Initialized WebsiteManager with sites directory: {self.sites_dir}")
        
        # 自动发现并注册现有爬虫
        self.discover_site_scrapers()
    
    def discover_site_scrapers(self) -> List[str]:
        """
        发现和注册网站目录中的所有爬虫
        
        Returns:
            注册的爬虫ID列表
        """
        # 使用registry的discover方法查找爬虫
        scraper_ids = self.registry.discover_scrapers('src.scrapers.sites')
        logger.info(f"Discovered {len(scraper_ids)} site scrapers: {scraper_ids}")
        return scraper_ids
    
    def list_websites(self) -> List[Dict[str, Any]]:
        """
        列出所有已注册的网站
        
        Returns:
            网站信息列表
        """
        return self.registry.get_all_websites()
    
    def get_website(self, website_id: str) -> Optional[Dict[str, Any]]:
        """
        获取网站信息
        
        Args:
            website_id: 网站ID
            
        Returns:
            网站信息或None
        """
        return self.registry.get_website(website_id)
    
    def add_website(self, 
                   website_id: str, 
                   name: str, 
                   url: str, 
                   description: str = "", 
                   metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        添加新网站
        
        Args:
            website_id: 网站唯一标识符
            name: 网站名称
            url: 网站URL
            description: 网站描述
            metadata: 网站元数据
            
        Returns:
            新添加的网站信息
        """
        return self.registry.register_website(
            website_id=website_id,
            name=name,
            url=url,
            description=description,
            metadata=metadata
        )
    
    def update_website(self,
                      website_id: str,
                      name: Optional[str] = None,
                      url: Optional[str] = None,
                      description: Optional[str] = None,
                      metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        更新网站信息
        
        Args:
            website_id: 网站ID
            name: 新的网站名称
            url: 新的网站URL
            description: 新的网站描述
            metadata: 新的网站元数据
            
        Returns:
            更新后的网站信息
            
        Raises:
            ValueError: 如果网站不存在
        """
        website = self.registry.get_website(website_id)
        if not website:
            raise ValueError(f"Website not found: {website_id}")
            
        if name:
            website["name"] = name
        if url:
            website["url"] = url
        if description:
            website["description"] = description
        if metadata:
            website["metadata"] = {**website.get("metadata", {}), **metadata}
            
        website["updated_at"] = self.registry._get_timestamp()
        
        self.registry.websites[website_id] = website
        self.registry.save_config()
        
        return website
    
    def remove_website(self, website_id: str) -> bool:
        """
        删除网站
        
        Args:
            website_id: 网站ID
            
        Returns:
            是否成功删除
        """
        if website_id not in self.registry.websites:
            return False
            
        # 删除网站关联的爬虫
        self.registry.website_scrapers.pop(website_id, None)
        
        # 删除网站
        self.registry.websites.pop(website_id)
        self.registry.save_config()
        
        return True
    
    def get_website_scrapers(self, website_id: str) -> List[Dict[str, Any]]:
        """
        获取网站关联的爬虫列表
        
        Args:
            website_id: 网站ID
            
        Returns:
            爬虫信息列表
        """
        return self.registry.get_website_scrapers(website_id)
    
    def create_site_scraper(self, 
                          website_id: str, 
                          scraper_name: str, 
                          website_name: str = None,
                          website_url: str = None) -> str:
        """
        为网站创建新的爬虫脚本
        
        Args:
            website_id: 网站ID，也用作文件名
            scraper_name: 爬虫类名
            website_name: 网站名称，如果不提供则使用网站ID
            website_url: 网站URL，如果不提供则为空
            
        Returns:
            创建的脚本文件路径
            
        Raises:
            ValueError: 如果爬虫已存在
        """
        # 规范化网站ID
        website_id = website_id.lower().replace(' ', '_').replace('-', '_')
        
        # 创建爬虫文件路径
        file_path = os.path.join(self.sites_dir, f"{website_id}.py")
        
        # 检查文件是否已存在
        if os.path.exists(file_path):
            raise ValueError(f"Scraper for website {website_id} already exists")
            
        # 规范化爬虫名称
        if not scraper_name.endswith('Scraper'):
            scraper_name = f"{scraper_name}Scraper"
            
        # 使用网站ID或提供的名称
        website_name = website_name or website_id.replace('_', ' ').title()
        website_url = website_url or ""
            
        # 生成爬虫代码
        scraper_code = self._generate_site_scraper_code(
            scraper_name=scraper_name,
            website_name=website_name,
            website_url=website_url
        )
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(scraper_code)
            
        logger.info(f"Created site scraper for {website_id} at {file_path}")
        
        # 刷新已发现的爬虫
        self.discover_site_scrapers()
        
        # 注册网站（如果不存在）
        if website_id not in self.registry.websites:
            self.add_website(
                website_id=website_id,
                name=website_name,
                url=website_url,
                description=f"Site scraper for {website_name}"
            )
        
        return file_path
        
    def run_website_scraper(self, website_id: str, task_name: str = None, **kwargs) -> Dict[str, Any]:
        """
        运行网站的爬虫
        
        Args:
            website_id: 网站ID
            task_name: 任务名称，如果不提供则运行第一个关联的爬虫
            **kwargs: 传递给爬虫的参数
            
        Returns:
            爬虫运行结果
            
        Raises:
            ValueError: 如果网站不存在或没有关联的爬虫
        """
        return self.registry.run_website_scraper(website_id, task_name, **kwargs)
    
    def _generate_site_scraper_code(self, 
                                  scraper_name: str, 
                                  website_name: str, 
                                  website_url: str) -> str:
        """
        生成网站爬虫代码
        
        Args:
            scraper_name: 爬虫类名
            website_name: 网站名称
            website_url: 网站URL
            
        Returns:
            生成的爬虫代码
        """
        # 检查是否有模板文件，如果有则使用模板
        template_path = os.path.join(self.template_dir, 'site_scraper_template.py')
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
                
            # 替换模板中的占位符
            return template.replace('{SCRAPER_NAME}', scraper_name) \
                          .replace('{WEBSITE_NAME}', website_name) \
                          .replace('{WEBSITE_URL}', website_url)
        
        # 如果没有模板，使用内置模板字符串
        return f'''"""
{website_name} scraper - Used for extracting art data from {website_name}
"""
import logging
from typing import Dict, List, Any

from ..base import BaseScraper

logger = logging.getLogger(__name__)

class {scraper_name}(BaseScraper):
    """
    {website_name} scraper - Extracts artwork and artist information
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.base_url = "{website_url}"
        
    def _scrape(self, **kwargs) -> None:
        """
        Implement scraping logic
        
        Args:
            **kwargs: Additional parameters like page, limit, etc.
        """
        # Get parameters
        page = kwargs.get('page', 1)
        limit = kwargs.get('limit', 20)
        
        logger.info(f"Scraping {website_name}, page={{page}}, limit={{limit}}")
        
        try:
            # Use Playwright to get dynamic content
            browser, page_obj, content = self._get_page_with_playwright(
                f"{{self.base_url}}"
            )
            
            try:
                if not content:
                    raise ValueError("Failed to get page content")
                
                # Parse page content and extract data
                items = self._extract_items(content)
                
                # Save results
                for item in items:
                    self.results.append(item)
                    
                logger.info(f"Scraped {{len(items)}} items from {website_name}")
                
                # Scrape next page if needed
                next_page = page + 1
                if next_page <= kwargs.get('max_pages', 1):
                    self._scrape(page=next_page, limit=limit, max_pages=kwargs.get('max_pages', 1))
            finally:
                # Close browser
                if browser:
                    browser.close()
        except Exception as e:
            logger.error(f"Error scraping {website_name}: {{str(e)}}", exc_info=True)
            self.errors.append(f"Failed to scrape page {{page}}: {{str(e)}}")
    
    def _extract_items(self, html_content: str) -> List[Dict[str, Any]]:
        """
        Extract items from HTML content
        
        Args:
            html_content: Page HTML content
            
        Returns:
            List of extracted items
        """
        from bs4 import BeautifulSoup
        
        items = []
        soup = BeautifulSoup(html_content, 'lxml')
        
        # TODO: Implement extraction logic based on site structure
        # For example:
        # item_elements = soup.select('div.item')
        # 
        # for elem in item_elements:
        #     try:
        #         title = elem.select_one('.title').text.strip()
        #         items.append({{"title": title, "source": "{website_name.lower()}"}}
        #     except Exception as e:
        #         logger.warning(f"Error extracting item data: {{str(e)}}")
        
        # Placeholder - return empty list for now
        return items
''' 