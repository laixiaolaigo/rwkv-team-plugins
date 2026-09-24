# RWKV 团队插件市场

面向 Codex 的团队 Git 插件市场。市场标识为 `rwkv-team`，界面名称为 **RWKV 团队插件市场**。仓库可放在团队自己的 GitHub、GitLab 或其他兼容 Git 的服务中。

## 首批插件

| 插件 ID | 界面名称 | 内容 | 额外配置 |
| --- | --- | --- | --- |
| `rwkv-oa` | RWKV OA / RWKV OA 配置 | OA 办公查询及独立认证配置；实际业务能力取决于 MCP 权限 | 个人 Token 或 `RWKV_OA_TOKEN`；配置脚本需要 Python 3.9+ |

“预置”表示这些插件已随仓库提供并列入市场。添加市场后，成员仍可按需安装；不会自动启用全部插件。

## 团队成员安装

需要已安装支持 `codex plugin` 命令的 Codex。本仓库的 CLI 结构检查使用 `codex-cli 0.154.0`；其他版本以实际命令支持为准。

源码仓库：[laixiaolaigo/rwkv-team-plugins](https://github.com/laixiaolaigo/rwkv-team-plugins)。在 PowerShell 中添加市场：

```powershell
codex plugin marketplace add https://github.com/laixiaolaigo/rwkv-team-plugins.git --ref main
codex plugin marketplace list

# 按需执行下面的安装命令
codex plugin add rwkv-oa@rwkv-team
```

默认使用 HTTPS，避免安装过程依赖 SSH 密钥和 22 端口。私有仓库仍需要成员具备访问权限并配置 Git 认证。不要把 Git 访问凭据写进 URL 或市场文件。

本地开发时，也可以在克隆后的仓库根目录执行本地注册：

```powershell
codex plugin marketplace add .
```

市场名称唯一。本机若先注册过这个本地市场，之后要切换到 Git 来源，可先执行 `codex plugin marketplace remove rwkv-team`，再添加远程地址。这是替换市场来源，不是修改插件文件。

### 添加市场时 SSH 连接失败

如果看到 `Connection closed ... port 22` 和 `Could not read from remote repository`，说明 Git 的 SSH 连接未成功建立，尚未读取插件市场配置。常见原因包括网络、防火墙或代理对 SSH 连接的限制；该错误本身不能证明仓库权限不足。

先用 HTTPS 检查仓库可达性，再执行本页的 HTTPS 添加命令：

```shell
git ls-remote https://github.com/laixiaolaigo/rwkv-team-plugins.git refs/heads/main
```

如果 `codex plugin marketplace list` 中已存在使用 SSH 来源的 `rwkv-team`，先移除这个市场来源，再以 HTTPS 注册：

```shell
codex plugin marketplace remove rwkv-team
codex plugin marketplace add https://github.com/laixiaolaigo/rwkv-team-plugins.git --ref main
```

如果 HTTPS 命令仍报告 SSH 的 22 端口错误，检查本机是否配置了 URL 自动改写：

```shell
git config --show-origin --get-regexp '^url\..*\.insteadof$'
```

如果团队必须使用 SSH，可先测试 `ssh -T -p 443 git@ssh.github.com`。测试通过后可使用 `ssh://git@ssh.github.com:443/laixiaolaigo/rwkv-team-plugins.git` 作为市场地址；这仍要求有效的 GitHub SSH 认证。参见 [GitHub：通过 HTTPS 端口使用 SSH](https://docs.github.com/en/authentication/troubleshooting-ssh/using-ssh-over-the-https-port)。

## RWKV OA 认证

每位成员使用自己从 OA 获得的 MCP Token。分发版的 `.mcp.json` 只引用环境变量 `RWKV_OA_TOKEN`，不含个人 Token。

### 通过“RWKV OA 配置”入口配置（0.1.2 起）

安装后完全退出并重新启动 Codex，再新建任务。在输入框通过 `@` 搜索 **RWKV OA 配置**，或输入：

```text
$rwkv-oa-setup 配置我的 OA Token
$rwkv-oa-setup 更换 Token
$rwkv-oa-setup 切换为环境变量认证
```

这个 skill 不依赖 OA MCP 已连接。需要 **Python 3.9+**，只使用标准库：Windows 通常用 `python`，macOS 通常用 `python3`。配置入口会定位自身所属的已安装插件并给出实际脚本路径；无需自己修改版本目录。

固定 Token 模式支持裸 Token、带 `Bearer ` 前缀的值，以及 `bearer_token` 或 `http_headers.Authorization` JSON 片段。也接受完整的 `mcpServers.oa_plugin` 配置。`bearer_token` 是配置输入别名，最终写入 Codex 接受的 `http_headers.Authorization`，不会把独立 `bearer_token` 字段写入运行配置。

需要手工执行时，将下面的路径替换为配置 skill 确认的已安装插件绝对路径（不要指向 Git 源码或市场下载目录）：

```shell
# Windows 用 python；macOS 用 python3。提示后输入 Token，不会回显。
python "<已安装插件根目录>/scripts/configure_auth.py" --mode token

# 恢复 RWKV_OA_TOKEN 引用；不会设置该环境变量本身。
python "<已安装插件根目录>/scripts/configure_auth.py" --mode env
```

脚本也支持 `--mode token --stdin`，从标准输入读取到 EOF；仅供能够安全传入 stdin 的工具使用，不要把 Token 放进命令行参数、shell 命令历史或临时文件。裸 Token 输入不得含换行；JSON 文档可分行，但 Token 字符串不能含换行。重复 JSON 键、冲突 Token、错误插件或服务地址会拒绝修改。输出只包含状态、模式、路径及固定错误说明。

固定 Token 保存于本机插件缓存 `.mcp.json`，这是本地配置文件。脚本原子更新 `oa_plugin` 的认证字段，保留其他 MCP 服务和无关配置。切换模式时清理冲突的 Authorization（包括来自 `env_http_headers` 的引用）。

**配置后需要完全退出并重新启动 Codex，再新建任务。** 使用 `$rwkv-oa 我是谁` 执行只读身份查询；只有工具来源确认为该插件的 `oa_plugin` 且查询成功，才完成连接验收。保存配置成功本身不代表连接成功，全局 `rwkv_oa` 服务的成功也不能代替此插件验收。

**升级或重新安装插件可能覆盖本地认证配置。** 固定 Token 用户届时重新调用配置入口；环境变量用户确认新的 Codex 进程能读取变量。个人认证不应同步回 Git 源码、市场下载目录或全局 MCP 配置。

### 环境变量模式

使用此模式时，先通过配置入口恢复环境变量引用（新安装的分发模板默认已如此），再设置变量。Windows 用户可以在克隆后的仓库根目录运行：

```powershell
& .\scripts\set-oa-token.ps1
```

脚本会遮蔽输入，将 Token 保存为当前 Windows 用户的环境变量，并更新当前 PowerShell 的环境。该方式是本机环境配置，不是加密凭据库。然后完全退出 Codex 并重新启动，在新任务中试用；应用进程必须能读取到该环境变量。

macOS/Linux 用户可通过自己的进程环境管理方式设置同名变量，并从继承了该变量的环境启动 Codex。仅在终端里 export 不保证从桌面启动的应用能够读取。

如果本机已安装旧的 `rwkv-oa@rwkv-local`，团队版本配置好以后，在插件界面停用旧版本，以免同时出现两个 OA 入口。

## 调用

安装并新建任务后，在输入框候选列表选择对应插件或 skill。支持的客户端可通过 `@` 搜索显示名称；也可以使用 skill 名称：

```text
$rwkv-oa 我是谁？
$rwkv-oa-setup 配置我的 OA Token
```

客户端可能显示带插件前缀的 skill 名称，以候选项实际名称为准。

## 维护和更新

```powershell
# 在仓库根目录运行静态检查，只需 Python 3.9+
python scripts/check_marketplace.py
python -m unittest discover -s tests -v

# 成员拉取更新后的 Git 市场，再重新安装所需插件
codex plugin marketplace upgrade rwkv-team
codex plugin add rwkv-oa@rwkv-team
```

发布插件改动时更新该插件 `.codex-plugin/plugin.json` 中的版本号，提交并推送到市场跟踪的分支。安装后新建任务以加载更新。增加插件的步骤见 [CONTRIBUTING.md](CONTRIBUTING.md)。

市场检查继续拒绝 `.mcp.json` 中的明文认证字段。若开发工作区已填入个人 Token，应保留该本机修改并从发布暂存区排除；在包含环境变量模板的干净发布副本中运行检查，不要为通过检查而放宽凭据规则。测试仅使用虚构 Token，不访问 OA 服务。

## 获取源码并提交更新

克隆团队仓库进行维护，市场跟踪分支为 `main`：

```powershell
git clone https://github.com/laixiaolaigo/rwkv-team-plugins.git
cd rwkv-team-plugins
python scripts/check_marketplace.py
```

修改后检查差异、提交，并通过团队约定的分支或 PR 流程合并到 `main`。

## 布局

```text
.agents/plugins/marketplace.json       市场目录与安装策略
plugins/<plugin-id>/.codex-plugin/     插件清单
plugins/<plugin-id>/skills/            工作流与界面元数据
plugins/rwkv-oa/.mcp.json               OA 服务连接及环境变量引用
plugins/rwkv-oa/scripts/configure_auth.py  已安装插件的跨平台认证配置
tests/test_configure_auth.py            虚构 Token 配置与失败保护测试
scripts/check_marketplace.py           静态结构和凭据字段检查
scripts/set-oa-token.ps1                Windows 本机 Token 配置
```

市场条目的 `source.path` 相对于仓库根目录，例如 `./plugins/rwkv-oa`。

参考：[OpenAI 插件打包与市场规范](https://developers.openai.com/plugins/build/plugins)、[插件 MCP 环境变量认证](https://developers.openai.com/api/docs/guides/agents-api/tools/plugins)。
