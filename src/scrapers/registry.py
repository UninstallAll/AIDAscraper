"""
爬虫注册表模块 - 管理网站与爬虫的关联关系
"""
import logging
import importlib
import inspect
from typing import Dict, List, Any, Type, Optional, Callable
import json
import os
from pathlib import Path

from .base import BaseScraper

logger = logging.getLogger(__name__)

class ScraperRegistry:
    """
    爬虫注册表 - 管理网站与爬虫的关联关系，实现爬虫的注册、查找和执行
    """
    
    def __init__(self, config_path: str = None):
        """
        初始化爬虫注册表
        
        Args:
            config_path: 配置文件路径，用于持久化存储配置
        """
        self.websites = {}  # website_id -> website_info
        self.scrapers = {}  # scraper_id -> scraper_class
        self.website_scrapers = {}  # website_id -> [scraper_id, ...]
        self.config_path = config_path
        
        # 如果配置文件存在，加载配置
        if config_path and os.path.exists(config_path):
            self.load_config()
    
    def register_scraper(self, scraper_class: Type[BaseScraper], scraper_id: str = None) -> str:
        """
        注册爬虫类
        
        Args:
            scraper_class: 爬虫类，必须是BaseScraper的子类
            scraper_id: 爬虫ID，如果不提供则使用类名
            
        Returns:
            注册的爬虫ID
            
        Raises:
            TypeError: 如果爬虫类不是BaseScraper的子类
        """
        if not inspect.isclass(scraper_class) or not issubclass(scraper_class, BaseScraper):
            raise TypeError(f"Scraper class must be a subclass of BaseScraper: {scraper_class}")
        
        # 如果未提供ID，使用类名
        if not scraper_id:
            scraper_id = scraper_class.__name__
            
        self.scrapers[scraper_id] = scraper_class
        logger.info(f"Registered scraper: {scraper_id}")
        
        return scraper_id
    
    def register_website(self, 
                        website_id: str, 
                        name: str, 
                        url: str, 
                        description: str = "", 
                        metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        注册网站
        
        Args:
            website_id: 网站唯一标识符
            name: 网站名称
            url: 网站URL
            description: 网站描述
            metadata: 网站元数据
            
        Returns:
            网站信息字典
        """
        website_info = {
            "id": website_id,
            "name": name,
            "url": url,
            "description": description,
            "metadata": metadata or {},
            "created_at": self._get_timestamp(),
            "updated_at": self._get_timestamp()
        }
        
        self.websites[website_id] = website_info
        
        # 初始化网站的爬虫列表
        if website_id not in self.website_scrapers:
            self.website_scrapers[website_id] = []
            
        logger.info(f"Registered website: {website_id} - {name}")
        
        # 保存配置
        self.save_config()
        
        return website_info
    
    def link_scraper_to_website(self, 
                              website_id: str, 
                              scraper_id: str, 
                              config: Dict[str, Any] = None,
                              task_name: str = None) -> bool:
        """
        将爬虫与网站关联
        
        Args:
            website_id: 网站ID
            scraper_id: 爬虫ID
            config: 爬虫配置
            task_name: 任务名称，用于标识该爬虫在网站上的用途
            
        Returns:
            是否成功关联
            
        Raises:
            ValueError: 如果网站ID或爬虫ID不存在
        """
        if website_id not in self.websites:
            raise ValueError(f"Website not found: {website_id}")
            
        if scraper_id not in self.scrapers:
            raise ValueError(f"Scraper not found: {scraper_id}")
            
        # 关联信息
        link_info = {
            "scraper_id": scraper_id,
            "config": config or {},
            "task_name": task_name or scraper_id,
            "created_at": self._get_timestamp()
        }
        
        # 检查是否已经存在相同任务名称的关联
        for i, link in enumerate(self.website_scrapers.get(website_id, [])):
            if link.get("task_name") == link_info["task_name"]:
                # 更新现有关联
                self.website_scrapers[website_id][i] = link_info
                logger.info(f"Updated scraper link: {website_id} -> {scraper_id} ({task_name})")
                self.save_config()
                return True
                
        # 添加新关联
        if website_id not in self.website_scrapers:
            self.website_scrapers[website_id] = []
            
        self.website_scrapers[website_id].append(link_info)
        logger.info(f"Linked scraper to website: {website_id} -> {scraper_id} ({task_name})")
        
        # 保存配置
        self.save_config()
        
        return True
    
    def unlink_scraper_from_website(self, website_id: str, task_name: str) -> bool:
        """
        解除爬虫与网站的关联
        
        Args:
            website_id: 网站ID
            task_name: 任务名称
            
        Returns:
            是否成功解除关联
        """
        if website_id not in self.website_scrapers:
            return False
            
        # 查找并移除关联
        for i, link in enumerate(self.website_scrapers[website_id]):
            if link.get("task_name") == task_name:
                self.website_scrapers[website_id].pop(i)
                logger.info(f"Unlinked scraper from website: {website_id} -> {task_name}")
                self.save_config()
                return True
                
        return False
    
    def get_website_scrapers(self, website_id: str) -> List[Dict[str, Any]]:
        """
        获取网站关联的爬虫列表
        
        Args:
            website_id: 网站ID
            
        Returns:
            爬虫信息列表，每个元素包含scraper_id, config和task_name
        """
        return self.website_scrapers.get(website_id, [])
    
    def get_all_websites(self) -> List[Dict[str, Any]]:
        """
        获取所有注册的网站
        
        Returns:
            网站信息列表
        """
        return list(self.websites.values())
    
    def get_all_scrapers(self) -> Dict[str, Type[BaseScraper]]:
        """
        获取所有注册的爬虫
        
        Returns:
            爬虫ID到爬虫类的映射
        """
        return self.scrapers
    
    def get_website(self, website_id: str) -> Optional[Dict[str, Any]]:
        """
        获取网站信息
        
        Args:
            website_id: 网站ID
            
        Returns:
            网站信息字典，如果不存在则返回None
        """
        return self.websites.get(website_id)
    
    def get_scraper_class(self, scraper_id: str) -> Optional[Type[BaseScraper]]:
        """
        获取爬虫类
        
        Args:
            scraper_id: 爬虫ID
            
        Returns:
            爬虫类，如果不存在则返回None
        """
        return self.scrapers.get(scraper_id)
    
    def run_website_scraper(self, 
                          website_id: str, 
                          task_name: str, 
                          **kwargs) -> Dict[str, Any]:
        """
        运行网站的特定爬虫任务
        
        Args:
            website_id: 网站ID
            task_name: 任务名称
            **kwargs: 传递给爬虫的其他参数
            
        Returns:
            爬虫运行结果
            
        Raises:
            ValueError: 如果网站ID或任务名称不存在
        """
        if website_id not in self.websites:
            raise ValueError(f"Website not found: {website_id}")
            
        # 查找关联的爬虫
        scraper_link = None
        for link in self.website_scrapers.get(website_id, []):
            if link.get("task_name") == task_name:
                scraper_link = link
                break
                
        if not scraper_link:
            raise ValueError(f"Task not found for website: {website_id} -> {task_name}")
            
        scraper_id = scraper_link["scraper_id"]
        scraper_class = self.scrapers.get(scraper_id)
        
        if not scraper_class:
            raise ValueError(f"Scraper not found: {scraper_id}")
            
        # 合并配置
        config = scraper_link.get("config", {}).copy()
        config.update(kwargs.pop("config", {}))
        
        # 创建爬虫实例并运行
        scraper = scraper_class(config=config)
        
        # 添加网站信息到参数
        kwargs["website"] = self.websites[website_id]
        
        return scraper.run(**kwargs)
    
    def save_config(self) -> bool:
        """
        保存配置到文件
        
        Returns:
            是否成功保存
        """
        if not self.config_path:
            logger.warning("Config path not set, skipping save")
            return False
            
        config = {
            "websites": self.websites,
            "website_scrapers": self.website_scrapers
        }
        
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                
            logger.info(f"Config saved to {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {str(e)}")
            return False
    
    def load_config(self) -> bool:
        """
        从文件加载配置
        
        Returns:
            是否成功加载
        """
        if not self.config_path or not os.path.exists(self.config_path):
            logger.warning(f"Config file not found: {self.config_path}")
            return False
            
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            self.websites = config.get("websites", {})
            self.website_scrapers = config.get("website_scrapers", {})
            
            logger.info(f"Config loaded from {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load config: {str(e)}")
            return False
    
    def discover_scrapers(self, package_path: str) -> List[str]:
        """
        自动发现并注册包中的爬虫类
        
        Args:
            package_path: 包路径，如"src.scrapers.sites"
            
        Returns:
            注册的爬虫ID列表
        """
        registered_scrapers = []
        
        try:
            package = importlib.import_module(package_path)
            
            # 获取包的文件系统路径
            package_dir = os.path.dirname(package.__file__)
            
            # 遍历包中的所有模块
            for file in os.listdir(package_dir):
                if file.endswith('.py') and not file.startswith('__'):
                    module_name = file[:-3]  # 去掉.py后缀
                    full_module_name = f"{package_path}.{module_name}"
                    
                    try:
                        module = importlib.import_module(full_module_name)
                        
                        # 查找模块中的爬虫类
                        for name, obj in inspect.getmembers(module):
                            if (inspect.isclass(obj) and 
                                issubclass(obj, BaseScraper) and 
                                obj != BaseScraper):
                                scraper_id = self.register_scraper(obj)
                                registered_scrapers.append(scraper_id)
                    except Exception as e:
                        logger.error(f"Failed to import module {full_module_name}: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to discover scrapers in {package_path}: {str(e)}")
            
        return registered_scrapers
    
    @staticmethod
    def _get_timestamp() -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat() 