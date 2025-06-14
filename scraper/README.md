# AIDA Scraper - 艺术家与策展人生态信息采集与分析平台

AIDA Scraper是一个用于收集、分析和可视化艺术家与策展人生态信息的SaaS平台。该系统可以自动化采集艺术相关内容，进行NLP驱动的信息挖掘，并构建艺术家-策展人-机构关系网络。

## 功能特点

- 全网自动化采集艺术相关内容（爬虫 + API抓取）
- NLP驱动的信息深度挖掘、自动分类、去重、关键词抽取
- 结构化/半结构化数据统一入库，可被检索与可视化
- 构建真实艺术家—策展人—机构关系网络，辅助学术研究与行业决策
- 多租户运营能力：不同团队/研究者的数据隔离、权限管理

## 技术栈

- 前端：Vue 3 + Element Plus
- 后端：FastAPI
- 爬虫：Scrapy + Playwright
- NLP：spaCy / Transformers
- 队列：Celery + Redis
- 数据库：PostgreSQL、Elasticsearch、Neo4j、MinIO
- 工作流：n8n
- 部署：Docker Compose → K8s

## 快速开始

### 环境要求

- Docker 和 Docker Compose
- Python 3.10+

### 安装步骤

1. 克隆仓库
   ```bash
   git clone https://github.com/yourusername/aida-scraper.git
   cd aida-scraper
   ```

2. 创建环境变量文件
   ```bash
   cp .env.example .env
   # 编辑.env文件，设置必要的环境变量
   ```

3. 启动服务
   ```bash
   docker-compose up -d
   ```

4. 初始化数据库
   ```bash
   docker-compose exec api python -m app.db.init_db
   ```

5. 访问API文档
   ```
   http://localhost:8000/docs
   ```

## 开发指南

### 本地开发环境设置

1. 创建虚拟环境
   ```bash
   python -m venv venv
   source venv/bin/activate  # 在Windows上使用: venv\Scripts\activate
   ```

2. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

3. 安装Playwright浏览器
   ```bash
   playwright install chromium
   ```

4. 运行API服务
   ```bash
   uvicorn app.main:app --reload
   ```

### 项目结构

```
scraper/
  app/
    api/            # API路由
    core/           # 核心配置
    db/             # 数据库相关
    models/         # SQLAlchemy模型
    schemas/        # Pydantic模式
    scrapers/       # 爬虫模块
    services/       # 业务逻辑
    tasks/          # Celery任务
    utils/          # 工具函数
  docker-compose.yml
  Dockerfile
  requirements.txt
```

## 贡献指南

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开Pull Request

## 许可证

本项目采用MIT许可证 - 详见[LICENSE](LICENSE)文件

## 联系方式

项目维护者 - [@yourname](https://github.com/yourname)

项目链接: [https://github.com/yourusername/aida-scraper](https://github.com/yourusername/aida-scraper) 