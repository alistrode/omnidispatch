# OmniDispatch 实施方案

日期：2026-10-27。工程根目录：E:\xxm\OmniDispatch；源码 dev、备份 backups、运行包 release。现有其他目录保留。

## 1. 产品目标与承诺

统一管理小红书、视频号、B站、YouTube、X 的素材、账号授权、发布任务、引擎版本、可信出口和审计记录。支持每个平台多条候选通道；只有完成指定版本、指定账号与环境的真实发布验收，才计入可用通道数。目标是安全恢复、结果可追踪、尽量不中断，不承诺平台故障时仍可发布。自动容错优先保证不重复发、不更换发布主体、不悄悄丢失参数。

## 2. 参考与核验结果

已于本日读取上游 README；这代表文档核验，不代表真实账号验收。

- https://github.com/gitroomhq/postiz-app ：官方 API/OAuth 聚合服务，支持 X、YouTube；当前技术栈列出 PostgreSQL、Temporal，部署说明还涉及 Redis。使用上游匹配版本部署文件，不手写简化依赖。开发者应用、权限和额度由使用方配置。
- https://github.com/inovector/mixpost ：公开仓库为 MIT Lite，README 明确与 Pro/Enterprise 区分。X、YouTube 和 API 的具体版本能力需读取对应源码与版本文档，核验前不计入覆盖。
- https://github.com/Resinat/Resin ：支持账号粘性、平台隔离、HTTP/SOCKS5、持久绑定与健康检查；它管理已有代理资源，不提供住宅出口资源。优先使用显式 platform.account 标识，不从 Cookie/Authorization 自动提取敏感身份。
- https://github.com/biliup/biliup ：CLI 支持上传、代理、账号 Cookie、查询等；README 存在禁止商业用途的声明。用途和许可证冲突未澄清前保留受限候选状态。
- https://github.com/xpzouying/xiaohongshu-mcp ：候选小红书通道；需锁定版本核验发布、查询、账号隔离和代理。
- https://github.com/dreammis/social-auto-upload 、https://github.com/BadKid90s/Spreado 、https://github.com/hanliang97/MatrixMedia 、https://github.com/gitcoffee-os/postbot ：进入候选注册表，逐平台核验，不按项目宣传直接计算通道。
- https://github.com/renovatebot/renovate ：参考其依赖版本发现、分组和兼容性策略；版本发现与生产升级分离。
- https://github.com/theupdateframework/python-tuf ：参考更新元数据签名、有效期和防版本回退机制。初版不虚称实现完整 TUF。

旧文档星数、最近提交与许可证不直接沿用。选型依据优先为指定版本能力、部署可复现性、认证可维持性、查询能力、许可证及共同故障域。

## 3. 总体架构

Hub：FastAPI + SQLAlchemy/Alembic + PostgreSQL，Vue3/TypeScript/Element Plus，Caddy 对外 HTTPS。Hub 负责身份、素材、发布账本、调度和策略。Windows Agent 先在本机 E 盘落地；区域是节点标签，不能把同一物理节点标成两个真实网络区域。后续按实际节点能力增加海外 Agent。

Agent 通过出站 HTTPS 长轮询领取任务，具备独立身份、心跳、撤销、最小权限和并发限制。每个引擎使用独立进程、虚拟环境或容器；浏览器会话按账号独占。引擎接口不暴露公网。

开发阶段允许 SQLite 单 worker；正式多 Agent/并发环境统一 PostgreSQL，不将 SQLite 的验证结果等同于生产事务语义。暂不引入第二套任务队列，数据库任务账本是唯一事实来源。

## 4. 引擎与覆盖管理

每条 Channel 绑定引擎版本、平台、节点和部署配置；声明媒体类型、字段限制、认证方式、代理能力、查询能力、定时语义、配额依赖、故障域和并发。状态分 documented、installed、authenticated、live_verified。只有最后一种纳入自动路由。

初始优先验证：小红书 xhs-mcp/sau；视频号 sau/Spreado；B站 sau/biliup（受用途条件限制）；YouTube 官方 OAuth uploader/已核验的 sau；X 官方 API/Postiz（共享 API 故障域）。浏览器 X 作为后续受限候选，无法通过风控或额度限制时不自动规避。重型 MatrixMedia、postbot、Mixpost 逐项核验后扩展。

矩阵显示可用数与独立故障域数。两条通道共用账号、API 项目或网页流程时明确标注相关性。没有两条实测通道的平台诚实显示缺口。

## 5. 发布状态与幂等

Post 是内容版本；Target 固定平台、发布账号、媒体版本、可见性、时间和必需参数。Job、Attempt、Submission、Verification、AuditEvent 记录全过程。

任务状态：draft → validated → queued → leased → preparing → submitting → submitted → verifying → succeeded；分支为 retry_wait、needs_action、needs_verify、failed、cancelled。平台审核和可见性另建状态，不把上传成功等同公开可见。

Target 使用调用方幂等键与数据库唯一约束。重复入队返回原任务；显式再次发布必须新建发布意图。所有通道共享同一发布意图，attempt 不创建新意图。提交前落盘提交意图及执行代次；提交中丢响应、超时、进程退出一律视为结果未知，先回查，无法唯一确认则 needs_verify。

lease 带租约续期、截止时间与 generation；结果写回需比较 generation。lease 过期仅回收未提交任务，submitting 进入核验。外部平台缺少幂等支持时不承诺 exactly-once。

## 6. 路由与故障处理

先做能力、账号授权、出口、配额、版本兼容性硬过滤，再按运营优先级、独立故障域、健康度与可用并发排序。评分使用已定义的归一化值，不直接相乘任意量纲。

engine_missing、明确提交前崩溃允许同账号同出口换通道；提交后崩溃先核验。auth_expired 暂停对应授权，保留发布账号。rate_limited 遵守 Retry-After 和账号/平台预算。risk_control 暂停并提示必要动作，保留当前出口，不自动换号或换 IP。egress_unavailable 提交前可按受信策略换出口，提交后先核验。invalid_input 保留发布语义，必需字段不支持则明确拒绝；无损转换可自动进行。

健康按引擎实例、平台和账号授权分别维护。业务输入错误不计引擎熔断；认证错误只影响该授权；限流不误判版本损坏。熔断有样本窗口、半开探测和抖动退避。恢复后只影响新任务，旧任务不自动重放。

## 7. 账号、凭证与出口

账号固定归属，调度不擅自改变发布主体。每账号拥有多条独立 ChannelCredential；Cookie、OAuth refresh token、storage_state、Electron partition、扩展会话分别管理，转换需契约验证。凭证加密存储、按节点短期授权落盘、严格 ACL、使用后清理；浏览器 profile 需要持久时存入受控私密卷，禁止打入源码或安装包。

主密钥本机使用 Windows DPAPI 或受控密钥文件，服务器使用外部 secret；数据库含 key_id 支持轮换。备份与密钥分离并测试恢复。

Resin 是可替换 provider；提供 direct、trusted-static、resin 模式。每次发布固定 EgressBinding，记录实际探测出口与绑定代次。验证引擎主进程、上传子进程和浏览器实际走指定代理。单次任务中不随意改出口。没有可信备用时停止，禁用公共免费代理降级。TZ/locale 按账号配置一致性校验，不保证仅凭地区一致就能消除风控。

## 8. 自动更新系统

对象分 Hub、Agent、adapter、engine、browser/runtime，分别版本化。EngineVersion 保存来源、固定版本、平台、架构、适配器版本范围、认证格式、数据库要求与验收证据。

流水线：discover → available → download → verify_source → staged → offline_check → contract_check → canary → observe → promote；失败进入 rejected 或 rollback。更新默认自动发现和隔离下载；仅通过策略的兼容补丁允许自动灰度提升。大版本、凭证格式或不可逆迁移停留 needs_action，不用不确定的回滚承诺替代验证。

每日检查带随机抖动和 API 限流；关键组件有安全公告记录。下载仅允许登记上游和预期资产，限制大小、超时、压缩展开路径及架构，保留来源证据；发布方有签名则验证，无签名则标明信任等级。拒绝执行上游任意安装脚本和直接 latest 覆盖。

版本独立目录安装；活动版本指针原子切换。Job 固定 engine_version，旧版本排空后回收。灰度只使用明确配置的测试账号与测试素材，平台存在真实写入才算实测。观察至少 24 小时且满足最少真实样本；零流量不自动算通过。失败率、未知结果、认证失效、出口异常任一越界暂停提升。回滚只切后续任务，已提交任务独立核验。

数据库采用 expand/contract 兼容迁移，更新前备份并核验恢复；存在不可逆迁移时阻止自动降级。凭证迁移保留旧副本和版本标记。禁止直接用自动容器镜像更新替代此流程。

## 9. 安全与公网部署

单管理员用成熟 Argon2id/TOTP 库、不透明服务端会话、恢复码、登录节流、CSRF、Secure/HttpOnly/SameSite Cookie。初始化令牌一次性生成，无默认密码。Agent 只接受结构化任务，不开放任意 shell 远程执行接口。

素材上传限制大小、类型、磁盘预算；ffprobe/ffmpeg 必需时缺失就阻止任务。下载仅允许授权的素材对象与短期地址，校验重定向、解析地址和私网目标，防止 SSRF。日志去除 token、Cookie、代理密码；保留审计事件和输出分页。

生产对外仅 HTTPS，数据库、Resin、引擎控制口限私网/回环。浏览器 sandbox 默认启用；非管理员服务账号运行。当前连接使用 SYSTEM 只用于初始化，不沿用为产品默认运行身份。

## 10. 页面与可观测性

总览、素材库、内容与日历、发布任务详情、账号授权、平台通道矩阵、Agent、出口绑定、更新中心、设置与审计。界面显示真实阶段、最后核验时间、错误原因及可执行动作。SSE 携带游标支持补读，数据库事件为准。指标包含提交成功、未知结果、人工处理、排队延迟、租约失效、引擎版本、通道/故障域可用性。ntfy 可选，失败告警限频。

## 11. 实施与验收顺序

P0：完成独立目录、上游证据、环境清单与该设计。
P1：模型/迁移、任务账本、提交状态机、租约和审计、版本注册表；用故障注入验证重复请求、执行代次和结果未知保护。
P2：Agent 协议、单平台单通道真实闭环、授权与媒体校验；真实发布需要账号授权和明确测试素材，缺项显示 needs_action。
P3：同账号第二通道与查询回查；验证提交前崩溃可以切换、提交中断绝不重复提交。
P4：可信出口与逐进程验证，再扩展其余四平台；分别记录可用范围，不以 fake 覆盖代替实测。
P5：自动更新发现、并存安装、灰度、排空、失败回滚及恢复演练。
P6：Web 全流程、认证、Windows 非管理员服务与公网 TLS 部署；域名、服务器和外网线路按实际配置接入。
P7：可选 L2 引擎与多节点扩容，按能力与维护收益逐项接入。

核心验收：同请求重复入队只有一个 Target；旧 lease 不能写回；提交响应丢失进入核验；账号失效不换主体；同账号并发串行；出口中断不泄漏为直连；更新不截断旧任务；灰度失败不提升；重启恢复账本与绑定；数据库/凭证备份能真实恢复。单元和 fake 证明内部逻辑，live 证据单独记录。

## 12. 当前执行记录

已使用 SSH Relay 5.4 连接真实 Windows LAPTOP-MCMQHDN4 并核验身份。已在 E:\xxm 新建 OmniDispatch，三个子目录创建成功。现有 E:\项目计划 等目录未改动。当前是 P0，未宣称完成五平台发布、真实账号验收、引擎安装或公网部署。

## 2026-11-01：本机桌面与平台扩展的社区选型

产品运行在 E:\xxm\OmniDispatch，不采用云端托管。原树形布局、器官状态、细线留白与玫雾蜜珀配色保留，通过平台分组维持每屏五个平台与一条支撑枝。

社区核查同时看实际源码、依赖范围与返回证据：

| 项目 | 实际核查 | 采用方式 |
| --- | --- | --- |
| dreammis/social-auto-upload | 固定 3847fff01f5434a8a32829833163cd6723cabc59；MIT；源码有抖音、快手、百家号、微博、知乎等 CLI；Python >=3.10,<3.13 | 内置独立 3.12.10 与固定 wheels，适配 argv、账号会话和结构化结果，不与主程序 3.14 混用；不启用上游 B站隐式更新路径 |
| BadKid90s/Spreado | 固定 v1.2.0/9c96764d，版本内 MIT；实际加载 5 个插件。最新 main 的许可证已变更，不能混淆版本 | 保留固定源码与许可证；扩展抖音、快手，修复单文件漏插件；返回无作品 ID 时待核验 |
| wechatsync/Wechatsync | 固定 42f61e39，GPL-3.0；公开适配器不少是草稿，豆瓣代码为私密日记；部分 README 通道来自 private 适配器 | 用作协议与能力调研，不将 README 清单冒充可复用自动发布能力；没有复制其 GPL 适配器到本产品 |
| gitroomhq/postiz-app | AGPL-3.0，多服务与 OAuth 应用部署，海外平台聚合 | 保留候选，不为本机桌面初版引入额外云托管或不完整服务栈 |
| lumina37/aiotieba | 4.8.3 / Unlicense；当前 client 有读取、管理等接口，但未找到 add_thread/add_post/add_comment | 不把它当作贴吧发帖器；贴吧使用明确标注的桌面填写与确认流程 |
| xpzouying/xiaohongshu-mcp | v2.5.5 源码确认 /feeds/comment 与 /feeds/comment/reply | 接入评论和回复接口；校验账号、feed_id、xsec_token 和回复对象，缺返回 ID 时仍待核验 |

平台分“社区引擎执行”和“桌面填写、用户确认”两种。后者是实际本机浏览器：绑定独立账号登录态，打开指定编辑器或原帖，填写标题/正文、交付本任务素材，并记录真实作品/草稿链接；不会宣称全自动发布。草稿单独记 drafted，不能增加真实发布成功数。继续编辑草稿必须打开原草稿链接。

任务 action 为 publish/comment/reply，评论目标 URL 与回复 ID 保存在原任务。路由按 action 过滤；评论不能落到只会发新帖的引擎。不同动作分别记录核验证据，评论通过不能自动证明视频发布能力。未知提交不重放。

本轮覆盖登记 23 个平台。新增文字：贴吧、知乎、豆瓣、微博、公众号、头条号、简书、掘金、CSDN、百家号。新增视频：抖音、快手、西瓜、好看、腾讯视频、优酷、爱奇艺、搜狐视频，并保留 B站、小红书、视频号、YouTube、X。公众号不提供泛化的他人文章评论操作；平台网页没有相应编辑能力时不能由浏览器壳凭空补出 API。没有真实授权或实际作品证据时保持未核验，不计为已实测自动发布。

### 小红书浏览器自包含修复

社区 v2.5.5 强制下载 CloakBrowser，分发源在本机返回 403。固定源码 a5c8f7799980ba1fdd501999843eb2d17e4c9a9f，构建 v2.5.5-omni：显式使用随包标准 Chrome for Testing；关闭指纹参数、stealth 注入并移除 headless_browser 的 --no-sandbox。保留 HTTP API，不绕过平台登录或验证码。修改源码与 Apache-2.0 LICENSE、二进制摘要保存在 vendor/xhsmcp 与运行目录 source。脚本 install-xhs-browser.py 仅安装经摘要核对的本地构建，不再访问原 CDN。真实账号未发布。

实机安全软件拦截 Rod 默认的 leakless.exe 后，源码禁用 Leakless；未更改杀毒设置。浏览器退出由 Go 的正常 Close 与 OmniDispatch 原有 Windows Job Object 管理，登录后后台实例交给 supervisor 创建，避免游离子进程。

### 统一桌面比例

所有路由共用按窗口计算的 ui-scale，树图的内部 k 固定为 1，取消首页按内容自行放大与二级页强制缩放的不一致。首页和二级页主内容共用 1120px 基准宽度，统一标题、输入框与动作字阶；resize 只重排当前可见树，不重建表单。验证 check-proportions.py 覆盖三种窗口、八个页面、五组树和输入保留。

桌面 App 导航：固定同一导航条与选中状态、Alt+1…8 切换；新任务未提交内容与幂等意图暂存在当前窗口内存，跨页可恢复，不把授权字段持久化到浏览器存储。

## 2026-11-01 桌面工作台美学与交互重构

参考 Microsoft Fluent 2 Layout（https://fluent2.microsoft.design/layout）、Windows NavigationView（https://learn.microsoft.com/en-us/windows/apps/design/controls/navigationview）、WCAG 2.2 文本对比度（https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html）。采用固定导航与内容网格、4px 间距、渐进展开和明确的状态文本；图标采用 Lucide static 0.468.0 ISC，离线内嵌，完整许可见 THIRD-PARTY.md。Carbon 页面返回403，未把不可读取内容当作调研证据。

保留树、细线、玫雾蜜珀与有机状态图形；改用暖白和浅鼠尾草工作区，玫瑰色只用于焦点与品牌。首页围绕任务计数、下一步与平台发布网络；详细引擎放到平台通道页；任务表单使用标签、分组和主要按钮。固定字体不再随窗口整体缩小，窄窗口收起侧栏文字，内容自然重排。Ctrl+K 快速切换，保留 Alt+1…8、跨页任务草稿和当前任务幂等意图。不改变账号授权、核验门槛、后台调度和真实平台写入权限。
