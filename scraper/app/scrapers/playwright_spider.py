"""
使用Playwright的爬虫类
"""
import logging
from typing import Dict, List, Optional, Any, Union

import scrapy
from scrapy.http import Request, Response
from scrapy_playwright.page import PageMethod

from app.models.site import SiteConfig
from app.scrapers.base_spider import BaseSpider


class PlaywrightSpider(BaseSpider):
    """
    使用Playwright的爬虫类，用于处理JavaScript渲染的页面
    """
    name = 'playwright_spider'
    
    def start_requests(self):
        """
        开始请求
        
        Returns:
            Iterator[Request]: 请求迭代器
        """
        # 设置请求头
        headers = {
            'User-Agent': self.config.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'),
        }
        
        # 设置Playwright参数
        playwright_args = {
            'wait_until': 'networkidle',
            'timeout': self.config.get('timeout', 30000),
        }
        
        self.logger.info(f"使用Playwright爬虫开始请求，站点: {self.site_config.name}")
        
        # 如果需要登录，先执行登录
        if self.site_config.requires_login:
            self.logger.info(f"站点需要登录，使用Playwright处理登录页面: {self.site_config.login_url}")
            yield scrapy.Request(
                url=self.site_config.login_url,
                headers=headers,
                meta={
                    'playwright': True,
                    'playwright_include_page': True,
                    'playwright_page_methods': [
                        PageMethod('wait_for_selector', f"input[name='{self.site_config.login_username_field}']"),
                    ],
                    'errback': self.errback,
                },
                callback=self._handle_login
            )
        else:
            # 否则直接开始爬取
            for url in self.start_urls:
                self.logger.info(f"请求URL (使用Playwright): {url}")
                yield scrapy.Request(
                    url=url,
                    headers=headers,
                    meta={
                        'playwright': True,
                        'playwright_include_page': True,
                        **playwright_args,
                        'errback': self.errback,
                    },
                    callback=self.parse_with_playwright
                )
    
    async def _handle_login(self, response):
        """
        处理登录
        
        Args:
            response: 登录页面响应
            
        Returns:
            Iterator[Request]: 请求迭代器
        """
        page = response.meta['playwright_page']
        
        try:
            self.logger.info(f"开始处理登录表单，URL: {response.url}")
            
            # 填写登录表单
            await page.fill(f"input[name='{self.site_config.login_username_field}']", self.site_config.login_username)
            self.logger.debug(f"已填写用户名字段: {self.site_config.login_username_field}")
            
            await page.fill(f"input[name='{self.site_config.login_password_field}']", "********")  # 不记录实际密码
            self.logger.debug(f"已填写密码字段: {self.site_config.login_password_field}")
            
            # 点击登录按钮（假设是第一个类型为submit的按钮）
            self.logger.info("点击登录按钮")
            await page.click("input[type='submit']")
            
            # 等待登录完成
            self.logger.info("等待登录完成...")
            await page.wait_for_navigation()
            
            # 关闭页面
            await page.close()
            
            self.logger.info("登录成功，开始爬取内容页面")
            
            # 开始爬取
            for url in self.start_urls:
                self.logger.info(f"请求内容页面: {url}")
                yield scrapy.Request(
                    url=url,
                    meta={
                        'playwright': True,
                        'playwright_include_page': True,
                        'wait_until': 'networkidle',
                        'errback': self.errback,
                    },
                    callback=self.parse_with_playwright
                )
        except Exception as e:
            self.logger.error(f"登录失败: {e}")
            # 尝试截图记录错误
            try:
                screenshot_path = f"error_login_{self.job_id}.png"
                await page.screenshot(path=screenshot_path)
                self.logger.info(f"错误截图已保存到: {screenshot_path}")
            except Exception as screenshot_error:
                self.logger.error(f"保存错误截图失败: {screenshot_error}")
            await page.close()
    
    async def parse_with_playwright(self, response):
        """
        使用Playwright解析页面
        
        Args:
            response: 响应对象
            
        Returns:
            Iterator[Dict[str, Any]]: 解析结果迭代器
        """
        page = response.meta['playwright_page']
        
        try:
            self.logger.info(f"使用Playwright解析页面: {response.url}")
            
            # 等待内容加载
            if self.list_page_xpath:
                self.logger.info(f"等待选择器加载: {self.list_page_xpath}")
                await page.wait_for_selector(self.list_page_xpath)
                self.logger.debug("选择器加载完成")
            
            # 获取页面内容
            self.logger.debug("获取页面内容")
            html_content = await page.content()
            
            # 创建新的响应对象，包含JavaScript渲染后的内容
            new_response = response.replace(body=html_content.encode('utf-8'))
            self.logger.debug(f"页面内容大小: {len(html_content)} 字节")
            
            # 关闭页面
            await page.close()
            
            # 使用基类的解析方法
            self.logger.info("开始解析页面内容")
            items_count = 0
            for item in self.parse_item(new_response):
                items_count += 1
                yield item
            
            self.logger.info(f"页面解析完成，提取到 {items_count} 个项目")
            
            # 提取下一页链接
            if self.next_page_xpath:
                next_page = new_response.xpath(self.next_page_xpath).get()
                if next_page:
                    next_url = response.urljoin(next_page)
                    self.logger.info(f"找到下一页链接: {next_url}")
                    yield scrapy.Request(
                        url=next_url,
                        meta={
                            'playwright': True,
                            'playwright_include_page': True,
                            'wait_until': 'networkidle',
                            'errback': self.errback,
                        },
                        callback=self.parse_with_playwright
                    )
                else:
                    self.logger.info("没有找到下一页链接，爬取结束")
        except Exception as e:
            self.logger.error(f"解析失败: {e}")
            # 尝试截图记录错误
            try:
                screenshot_path = f"error_parse_{self.job_id}_{response.url.split('/')[-1]}.png"
                await page.screenshot(path=screenshot_path)
                self.logger.info(f"错误截图已保存到: {screenshot_path}")
            except Exception as screenshot_error:
                self.logger.error(f"保存错误截图失败: {screenshot_error}")
            await page.close()
    
    async def errback(self, failure):
        """
        错误回调函数
        
        Args:
            failure: 失败对象
        """
        page = failure.request.meta.get('playwright_page')
        if page:
            self.logger.error(f"请求失败: {failure.request.url}")
            # 尝试截图记录错误
            try:
                screenshot_path = f"error_request_{self.job_id}.png"
                await page.screenshot(path=screenshot_path)
                self.logger.info(f"错误截图已保存到: {screenshot_path}")
            except Exception as screenshot_error:
                self.logger.error(f"保存错误截图失败: {screenshot_error}")
            await page.close()
        
        self.logger.error(f"请求失败详情: {failure.value}")
        
    def parse_item(self, response):
        """
        解析详情页
        
        Args:
            response: 响应对象
            
        Returns:
            Dict[str, Any]: 解析结果
        """
        # 使用基类的解析方法
        return super().parse_item(response) 