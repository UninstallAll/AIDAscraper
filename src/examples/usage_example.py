"""
爬虫系统使用示例 - 展示如何使用爬虫注册表和深度搜索引擎
"""
import os
import sys
import logging
import json
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.scrapers.registry import ScraperRegistry
from src.scrapers.sites.artsy import ArtsyArtworkScraper, ArtsyArtistScraper
from src.scrapers.deep_search.engine import DeepSearchEngine

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def example_registry_usage():
    """展示如何使用爬虫注册表"""
    logger.info("=== 爬虫注册表使用示例 ===")
    
    # 创建配置文件目录
    os.makedirs("data/config", exist_ok=True)
    
    # 初始化爬虫注册表
    registry = ScraperRegistry(config_path="data/config/registry_config.json")
    
    # 注册爬虫类
    registry.register_scraper(ArtsyArtworkScraper, "artsy_artwork")
    registry.register_scraper(ArtsyArtistScraper, "artsy_artist")
    
    # 注册网站
    registry.register_website(
        website_id="artsy",
        name="Artsy",
        url="https://www.artsy.net",
        description="Artsy是一个艺术作品与艺术家信息的在线平台",
        metadata={
            "founded": 2009,
            "headquarters": "New York",
            "focus": "Contemporary Art"
        }
    )
    
    # 将爬虫与网站关联
    registry.link_scraper_to_website(
        website_id="artsy",
        scraper_id="artsy_artwork",
        config={
            "timeout": 60,
            "retry_count": 5,
            "headless": True
        },
        task_name="artwork_list"
    )
    
    registry.link_scraper_to_website(
        website_id="artsy",
        scraper_id="artsy_artist",
        config={
            "timeout": 60,
            "retry_count": 5,
            "headless": True
        },
        task_name="artist_list"
    )
    
    # 获取网站信息
    website = registry.get_website("artsy")
    logger.info(f"网站信息: {website['name']} - {website['url']}")
    
    # 获取网站关联的爬虫
    scrapers = registry.get_website_scrapers("artsy")
    logger.info(f"网站关联的爬虫任务: {len(scrapers)}")
    for scraper in scrapers:
        logger.info(f"  - {scraper['task_name']} (使用 {scraper['scraper_id']} 爬虫)")
    
    # 运行网站的特定爬虫任务
    # 注意：实际运行时会请求网络，这里注释掉
    """
    result = registry.run_website_scraper(
        website_id="artsy",
        task_name="artwork_list",
        page=1,
        limit=10,
        max_pages=1  # 只爬取一页
    )
    
    logger.info(f"爬取结果: {result['status']}, 获取到 {result['results_count']} 条数据")
    """
    
    logger.info("爬虫注册表示例运行完成")

def example_deep_search_usage():
    """展示如何使用深度搜索引擎"""
    logger.info("=== 深度搜索引擎使用示例 ===")
    
    # 创建保存目录
    os.makedirs("data/search_results", exist_ok=True)
    
    # 初始化深度搜索引擎
    config = {
        "max_depth": 2,  # 最大搜索深度
        "max_urls": 20,  # 最大处理URL数量
        "concurrency": 1,  # 并发数
        "request_delay": 2000,  # 请求延迟（毫秒）
        "use_playwright": True,  # 使用Playwright处理JavaScript
        "headless": True,  # 无头模式
        "save_path": "data/search_results",  # 结果保存路径
        "url_filter": {
            "allowed_domains": ["example.com"],  # 允许的域名
            "excluded_paths": ["/login", "/register"]  # 排除的路径
        }
    }
    
    search_engine = DeepSearchEngine(config)
    
    # 运行深度搜索
    # 注意：实际运行时会请求网络，这里注释掉
    """
    result = search_engine.search("https://example.com")
    
    logger.info(f"搜索结果: {result['status']}")
    logger.info(f"访问URL数: {result['visited_urls_count']}")
    logger.info(f"提取数据条数: {result['results_count']}")
    logger.info(f"搜索耗时: {result['duration']} 秒")
    logger.info(f"结果保存在: {result['save_path']}")
    """
    
    logger.info("深度搜索引擎示例运行完成")

def example_custom_extractor():
    """展示如何创建自定义数据提取器"""
    from src.scrapers.deep_search.engine import DataExtractor, DeepSearchEngine
    
    class ArtworkExtractor(DataExtractor):
        """自定义艺术品数据提取器"""
        
        def extract(self, html_content: str, url: str) -> dict:
            """提取艺术品信息"""
            from bs4 import BeautifulSoup
            
            # 调用父类方法获取基本信息
            base_data = super().extract(html_content, url)
            
            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(html_content, 'lxml')
            
            # 提取艺术品特定信息
            artworks = []
            artwork_elements = soup.select('div.artwork-item')
            
            for elem in artwork_elements:
                try:
                    title_elem = elem.select_one('.artwork-title')
                    artist_elem = elem.select_one('.artist-name')
                    
                    artwork = {
                        "title": title_elem.text.strip() if title_elem else "Unknown",
                        "artist": artist_elem.text.strip() if artist_elem else "Unknown",
                        "url": url
                    }
                    
                    artworks.append(artwork)
                    
                except Exception as e:
                    logger.warning(f"Error extracting artwork: {e}")
            
            # 将艺术品信息添加到基本数据中
            base_data["artworks"] = artworks
            base_data["artwork_count"] = len(artworks)
            
            return base_data
    
    # 创建使用自定义提取器的搜索引擎
    config = {
        "max_depth": 2,
        "max_urls": 10
    }
    
    # 初始化搜索引擎，设置自定义提取器
    search_engine = DeepSearchEngine(config)
    search_engine.data_extractor = ArtworkExtractor()
    
    logger.info("自定义提取器示例完成")

if __name__ == "__main__":
    logger.info("开始运行爬虫系统使用示例")
    
    example_registry_usage()
    print("\n")
    
    example_deep_search_usage()
    print("\n")
    
    example_custom_extractor()
    
    logger.info("示例运行完成") 