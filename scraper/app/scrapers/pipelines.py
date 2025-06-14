"""
Scrapy Pipeline
"""
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any

from app.tasks.scraper_tasks import update_job_progress

# 设置日志
logger = logging.getLogger(__name__)


class JsonWriterPipeline:
    """
    将爬取的数据写入JSON文件
    """
    
    def __init__(self):
        """
        初始化Pipeline
        """
        self.items = []
        self.item_count = 0
        self.saved_count = 0
        self.output_dir = "output"
        
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
    
    def process_item(self, item: Dict[str, Any], spider) -> Dict[str, Any]:
        """
        处理爬取的数据
        
        Args:
            item: 爬取的数据项
            spider: 爬虫实例
            
        Returns:
            Dict[str, Any]: 处理后的数据项
        """
        # 添加时间戳
        item['timestamp'] = datetime.now().isoformat()
        
        # 保存到内存
        self.items.append(item)
        self.item_count += 1
        
        # 每50个项目保存一次
        if self.item_count % 50 == 0:
            self._save_items(spider)
            
            # 更新任务进度
            if hasattr(spider, 'job_id'):
                # 计算进度（假设每个任务最多抓取1000个项目）
                progress = min(int(self.item_count / 1000 * 100), 99)
                update_job_progress.delay(
                    job_id=spider.job_id,
                    progress=progress,
                    items_scraped=self.item_count,
                    items_saved=self.saved_count
                )
        
        return item
    
    def close_spider(self, spider) -> None:
        """
        爬虫关闭时的处理
        
        Args:
            spider: 爬虫实例
        """
        # 保存剩余的项目
        if self.items:
            self._save_items(spider)
    
    def _save_items(self, spider) -> None:
        """
        保存爬取的数据到JSON文件
        
        Args:
            spider: 爬虫实例
        """
        if not self.items:
            return
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        tenant_id = getattr(spider.site_config, 'tenant_id', 'default')
        job_id = getattr(spider, 'job_id', 'unknown')
        
        # 创建租户目录
        tenant_dir = os.path.join(self.output_dir, tenant_id)
        os.makedirs(tenant_dir, exist_ok=True)
        
        # 创建任务目录
        job_dir = os.path.join(tenant_dir, str(job_id))
        os.makedirs(job_dir, exist_ok=True)
        
        # 保存到文件
        filename = os.path.join(job_dir, f"items_{timestamp}_{self.saved_count}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.items, f, ensure_ascii=False, indent=2)
        
        # 更新计数
        self.saved_count += len(self.items)
        logger.info(f"已保存 {len(self.items)} 个项目到 {filename}")
        
        # 清空内存中的项目
        self.items = [] 