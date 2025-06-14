param (
    [Parameter(Mandatory=$true)]
    [string]$Command,
    
    [Parameter(Mandatory=$false)]
    [int]$TimeoutSeconds = 30
)

Write-Host "执行命令: $Command"
Write-Host "超时设置: $TimeoutSeconds 秒"

# 创建一个作业来运行命令
$job = Start-Job -ScriptBlock {
    param($cmd)
    Invoke-Expression $cmd
} -ArgumentList $Command

# 等待作业完成或超时
$completed = Wait-Job -Job $job -Timeout $TimeoutSeconds

# 检查是否超时
if ($null -eq $completed) {
    Write-Host "命令执行超时 ($TimeoutSeconds 秒)，正在终止..." -ForegroundColor Red
    Stop-Job -Job $job
    Remove-Job -Job $job -Force
    exit 1
} else {
    # 获取并显示命令输出
    Receive-Job -Job $job
    Remove-Job -Job $job
    Write-Host "命令已成功完成" -ForegroundColor Green
} 