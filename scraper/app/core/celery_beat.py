"""
Celery Beat定时任务配置
"""
from celery.schedules import crontab

from app.core.celery_app import celery_app
from app.tasks.scraper_tasks import cleanup_stalled_jobs

# 定义定时任务
celery_app.conf.beat_schedule = {
    # 每10分钟清理一次卡住的任务
    'cleanup-stalled-jobs-every-10-minutes': {
        'task': 'app.tasks.scraper_tasks.cleanup_stalled_jobs',
        'schedule': 600.0,  # 10分钟
    },
    
    # 每天凌晨3点执行的任务示例
    'daily-maintenance-tasks': {
        'task': 'app.tasks.maintenance_tasks.daily_maintenance',
        'schedule': crontab(hour=3, minute=0),
    },
}

# 设置时区
celery_app.conf.timezone = 'Asia/Shanghai' 