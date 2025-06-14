"""
Scrapy日志处理器
用于将Scrapy的日志集成到我们的JobLogger系统中
"""
import logging
from typing import Optional

from scrapy.utils.log import LogFormatter

from app.utils.logger import get_job_logger


class JobLoggerHandler(logging.Handler):
    """
    将Scrapy的日志重定向到JobLogger
    """
    def __init__(self, job_id: int, level: int = logging.INFO):
        """
        初始化日志处理器
        
        Args:
            job_id: 任务ID
            level: 日志级别
        """
        super().__init__(level)
        self.job_id = job_id
        self.job_logger = get_job_logger(job_id)
        self.formatter = LogFormatter()
    
    def emit(self, record):
        """
        发送日志记录
        
        Args:
            record: 日志记录
        """
        try:
            # 获取日志级别
            level_name = record.levelname
            
            # 格式化消息
            message = self.format(record)
            
            # 根据级别发送日志
            if level_name == 'DEBUG':
                self.job_logger.debug(message)
            elif level_name == 'INFO':
                self.job_logger.info(message)
            elif level_name == 'WARNING':
                self.job_logger.warning(message)
            elif level_name == 'ERROR':
                self.job_logger.error(message)
            elif level_name == 'CRITICAL':
                self.job_logger.error(f"CRITICAL: {message}")
            else:
                self.job_logger.info(message)
        except Exception as e:
            # 避免日志处理器出错导致程序崩溃
            print(f"Error in JobLoggerHandler: {e}")


def setup_job_logger(job_id: int, level: int = logging.INFO) -> None:
    """
    设置任务日志处理器
    
    Args:
        job_id: 任务ID
        level: 日志级别
    """
    # 获取Scrapy的根日志记录器
    root_logger = logging.getLogger('scrapy')
    
    # 创建任务日志处理器
    handler = JobLoggerHandler(job_id, level)
    
    # 设置格式化器
    formatter = LogFormatter()
    handler.setFormatter(formatter)
    
    # 添加处理器到根日志记录器
    root_logger.addHandler(handler)
    
    # 设置日志级别
    root_logger.setLevel(level)
    
    # 获取其他相关日志记录器并添加处理器
    loggers = [
        logging.getLogger('scrapy.core'),
        logging.getLogger('scrapy.middleware'),
        logging.getLogger('scrapy.extensions'),
        logging.getLogger('scrapy.crawler'),
        logging.getLogger('scrapy.dupefilters'),
        logging.getLogger('scrapy.spiders'),
        logging.getLogger('scrapy.downloadermiddlewares'),
        logging.getLogger('scrapy.pipelines'),
        logging.getLogger('aida_scraper'),
    ]
    
    for logger in loggers:
        logger.addHandler(handler)
        logger.setLevel(level)
        # 避免日志消息被传递到父记录器
        logger.propagate = False 