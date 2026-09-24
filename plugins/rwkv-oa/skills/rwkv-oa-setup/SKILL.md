---
name: rwkv-oa-setup
description: 配置 RWKV OA 的 RWKV_OA_TOKEN 环境变量、指导重启 Codex，并通过 identity_whoami 检查 Token 和 MCP 连接。用于首次设置、更换 Token 或排查 OA 连接。
---

# RWKV OA 配置与检查

本插件使用 `RWKV_OA_TOKEN` 连接 `https://mcp.oa.rwkvos.com/mcp`。配置环境变量不需要 MCP 已连接。

## 设置环境变量

- 用户只要求检查连接时，先执行下方探测，不修改环境变量。
- 用户要求配置或更换 Token，即授权设置本机当前用户的 `RWKV_OA_TOKEN`，沿用已经给出的信息。用户没有提供 Token 时，指导从 OA 获取，并优先在本机环境变量界面或隐藏输入中填写。
- **Windows**：指导在“环境变量”中添加当前用户变量；用户要求 Codex 代为设置且能安全取得 Token 时，用 `[Environment]::SetEnvironmentVariable('RWKV_OA_TOKEN', $oaToken, 'User')` 保存。`$oaToken` 应来自安全输入通道，不能将实际 Token 嵌入命令文本。仅设置子进程中的 `$env:RWKV_OA_TOKEN` 不会更新正在运行的 Codex。
- **macOS / Linux**：根据 Codex 的启动方式设置当前用户的环境；终端启动需继承变量，桌面启动需在对应启动环境中设置。不要把一次子 shell 的 `export` 当作桌面应用已配置成功。
- 不回显 Token，不写入仓库、插件配置或临时文件。工具不能安全传入凭据时，改为指导本机填写。检查变量时仅报告是否存在，不打印其值。

## 重启 Codex

设置完成后，报告“环境变量已设置，待重启验证”。指导用户完全退出 Codex（包括后台进程），重新打开并新建任务，再执行：

```text
$rwkv-oa-setup 检查 OA 连接
```

不要自行结束用户正在使用的 Codex。当前任务中的工具可能仍使用旧配置，不能据此验证刚更新的 Token。

## MCP 探测

1. 查找本插件 `oa_plugin` 提供的 `identity_whoami` 工具；支持工具发现时先搜索。使用实际工具名称（可能带命名空间前缀）和参数定义执行只读查询，不猜参数。
2. 成功返回身份信息后，报告“Token 与 MCP 连接验证成功”，简要展示姓名或账号。需确认工具来自此插件；其他全局 OA 连接的成功不能证明本插件已配置好。
3. 认证失败时，提示检查或更换 Token 并重启；权限不足时按工具返回说明权限问题；网络错误时报告连接失败，不推断 Token 无效。
4. 工具未出现时，提示检查插件是否启用、Codex 是否继承变量，并完全重启后新建任务重试。只有变量存在或插件安装成功时，仍应报告“尚未验证连接”。
