@echo off
setlocal enabledelayedexpansion

REM 获取命令和超时时间参数
set "command=%~1"
set "timeout=%~2"

if "%command%"=="" (
    echo 错误: 必须提供要执行的命令
    echo 用法: command_timeout.bat "命令" 超时秒数
    exit /b 1
)

if "%timeout%"=="" (
    set "timeout=30"
)

echo 执行命令: %command%
echo 超时设置: %timeout% 秒

REM 使用start命令和timeout命令实现超时控制
start /b cmd /c "%command% > command_output.txt 2>&1"
set "start_pid=%errorlevel%"

REM 等待指定的秒数
timeout /t %timeout% /nobreak > nul

REM 检查进程是否仍在运行
tasklist /fi "pid eq %start_pid%" > nul 2>&1
if %errorlevel% equ 0 (
    echo 命令执行超时 (%timeout% 秒)，正在终止...
    taskkill /pid %start_pid% /f > nul 2>&1
    exit /b 1
) else (
    echo 命令已成功完成
    type command_output.txt
)

del command_output.txt > nul 2>&1
exit /b 0

endlocal 