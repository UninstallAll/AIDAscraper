"""
Artsy网站爬虫
"""
import logging
from typing import Dict, Any, List, Iterator
import json
import re

import scrapy
from scrapy.http import Request, Response
from scrapy_playwright.page import PageMethod

from app.scrapers.playwright_spider import PlaywrightSpider


class ArtsySpider(PlaywrightSpider):
    """
    Artsy网站爬虫，用于爬取艺术家、展览和艺术品信息
    
    需要登录和处理JavaScript动态加载内容
    """
    name = 'artsy_spider'
    
    def start_requests(self):
        """
        开始请求，首先进行登录
        
        Returns:
            Iterator[Request]: 请求迭代器
        """
        # 设置请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        
        # 如果需要登录
        if self.site_config.requires_login:
            self.logger.info(f"准备登录Artsy: {self.site_config.login_url}")
            
            yield scrapy.Request(
                url=self.site_config.login_url or 'https://www.artsy.net/login',
                headers=headers,
                meta={
                    'playwright': True,
                    'playwright_include_page': True,
                    'playwright_page_methods': [
                        PageMethod('wait_for_selector', 'input[type="email"]'),
                    ],
                    'errback': self.errback,
                },
                callback=self._handle_login
            )
        else:
            # 否则直接开始爬取
            for url in self.start_urls:
                yield scrapy.Request(
                    url=url,
                    headers=headers,
                    meta={
                        'playwright': True,
                        'playwright_include_page': True,
                        'wait_until': 'networkidle',
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
            self.logger.info("开始填写登录表单")
            
            # 填写登录表单
            await page.fill('input[type="email"]', self.site_config.login_username)
            await page.fill('input[type="password"]', self.site_config.login_password)
            
            # 点击登录按钮
            await page.click('button[type="submit"]')
            
            # 等待登录完成，页面跳转或出现用户菜单
            await page.wait_for_selector('.user-menu, .user-profile-dropdown', timeout=30000)
            
            self.logger.info("登录成功，开始爬取")
            
            # 获取登录后的cookies
            cookies = await page.context.cookies()
            self.logger.info(f"获取到 {len(cookies)} 个cookies")
            
            # 关闭页面
            await page.close()
            
            # 开始爬取
            for url in self.start_urls:
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
            await page.close()
    
    async def parse_with_playwright(self, response):
        """
        使用Playwright解析页面，处理动态加载内容
        
        Args:
            response: 响应对象
            
        Returns:
            Iterator[Dict[str, Any]]: 解析结果迭代器
        """
        page = response.meta['playwright_page']
        
        try:
            # 等待内容加载
            await page.wait_for_load_state('networkidle')
            
            # 处理无限滚动加载（如果有）
            if 'artists' in response.url or 'shows' in response.url:
                # 滚动加载更多内容
                self.logger.info("检测到列表页面，开始滚动加载更多内容")
                
                for _ in range(3):  # 最多滚动3次，避免无限滚动
                    # 滚动到页面底部
                    await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                    # 等待加载
                    await page.wait_for_timeout(2000)
            
            # 获取页面内容
            html_content = await page.content()
            
            # 创建新的响应对象，包含JavaScript渲染后的内容
            new_response = response.replace(body=html_content.encode('utf-8'))
            
            # 关闭页面
            await page.close()
            
            # 根据URL类型处理不同页面
            if '/artist/' in response.url:
                yield self.parse_artist(new_response)
            elif '/show/' in response.url:
                yield self.parse_exhibition(new_response)
            elif '/artwork/' in response.url:
                yield self.parse_artwork(new_response)
            else:
                # 列表页面，提取链接并跟进
                for link in self.extract_item_links(new_response):
                    yield scrapy.Request(
                        url=response.urljoin(link),
                        meta={
                            'playwright': True,
                            'playwright_include_page': True,
                            'wait_until': 'networkidle',
                            'errback': self.errback,
                        },
                        callback=self.parse_with_playwright
                    )
        except Exception as e:
            self.logger.error(f"解析失败: {e}")
            await page.close()
    
    def extract_item_links(self, response):
        """
        从列表页提取详情页链接
        
        Args:
            response: 响应对象
            
        Returns:
            List[str]: 链接列表
        """
        links = []
        
        # 提取艺术家链接
        if 'artists' in response.url:
            links.extend(response.css('a[href*="/artist/"]::attr(href)').getall())
        
        # 提取展览链接
        elif 'shows' in response.url:
            links.extend(response.css('a[href*="/show/"]::attr(href)').getall())
        
        # 提取艺术品链接
        elif 'artworks' in response.url:
            links.extend(response.css('a[href*="/artwork/"]::attr(href)').getall())
        
        # 去重
        return list(set(links))
    
    def parse_artist(self, response):
        """
        解析艺术家页面
        
        Args:
            response: 响应对象
            
        Returns:
            Dict[str, Any]: 解析结果
        """
        # 基础信息提取
        item = {
            'url': response.url,
            'page_type': 'artist',
            'name': response.css('h1::text').get('').strip(),
            'nationality': response.css('.artist-nationality::text').get(''),
            'birth_year': None,
            'death_year': None,
        }
        
        # 提取生卒年
        bio_text = response.css('.artist-bio-birthdate::text').get('')
        if bio_text:
            years = re.findall(r'\d{4}', bio_text)
            if len(years) >= 1:
                item['birth_year'] = years[0]
            if len(years) >= 2:
                item['death_year'] = years[1]
        
        # 提取简介
        bio = response.css('.artist-bio-content p::text').getall()
        if bio:
            item['biography'] = ' '.join([b.strip() for b in bio])
        
        # 提取代表作品
        artworks = []
        artwork_elements = response.css('.artist-artworks .artwork-item')
        for element in artwork_elements[:5]:  # 最多提取5个作品
            artwork = {
                'title': element.css('.artwork-title::text').get('').strip(),
                'date': element.css('.artwork-date::text').get('').strip(),
                'url': response.urljoin(element.css('a::attr(href)').get(''))
            }
            if artwork['title']:
                artworks.append(artwork)
        
        if artworks:
            item['artworks'] = artworks
        
        return item
    
    def parse_exhibition(self, response):
        """
        解析展览页面
        
        Args:
            response: 响应对象
            
        Returns:
            Dict[str, Any]: 解析结果
        """
        # 基础信息提取
        item = {
            'url': response.url,
            'page_type': 'exhibition',
            'title': response.css('h1::text').get('').strip(),
            'gallery': response.css('.exhibition-gallery::text').get('').strip(),
        }
        
        # 提取展览日期
        date_text = response.css('.exhibition-dates::text').get('')
        if date_text:
            item['date_range'] = date_text.strip()
        
        # 提取展览描述
        description = response.css('.exhibition-description p::text').getall()
        if description:
            item['description'] = ' '.join([d.strip() for d in description])
        
        # 提取参展艺术家
        artists = []
        artist_elements = response.css('.exhibition-artists a')
        for element in artist_elements:
            artist = {
                'name': element.css('::text').get('').strip(),
                'url': response.urljoin(element.css('::attr(href)').get(''))
            }
            if artist['name']:
                artists.append(artist)
        
        if artists:
            item['artists'] = artists
        
        return item
    
    def parse_artwork(self, response):
        """
        解析艺术品页面
        
        Args:
            response: 响应对象
            
        Returns:
            Dict[str, Any]: 解析结果
        """
        # 基础信息提取
        item = {
            'url': response.url,
            'page_type': 'artwork',
            'title': response.css('h1::text').get('').strip(),
            'artist_name': response.css('.artwork-artist-name::text').get('').strip(),
        }
        
        # 提取艺术品图片
        image_url = response.css('.artwork-image img::attr(src)').get('')
        if image_url:
            item['image_url'] = image_url
        
        # 提取艺术品详情
        details = {}
        detail_elements = response.css('.artwork-details .artwork-detail')
        for element in detail_elements:
            label = element.css('.artwork-detail-label::text').get('').strip().lower()
            value = element.css('.artwork-detail-value::text').get('').strip()
            if label and value:
                details[label] = value
        
        # 添加详情到主项目
        if 'date' in details:
            item['date'] = details['date']
        if 'medium' in details:
            item['medium'] = details['medium']
        if 'dimensions' in details:
            item['dimensions'] = details['dimensions']
        
        # 保存所有详情
        if details:
            item['details'] = details
        
        return item 