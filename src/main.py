#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
艺术数据爬虫主模块
"""

import argparse
import logging
import sys

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
    parser.add_argument('--site', type=str, help='要爬取的网站名称')
    parser.add_argument('--limit', type=int, default=100, help='爬取数量限制')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("调试模式已启用")
    
    logger.info("艺术数据爬虫启动")
    logger.info(f"目标网站: {args.site if args.site else '所有'}")
    logger.info(f"爬取数量限制: {args.limit}")
    
    # TODO: 实现爬虫调用逻辑
    
    logger.info("爬虫执行完成")


if __name__ == "__main__":
    main() 