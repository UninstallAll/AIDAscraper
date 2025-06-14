@echo off
REM 启动Celery Beat的批处理脚本

echo 启动Celery Beat...

REM 设置环境变量
set PYTHONPATH=%~dp0
set APP_MODULE=app.core.celery_app

REM 启动Beat
python start_worker.py --mode beat

pause 