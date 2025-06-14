# 项目开发计划 (TODOLIST.md)

> 本计划与 `SYSTEM.md`、`DESIGN.md` 对应，默认 2 周一个 Sprint，可由 Cursor Auto Helper 自动推进。

## 里程碑概览
| 里程碑 | Sprint 周期 | 目标 |
| ------ | ----------- | ---- |
| M1 | Sprint 1-2 | 核心爬虫原型 & 站点管理 UI |
| M2 | Sprint 3-4 | NLP 流水线 & 数据索引 |
| M3 | Sprint 5-6 | 关系网络可视化 & 搜索界面 |
| M4 | Sprint 7-8 | SaaS 多租户、CI/CD、监控 |

---

## Sprint 1 – 核心爬虫原型 (2 周)
| # | Task | Owner | Status | Est (d) | Note |
| - | ---- | ----- | ------ | ------- | ---- |
| 1 | 初始化 Git 仓库 & CI 流水线 | DevOps | DONE | 1 | GitHub Actions 模板 |
| 2 | 设置 Docker Compose 基础服务 | DevOps | DONE | 1 | postgres, redis, minio |
| 3 | FastAPI 项目脚手架 | Backend | DONE | 1 | 生成 OpenAPI |
| 4 | 用户 & 认证模型 | Backend | DONE | 2 | OAuth2 Password |
| 5 | SiteConfig 表 & CRUD API | Backend | DONE | 2 | Pydantic Schema |
| 6 | Vue3 UI – 登录/仪表盘 | Frontend | DONE | 2 | Element Plus 布局 |
| 7 | Scrapy 爬虫基类 & Pipeline | Backend | DONE | 3 | 本地磁盘输出 JSON |
| 8 | Playwright 集成示例 Spider | Backend | DONE | 2 | 登录 + 动态加载 |
| 9 | Celery Worker & Job 队列 | Backend | DONE | 1 | 支持失败重试 |
| 10 | E2E Demo：抓取 1 个站点并写 DB | Team | DONE | 2 | 成功数据行 > 50 |

## Sprint 2 – 管理 UI & 任务监控 (2 周)
| # | Task | Owner | Status | Est (d) |
| 1 | 前端站点配置表单 (JSON Schema) | Frontend | PENDING | 2 |
| 2 | 任务列表 & 进度条组件 | Frontend | PENDING | 2 |
| 3 | Worker 日志 WebSocket 推送 | Backend | PENDING | 2 |
| 4 | Scrapy 日志格式化 & 存储 | Backend | PENDING | 2 |
| 5 | 功能验收 & 文档 | Team | PENDING | 1 |

## Sprint 3 – NLP 流水线 & 搜索 (2 周)
| # | Task | Owner | Status | Est (d) |
| 1 | spaCy Pipeline 原型 | Data | PENDING | 2 |
| 2 | SentenceTransformer 嵌入 | Data | PENDING | 2 |
| 3 | Elasticsearch 集群部署 | DevOps | PENDING | 1 |
| 4 | 向量 KNN 索引 Mapping | Backend | PENDING | 1 |
| 5 | 搜索 API & UI 集成 | Frontend/Backend | PENDING | 2 |
| 6 | 自动分类模型 (BERT) | Data | PENDING | 3 |

## Sprint 4 – 关系图谱 & 可视化 (2 周)
| # | Task | Owner | Status | Est (d) |
| 1 | Neo4j 部署 & Schema | DevOps | PENDING | 1 |
| 2 | 数据导入脚本 (Art, Exhibition) | Backend | PENDING | 2 |
| 3 | API: 最短路径 & 社区发现 | Backend | PENDING | 2 |
| 4 | D3.js 图谱组件 | Frontend | PENDING | 3 |
| 5 | 交互过滤 & 时间轴 | Frontend | PENDING | 2 |

## Sprint 5 – SaaS & 监控 (2 周)
| # | Task | Owner | Status | Est (d) |
| 1 | 多租户 Schema per tenant | Backend | PENDING | 2 |
| 2 | Keycloak 集成 | DevOps | PENDING | 2 |
| 3 | Prometheus + Grafana 仪表盘 | DevOps | PENDING | 2 |
| 4 | GitHub Actions → ArgoCD | DevOps | PENDING | 2 |
| 5 | 负载/压力测试 | QA | PENDING | 2 |

---

## 风险 & 缓解
| 风险 | 等级 | 缓解措施 |
| ---- | ---- | -------- |
| 目标站反爬升级 | 高 | 快速调整 XPath、代理池热更新 |
| GPU 资源不足 | 中 | 租用云 GPU / 推迟大模型训练 |
| 需求变更 | 中 | 每 Sprint Review 及时同步 |

---

## 自动继续反馈提示词（供 Cursor Auto Helper）
> **核心指令**：
> 1. 从上到下读取 TODOLIST.md，定位第一个 `Status = PENDING` 的任务。
> 2. 依据任务 `Owner` 的角色与 `Est` 天数，生成对应代码/配置/文档，并提交。
> 3. 将任务状态更新为 `DONE` 并写入简要 commit message。
> 4. 返回 `是` 并附上 "已完成任务 #X: <Task>"；若受阻则标 `BLOCKED` 并返回 `否` + 原因。 