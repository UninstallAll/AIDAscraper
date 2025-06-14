"""
启动Celery Worker的脚本
"""
import os
import sys
import argparse
import logging
import subprocess
from typing import List

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def start_worker(concurrency: int = 4, loglevel: str = "info", queue: str = "default"):
    """
    启动Celery Worker
    
    Args:
        concurrency: 并发数
        loglevel: 日志级别
        queue: 队列名称
    """
    logger.info(f"启动Celery Worker: 并发数={concurrency}, 日志级别={loglevel}, 队列={queue}")
    
    # 构建命令
    cmd = [
        "celery", 
        "-A", "app.core.celery_app", 
        "worker",
        "--loglevel", loglevel,
        "--concurrency", str(concurrency),
        "--queues", queue,
        "--hostname", f"worker@%h.{queue}",
    ]
    
    # 启动Worker
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        logger.info("Worker已停止")
    except Exception as e:
        logger.exception(f"启动Worker失败: {e}")
        sys.exit(1)


def start_beat(loglevel: str = "info"):
    """
    启动Celery Beat
    
    Args:
        loglevel: 日志级别
    """
    logger.info(f"启动Celery Beat: 日志级别={loglevel}")
    
    # 构建命令
    cmd = [
        "celery", 
        "-A", "app.core.celery_app", 
        "beat",
        "--loglevel", loglevel,
    ]
    
    # 启动Beat
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        logger.info("Beat已停止")
    except Exception as e:
        logger.exception(f"启动Beat失败: {e}")
        sys.exit(1)


def start_flower(port: int = 5555):
    """
    启动Flower监控
    
    Args:
        port: 端口号
    """
    logger.info(f"启动Flower监控: 端口={port}")
    
    # 构建命令
    cmd = [
        "celery", 
        "-A", "app.core.celery_app", 
        "flower",
        "--port", str(port),
    ]
    
    # 启动Flower
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        logger.info("Flower已停止")
    except Exception as e:
        logger.exception(f"启动Flower失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="启动Celery Worker/Beat/Flower")
    parser.add_argument("--mode", choices=["worker", "beat", "flower"], default="worker", help="启动模式")
    parser.add_argument("--concurrency", type=int, default=4, help="Worker并发数")
    parser.add_argument("--loglevel", default="info", help="日志级别")
    parser.add_argument("--queue", default="default", help="队列名称")
    parser.add_argument("--port", type=int, default=5555, help="Flower端口号")
    
    args = parser.parse_args()
    
    # 根据模式启动相应服务
    if args.mode == "worker":
        start_worker(args.concurrency, args.loglevel, args.queue)
    elif args.mode == "beat":
        start_beat(args.loglevel)
    elif args.mode == "flower":
        start_flower(args.port) 