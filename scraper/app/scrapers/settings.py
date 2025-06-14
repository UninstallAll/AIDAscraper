"""
Scrapy设置
"""

# Scrapy设置
BOT_NAME = 'aida_scraper'

SPIDER_MODULES = ['app.scrapers.spiders']
NEWSPIDER_MODULE = 'app.scrapers.spiders'

# 爬虫设置
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
ROBOTSTXT_OBEY = False
CONCURRENT_REQUESTS = 16
DOWNLOAD_DELAY = 1
COOKIES_ENABLED = True
TELNETCONSOLE_ENABLED = False

# 下载中间件
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
    'scrapy_playwright.middleware.PlaywrightMiddleware': 100,
}

# 项目管道
ITEM_PIPELINES = {
    'app.scrapers.pipelines.JsonWriterPipeline': 300,
    'app.scrapers.pipelines.DatabasePipeline': 400,
}

# 重试设置
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# 缓存设置
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 86400
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = [401, 403, 404, 500, 502, 503, 504]

# 日志设置
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
LOG_DATEFORMAT = '%Y-%m-%d %H:%M:%S'
LOG_STDOUT = False
LOG_FILE = None  # 不使用默认文件日志，我们使用自定义的JobLogger

# 禁用默认的日志配置，使用我们自己的日志处理器
LOG_ENABLED = True
LOG_ENCODING = 'utf-8'

# 扩展设置
EXTENSIONS = {
    'scrapy.extensions.logstats.LogStats': None,  # 禁用默认的日志统计
}

# Playwright设置
PLAYWRIGHT_LAUNCH_OPTIONS = {
    'headless': True,
    'timeout': 30000,
}

PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 30000

# 输出目录
OUTPUT_DIR = 'output'

# 错误处理
DOWNLOAD_FAIL_ON_DATALOSS = False 