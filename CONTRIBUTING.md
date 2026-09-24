# 维护插件

插件源码放在 `plugins/<插件名>/`。参考 `rwkv-oa` 创建 `.codex-plugin/plugin.json` 和 `.mcp.json`，再将插件加入 `.agents/plugins/marketplace.json`；市场条目的 `source.path` 相对于仓库根目录。认证通过环境变量配置，提交前检查文件中没有个人 Token。

修改现有插件时更新清单版本号，并同步 README 中的使用说明。在仓库根目录注册本地市场并安装验证：

```shell
codex plugin marketplace add .
codex plugin add rwkv-oa@rwkv-team
```

如果已注册同名远程市场，可使用独立的 `CODEX_HOME` 目录进行本地验证。检查安装成功后，由配置了个人 Token 的成员重启 Codex、新建任务并执行只读 OA 查询。

检查差异后，按团队流程提交并合并到市场跟踪的 `main` 分支。正式发布源是本仓库的 `plugins/`，不要将已安装缓存中的个人配置复制回来。
