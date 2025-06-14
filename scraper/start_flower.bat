@echo off
REM 启动Celery Flower监控的批处理脚本

echo 启动Celery Flower监控...

REM 设置环境变量
set PYTHONPATH=%~dp0
set APP_MODULE=app.core.celery_app

REM 启动Flower
python start_worker.py --mode flower --port 5555

pause 