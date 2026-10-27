# OmniDispatch 当前交接

日期：2026-10-27（北京时间）。本文件记录已完成范围及仍待完成的部分，不把模拟结果当作平台发布验收。

## 真实部署

- 主机：LAPTOP-MCMQHDN4，使用 SSH Relay 5.4 核验后操作。
- 根目录：E:\xxm\OmniDispatch；dev 源码、backups 备份、release 运行环境。旧 E:\项目计划 等目录保留。
- Windows 后台：OmniDispatch-Hub-Agent 计划任务；专用 OmniDispatchRun 普通账号，实测 administrator=false。赋予该账号 SeBatchLogonRight，未加入管理员组。
- Hub 仅监听 127.0.0.1:8791；监督锁端口 8792；Resin 仅监听 127.0.0.1:2260。
- release 内置 CPython 3.14.10 与固定生产依赖。state 的管理员/用户/应用 ACL 已限制。发布者签名私钥在 backups/update-signer-private，应用账号不可读取。
- 初始登录账号 admin；初始密码仅位于 release/state/ADMIN-CREDENTIALS.private.txt，未上传仓库。
- 临时公网入口由本应用自己的 cloudflared 提供。当前进程观察到 https://professional-conf-addresses-intranet.trycloudflare.com ，远端电脑通过 HTTPS 回查 /api/health 为 200。本云执行环境请求同类域名遭 Cloudflare 403 拦截；这不等于所有访问来源都能打开。进程重建域名变化，最新地址由 supervisor 自动写入 release/state/PUBLIC-URL.txt。生产固定域名尚未配置。

## 已验证

1. Windows：19 项测试通过，含同账号并发隔离、提交结果未知保护、旧租约拒绝、提交前切换、授权/限流处理、CSRF、TOTP 一次性恢复码、签名更新与路径防护、分块上传幂等、原生 Job Object 回收。
2. 云端：核心测试通过；并发、幂等、租约在 PostgreSQL 17.6 上重复验证。原生 Windows 进程测试在 Linux 跳过，未冒充通过。
3. Docker：真实多阶段镜像构建通过，CPython 3.14.10；实际以 UID 10001 启动，连接 PostgreSQL 完成登录、创建任务和取消任务，全程未向平台发布。
4. 浏览器：九个页面、登录、账号创建、无效表单拒绝、桌面/窄屏布局及分块上传展示经过 Chromium 操作。远端 Windows 的管理员登录与 Agent 在线也由实际服务 API 验证。
5. Windows 主服务实际返回 health ok、SQLite、管理员登录通过、匿名请求被拒绝、Agent 在线。19 项测试不包含任何真实平台作品发布。

## 真实引擎状态

- xhs-mcp v2.5.5：程序安装，--help 返回零；未启动账号专属实例，未登录平台。
- youtubeuploader v1.25.5：程序安装，--help 返回零；无 OAuth 频道授权。
- Spreado v1.2.0：程序安装，--help 返回零；未导入小红书/视频号账号。
- ffprobe 5.1.0：程序安装，版本检查通过。
- Resin v1.3.0：已配置随机私密管理/代理 token，实际监听本机端口；没有导入可信代理节点。初次 --help 因缺少必需环境变量返回 1，后续启动使用明确环境配置，未将初次检查伪报为成功。
- Agent 已配置 xapi-x、ytuploader-youtube、spreado-xiaohongshu、spreado-tencent 的本机程序/版本；注册表中所有发布通道默认未核验、未启用。

## 更新机制

已实现：每日 GitHub 版本发现、受信 Ed25519 签名包、独立版本槽、同机 Agent 解析活动/灰度版本、测试账号专用灰度通道、24 小时与每条在用通道至少三次成功的提升门槛、回滚、可选签名发布源、防元数据过期与代次回退。

当前已配置受信公钥；未配置 OMNI_UPDATE_FEED_URL，OMNI_AUTO_PROMOTE 为关闭。现阶段自动发现开启，自动生产升级没有启用。灰度没有真实账号和真实样本，未开始计为验收通过。跨节点二进制分发、Hub 自更新、通用凭证迁移和不可逆数据库回滚仍未实现。

## 完整目标尚未完成的部分

- 五平台账号授权与实际作品验收尚缺；本轮真实平台发布数为零。
- X API 适配器当前只支持纯文本。X 视频/浏览器通道未实现。
- sau/Spreado/biliup/MatrixMedia 的 CLI 路径已封装，但缺少结构化平台 ID 时转 needs_verify；sau B站隐式更新尚未隔离，因此该通道禁止启用。
- sau、biliup、MatrixMedia 尚未完成本机安装与平台登录；biliup 的用途限制未确认。
- Postiz 写入、Mixpost Lite 能力与接入、postbot 扩展接管仍为未完成的 L2 候选；“每平台两条实测独立通道”尚未达到。
- Resin 管理 API 自动换绑、地区/进程级出口实测、多节点出口资源、平台级全局配额策略和告警服务仍待实现/验收；当前保守策略遇风控、未知结果或未验证出口会暂停。
- PostgreSQL 容器已进行实际集成验证；Windows 当前运行 SQLite。没有未声明的自动迁移。

## 维护

停止本应用：以管理员执行 scripts/stop-windows.ps1；它只处理专用应用账号与本应用路径/隧道范围的进程。正常关闭监督进程时由 Windows Job Object 回收子进程。不要停止 SSH Relay 或用户其他应用。

后续更新必须保留 release/state 与 backups/update-signer-private，不将其打入包或提交 Git。源码备份在 backups。原始凭证、私钥和原始运行日志不上传。

最终浏览器补充：通过已认证 SSH 的回环转发访问真实 Windows 服务，完成管理员登录、九个页面浏览与退出；未发现前端运行错误，未创建平台作品。该结果验证 Windows 上的真实 Web 服务，独立于 Cloudflare 多地区公网可达性。
