"""
深度搜索引擎 - 实现递归爬取与信息提取
"""
import logging
import time
import random
from typing import Dict, List, Any, Optional, Callable, Set, Tuple
from datetime import datetime
import json
import os
from urllib.parse import urljoin, urlparse
from queue import Queue, PriorityQueue
import threading

from bs4 import BeautifulSoup
import requests
from playwright.sync_api import sync_playwright, Browser, Page

logger = logging.getLogger(__name__)

class SearchNode:
    """
    搜索节点，代表深度搜索中的一个URL及其相关信息
    """
    
    def __init__(self, url: str, depth: int = 0, parent_url: str = None, priority: int = 0):
        """
        初始化搜索节点
        
        Args:
            url: 节点URL
            depth: 节点深度，从0开始
            parent_url: 父节点URL
            priority: 节点优先级，数值越小优先级越高
        """
        self.url = url
        self.depth = depth
        self.parent_url = parent_url
        self.priority = priority
        self.created_at = datetime.now()
        self.processed = False
        self.content = None
        self.extracted_data = None
        self.error = None
        
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典表示
        
        Returns:
            节点的字典表示
        """
        return {
            "url": self.url,
            "depth": self.depth,
            "parent_url": self.parent_url,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "processed": self.processed,
            "has_content": self.content is not None,
            "has_data": self.extracted_data is not None,
            "error": self.error
        }
        
    def __lt__(self, other):
        """用于优先队列排序"""
        if self.priority != other.priority:
            return self.priority < other.priority
        return self.created_at < other.created_at


class DataExtractor:
    """
    数据提取器，负责从HTML内容中提取结构化数据
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化数据提取器
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        
    def extract(self, html_content: str, url: str) -> Dict[str, Any]:
        """
        从HTML内容中提取数据
        
        Args:
            html_content: HTML内容
            url: 内容的来源URL
            
        Returns:
            提取的结构化数据
        """
        # 默认实现使用BeautifulSoup进行基础提取
        soup = BeautifulSoup(html_content, 'lxml')
        
        # 提取基本页面信息
        title = self._extract_title(soup)
        description = self._extract_description(soup)
        
        # 默认提取页面中的所有链接
        links = self._extract_links(soup, url)
        
        # 默认提取页面中的所有图片
        images = self._extract_images(soup, url)
        
        return {
            "url": url,
            "title": title,
            "description": description,
            "links": links,
            "images": images,
            "extracted_at": datetime.now().isoformat()
        }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """提取页面标题"""
        title_tag = soup.find('title')
        return title_tag.text.strip() if title_tag else ""
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """提取页面描述"""
        description_tag = soup.find('meta', attrs={'name': 'description'})
        if description_tag and 'content' in description_tag.attrs:
            return description_tag['content'].strip()
        return ""
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """提取页面中的链接"""
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            text = a_tag.text.strip()
            
            # 处理相对URL
            absolute_url = urljoin(base_url, href)
            
            links.append({
                "url": absolute_url,
                "text": text
            })
        return links
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """提取页面中的图片"""
        images = []
        for img_tag in soup.find_all('img', src=True):
            src = img_tag['src']
            alt = img_tag.get('alt', '')
            
            # 处理相对URL
            absolute_url = urljoin(base_url, src)
            
            images.append({
                "url": absolute_url,
                "alt": alt
            })
        return images


class URLFilter:
    """
    URL过滤器，用于过滤不需要处理的URL
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化URL过滤器
        
        Args:
            config: 配置参数，可以包含白名单、黑名单等
        """
        self.config = config or {}
        self.allowed_domains = self.config.get('allowed_domains', [])
        self.excluded_domains = self.config.get('excluded_domains', [])
        self.allowed_paths = self.config.get('allowed_paths', [])
        self.excluded_paths = self.config.get('excluded_paths', [])
        self.allowed_extensions = self.config.get('allowed_extensions', 
                                               ['.html', '.htm', '.php', '.asp', '.aspx', '.jsp', ''])
        self.excluded_extensions = self.config.get('excluded_extensions', 
                                               ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar', 
                                               '.jpg', '.jpeg', '.png', '.gif', '.svg', '.mp3', '.mp4'])
    
    def should_process(self, url: str) -> bool:
        """
        判断URL是否应该被处理
        
        Args:
            url: 要判断的URL
            
        Returns:
            是否应该处理该URL
        """
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        path = parsed_url.path
        
        # 检查文件扩展名
        _, ext = os.path.splitext(path)
        ext = ext.lower()
        
        # 如果是排除的扩展名，不处理
        if ext in self.excluded_extensions:
            return False
            
        # 如果设置了允许的扩展名，但当前扩展名不在其中，不处理
        if self.allowed_extensions and ext not in self.allowed_extensions:
            return False
            
        # 检查域名
        if self.allowed_domains and domain not in self.allowed_domains:
            return False
            
        if domain in self.excluded_domains:
            return False
            
        # 检查路径
        if self.excluded_paths:
            for excluded_path in self.excluded_paths:
                if path.startswith(excluded_path):
                    return False
                    
        if self.allowed_paths:
            for allowed_path in self.allowed_paths:
                if path.startswith(allowed_path):
                    return True
            return False
            
        return True


class LinkExtractor:
    """
    链接提取器，从页面中提取下一步要处理的链接
    """
    
    def __init__(self, url_filter: URLFilter = None, config: Dict[str, Any] = None):
        """
        初始化链接提取器
        
        Args:
            url_filter: URL过滤器
            config: 配置参数
        """
        self.config = config or {}
        self.url_filter = url_filter or URLFilter()
        
    def extract_links(self, html_content: str, base_url: str) -> List[str]:
        """
        从HTML内容中提取链接
        
        Args:
            html_content: HTML内容
            base_url: 基础URL，用于将相对路径转为绝对路径
            
        Returns:
            提取的链接列表
        """
        soup = BeautifulSoup(html_content, 'lxml')
        links = []
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            
            # 跳过空链接和JavaScript链接
            if not href or href.startswith('javascript:') or href.startswith('#'):
                continue
                
            # 处理相对URL
            absolute_url = urljoin(base_url, href)
            
            # 去除URL中的锚点
            absolute_url = absolute_url.split('#')[0]
            
            # 应用URL过滤器
            if self.url_filter.should_process(absolute_url):
                links.append(absolute_url)
                
        return links


class DeepSearchEngine:
    """
    深度搜索引擎，实现递归爬取与信息提取
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化深度搜索引擎
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        
        # 基本配置
        self.max_depth = self.config.get('max_depth', 3)
        self.max_urls = self.config.get('max_urls', 1000)
        self.request_delay = self.config.get('request_delay', 1000) / 1000  # 毫秒转秒
        self.timeout = self.config.get('timeout', 30)
        self.retry_count = self.config.get('retry_count', 3)
        self.use_playwright = self.config.get('use_playwright', True)
        self.concurrency = self.config.get('concurrency', 1)
        self.user_agent = self.config.get('user_agent', 
                            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        # URL过滤器
        url_filter_config = self.config.get('url_filter', {})
        self.url_filter = URLFilter(url_filter_config)
        
        # 链接提取器
        self.link_extractor = LinkExtractor(self.url_filter)
        
        # 数据提取器
        extractor_config = self.config.get('data_extractor', {})
        self.data_extractor = DataExtractor(extractor_config)
        
        # 运行状态
        self.start_time = None
        self.end_time = None
        self.status = "initialized"
        self.visited_urls = set()
        self.results = []
        self.errors = []
        
        # URL队列
        self.queue = PriorityQueue() if self.config.get('use_priority_queue', False) else Queue()
        
        # 保存路径
        self.save_path = self.config.get('save_path', 'data/search_results')
        
        # 创建保存目录
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path, exist_ok=True)
            
    def search(self, start_url: str, **kwargs) -> Dict[str, Any]:
        """
        从起始URL开始进行深度搜索
        
        Args:
            start_url: 起始URL
            **kwargs: 其他参数，可能覆盖配置
            
        Returns:
            搜索结果报告
        """
        # 更新配置
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
                
        # 重置状态
        self.start_time = datetime.now()
        self.status = "running"
        self.visited_urls = set()
        self.results = []
        self.errors = []
        
        # 添加起始URL到队列
        start_node = SearchNode(start_url, depth=0)
        self.queue.put((start_node.priority, start_node))
        
        try:
            # 如果启用并发，使用线程池
            if self.concurrency > 1:
                self._search_concurrent()
            else:
                self._search_sequential()
                
            self.status = "completed"
        except Exception as e:
            logger.error(f"Error in deep search: {str(e)}", exc_info=True)
            self.errors.append(str(e))
            self.status = "failed"
        finally:
            self.end_time = datetime.now()
            
        # 保存结果
        self._save_results()
            
        return self.get_report()
    
    def _search_sequential(self) -> None:
        """
        顺序执行搜索过程
        """
        processed_count = 0
        
        while not self.queue.empty() and processed_count < self.max_urls:
            # 获取下一个要处理的URL节点
            _, node = self.queue.get()
            
            # 如果URL已经访问过，跳过
            if node.url in self.visited_urls:
                continue
                
            # 添加到已访问集合
            self.visited_urls.add(node.url)
            
            logger.info(f"Processing URL: {node.url} (depth={node.depth})")
            
            # 处理当前节点
            self._process_node(node)
            
            # 增加计数
            processed_count += 1
            
            # 请求延迟
            if self.request_delay > 0:
                jitter = random.uniform(0.5, 1.5) * self.request_delay
                time.sleep(jitter)
    
    def _search_concurrent(self) -> None:
        """
        并发执行搜索过程
        """
        threads = []
        processed_count = 0
        lock = threading.Lock()
        
        def worker():
            nonlocal processed_count
            
            while True:
                # 检查是否达到最大URL数量
                with lock:
                    if processed_count >= self.max_urls:
                        break
                    
                # 获取下一个要处理的URL节点
                try:
                    _, node = self.queue.get(block=False)
                except Exception:
                    # 队列为空
                    break
                    
                # 如果URL已经访问过，跳过
                with lock:
                    if node.url in self.visited_urls:
                        continue
                    self.visited_urls.add(node.url)
                
                logger.info(f"Processing URL: {node.url} (depth={node.depth})")
                
                # 处理当前节点
                self._process_node(node)
                
                # 增加计数
                with lock:
                    processed_count += 1
                
                # 请求延迟
                if self.request_delay > 0:
                    jitter = random.uniform(0.5, 1.5) * self.request_delay
                    time.sleep(jitter)
        
        # 创建工作线程
        for _ in range(self.concurrency):
            thread = threading.Thread(target=worker)
            thread.daemon = True
            threads.append(thread)
            thread.start()
            
        # 等待所有线程完成
        for thread in threads:
            thread.join()
    
    def _process_node(self, node: SearchNode) -> None:
        """
        处理单个搜索节点
        
        Args:
            node: 要处理的搜索节点
        """
        try:
            # 获取页面内容
            content = self._get_page_content(node.url)
            if not content:
                node.error = "Failed to get page content"
                self.errors.append(f"Failed to get content for URL: {node.url}")
                return
                
            node.content = content
            
            # 提取数据
            extracted_data = self.data_extractor.extract(content, node.url)
            node.extracted_data = extracted_data
            
            # 添加到结果
            self.results.append(extracted_data)
            
            # 如果未达到最大深度，提取链接并加入队列
            if node.depth < self.max_depth:
                links = self.link_extractor.extract_links(content, node.url)
                
                for link in links:
                    # 创建新的搜索节点
                    new_node = SearchNode(
                        url=link,
                        depth=node.depth + 1,
                        parent_url=node.url,
                        priority=node.priority + 1
                    )
                    
                    # 加入队列
                    self.queue.put((new_node.priority, new_node))
                    
            node.processed = True
            
        except Exception as e:
            logger.error(f"Error processing node {node.url}: {str(e)}", exc_info=True)
            node.error = str(e)
            self.errors.append(f"Error processing URL {node.url}: {str(e)}")
    
    def _get_page_content(self, url: str) -> Optional[str]:
        """
        获取页面内容
        
        Args:
            url: 页面URL
            
        Returns:
            页面HTML内容，失败时返回None
        """
        if self.use_playwright:
            return self._get_page_with_playwright(url)
        else:
            return self._get_page_with_requests(url)
    
    def _get_page_with_requests(self, url: str) -> Optional[str]:
        """
        使用requests获取页面内容
        
        Args:
            url: 页面URL
            
        Returns:
            页面HTML内容，失败时返回None
        """
        headers = {'User-Agent': self.user_agent}
        
        for attempt in range(self.retry_count + 1):
            try:
                response = requests.get(url, headers=headers, timeout=self.timeout)
                response.raise_for_status()
                return response.text
            except Exception as e:
                logger.warning(f"Request failed (attempt {attempt+1}/{self.retry_count+1}): {url} - {str(e)}")
                if attempt == self.retry_count:
                    logger.error(f"All retry attempts failed for URL: {url}")
                    return None
                time.sleep((attempt + 1) * 2)
                
        return None
    
    def _get_page_with_playwright(self, url: str) -> Optional[str]:
        """
        使用Playwright获取页面内容
        
        Args:
            url: 页面URL
            
        Returns:
            页面HTML内容，失败时返回None
        """
        browser = None
        
        try:
            playwright = sync_playwright().start()
            
            browser_type = self.config.get('browser', 'chromium')
            headless = self.config.get('headless', True)
            
            if browser_type == 'firefox':
                browser = playwright.firefox.launch(headless=headless)
            elif browser_type == 'webkit':
                browser = playwright.webkit.launch(headless=headless)
            else:
                browser = playwright.chromium.launch(headless=headless)
                
            context = browser.new_context(
                user_agent=self.user_agent,
                viewport={'width': 1280, 'height': 800}
            )
            
            page = context.new_page()
            page.set_default_timeout(self.timeout * 1000)
            
            page.goto(url, wait_until='networkidle')
            
            # 等待页面加载完成
            page.wait_for_load_state('networkidle')
            
            content = page.content()
            
            browser.close()
            playwright.stop()
            
            return content
            
        except Exception as e:
            logger.error(f"Error getting page with Playwright: {url} - {str(e)}")
            if browser:
                browser.close()
            return None
    
    def get_report(self) -> Dict[str, Any]:
        """
        获取搜索结果报告
        
        Returns:
            包含搜索状态和结果的字典
        """
        duration = None
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
            
        return {
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": duration,
            "visited_urls_count": len(self.visited_urls),
            "results_count": len(self.results),
            "errors_count": len(self.errors),
            "max_depth": self.max_depth,
            "max_urls": self.max_urls,
            "save_path": self.save_path,
            "errors": self.errors[:10]  # 仅返回前10个错误
        }
    
    def _save_results(self) -> None:
        """
        保存搜索结果到文件
        """
        if not self.results:
            return
            
        # 创建保存目录
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_dir = os.path.join(self.save_path, f"search_{timestamp}")
        os.makedirs(result_dir, exist_ok=True)
        
        # 保存结果数据
        results_file = os.path.join(result_dir, "results.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
            
        # 保存报告
        report_file = os.path.join(result_dir, "report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.get_report(), f, ensure_ascii=False, indent=2)
            
        # 保存已访问URL列表
        urls_file = os.path.join(result_dir, "visited_urls.txt")
        with open(urls_file, 'w', encoding='utf-8') as f:
            for url in sorted(self.visited_urls):
                f.write(f"{url}\n")
                
        logger.info(f"Search results saved to {result_dir}")
        
    def load_checkpoint(self, checkpoint_path: str) -> bool:
        """
        从检查点恢复搜索状态
        
        Args:
            checkpoint_path: 检查点文件路径
            
        Returns:
            是否成功加载检查点
        """
        try:
            with open(checkpoint_path, 'r', encoding='utf-8') as f:
                checkpoint = json.load(f)
                
            self.visited_urls = set(checkpoint.get('visited_urls', []))
            self.results = checkpoint.get('results', [])
            self.errors = checkpoint.get('errors', [])
            self.status = checkpoint.get('status', 'restored')
            
            # 恢复队列
            for node_data in checkpoint.get('queue', []):
                node = SearchNode(
                    url=node_data['url'],
                    depth=node_data['depth'],
                    parent_url=node_data['parent_url'],
                    priority=node_data['priority']
                )
                self.queue.put((node.priority, node))
                
            logger.info(f"Checkpoint loaded from {checkpoint_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {str(e)}")
            return False
    
    def save_checkpoint(self, checkpoint_path: str) -> bool:
        """
        保存当前搜索状态到检查点
        
        Args:
            checkpoint_path: 检查点文件路径
            
        Returns:
            是否成功保存检查点
        """
        try:
            # 提取队列中的节点
            queue_items = []
            while not self.queue.empty():
                try:
                    priority, node = self.queue.get(block=False)
                    queue_items.append((priority, node))
                except Exception:
                    break
            
            # 重新放回队列
            for priority, node in queue_items:
                self.queue.put((priority, node))
                
            # 准备检查点数据
            checkpoint = {
                "visited_urls": list(self.visited_urls),
                "results": self.results,
                "errors": self.errors,
                "status": self.status,
                "queue": [
                    {
                        "url": node.url,
                        "depth": node.depth,
                        "parent_url": node.parent_url,
                        "priority": node.priority
                    }
                    for _, node in queue_items
                ],
                "saved_at": datetime.now().isoformat()
            }
            
            # 确保目录存在
            os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)
            
            # 保存检查点
            with open(checkpoint_path, 'w', encoding='utf-8') as f:
                json.dump(checkpoint, f, ensure_ascii=False, indent=2)
                
            logger.info(f"Checkpoint saved to {checkpoint_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {str(e)}")
            return False 