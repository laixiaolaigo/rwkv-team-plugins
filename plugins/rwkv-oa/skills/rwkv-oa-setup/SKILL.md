---
name: rwkv-oa-setup
description: 配置或更换当前已安装 RWKV OA 插件的个人 Token，或切换为 RWKV_OA_TOKEN 环境变量认证。用于首次安装、认证失效后的配置修复，以及用户明确要求修改 OA 认证；不依赖 OA MCP 已连接。
---

# RWKV OA 配置

为本 skill 所属的已安装 `rwkv-oa` 插件配置认证。办公查询仍使用 `$rwkv-oa`。

## 定位与执行

1. 从当前加载的 `SKILL.md` 实际绝对路径向上三级定位插件根目录，再定位 `scripts/configure_auth.py`。不要硬编码版本号、市场名或用户目录。目标应位于 `$CODEX_HOME/plugins/cache/<市场>/rwkv-oa/<版本>/`，未设置 `CODEX_HOME` 时为 `~/.codex/plugins/cache/...`。若加载的是源码或市场下载副本，先找到用户启用的已安装 skill；多个安装且来源不明时询问用户选择，不猜测目标。
2. 使用 Python 3.9+（Windows 通常 `python`，macOS 通常 `python3`）。不需要 OA MCP 连接、网络请求或额外 Python 包。缺少 Python 时说明要求，保留原配置。
3. 用户要求配置或更换 Token，即授权此次认证修改；沿用已提供的模式与 Token。没有 Token 时优先让用户在本机终端运行隐藏输入命令。不要要求粘贴凭据到聊天，不读取其他凭据文件或环境变量值，不用旧聊天里的 Token 自行补全。
4. 执行下列相应命令，将 `<插件根目录>` 替换为本 skill 定位出的实际路径；不要在命令行参数或 shell 命令文本中嵌入 Token。

```shell
python "<插件根目录>/scripts/configure_auth.py" --mode token
python "<插件根目录>/scripts/configure_auth.py" --mode env
```

Token 模式默认使用隐藏输入；无交互终端时可加 `--stdin`，通过工具提供的独立 stdin 输入通道传入用户已提供的值并结束输入。不要使用会回显输入的伪终端、shell 字面量、命令历史或临时凭据文件来传递 Token。工具不能安全提供 stdin 时，给出已解析绝对路径的隐藏输入命令让用户本机执行。

## 输入与更新规则

- 支持裸 Token、`Bearer ` 前缀、`{"bearer_token":"..."}`、`{"http_headers":{"Authorization":"Bearer ..."}}`，也支持这些字段放在 `oa_plugin` 或 `mcpServers.oa_plugin` 中。完整 JSON 可分行；Token 值本身不能含换行。裸 Token 经 stdin 传入时不要附加行尾换行。
- `bearer_token` 仅作为输入别名；最终运行配置使用 `http_headers.Authorization`，当前 Codex 不接受独立 `bearer_token` 字段。
- 脚本只修改已安装插件 `.mcp.json` 中 `oa_plugin` 的认证相关字段，检查插件名、版本目录和准确地址 `https://mcp.oa.rwkvos.com/mcp`。固定 Token 模式移除环境变量认证；环境变量模式恢复 `bearer_token_env_var: RWKV_OA_TOKEN`。两种模式都会清理冲突的 Authorization（包括 `env_http_headers` 中的同名字段），保留其他服务和无关字段。
- 空值、换行、无效 Token 字符、冲突输入、损坏 JSON、错误路径、错误插件或异常服务地址均拒绝更新。脚本原子写入，失败时保留原文件。不要绕过校验手写配置。
- 环境变量模式只恢复变量引用，不设置或检查变量值。用户需自行在启动 Codex 的环境中提供 `RWKV_OA_TOKEN`。

## 结果、错误与重新连接

仅报告配置模式、目标文件和成功/失败状态；不回显 Token、完整 JSON、请求头、原始异常或包含凭据的 diff。读取脚本返回的固定错误说明帮助用户纠正路径、JSON、输入或权限问题，不盲目重试其他插件位置。

写入成功后说明：**配置已写入**。让用户完全退出并重新启动 Codex，然后新建任务使用 `$rwkv-oa 我是谁`。只有确认身份查询工具来自本次配置的插件 `oa_plugin` 连接，并实际成功执行只读身份查询后，才能说插件连接已验证。仅有全局 `rwkv_oa` 工具、无法确认工具来源或当前任务尚未重新加载时，维持“配置已写入”的结论。

插件升级或重新安装可能覆盖缓存内个人认证配置，届时重新调用本 skill；环境变量模式用户仍需保证新进程继承了变量。不要把个人认证同步回 Git 模板或全局 MCP 配置。
