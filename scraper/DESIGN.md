# 系统开发设计方案文档 (DESIGN.md)

> 本设计文档基于 `SYSTEM.md` 确定的需求编写，目标是为开发与运维团队提供完整、可落地的技术实现细节与决策依据。

## 1. 总体架构概览
```
┌───────────────────────────────┐
│           Browser (SPA)        │
│    Vue 3 + Element Plus        │
└──────────────┬────────────────┘
               │ HTTPS / WSS
┌──────────────▼────────────────┐
│           API Gateway          │  Nginx / Traefik / Caddy
└──────────────┬────────────────┘
               │  JWT / OAuth2
┌──────────────▼────────────────┐
│          FastAPI  (Uvicorn)    │
│  - Auth & RBAC                 │
│  - REST / WebSocket            │
│  - GraphQL (future)            │
└────┬─────────┬─────┬──────────┘
     │         │     │
     │         │     │Celery RPC/Redis
     │         │     ▼
     │         │  Worker Pods (爬虫 / NLP)
     │         │    - Scrapy + Playwright
     │         │    - spaCy / Transformers
     │         │
     │  SQL ORM │
     ▼         ▼
 PostgreSQL   Elasticsearch   Neo4j   MinIO
```

## 2. 组件明细
| 组件 | 责任 | 关键技术 | 高可用策略 |
| ---- | ---- | -------- | ---------- |
| 前端 SPA | 用户界面、数据可视化 | Vue3, Pinia, Vite, D3.js | Nginx + CDN, PWA 离线缓存 |
| API 服务 | 业务 API、鉴权、文件上传 | FastAPI, SQLAlchemy, Pydantic | 多实例 + K8s HPA |
| 爬虫 Worker | 网页抓取、API 调用 | Scrapy, Playwright, Celery | 多队列分片、自动重试 |
| NLP Worker | 文本处理、Embedding | spaCy, SentenceTransformers | GPU 节点，模型热加载 |
| 任务队列 | 异步任务、定时调度 | Redis, Celery beat | 主从复制、哨兵 |
| 工作流 | 可视化编排 | n8n (独立容器) | 单独部署，Postgres backend |
| 数据库 | 结构化数据 | PostgreSQL 15 | 主备、异地灾备 |
| 搜索引擎 | 全文／向量搜索 | Elasticsearch 8.x | 3 节点集群、Snapshot |
| 图数据库 | 艺术家关系网 | Neo4j 5 | 主从、物理备份 |
| 对象存储 | 文件/图片 | MinIO 或 S3 | EC + 纠删码 |

## 3. 模块设计
### 3.1 用户鉴权模块
- 使用 OAuth2 Password & Bearer Token，支持多租户隔离 (tenant_id in JWT Claim)。
- RBAC 权限模型：角色（Admin / Editor / Viewer）+ 资源 (Endpoint, Action)。

### 3.2 爬虫子系统
1. **配置管理**：`SiteConfig` 表保存目标站点规则；由前端表单生成 JSON Schema。
2. **调度流程**：用户提交爬取任务 → FastAPI 创建 `Job` 记录 → 推送 Celery → Worker 拉取执行。
3. **中间件**：
   - `ProxyMiddleware`：自动切换代理。
   - `CaptchaSolverMiddleware`：接入第三方打码服务。
4. **数据输出**：Spider Pipeline → Kafka Topic (未来) → Saver Service → PostgreSQL / MinIO。

### 3.3 NLP 流水线
- 采用 spaCy `Language` pipeline：`Tokenizer -> NER -> TextCategorizer -> Vectorizer`。
- 向量存储：`Elasticsearch KNN` (dense_vector)；备选方案：FAISS + PostgreSQL fdw。
- 模型管理：MLflow 追踪版本；容器启动时拉取最新模型。

### 3.4 关系图谱
- `Node` 标签：Artist, Curator, Institution, Exhibition, Work。
- `Edge` 类型：PARTICIPATED, CURATED, BELONGS_TO, COLLABORATED。
- 定义 Cypher APOC 过程：生成子图、计算中心性。

### 3.5 API 设计示例
| 方法 | 路径 | 描述 |
| ---- | ---- | ---- |
| GET | /api/v1/sites | 查询站点配置 |
| POST | /api/v1/jobs | 创建爬虫任务 |
| GET | /api/v1/search | 全文/向量检索 |
| GET | /api/v1/graph/path | 查询两节点最短路径 |

### 3.6 前端路由
```
/                           -> Dashboard
/sites                      -> 站点管理
/jobs                       -> 爬虫任务列表
/search                     -> 搜索界面
/graph                      -> 关系网络
/settings                   -> 系统设置
```

## 4. 数据库 ER 轮廓
```
Artist(id, name, birth_year, nationality, bio)
Exhibition(id, title, location, start_date, end_date)
Work(id, artist_id, title, year, medium)
Curator(id, name, institution)
Institution(id, name, city, country)
ArtistExhibition(artist_id, exhibition_id, role)
CuratorExhibition(curator_id, exhibition_id)
```

## 5. 部署方案
1. **开发**：`docker-compose up` 启动 web、worker、redis、db、es、neo4j、minio。
2. **CI/CD**：GitHub Actions → Run tests → Build Docker → Push GHCR → Trigger ArgoCD。
3. **生产**：
   - K8s Namespace per tenant (可选)。
   - Ingress TLS, HPA, Pod Disruption Budget。
   - Prometheus Operator 收集指标，Grafana Dashboard。

## 6. 安全设计
- HTTPS 全站加密，HSTS。
- CSRF Token (SameSite Cookie)。
- 输入输出统一 XSS/SQL 注入过滤。
- OWASP Dependency Check，SCA 扫描。

## 7. 性能与容量规划
| 资源 | 初始规格 | 扩展策略 |
| ---- | -------- | -------- |
| API Pod | 2 vCPU / 4 GB | HPA 基于 CPU 60% |
| Worker | 4 vCPU / 8 GB | 队列长度 > 100 自动扩容 |
| PostgreSQL | 2C / 8 GB / 100 GB | 分区表 + 只读副本 |
| ES | 3 节点 x 4 CPU | Shard 重均衡 |

## 8. 监控与日志
- **Metrics**：FastAPI Prometheus 中间件、Celery Exporter。
- **Logs**：JSON 格式写 stdout，收集到 Loki 或 Elasticsearch。
- **Tracing**：OpenTelemetry → Jaeger。

## 9. 备份与恢复
- PostgreSQL：每日逻辑备份 + WAL Streaming。
- ES Snapshot to MinIO 每 4 小时。
- Neo4j：`neo4j-admin dump` 每日。

## 10. Roadmap 对应里程碑
| 里程碑 | 主要交付 | 关键验收 |
| ------ | -------- | -------- |
| M1 | 用户登录 + 站点配置 CRUD + 本地爬虫 Demo | 成功抓取并入库 ≥ 1 个站点 |
| M2 | NLP 流水线 + 搜索 API | 关键词检索命中率 ≥ 85% |
| M3 | 社交网络图谱 + 可视化界面 | 任意两节点查询延迟 < 2s |
| M4 | SaaS 多租户 + CI/CD + 监控 | 生产环境稳定运行 72h 无重大故障 |

---

> **自动继续反馈提示词**（供 Cursor Auto Helper）
> 1. 读取 TODOLIST.md，选择状态为 `PENDING` 的第一项。
> 2. 执行开发并更新状态为 `DONE` 或 `BLOCKED`。
> 3. 返回 `是` 或 `否` 并附加进度说明。 