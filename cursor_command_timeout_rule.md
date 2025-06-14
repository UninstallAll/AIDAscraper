# Cursor 命令超时与自动执行规则

为了解决命令执行时可能卡住的问题，以及实现无需用户批准的自动化执行，请将以下规则添加到 `rules` 部分：

```
<always_applied_workspace_rules description="这些是工作区级别的规则，代理必须始终遵循。">
- 如果我的命令执行超过30秒没有响应，你就取消当前命令并尝试其他方法。
- 在每次执行命令前，评估该命令可能的执行时间。
- 对于可能耗时较长的命令，建议使用command_timeout.ps1脚本执行。
- 如果命令执行时间超过60秒，请自动终止并提示我使用替代方案。
- 对于Windows环境，避免使用Unix风格命令，改用PowerShell兼容命令。
- 在每次执行命令前，评估该命令可能的执行时间。
- 对于可能耗时较长的命令，使用auto_approve.ps1脚本执行。
- 对于需要批量执行的命令，将其添加到commands.txt并使用auto_run.bat执行。
- 对于启动服务器或持续运行的命令，使用--background参数在后台运行。
</always_applied_workspace_rules>
```

## 自动执行工具说明

本项目提供了以下工具来解决命令执行超时和自动批准问题：

1. **command_timeout.bat/ps1**：
   - 用于执行单个命令并设置超时时间
   - 示例：`command_timeout.bat "python script.py" 30`

2. **auto_approve.ps1**：
   - 批量执行命令，支持超时控制，无需用户批准
   - 从命令列表文件读取要执行的命令
   - 记录执行日志

3. **commands.txt**：
   - 命令列表文件，每行一个命令
   - 可选指定每个命令的超时时间
   - 支持注释（以#开头）

4. **auto_run.bat**：
   - 启动自动执行脚本的快捷方式
   - 执行完成后会生成日志文件

## 使用方法

1. 编辑 `commands.txt` 添加需要执行的命令
2. 运行 `auto_run.bat` 启动自动执行
3. 查看 `auto_run.log` 了解执行结果

## 注意事项

- 确保PowerShell执行策略允许运行脚本（脚本会尝试使用 `-ExecutionPolicy Bypass`）
- 命令执行失败不会中断整个流程，会继续执行下一个命令
- 日志文件会记录所有命令的执行状态和输出 