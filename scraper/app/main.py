"""
AIDA Scraper 主应用程序
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import auth, sites, jobs, search
from app.core.config import settings

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="艺术家与策展人生态信息采集与分析平台",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 配置CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# 注册路由
app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["认证"])
app.include_router(sites.router, prefix=settings.API_V1_STR, tags=["站点配置"])
app.include_router(jobs.router, prefix=settings.API_V1_STR, tags=["爬虫任务"])
app.include_router(search.router, prefix=settings.API_V1_STR, tags=["搜索"])


@app.get("/", tags=["状态"])
async def root():
    """
    根路径，返回API状态
    """
    return {"status": "ok", "message": "AIDA Scraper API 正在运行"}


@app.get("/health", tags=["状态"])
async def health():
    """
    健康检查
    """
    return {"status": "healthy"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    全局异常处理器
    """
    logger.error(f"全局异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误"},
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 