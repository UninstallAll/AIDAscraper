param (
    [Parameter(Mandatory=$true)]
    [string]$CommandsFile,
    
    [Parameter(Mandatory=$false)]
    [int]$DefaultTimeout = 60,
    
    [Parameter(Mandatory=$false)]
    [string]$LogFile = "auto_run.log"
)

# 创建或清空日志文件
"[$(Get-Date)] Auto-approve session started" | Out-File -FilePath $LogFile

function Write-Log {
    param (
        [string]$Message,
        [string]$Level = "INFO"
    )
    
    $logMessage = "[$(Get-Date)] [$Level] $Message"
    $logMessage | Out-File -FilePath $LogFile -Append
    Write-Host $logMessage
}

function Run-CommandWithTimeout {
    param (
        [string]$Command,
        [int]$Timeout
    )
    
    Write-Log "Executing: $Command (timeout: ${Timeout}s)"
    
    try {
        $job = Start-Job -ScriptBlock { 
            param($cmd)
            Invoke-Expression $cmd 
        } -ArgumentList $Command
        
        $completed = Wait-Job -Job $job -Timeout $Timeout
        
        if ($null -eq $completed) {
            Write-Log "Command timed out after ${Timeout}s: $Command" -Level "WARNING"
            Stop-Job -Job $job
            Remove-Job -Job $job -Force
            return $false
        } else {
            $result = Receive-Job -Job $job
            Remove-Job -Job $job
            
            if ($result) {
                $result | ForEach-Object { Write-Log "Output: $_" }
            }
            
            Write-Log "Command completed successfully" -Level "SUCCESS"
            return $true
        }
    }
    catch {
        Write-Log "Error executing command: $_" -Level "ERROR"
        return $false
    }
}

# 检查命令文件是否存在
if (-not (Test-Path $CommandsFile)) {
    Write-Log "Commands file not found: $CommandsFile" -Level "ERROR"
    exit 1
}

# 读取命令列表
$commands = Get-Content $CommandsFile | Where-Object { $_ -and -not $_.StartsWith('#') }

Write-Log "Loaded ${commands.Count} commands to execute"

# 执行每个命令
foreach ($line in $commands) {
    if ($line -match '^(.+?)(?:\s+(\d+))?$') {
        $cmd = $Matches[1].Trim()
        $timeout = if ($Matches[2]) { [int]$Matches[2] } else { $DefaultTimeout }
        
        $success = Run-CommandWithTimeout -Command $cmd -Timeout $timeout
        
        # 如果命令执行失败，记录但继续执行下一个
        if (-not $success) {
            Write-Log "Command failed, continuing with next command" -Level "WARNING"
        }
        
        # 在命令之间暂停一下
        Start-Sleep -Seconds 2
    }
    else {
        Write-Log "Invalid command format: $line" -Level "WARNING"
    }
}

Write-Log "All commands executed" -Level "INFO" 