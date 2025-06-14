#!/usr/bin/env python
"""
AIDA Scraper 启动脚本
"""
import argparse
import logging
import os
import sys
import uvicorn

from app.db.init_db import create_tables, init_db
from app.db.database import SessionLocal

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database():
    """初始化数据库"""
    logger.info("初始化数据库")
    create_tables()
    
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()
    
    logger.info("数据库初始化完成")


def start_api(host="0.0.0.0", port=8000, reload=True):
    """启动API服务"""
    logger.info(f"启动API服务 - http://{host}:{port}")
    uvicorn.run("app.main:app", host=host, port=port, reload=reload)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AIDA Scraper 启动脚本")
    parser.add_argument("--init-db", action="store_true", help="初始化数据库")
    parser.add_argument("--start-api", action="store_true", help="启动API服务")
    parser.add_argument("--host", default="0.0.0.0", help="API服务主机")
    parser.add_argument("--port", type=int, default=8000, help="API服务端口")
    parser.add_argument("--no-reload", action="store_true", help="禁用热重载")
    
    args = parser.parse_args()
    
    if args.init_db:
        init_database()
    
    if args.start_api:
        start_api(host=args.host, port=args.port, reload=not args.no_reload)
    
    if not (args.init_db or args.start_api):
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main() 