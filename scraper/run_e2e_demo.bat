@echo off
REM E2E演示批处理脚本

echo 运行E2E演示：抓取艺术网站并将数据写入数据库...

REM 设置环境变量
set PYTHONPATH=%~dp0

REM 创建输出目录
if not exist output mkdir output

REM 运行E2E演示
python e2e_demo.py --config app/scrapers/spiders/demo_config.json --output output

echo.
echo 演示完成，请查看输出目录中的结果。

pause 