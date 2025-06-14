"""
Scrapy设置
"""

# Scrapy设置
BOT_NAME = 'aida_scraper'

SPIDER_MODULES = ['app.scrapers']
NEWSPIDER_MODULE = 'app.scrapers'

# 遵循robots.txt规则
ROBOTSTXT_OBEY = True

# 并发请求数
CONCURRENT_REQUESTS = 16

# 下载延迟
DOWNLOAD_DELAY = 1

# 随机下载延迟
RANDOMIZE_DOWNLOAD_DELAY = True

# 请求头
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

# 启用的中间件
SPIDER_MIDDLEWARES = {
    'scrapy.spidermiddlewares.httperror.HttpErrorMiddleware': 50,
    'scrapy.spidermiddlewares.offsite.OffsiteMiddleware': 500,
    'scrapy.spidermiddlewares.referer.RefererMiddleware': 700,
    'scrapy.spidermiddlewares.urllength.UrlLengthMiddleware': 800,
    'scrapy.spidermiddlewares.depth.DepthMiddleware': 900,
}

# 下载中间件
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware': 300,
    'scrapy.downloadermiddlewares.downloadtimeout.DownloadTimeoutMiddleware': 350,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 500,
    'scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware': 580,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 590,
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': 600,
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': 700,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 750,
    'scrapy_playwright.middleware.PlaywrightMiddleware': 800,
}

# 启用的Pipeline
ITEM_PIPELINES = {
    'app.scrapers.pipelines.JsonWriterPipeline': 300,
}

# 日志级别
LOG_LEVEL = 'INFO'

# 日志文件
LOG_FILE = 'logs/scrapy.log'

# 超时时间
DOWNLOAD_TIMEOUT = 30

# 重试次数
RETRY_TIMES = 3

# 重试HTTP状态码
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429]

# Playwright设置
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,
    "timeout": 30000,
}

PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 30000

# 启用Playwright
PLAYWRIGHT_ENABLED = True

# 关闭遥测
TELNETCONSOLE_ENABLED = False 