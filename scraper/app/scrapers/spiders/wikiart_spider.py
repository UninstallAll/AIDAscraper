"""
WikiArt网站爬虫
"""
import logging
from typing import Dict, Any, List, Iterator
import json
import re

import scrapy
from scrapy.http import Request, Response
from scrapy_playwright.page import PageMethod

from app.scrapers.playwright_spider import PlaywrightSpider


class WikiArtSpider(PlaywrightSpider):
    """
    WikiArt网站爬虫，用于爬取艺术家、作品和流派信息
    """
    name = 'wikiart_spider'
    
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
            if '/artists-by-century/' in response.url or '/paintings-by-genre/' in response.url:
                # 滚动加载更多内容
                self.logger.info("检测到列表页面，开始滚动加载更多内容")
                
                max_scrolls = self.site_config.config.get('max_pages', 3)
                scroll_delay = self.site_config.config.get('scroll_delay', 1000)
                
                for i in range(max_scrolls):
                    # 滚动到页面底部
                    await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                    # 等待加载
                    await page.wait_for_timeout(scroll_delay)
                    self.logger.info(f"完成第 {i+1}/{max_scrolls} 次滚动")
            
            # 获取页面内容
            html_content = await page.content()
            
            # 创建新的响应对象，包含JavaScript渲染后的内容
            new_response = response.replace(body=html_content.encode('utf-8'))
            
            # 关闭页面
            await page.close()
            
            # 根据URL类型处理不同页面
            if '/artist/' in response.url:
                yield self.parse_artist(new_response)
            elif '/painting/' in response.url:
                yield self.parse_artwork(new_response)
            elif '/artists-by-century/' in response.url:
                # 处理艺术家列表页
                for link in self.extract_artist_links(new_response):
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
            elif '/paintings-by-genre/' in response.url:
                # 处理作品列表页
                for link in self.extract_artwork_links(new_response):
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
            else:
                self.logger.info(f"未知页面类型: {response.url}")
        except Exception as e:
            self.logger.error(f"解析失败: {e}")
            await page.close()
    
    def extract_artist_links(self, response):
        """
        从艺术家列表页提取艺术家链接
        
        Args:
            response: 响应对象
            
        Returns:
            List[str]: 艺术家链接列表
        """
        links = response.css('a.artist-name::attr(href)').getall()
        
        # 限制数量
        max_items = self.site_config.config.get('max_items_per_category', 50)
        if len(links) > max_items:
            self.logger.info(f"提取的艺术家链接数量 ({len(links)}) 超过限制 ({max_items})，将截断")
            links = links[:max_items]
        
        self.logger.info(f"从页面 {response.url} 提取了 {len(links)} 个艺术家链接")
        return links
    
    def extract_artwork_links(self, response):
        """
        从作品列表页提取作品链接
        
        Args:
            response: 响应对象
            
        Returns:
            List[str]: 作品链接列表
        """
        links = response.css('a.artwork-name::attr(href), a.artwork-image::attr(href)').getall()
        
        # 去重
        links = list(set(links))
        
        # 限制数量
        max_items = self.site_config.config.get('max_items_per_category', 50)
        if len(links) > max_items:
            self.logger.info(f"提取的作品链接数量 ({len(links)}) 超过限制 ({max_items})，将截断")
            links = links[:max_items]
        
        self.logger.info(f"从页面 {response.url} 提取了 {len(links)} 个作品链接")
        return links
    
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
        }
        
        # 提取生卒年
        years_text = response.css('span.lifespan::text').get('')
        if years_text:
            years = re.findall(r'\d{4}', years_text)
            if len(years) >= 1:
                item['birth_year'] = years[0]
            if len(years) >= 2:
                item['death_year'] = years[1]
        
        # 提取国籍
        nationality = response.css('span.nationality::text').get('')
        if nationality:
            item['nationality'] = nationality.strip()
        
        # 提取艺术流派
        art_movement = response.css('a.dict::text').get('')
        if art_movement:
            item['art_movement'] = art_movement.strip()
        
        # 提取简介
        bio = response.css('div.wiki-layout-artist-bio p::text').getall()
        if bio:
            item['biography'] = ' '.join([b.strip() for b in bio])
        
        # 提取代表作品
        artworks = []
        artwork_elements = response.css('ul.wiki-masonry-container li.wiki-masonry-item')
        for element in artwork_elements[:10]:  # 最多提取10个作品
            artwork = {
                'title': element.css('span.artwork-name::text').get('').strip(),
                'url': response.urljoin(element.css('a::attr(href)').get('')),
                'image_url': element.css('img::attr(src)').get('')
            }
            if artwork['title']:
                artworks.append(artwork)
        
        if artworks:
            item['artworks'] = artworks
        
        return item
    
    def parse_artwork(self, response):
        """
        解析作品页面
        
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
        }
        
        # 提取艺术家信息
        artist_name = response.css('a.artist-name::text').get('')
        if artist_name:
            item['artist_name'] = artist_name.strip()
            item['artist_url'] = response.urljoin(response.css('a.artist-name::attr(href)').get(''))
        
        # 提取年份
        year = response.css('span.date::text').get('')
        if year:
            item['year'] = year.strip()
        
        # 提取风格
        style = response.css('a.dict[href*="style"]::text').get('')
        if style:
            item['style'] = style.strip()
        
        # 提取流派
        genre = response.css('a.dict[href*="genre"]::text').get('')
        if genre:
            item['genre'] = genre.strip()
        
        # 提取媒介
        medium = response.css('span[itemprop="artMedium"]::text').get('')
        if medium:
            item['medium'] = medium.strip()
        
        # 提取尺寸
        dimensions = response.css('span[itemprop="width"], span[itemprop="height"]::text').getall()
        if dimensions and len(dimensions) >= 2:
            item['dimensions'] = f"{dimensions[0]} × {dimensions[1]}"
        
        # 提取图片URL
        image_url = response.css('img.wiki-image::attr(src)').get('')
        if image_url:
            item['image_url'] = image_url
        
        # 提取描述
        description = response.css('div.wiki-layout-artist-info p::text').getall()
        if description:
            item['description'] = ' '.join([d.strip() for d in description])
        
        return item 