"""
爬虫运行脚本
"""
import argparse
import json
import logging
import os
import sys
from typing import Dict, Any

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from app.models.site import SiteConfig
from app.scrapers.spider_factory import SpiderFactory

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_config(config_file: str) -> Dict[str, Any]:
    """
    加载配置文件
    
    Args:
        config_file: 配置文件路径
        
    Returns:
        Dict[str, Any]: 配置字典
    """
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def run_spider(config_file: str, output_dir: str = 'output'):
    """
    运行爬虫
    
    Args:
        config_file: 配置文件路径
        output_dir: 输出目录
    """
    # 加载配置
    config = load_config(config_file)
    logger.info(f"加载配置: {config['name']}")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建SiteConfig对象
    site_config = SiteConfig(
        id=1,  # 示例ID
        name=config['name'],
        url=config['url'],
        description=config.get('description', ''),
        requires_login=config.get('requires_login', False),
        login_url=config.get('login_url', ''),
        login_username_field=config.get('login_username_field', ''),
        login_password_field=config.get('login_password_field', ''),
        login_username=config.get('login_username', ''),
        login_password=config.get('login_password', ''),
        start_urls=config.get('start_urls', [config['url']]),
        allowed_domains=config.get('allowed_domains', []),
        list_page_xpath=config.get('list_page_xpath', ''),
        next_page_xpath=config.get('next_page_xpath', ''),
        detail_page_xpath=config.get('detail_page_xpath', ''),
        field_mappings=config.get('field_mappings', {}),
        use_playwright=config.get('use_playwright', False),
        config=config.get('config', {}),
        tenant_id='test',
        is_active=True
    )
    
    # 获取Scrapy设置
    settings = get_project_settings()
    
    # 设置输出目录
    settings['FEEDS'] = {
        f'{output_dir}/items.json': {
            'format': 'json',
            'encoding': 'utf8',
            'indent': 2,
            'overwrite': True,
        },
    }
    
    # 创建爬虫进程
    process = CrawlerProcess(settings)
    
    # 创建爬虫
    spider = SpiderFactory.create_spider(site_config=site_config, job_id=999)
    
    logger.info(f"启动爬虫: {spider.name}")
    
    # 运行爬虫
    process.crawl(spider)
    process.start()
    
    logger.info("爬虫运行完成")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='运行爬虫')
    parser.add_argument('config', help='配置文件路径')
    parser.add_argument('--output', '-o', default='output', help='输出目录')
    
    args = parser.parse_args()
    
    run_spider(args.config, args.output) 