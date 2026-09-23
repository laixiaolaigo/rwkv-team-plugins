# RWKV 团队插件市场

面向 Codex 的团队 Git 插件市场。市场标识为 `rwkv-team`，界面名称为 **RWKV 团队插件市场**。仓库可放在团队自己的 GitHub、GitLab 或其他兼容 Git 的服务中。

## 首批插件

| 插件 ID | 界面名称 | 内容 | 额外配置 |
| --- | --- | --- | --- |
| `rwkv-oa` | RWKV OA | OA 身份及办公信息查询、已授权操作；实际能力取决于 MCP 权限 | 每位成员自己的 `RWKV_OA_TOKEN` |

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

Windows 用户可以在克隆后的仓库根目录运行：

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
```

客户端可能显示带插件前缀的 skill 名称，以候选项实际名称为准。

## 维护和更新

```powershell
# 在仓库根目录运行静态检查，只需 Python 3.9+
python scripts/check_marketplace.py

# 成员拉取更新后的 Git 市场，再重新安装所需插件
codex plugin marketplace upgrade rwkv-team
codex plugin add rwkv-oa@rwkv-team
```

发布插件改动时更新该插件 `.codex-plugin/plugin.json` 中的版本号，提交并推送到市场跟踪的分支。安装后新建任务以加载更新。增加插件的步骤见 [CONTRIBUTING.md](CONTRIBUTING.md)。

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
scripts/check_marketplace.py           静态结构和凭据字段检查
scripts/set-oa-token.ps1                Windows 本机 Token 配置
```

市场条目的 `source.path` 相对于仓库根目录，例如 `./plugins/rwkv-oa`。

参考：[OpenAI 插件打包与市场规范](https://developers.openai.com/plugins/build/plugins)、[插件 MCP 环境变量认证](https://developers.openai.com/api/docs/guides/agents-api/tools/plugins)。
