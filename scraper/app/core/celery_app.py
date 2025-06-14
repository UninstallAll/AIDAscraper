"""
Celery应用配置
"""
from celery import Celery

from app.core.config import settings

# 创建Celery实例
celery_app = Celery(
    "worker",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
)

# 配置Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    worker_hijack_root_logger=False,
    task_track_started=True,
    task_time_limit=3600,  # 任务超时时间（秒）
    worker_max_tasks_per_child=200,  # 每个worker最多执行的任务数
    broker_connection_retry_on_startup=True,
    
    # 失败重试配置
    task_acks_late=True,  # 任务完成后才确认，确保任务不会丢失
    task_reject_on_worker_lost=True,  # worker异常终止时拒绝任务，让其重新分配
    worker_prefetch_multiplier=1,  # 每个worker一次只预取一个任务，避免任务堆积
    
    # 重试策略
    task_default_retry_delay=60,  # 默认重试延迟（秒）
    task_max_retries=3,  # 最大重试次数
    
    # 任务结果配置
    task_ignore_result=False,  # 不忽略任务结果
    result_expires=86400,  # 结果过期时间（秒）
    
    # 心跳监控
    worker_send_task_events=True,  # 发送任务事件
    task_send_sent_event=True,  # 发送任务发送事件
)

# 包含任务模块
celery_app.autodiscover_tasks(["app.tasks"]) 