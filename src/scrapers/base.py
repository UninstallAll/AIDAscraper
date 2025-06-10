"""
爬虫基类模块 - 定义所有爬虫的通用接口和功能
"""
from abc import ABC, abstractmethod
import logging
from typing import Dict, List, Any, Optional, Union
import time
import random
from datetime import datetime

from playwright.sync_api import sync_playwright, Browser, Page
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """
    爬虫基类，定义所有爬虫应实现的通用接口和方法
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化爬虫
        
        Args:
            config: 爬虫配置参数
        """
        self.config = config or {}
        self.name = self.__class__.__name__
        self.results = []
        self.errors = []
        self.start_time = None
        self.end_time = None
        
        # 默认配置
        self.timeout = self.config.get('timeout', 30)
        self.retry_count = self.config.get('retry_count', 3)
        self.request_delay = self.config.get('request_delay', 1000) / 1000  # ms to seconds
        self.user_agent = self.config.get('user_agent', 
                         'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        # 状态
        self.status = "initialized"
        
        logger.info(f"Initialized scraper: {self.name}")
    
    def run(self, **kwargs) -> Dict[str, Any]:
        """
        运行爬虫的主方法
        
        Returns:
            包含爬虫运行结果的字典
        """
        self.start_time = datetime.now()
        self.status = "running"
        
        try:
            logger.info(f"Starting scraper: {self.name}")
            self._before_scrape(**kwargs)
            self._scrape(**kwargs)
            self._after_scrape(**kwargs)
            self.status = "completed"
        except Exception as e:
            logger.error(f"Error in scraper {self.name}: {str(e)}", exc_info=True)
            self.errors.append(str(e))
            self.status = "failed"
        finally:
            self.end_time = datetime.now()
            
        return self.get_report()
    
    def get_report(self) -> Dict[str, Any]:
        """
        获取爬虫运行报告
        
        Returns:
            包含爬虫运行状态和结果的字典
        """
        duration = None
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
            
        return {
            "name": self.name,
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": duration,
            "results_count": len(self.results),
            "errors_count": len(self.errors),
            "errors": self.errors[:10],  # 仅返回前10个错误
        }
    
    def _before_scrape(self, **kwargs) -> None:
        """爬取前的准备工作"""
        pass
    
    def _after_scrape(self, **kwargs) -> None:
        """爬取后的清理工作"""
        pass
    
    @abstractmethod
    def _scrape(self, **kwargs) -> None:
        """
        实际的爬取逻辑，必须由子类实现
        """
        pass
    
    def _request_with_retry(self, url: str, method: str = 'GET', **kwargs) -> Optional[requests.Response]:
        """
        带重试的HTTP请求
        
        Args:
            url: 请求URL
            method: HTTP方法
            **kwargs: 传递给requests的其他参数
            
        Returns:
            Response对象或None（如果所有重试都失败）
        """
        headers = kwargs.pop('headers', {})
        if 'User-Agent' not in headers:
            headers['User-Agent'] = self.user_agent
            
        kwargs['headers'] = headers
        kwargs['timeout'] = kwargs.get('timeout', self.timeout)
        
        for attempt in range(self.retry_count + 1):
            try:
                response = requests.request(method, url, **kwargs)
                response.raise_for_status()
                
                # 请求延迟
                if self.request_delay > 0:
                    jitter = random.uniform(0.5, 1.5) * self.request_delay
                    time.sleep(jitter)
                    
                return response
            except Exception as e:
                logger.warning(f"Request failed (attempt {attempt+1}/{self.retry_count+1}): {url} - {str(e)}")
                if attempt == self.retry_count:
                    logger.error(f"All retry attempts failed for URL: {url}")
                    return None
                # 重试前等待，每次重试增加等待时间
                time.sleep((attempt + 1) * 2)
        
        return None
    
    def _get_soup(self, url: str, **kwargs) -> Optional[BeautifulSoup]:
        """
        获取页面的BeautifulSoup对象
        
        Args:
            url: 页面URL
            **kwargs: 传递给_request_with_retry的参数
            
        Returns:
            BeautifulSoup对象或None
        """
        response = self._request_with_retry(url, **kwargs)
        if response:
            return BeautifulSoup(response.text, 'lxml')
        return None
    
    def _setup_playwright(self) -> tuple[Browser, Page]:
        """
        设置Playwright浏览器
        
        Returns:
            Browser和Page对象的元组
        """
        playwright = sync_playwright().start()
        
        browser_type = self.config.get('browser', 'chromium')
        headless = self.config.get('headless', True)
        
        if browser_type == 'firefox':
            browser = playwright.firefox.launch(headless=headless)
        elif browser_type == 'webkit':
            browser = playwright.webkit.launch(headless=headless)
        else:
            browser = playwright.chromium.launch(headless=headless)
            
        context = browser.new_context(
            user_agent=self.user_agent,
            viewport={'width': 1280, 'height': 800}
        )
        
        page = context.new_page()
        page.set_default_timeout(self.timeout * 1000)
        
        return browser, page
    
    def _get_page_with_playwright(self, url: str) -> tuple[Optional[Browser], Optional[Page], Optional[str]]:
        """
        使用Playwright获取动态渲染页面
        
        Args:
            url: 页面URL
            
        Returns:
            元组(Browser, Page, HTML内容)，失败时元素为None
        """
        browser = None
        page = None
        content = None
        
        try:
            browser, page = self._setup_playwright()
            page.goto(url, wait_until='networkidle')
            
            # 等待页面加载完成
            page.wait_for_load_state('networkidle')
            
            content = page.content()
            return browser, page, content
            
        except Exception as e:
            logger.error(f"Error getting page with Playwright: {url} - {str(e)}")
            if browser:
                browser.close()
            return None, None, None 