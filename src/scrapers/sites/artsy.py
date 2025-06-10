"""
Artsy网站爬虫 - 用于爬取Artsy网站的艺术品数据
"""
import logging
import json
from typing import Dict, List, Any, Optional

from ..base import BaseScraper

logger = logging.getLogger(__name__)

class ArtsyArtworkScraper(BaseScraper):
    """
    Artsy艺术品爬虫 - 爬取艺术品列表和详情
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.base_url = "https://www.artsy.net"
        self.api_url = "https://www.artsy.net/api/v1"
        
    def _scrape(self, **kwargs) -> None:
        """
        实现爬取逻辑
        
        Args:
            **kwargs: 可能包含起始页、过滤条件等参数
        """
        # 获取参数
        page = kwargs.get('page', 1)
        limit = kwargs.get('limit', 20)
        category = kwargs.get('category', None)
        
        # 构建API URL
        url = f"{self.api_url}/search/artworks"
        params = {
            "page": page,
            "size": limit
        }
        
        if category:
            params["gene"] = category
            
        # 发起请求
        logger.info(f"Scraping artworks from Artsy, page={page}, limit={limit}")
        
        try:
            # 使用Playwright获取动态内容
            browser, page_obj, content = self._get_page_with_playwright(
                f"{self.base_url}/collect?page={page}"
            )
            
            try:
                if not content:
                    raise ValueError("Failed to get page content")
                
                # 这里我们可以解析页面内容
                # 在实际应用中，需要根据网站结构提取数据
                artworks = self._extract_artworks(content)
                
                # 保存结果
                for artwork in artworks:
                    self.results.append(artwork)
                    
                logger.info(f"Scraped {len(artworks)} artworks from Artsy")
                
                # 如果需要，可以爬取下一页
                next_page = page + 1
                if next_page <= kwargs.get('max_pages', 1):
                    self._scrape(page=next_page, limit=limit, category=category, 
                                max_pages=kwargs.get('max_pages', 1))
            finally:
                # 确保关闭浏览器
                if browser:
                    browser.close()
        except Exception as e:
            logger.error(f"Error scraping Artsy: {str(e)}", exc_info=True)
            self.errors.append(f"Failed to scrape page {page}: {str(e)}")
    
    def _extract_artworks(self, html_content: str) -> List[Dict[str, Any]]:
        """
        从HTML内容中提取艺术品信息
        
        Args:
            html_content: 页面HTML内容
            
        Returns:
            艺术品信息列表
        """
        from bs4 import BeautifulSoup
        
        artworks = []
        soup = BeautifulSoup(html_content, 'lxml')
        
        # 找到艺术品容器
        # 注意：以下选择器需要根据实际网站结构调整
        artwork_elements = soup.select('div[data-test="artworkGridItem"]')
        
        for elem in artwork_elements:
            try:
                # 提取艺术品信息
                title_elem = elem.select_one('div[data-test="title"]')
                artist_elem = elem.select_one('div[data-test="artist"]')
                price_elem = elem.select_one('div[data-test="price"]')
                image_elem = elem.select_one('img')
                
                artwork = {
                    "title": title_elem.text.strip() if title_elem else "Unknown Title",
                    "artist": artist_elem.text.strip() if artist_elem else "Unknown Artist",
                    "price": price_elem.text.strip() if price_elem else None,
                    "image_url": image_elem.get('src') if image_elem else None,
                    "source": "artsy",
                    "source_url": self.base_url + elem.select_one('a').get('href') if elem.select_one('a') else None
                }
                
                artworks.append(artwork)
                
            except Exception as e:
                logger.warning(f"Error extracting artwork data: {str(e)}")
                continue
                
        return artworks


class ArtsyArtistScraper(BaseScraper):
    """
    Artsy艺术家爬虫 - 爬取艺术家列表和详情
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.base_url = "https://www.artsy.net"
        self.api_url = "https://www.artsy.net/api/v1"
        
    def _scrape(self, **kwargs) -> None:
        """
        实现爬取逻辑
        
        Args:
            **kwargs: 可能包含起始页、过滤条件等参数
        """
        # 获取参数
        page = kwargs.get('page', 1)
        limit = kwargs.get('limit', 20)
        nationality = kwargs.get('nationality', None)
        
        # 构建请求URL
        url = f"{self.base_url}/artists?page={page}"
        
        logger.info(f"Scraping artists from Artsy, page={page}, limit={limit}")
        
        try:
            # 使用Playwright获取动态内容
            browser, page_obj, content = self._get_page_with_playwright(url)
            
            try:
                if not content:
                    raise ValueError("Failed to get page content")
                
                # 解析页面内容
                artists = self._extract_artists(content)
                
                # 保存结果
                for artist in artists:
                    self.results.append(artist)
                    
                logger.info(f"Scraped {len(artists)} artists from Artsy")
                
                # 如果需要，可以爬取下一页
                next_page = page + 1
                if next_page <= kwargs.get('max_pages', 1):
                    self._scrape(page=next_page, limit=limit, nationality=nationality, 
                                max_pages=kwargs.get('max_pages', 1))
            finally:
                # 确保关闭浏览器
                if browser:
                    browser.close()
        except Exception as e:
            logger.error(f"Error scraping Artsy artists: {str(e)}", exc_info=True)
            self.errors.append(f"Failed to scrape artist page {page}: {str(e)}")
    
    def _extract_artists(self, html_content: str) -> List[Dict[str, Any]]:
        """
        从HTML内容中提取艺术家信息
        
        Args:
            html_content: 页面HTML内容
            
        Returns:
            艺术家信息列表
        """
        from bs4 import BeautifulSoup
        
        artists = []
        soup = BeautifulSoup(html_content, 'lxml')
        
        # 找到艺术家容器
        # 注意：以下选择器需要根据实际网站结构调整
        artist_elements = soup.select('div.artist-rail__item')
        
        for elem in artist_elements:
            try:
                # 提取艺术家信息
                name_elem = elem.select_one('div.artist-rail__name')
                info_elem = elem.select_one('div.artist-rail__info')
                image_elem = elem.select_one('img')
                link_elem = elem.select_one('a')
                
                artist = {
                    "name": name_elem.text.strip() if name_elem else "Unknown Artist",
                    "info": info_elem.text.strip() if info_elem else None,
                    "image_url": image_elem.get('src') if image_elem else None,
                    "source": "artsy",
                    "source_url": self.base_url + link_elem.get('href') if link_elem else None
                }
                
                artists.append(artist)
                
            except Exception as e:
                logger.warning(f"Error extracting artist data: {str(e)}")
                continue
                
        return artists 