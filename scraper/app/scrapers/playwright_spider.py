"""
Playwright-based spider class
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
    Playwright-based spider class for handling JavaScript-rendered pages
    """
    name = 'playwright_spider'
    
    def start_requests(self):
        """
        Start requests
        
        Returns:
            Iterator[Request]: Request iterator
        """
        # Set request headers
        headers = {
            'User-Agent': self.config.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'),
        }
        
        # Set Playwright parameters
        playwright_args = {
            'wait_until': 'networkidle',
            'timeout': self.config.get('timeout', 30000),
        }
        
        self.logger.info(f"Starting Playwright spider requests, site: {self.site_config.name}")
        
        # If login is required, handle login first
        if self.site_config.requires_login:
            self.logger.info(f"Site requires login, handling login page with Playwright: {self.site_config.login_url}")
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
            # Otherwise start crawling directly
            for url in self.start_urls:
                self.logger.info(f"Request URL (using Playwright): {url}")
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
        Handle login
        
        Args:
            response: Login page response
            
        Returns:
            Iterator[Request]: Request iterator
        """
        page = response.meta['playwright_page']
        
        try:
            self.logger.info(f"Starting to process login form, URL: {response.url}")
            
            # Fill login form
            await page.fill(f"input[name='{self.site_config.login_username_field}']", self.site_config.login_username)
            self.logger.debug(f"Filled username field: {self.site_config.login_username_field}")
            
            await page.fill(f"input[name='{self.site_config.login_password_field}']", "********")  # Don't log actual password
            self.logger.debug(f"Filled password field: {self.site_config.login_password_field}")
            
            # Click login button (assume it's the first submit button)
            self.logger.info("Clicking login button")
            await page.click("input[type='submit']")
            
            # Wait for login to complete
            self.logger.info("Waiting for login to complete...")
            await page.wait_for_navigation()
            
            # Close page
            await page.close()
            
            self.logger.info("Login successful, starting to crawl content pages")
            
            # Start crawling
            for url in self.start_urls:
                self.logger.info(f"Request content page: {url}")
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
            self.logger.error(f"Login failed: {e}")
            # Try to take a screenshot to record the error
            try:
                screenshot_path = f"error_login_{self.job_id}.png"
                await page.screenshot(path=screenshot_path)
                self.logger.info(f"Error screenshot saved to: {screenshot_path}")
            except Exception as screenshot_error:
                self.logger.error(f"Failed to save error screenshot: {screenshot_error}")
            await page.close()
    
    async def parse_with_playwright(self, response):
        """
        Parse page using Playwright
        
        Args:
            response: Response object
            
        Returns:
            Iterator[Dict[str, Any]]: Parse result iterator
        """
        page = response.meta['playwright_page']
        
        try:
            self.logger.info(f"Parsing page with Playwright: {response.url}")
            
            # Wait for content to load
            if self.list_page_xpath:
                self.logger.info(f"Waiting for selector to load: {self.list_page_xpath}")
                await page.wait_for_selector(self.list_page_xpath)
                self.logger.debug("Selector loaded")
            
            # Get page content
            self.logger.debug("Getting page content")
            html_content = await page.content()
            
            # Create new response object with JavaScript-rendered content
            new_response = response.replace(body=html_content.encode('utf-8'))
            self.logger.debug(f"Page content size: {len(html_content)} bytes")
            
            # Close page
            await page.close()
            
            # Use base class parsing method
            self.logger.info("Starting to parse page content")
            items_count = 0
            for item in self.parse_item(new_response):
                items_count += 1
                yield item
            
            self.logger.info(f"Page parsing completed, extracted {items_count} items")
            
            # Extract next page link
            if self.next_page_xpath:
                next_page = new_response.xpath(self.next_page_xpath).get()
                if next_page:
                    next_url = response.urljoin(next_page)
                    self.logger.info(f"Found next page link: {next_url}")
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
                    self.logger.info("No next page link found, crawling finished")
        except Exception as e:
            self.logger.error(f"Parsing failed: {e}")
            # Try to take a screenshot to record the error
            try:
                screenshot_path = f"error_parse_{self.job_id}_{response.url.split('/')[-1]}.png"
                await page.screenshot(path=screenshot_path)
                self.logger.info(f"Error screenshot saved to: {screenshot_path}")
            except Exception as screenshot_error:
                self.logger.error(f"Failed to save error screenshot: {screenshot_error}")
            await page.close()
    
    async def errback(self, failure):
        """
        Error callback function
        
        Args:
            failure: Failure object
        """
        page = failure.request.meta.get('playwright_page')
        if page:
            self.logger.error(f"Request failed: {failure.request.url}")
            # Try to take a screenshot to record the error
            try:
                screenshot_path = f"error_request_{self.job_id}.png"
                await page.screenshot(path=screenshot_path)
                self.logger.info(f"Error screenshot saved to: {screenshot_path}")
            except Exception as screenshot_error:
                self.logger.error(f"Failed to save error screenshot: {screenshot_error}")
            await page.close()
        
        self.logger.error(f"Request failure details: {failure.value}")
        
    def parse_item(self, response):
        """
        Parse detail page
        
        Args:
            response: Response object
            
        Returns:
            Dict[str, Any]: Parse result
        """
        # Use base class parsing method
        return super().parse_item(response) 