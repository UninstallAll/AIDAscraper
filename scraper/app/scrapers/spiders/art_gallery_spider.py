"""
艺术画廊网站爬虫示例
"""
import logging
from typing import Dict, Any, List

import scrapy
from scrapy.http import Response

from app.scrapers.playwright_spider import PlaywrightSpider


class ArtGallerySpider(PlaywrightSpider):
    """
    艺术画廊网站爬虫示例
    
    用于爬取艺术家信息、展览信息等
    """
    name = 'art_gallery_spider'
    
    def parse_item(self, response: Response) -> Dict[str, Any]:
        """
        解析详情页
        
        Args:
            response: 响应对象
            
        Returns:
            Dict[str, Any]: 解析结果
        """
        # 首先使用通用字段映射提取数据
        item = super().parse_item(response)
        
        # 根据页面类型进行特殊处理
        if 'artist' in response.url.lower():
            self._parse_artist_page(response, item)
        elif 'exhibition' in response.url.lower():
            self._parse_exhibition_page(response, item)
        elif 'artwork' in response.url.lower():
            self._parse_artwork_page(response, item)
        
        return item
    
    def _parse_artist_page(self, response: Response, item: Dict[str, Any]) -> None:
        """
        解析艺术家页面
        
        Args:
            response: 响应对象
            item: 已提取的数据项
        """
        # 提取社交媒体链接
        social_links = response.xpath('//a[contains(@href, "instagram.com") or contains(@href, "twitter.com")]/@href').getall()
        if social_links:
            item['social_links'] = social_links
        
        # 提取展览历史
        exhibitions = []
        exhibition_elements = response.xpath('//div[contains(@class, "exhibition-history")]//li')
        for element in exhibition_elements:
            exhibition = {
                'title': element.xpath('.//a/text()').get('').strip(),
                'year': element.xpath('.//span[@class="year"]/text()').get('').strip(),
                'location': element.xpath('.//span[@class="location"]/text()').get('').strip()
            }
            if exhibition['title']:
                exhibitions.append(exhibition)
        
        if exhibitions:
            item['exhibitions'] = exhibitions
        
        # 标记页面类型
        item['page_type'] = 'artist'
    
    def _parse_exhibition_page(self, response: Response, item: Dict[str, Any]) -> None:
        """
        解析展览页面
        
        Args:
            response: 响应对象
            item: 已提取的数据项
        """
        # 提取参展艺术家
        artists = []
        artist_elements = response.xpath('//div[contains(@class, "artists-list")]//a')
        for element in artist_elements:
            artist = {
                'name': element.xpath('./text()').get('').strip(),
                'url': response.urljoin(element.xpath('./@href').get(''))
            }
            if artist['name']:
                artists.append(artist)
        
        if artists:
            item['artists'] = artists
        
        # 提取展览日期
        date_range = response.xpath('//div[contains(@class, "exhibition-dates")]/text()').get('')
        if date_range:
            item['date_range'] = date_range.strip()
        
        # 提取策展人
        curator = response.xpath('//div[contains(@class, "curator")]/text()').get('')
        if curator:
            item['curator'] = curator.strip()
        
        # 标记页面类型
        item['page_type'] = 'exhibition'
    
    def _parse_artwork_page(self, response: Response, item: Dict[str, Any]) -> None:
        """
        解析艺术作品页面
        
        Args:
            response: 响应对象
            item: 已提取的数据项
        """
        # 提取作品图片
        image_url = response.xpath('//div[contains(@class, "artwork-image")]//img/@src').get('')
        if image_url:
            item['image_url'] = response.urljoin(image_url)
        
        # 提取作品尺寸
        dimensions = response.xpath('//div[contains(@class, "dimensions")]/text()').get('')
        if dimensions:
            item['dimensions'] = dimensions.strip()
        
        # 提取作品材质
        medium = response.xpath('//div[contains(@class, "medium")]/text()').get('')
        if medium:
            item['medium'] = medium.strip()
        
        # 提取作品年份
        year = response.xpath('//div[contains(@class, "year")]/text()').get('')
        if year:
            item['year'] = year.strip()
        
        # 标记页面类型
        item['page_type'] = 'artwork' 