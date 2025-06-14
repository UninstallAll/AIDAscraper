@echo off
setlocal enabledelayedexpansion

:: 获取命令和超时时间
set "command=%~1"
set "timeout=%~2"

if "%command%"=="" (
    echo 错误: 未提供命令
    echo 用法: command_timeout.bat "命令" 超时秒数
    exit /b 1
)

if "%timeout%"=="" (
    set "timeout=30"
)

echo 执行命令: %command%
echo 超时设置: %timeout% 秒

:: 创建临时文件来存储开始时间
set "temp_file=%temp%\cmd_timeout_%random%.tmp"
echo %time% > "%temp_file%"

:: 启动命令
start /b cmd /c "%command% > %temp%\cmd_output_%random%.txt 2>&1"
set "cmd_pid=%errorlevel%"

:: 等待循环
set /a elapsed=0
:wait_loop
    :: 检查是否超时
    if %elapsed% geq %timeout% (
        echo 命令执行超时 (%timeout% 秒)，正在终止...
        taskkill /F /PID %cmd_pid% > nul 2>&1
        del "%temp_file%" > nul 2>&1
        exit /b 1
    )
    
    :: 检查命令是否仍在运行
    tasklist /FI "PID eq %cmd_pid%" 2>nul | find "%cmd_pid%" > nul
    if %errorlevel% neq 0 (
        echo 命令已成功完成
        del "%temp_file%" > nul 2>&1
        exit /b 0
    )
    
    :: 等待1秒
    timeout /t 1 /nobreak > nul
    set /a elapsed+=1
    
    goto wait_loop

endlocal 