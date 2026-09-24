# RWKV 团队插件市场

面向 Codex 的团队插件市场 `rwkv-team`，提供 **RWKV OA** 插件 `rwkv-oa`，通过远程 MCP 服务查询办公信息和处理已授权事务。可用工具取决于 OA 服务及个人权限。

## 安装

需要支持 `codex plugin` 命令的 Codex：

```shell
codex plugin marketplace add https://github.com/laixiaolaigo/rwkv-team-plugins.git --ref main
codex plugin add rwkv-oa@rwkv-team
```

## 设置 Token

从 OA 获取个人 MCP Token，将其设置为环境变量 `RWKV_OA_TOKEN`：

- **Windows**：打开系统的“环境变量”设置，在当前用户的变量中添加 `RWKV_OA_TOKEN`，值为个人 Token。
- **macOS / Linux**：在启动 Codex 的环境中设置同名变量，确保 Codex 进程继承它；仅在终端中设置变量，不保证从桌面启动的应用能够读取。

插件的 `.mcp.json` 只引用环境变量。个人 Token 留在本机，不写入仓库。

也可以使用插件中的“RWKV OA 配置”入口，获取设置指导，或让 Codex 帮助设置本机用户环境变量：

```text
$rwkv-oa-setup 帮我配置 OA 环境变量
```

## 使用

完全退出并重新启动 Codex，再新建任务，直接输入：

```text
$rwkv-oa-setup 检查 OA 连接
```

配置 skill 会调用插件提供的 `identity_whoami`，成功返回身份信息后确认 Token 和 MCP 连接可用。若工具未出现，会指导检查插件和环境变量并重启。验证成功后可直接提出 OA 请求，例如“使用 RWKV OA 查询我是谁”。

此前使用固定 Token 的成员，升级时需改用环境变量认证。

## 更新

```shell
codex plugin marketplace upgrade rwkv-team
codex plugin add rwkv-oa@rwkv-team
```

更新后完全退出并重新启动 Codex，再新建任务。

## 维护

市场清单位于 `.agents/plugins/marketplace.json`，插件源码位于 `plugins/rwkv-oa/`，包含插件清单、MCP 配置和一个配置 skill。维护方式见 [CONTRIBUTING.md](CONTRIBUTING.md)。
