#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
艺术数据爬虫主模块
"""

import argparse
import logging
import sys
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='艺术数据爬虫')
    
    # 添加子命令分组
    subparsers = parser.add_subparsers(dest='command', help='子命令')
    
    # 爬虫命令
    scrape_parser = subparsers.add_parser('scrape', help='运行爬虫')
    scrape_parser.add_argument('--site', type=str, help='要爬取的网站名称')
    scrape_parser.add_argument('--limit', type=int, default=100, help='爬取数量限制')
    scrape_parser.add_argument('--debug', action='store_true', help='启用调试模式')
    
    # 网站管理命令
    site_parser = subparsers.add_parser('sites', help='网站管理')
    site_subparsers = site_parser.add_subparsers(dest='site_command', help='网站管理子命令')
    
    # 列出网站
    list_parser = site_subparsers.add_parser('list', help='列出所有网站')
    list_parser.add_argument('-v', '--verbose', action='store_true', help='显示详细信息')
    
    # 添加网站
    add_parser = site_subparsers.add_parser('add', help='添加网站')
    add_parser.add_argument('--id', required=True, help='网站ID')
    add_parser.add_argument('--name', required=True, help='网站名称')
    add_parser.add_argument('--url', required=True, help='网站URL')
    add_parser.add_argument('--description', help='网站描述')
    
    # 创建网站爬虫
    create_parser = site_subparsers.add_parser('create-scraper', help='创建网站爬虫')
    create_parser.add_argument('--id', required=True, help='网站ID')
    create_parser.add_argument('--name', required=True, help='爬虫类名')
    
    # 运行网站爬虫
    run_parser = site_subparsers.add_parser('run', help='运行网站爬虫')
    run_parser.add_argument('--id', required=True, help='网站ID')
    run_parser.add_argument('--content', choices=['artworks', 'artists', 'exhibitions'], 
                         default='artworks', help='爬取内容类型')
    run_parser.add_argument('--pages', type=int, default=1, help='最大页数')
    run_parser.add_argument('--limit', type=int, default=20, help='每页数量')
    
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_args()
    
    # 确保配置目录存在
    os.makedirs('config', exist_ok=True)
    
    # 如果没有指定命令，显示帮助信息
    if not hasattr(args, 'command') or args.command is None:
        logging.info("未指定命令，使用默认爬虫模式")
        run_default_scraper(args)
        return
        
    # 根据命令执行相应操作
    if args.command == 'scrape':
        run_scraper(args)
    elif args.command == 'sites':
        manage_sites(args)
    else:
        logging.error(f"未知命令: {args.command}")
        sys.exit(1)


def run_default_scraper(args):
    """运行默认爬虫（向后兼容）"""
    if getattr(args, 'debug', False):
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("调试模式已启用")
    
    logger.info("艺术数据爬虫启动")
    logger.info(f"目标网站: {getattr(args, 'site', '所有')}")
    logger.info(f"爬取数量限制: {getattr(args, 'limit', 100)}")
    
    # 尝试导入网站管理器
    try:
        from scrapers.site_manager import WebsiteManager
        from scrapers.registry import ScraperRegistry
        
        registry = ScraperRegistry(config_path='config/sites_registry.json')
        manager = WebsiteManager(registry=registry)
        
        websites = manager.list_websites()
        if websites:
            logger.info(f"已注册 {len(websites)} 个网站，使用 'python -m src.main sites list' 查看详情")
        else:
            logger.info("未注册任何网站，使用 'python -m src.main sites add --id <id> --name <name> --url <url>' 添加网站")
    except Exception as e:
        logger.warning(f"无法初始化网站管理器: {str(e)}")
    
    logger.info("爬虫执行完成")


def run_scraper(args):
    """运行爬虫命令"""
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("调试模式已启用")
    
    logger.info("爬虫任务开始")
    
    if args.site:
        logger.info(f"使用网站管理器运行爬虫: {args.site}")
        try:
            from scrapers.site_manager import WebsiteManager
            from scrapers.registry import ScraperRegistry
            
            registry = ScraperRegistry(config_path='config/sites_registry.json')
            manager = WebsiteManager(registry=registry)
            
            result = manager.run_website_scraper(
                website_id=args.site,
                limit=args.limit,
                max_pages=args.limit // 20 + 1
            )
            
            logger.info(f"爬虫执行完成，获取 {result.get('results_count', 0)} 个结果")
            
            if result.get('errors_count', 0) > 0:
                logger.warning(f"爬虫执行过程中出现 {result['errors_count']} 个错误")
                for error in result.get('errors', [])[:5]:
                    logger.warning(f"错误: {error}")
                    
        except Exception as e:
            logger.error(f"爬虫执行失败: {str(e)}", exc_info=True)
    else:
        logger.info("未指定网站，尝试运行所有已注册网站的爬虫")
        try:
            from scrapers.site_manager import WebsiteManager
            from scrapers.registry import ScraperRegistry
            
            registry = ScraperRegistry(config_path='config/sites_registry.json')
            manager = WebsiteManager(registry=registry)
            
            websites = manager.list_websites()
            
            if not websites:
                logger.warning("未注册任何网站，使用 'python -m src.main sites add' 添加网站")
                return
                
            for website in websites:
                try:
                    logger.info(f"运行网站爬虫: {website['name']}")
                    result = manager.run_website_scraper(
                        website_id=website['id'],
                        limit=args.limit // len(websites),
                        max_pages=(args.limit // len(websites)) // 20 + 1
                    )
                    logger.info(f"完成网站 {website['name']}，获取 {result.get('results_count', 0)} 个结果")
                except Exception as site_e:
                    logger.error(f"网站 {website['name']} 爬虫失败: {str(site_e)}")
                    
        except Exception as e:
            logger.error(f"爬虫批量执行失败: {str(e)}", exc_info=True)


def manage_sites(args):
    """管理网站命令"""
    if not hasattr(args, 'site_command') or args.site_command is None:
        logger.error("未指定网站管理子命令")
        sys.exit(1)
        
    try:
        from scrapers.site_cli import WebsiteManagerCLI
        
        cli = WebsiteManagerCLI()
        
        # 构造CLI参数
        cli_args = [args.site_command]
        
        # 添加各命令的相关参数
        if args.site_command == 'list':
            if getattr(args, 'verbose', False):
                cli_args.append('--verbose')
        elif args.site_command == 'add':
            cli_args.extend(['--id', args.id, '--name', args.name, '--url', args.url])
            if getattr(args, 'description', None):
                cli_args.extend(['--description', args.description])
        elif args.site_command == 'create-scraper':
            cli_args.extend(['--id', args.id, '--name', args.name])
        elif args.site_command == 'run':
            cli_args.extend([
                '--id', args.id, 
                '--content', args.content, 
                '--pages', str(args.pages),
                '--limit', str(args.limit)
            ])
            
        # 执行CLI命令
        cli.run(cli_args)
        
    except Exception as e:
        logger.error(f"网站管理操作失败: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main() 