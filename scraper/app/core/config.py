"""
应用配置模块
"""
import os
import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, Field, field_validator, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""
    # API配置
    PROJECT_NAME: str = "AIDA Scraper"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = Field(default_factory=lambda: os.getenv("SECRET_KEY", secrets.token_urlsafe(32)))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8天
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """验证CORS配置"""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # 数据库配置
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "aida_scraper"
    DATABASE_URL: Optional[str] = None
    USE_SQLITE: bool = True  # 默认使用SQLite

    @model_validator(mode="after")
    def assemble_db_connection(self) -> "Settings":
        """构建数据库连接字符串"""
        # 首先检查环境变量中是否有DATABASE_URL
        env_db_url = os.getenv("DATABASE_URL")
        if env_db_url:
            self.DATABASE_URL = env_db_url
        elif not self.DATABASE_URL:
            # 如果环境变量中没有，且对象中也没有
            if self.USE_SQLITE:
                # 使用SQLite
                db_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../..", "aida_scraper.db"))
                self.DATABASE_URL = f"sqlite:///{db_file}"
            else:
                # 使用PostgreSQL
                self.DATABASE_URL = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
        return self

    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # Elasticsearch配置
    ELASTICSEARCH_HOST: str = "localhost"
    ELASTICSEARCH_PORT: int = 9200

    # MinIO配置
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False

    # 初始超级用户
    FIRST_SUPERUSER_EMAIL: str = "admin@example.com"
    FIRST_SUPERUSER_USERNAME: str = "admin"
    FIRST_SUPERUSER_PASSWORD: str = "admin"
    FIRST_SUPERUSER_TENANT: str = "default"

    class Config:
        """配置元数据"""
        case_sensitive = True
        env_file = None  # 不使用.env文件


# 创建设置实例
settings = Settings() 