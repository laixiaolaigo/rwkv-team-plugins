# 添加和维护插件

每个插件独立维护版本、skill 和可选 MCP 配置。先在本地完成修改与检查，再提交到团队仓库。

## 添加一个只包含 skill 的插件

1. 在 `plugins/` 下创建以小写字母和连字符命名的目录，例如 `rwkv-docs`。
2. 参考 `rwkv-oa/.codex-plugin/plugin.json` 创建自己的插件清单，修改 `name`、描述、显示名称、默认提示和版本。只包含 skill 的插件应省略 `mcpServers`，并在 skill 的界面配置中省略 MCP `dependencies`。名称必须与目录及市场条目一致。
3. 在 `skills/rwkv-docs/SKILL.md` 的 YAML 头部写入 `name`、`description`，正文写明工作流、实际能力与结果要求。不要把团队尚未确定的约定写成强制规则。
4. 创建 `skills/rwkv-docs/agents/openai.yaml`，配置显示名称、短描述和包含 `$rwkv-docs` 的默认提示。
5. 将下面的条目追加到 `.agents/plugins/marketplace.json` 的 `plugins` 数组中。数组顺序就是市场展示顺序。

```json
{
  "name": "rwkv-docs",
  "source": {
    "source": "local",
    "path": "./plugins/rwkv-docs"
  },
  "policy": {
    "installation": "AVAILABLE",
    "authentication": "ON_INSTALL"
  },
  "category": "Productivity"
}
```

这里的示例只有在对应插件目录创建完成后才能加入市场。

## 添加 MCP 工具

参考 `rwkv-oa/.mcp.json` 配置服务，在插件清单中增加 `"mcpServers": "./.mcp.json"`。每个服务使用独立、含义明确的环境变量读取认证信息，禁止从开发者机器复制包含 Token 的缓存配置。

Skill 应根据实际工具描述选择接口，不应编造工具名或业务功能。README 中说明成员如何配置认证和判断连接是否成功。仅运行静态检查不能证明服务认证和真实业务操作可用。

## 检查和发布

1. 运行 `python scripts/check_marketplace.py`。
2. 在本机注册此市场，并安装或重新安装改动的插件。已有插件的功能改动需要更新插件清单版本。
3. 新建 Codex 任务，选择 skill，完成与变更有关的代表性验证；需要凭据的插件由使用者配置自己的认证。
4. 将插件版本变化和兼容性说明一起提交，推送到远程市场跟踪的分支。

不要修改已安装缓存作为正式发布源。本仓库的 `plugins/` 才是团队维护的源码。

`scripts/check_marketplace.py` 检查此仓库约定的本地插件结构、路径、skill 头部和常见明文认证字段，不是完整的官方插件 schema 校验器，也不是通用秘密扫描器。
