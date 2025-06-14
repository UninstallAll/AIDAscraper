@echo off
REM 启动Celery Worker的批处理脚本

echo 启动Celery Worker...

REM 设置环境变量
set PYTHONPATH=%~dp0
set APP_MODULE=app.core.celery_app

REM 启动Worker
python start_worker.py --mode worker --concurrency 2 --queue default

pause 