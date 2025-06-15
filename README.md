# AIDA Scraper

AIDA Scraper是一个用于艺术网站数据采集和分析的工具，支持多种艺术网站的数据抓取、存储和分析。

## 快速开始

### 一键启动

使用`start_all.bat`脚本可以一键启动所有服务：

```
.\start_all.bat
```

此脚本会自动执行以下操作：
1. 初始化数据库
2. 启动API服务器
3. 启动Celery工作进程
4. 运行SaatchiArt爬虫测试

### 停止所有服务

使用`stop_all.bat`脚本可以一键停止所有服务：

```
.\stop_all.bat
```

## 服务访问

- API文档: http://localhost:8000/docs
- API端点: http://localhost:8000/api/v1/

## 系统架构

AIDA Scraper由以下组件组成：

1. **API服务器**: 基于FastAPI的RESTful API
2. **爬虫引擎**: 基于Scrapy的爬虫系统
3. **任务队列**: 基于Celery的异步任务处理系统
4. **数据库**: 使用SQLAlchemy ORM的关系型数据库

## 爬虫配置

系统支持多种艺术网站的爬虫，包括：

- SaatchiArt: 世界领先的在线艺术画廊
- Artsy: 艺术品发现和收藏平台
- WikiArt: 视觉艺术百科全书
- 各种艺术画廊网站

## 手动启动

如果需要单独启动各个组件，可以使用以下命令：

### 初始化数据库
```
cd scraper
python start.py --init-db
```

### 启动API服务器
```
cd scraper
python start.py --start-api
```

### 启动Celery工作进程
```
cd scraper
python start_worker.py
```

### 运行特定爬虫
```
cd scraper
python run_saatchi_spider.py
```

## API Documentation

Once the API server is running, you can access the documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Architecture

AIDA Scraper follows a modular architecture:

- **API Layer**: FastAPI for high-performance REST endpoints
- **Scraper Layer**: Scrapy + Playwright for handling JavaScript-rendered sites
- **Processing Layer**: NLP pipelines for text analysis
- **Storage Layer**: PostgreSQL/SQLite for structured data, Elasticsearch for search
- **Task Queue**: Celery + Redis for asynchronous job processing

## Spiders

The following spiders are currently implemented:

- **SaatchiArt**: Scrapes artists and artworks from SaatchiArt
- **Artsy**: Scrapes artists, exhibitions, and artworks from Artsy
- **WikiArt**: Scrapes artists, artworks, and genres from WikiArt
- **ArtGallery**: Generic spider for art gallery websites

## Configuration

Configuration is managed through JSON files in `scraper/app/scrapers/spiders/`.

Example configuration:

```json
{
  "name": "SaatchiArt",
  "url": "https://www.saatchiart.com",
  "description": "Scrape artists and artworks from SaatchiArt website",
  "requires_login": false,
  "start_urls": [
    "https://www.saatchiart.com/artists",
    "https://www.saatchiart.com/paintings"
  ],
  "allowed_domains": [
    "www.saatchiart.com",
    "saatchiart.com"
  ],
  "use_playwright": true,
  "config": {
    "max_pages": 2,
    "max_items_per_category": 20
  }
}
```

## License

MIT 