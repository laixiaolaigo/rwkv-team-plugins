# RWKV 团队插件市场

面向 Codex 的团队 Git 插件市场。市场标识为 `rwkv-team`，界面名称为 **RWKV 团队插件市场**。仓库可放在团队自己的 GitHub、GitLab 或其他兼容 Git 的服务中。

## 首批插件

| 插件 ID | 界面名称 | 内容 | 额外配置 |
| --- | --- | --- | --- |
| `rwkv-oa` | RWKV OA | OA 身份及办公信息查询、已授权操作；实际能力取决于 MCP 权限 | 每位成员自己的 `RWKV_OA_TOKEN` |
| `rwkv-code-review` | RWKV 代码审查 | 审查指定代码变更，报告有证据的问题 | 无；在代码仓库中使用 |
| `rwkv-release-notes` | RWKV 更新说明 | 从指定 Git 范围生成更新说明草稿 | 无；在代码仓库中使用 |

“预置”表示这些插件已随仓库提供并列入市场。添加市场后，成员仍可按需安装；不会自动启用全部插件。

## 团队成员安装

需要已安装支持 `codex plugin` 命令的 Codex。本仓库的 CLI 结构检查使用 `codex-cli 0.154.0`；其他版本以实际命令支持为准。

远程仓库建立后，在 PowerShell 中输入它的真实克隆地址：

```powershell
$marketRepoUrl = Read-Host '团队插件市场的 Git 克隆地址'
codex plugin marketplace add $marketRepoUrl --ref main
codex plugin marketplace list

# 按需执行下面的安装命令
codex plugin add rwkv-oa@rwkv-team
codex plugin add rwkv-code-review@rwkv-team
codex plugin add rwkv-release-notes@rwkv-team
```

私有仓库使用成员本机已有的 Git 认证；若 HTTPS 未配置访问权限，可使用团队提供的 SSH 克隆地址。不要把 Git 访问凭据写进 URL 或市场文件。

仓库尚未上传时，也可以在本仓库根目录执行本地注册：

```powershell
codex plugin marketplace add .
```

市场名称唯一。本机若先注册过这个本地市场，之后要切换到 Git 来源，可先执行 `codex plugin marketplace remove rwkv-team`，再添加远程地址。这是替换市场来源，不是修改插件文件。

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
$rwkv-code-review 审查当前未提交改动，重点关注权限和数据一致性。
$rwkv-release-notes 根据 v1.2.0 到 v1.3.0 的差异生成更新说明。
```

最后一个示例里的标签必须在当前项目中真实存在；请替换成自己的版本范围。客户端可能显示带插件前缀的 skill 名称，以候选项实际名称为准。

## 维护和更新

```powershell
# 在仓库根目录运行静态检查，只需 Python 3.9+
python scripts/check_marketplace.py

# 成员拉取更新后的 Git 市场，再重新安装所需插件
codex plugin marketplace upgrade rwkv-team
codex plugin add rwkv-oa@rwkv-team
```

发布插件改动时更新该插件 `.codex-plugin/plugin.json` 中的版本号，提交并推送到市场跟踪的分支。安装后新建任务以加载更新。增加插件的步骤见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 上传到新 Git 仓库

本地目录已初始化为 Git 仓库，分支为 `main`。在 Git 平台创建空仓库后，在这个目录执行：

```powershell
$marketRepoUrl = Read-Host '新建空仓库的 Git 克隆地址'
git remote add origin $marketRepoUrl
git push -u origin main
```

远程若已包含 README 或其他提交，应先查看远程历史并合并；不要用强制推送覆盖它。

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
