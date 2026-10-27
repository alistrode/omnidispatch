# OmniDispatch

五平台内容发布中枢：固定账号、持久任务账本、多通道候选、提交结果未知保护、独立 Agent、凭证加密与受控更新。

## Windows 已部署目录

`E:\xxm\OmniDispatch`，dev 源码、backups 备份、release 独立运行环境。release 内置官方 Python 与生产依赖，不使用系统 Python。`Start.cmd` 打开本机 http://127.0.0.1:8791；部署脚本安装专用非管理员账号及唯一的 `OmniDispatch-Hub-Agent` 计划任务，系统启动后运行 Hub/Agent。任务只管理本应用进程，不终止其他程序。

初始化凭据仅存本机 `release\state\ADMIN-CREDENTIALS.private.txt`，登录后在“安全设置”修改密码并启用 TOTP。恢复码仅展示一次；验证码框也接受未使用的恢复码。本地管理员可用 `runtime\python.exe -m omnidispatch.cli --state state reset-admin` 恢复访问，该操作撤销所有会话和 TOTP。

`release\state` 含私钥、凭证与令牌，严格 ACL，禁止上传仓库/打包。SQLite 使用 WAL；正式并发节点部署可设置 PostgreSQL URL。只支持初始 schema v1；未来 schema 迁移必须明确实现，当前不承诺通用自动迁移。

## 已实现的应用能力

- 管理员登录、持久登录节流、CSRF/Origin 检查、TOTP/一次性恢复码、会话撤销。
- 五平台账号及独立通道授权，Fernet 加密，公开接口不回显凭证。
- 图片/视频素材上传、定时任务、幂等入队、同账号串行、租约续期与执行代次、审计与 SSE。
- 提交前明确故障可以同账号切通道；提交过程中断转 needs_verify 并锁定账号，核验前不自动重发。
- 限流冷却、账号授权过期暂停、风控暂停且不擅自换号/换 IP；未经验证的代理链路停止执行。
- Agent 出站认证、撤销、只读引擎检查、任务固定版本、任务范围素材下载。
- 每日发现上游版本、独立签名包隔离安装、防压缩包路径穿越、版本槽、24h/实际样本灰度门槛、切换/回滚元数据。
- Vue3 九个管理页面、响应式布局、无演示成功数据。

## 通道的真实边界

通道注册表中的项目是候选，不等于已安装、已授权或已验收。路由默认全部关闭。先在 Agent 私密配置中填入本机真实程序路径和固定版本，节点只读检查通过后，在界面配置版本，记录真实发布作品 ID 的管理员核验，再启用。人工填写 ID 是管理员证明，不伪称系统自动验证了该平台作品。

X API 适配器支持用户 OAuth token 的纯文本发布。youtubeuploader 使用 OAuth JSON，并从结构化输出读取实际 ID。xhs-mcp 需要每账号独立实例与共享本机素材路径。sau、Spreado、biliup、MatrixMedia 使用固定 CLI argv，不通过 shell 拼接；缺少结构化平台 ID 时进入 needs_verify，不能把退出码零当发布成功。视频发布必须有 ffprobe。sau 的 B站通道因上游隐式自动更新尚未隔离而禁止启用。Postiz 写入接口、Mixpost、postbot 和 X 浏览器通道未完成集成，保持候选关闭。

配额、OAuth 应用审批、扫码及平台发布权限仍需真实账号提供；仓库和运行包不包含用户平台授权。未执行真实五平台发布前，不能宣称“两条可用独立通道”或五平台验收通过。

## 出口

账号可选择 direct、trusted-static、resin，代理密码加密保管。当前实现验证了适配器的显式模式门槛；X API 和 biliup 有显式代理参数，其余通道禁止非直连模式，直到逐进程代理链路完成实测。不会导入公共免费代理，也不自动为风控更换出口。Resin 安装是外部网关安装，需用户自己配置可信代理资源；当前尚未实现管理 API 自动换绑与出口地理一致性实测。

## 更新

每日自动拉取 GitHub Releases 只产生候选。上传隔离安装包需 `X-Update-Signature` 和部署侧 OMNI_UPDATE_PUBLIC_KEY，zip 根目录包含 omni-engine.json（engine/version/adapter_protocol=1）。签名公钥不允许从包中注入。可使用 API multipart `/api/updates/{id}/stage` 上传。

灰度需要标记“允许灰度”的账号和“灰度任务”，成功结果计入对应版本样本；至少 24 小时且三次成功、无失败才允许提升。Agent 必须已安装并上报匹配版本。当前自动更新没有实现跨节点二进制分发、通用凭证格式迁移、Hub 自更新和不可逆数据库自动降级，这些必须继续以明确实现和恢复验证为前提。没有信任公钥、测试账号或实际样本时保持阻塞。

## 源码运行与验证

Python 3.11+：`python -m venv .venv`，激活后 `pip install -r requirements.lock.txt`。前端 `cd apps/web && npm ci && npm run build`。

初始化：`python -m omnidispatch.cli --state state init`；Hub：`python -m omnidispatch.cli --state state serve`；节点注册：`python -m omnidispatch.cli --state state register-agent`；Agent：`python -m omnidispatch.cli agent --config state/agent.json`。

验证：`python -m pytest -q`。测试使用独立临时数据库和测试凭证，绝不向平台提交。真实发布验收记录需单列。SQLite 备份：`python -m omnidispatch.cli --state state backup`，在线备份后执行完整性检查；vault.key 独立备份，不能只备数据库。PostgreSQL 使用 pg_dump/restore，Compose 模板尚需在目标生产环境验收。

完整设计与参考来源见 DESIGN.md；安装和运行状态以 HANDOFF.md 为准。
