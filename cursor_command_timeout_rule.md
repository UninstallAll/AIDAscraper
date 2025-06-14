# 命令执行超时处理规则

<user_specific_rule description="命令执行超时自动处理规则">
如果我的命令执行超过30秒没有响应，你就取消当前命令并尝试其他方法。
在每次执行命令前，评估该命令可能的执行时间。
对于可能耗时较长的命令，建议使用command_timeout.ps1脚本执行。
如果命令执行时间超过30秒，请自动终止并提示我使用替代方案。
对于Windows环境，避免使用Unix风格命令，改用PowerShell兼容命令。
</user_specific_rule>

## 使用方法

1. 将这个规则添加到Cursor的规则配置中
2. 确保已经创建了command_timeout.ps1脚本
3. 对于可能耗时较长的命令，使用以下格式：
   ```
   powershell -ExecutionPolicy Bypass -File command_timeout.ps1 -Command "你的命令" -TimeoutSeconds 30
   ```

## 示例

- 创建目录结构：
  ```
  powershell -ExecutionPolicy Bypass -File command_timeout.ps1 -Command "mkdir -p path\to\directory" -TimeoutSeconds 30
  ```

- 运行耗时较长的安装命令：
  ```
  powershell -ExecutionPolicy Bypass -File command_timeout.ps1 -Command "npm install" -TimeoutSeconds 120
  ``` 