# OmniDispatch 1.1.0-desktop 交付

目标仓库：https://github.com/alistrode/omnidispatch 。当前完整源码、有效维护脚本与补丁、原始测试依赖、自包含免安装运行包一起交付。

- 直接使用（推荐）：下载完整 Windows x64 运行包
  `https://github.com/alistrode/omnidispatch/releases/download/v1.1.0/OmniDispatch-Desktop-Windows-x64.zip`
  解压出 `OmniDispatch` 文件夹，双击其中的 `OmniDispatch.exe`。SHA-256 `211d6534fcec9d51ecb4d9a71da400e6178dad1692c79fa2c7412b7489367a4e`，见 packages/DOWNLOAD.md。
- 或者用仓库脚本：`Start-Packaged.cmd` 会先按 `packages/*.sha256` 核对，缺包时从同一 Release 下载，再解压启动。
- 开发：查看 DEPENDENCIES.md 与 `.agents/skills/omnidispatch/SKILL.md`；发行与下载验收流程见 `.agents/skills/omnidispatch-delivery/SKILL.md`。所有实际采用的版本、环境恢复和维护命令均有索引。
- 运行包为什么不进 Git：单文件 1.0 GB 超过 GitHub 100 MB 上限（Git LFS 免费额度也不够），因此作为 Release 附件发布；仓库只保留摘要、清单与源码。
- 当前运行包的真实数据不在仓库：state、授权、Cookie、私钥、原始日志、调试截图和构建缓存均排除。当前 SHA-256 与文件清单见 packages 和 DELIVERY-MANIFEST.json。
- 本轮下载回验记录见 VERIFICATION.md。旧 packages/OmniDispatch-0.1.0-windows.zip 只保留历史，不自动继承当前包的验收结论。

---

# OmniDispatch 桌面版

Windows 本机内容发布工作台。保留来源树、器官状态、细线与留白、玫雾和蜜珀配色；数据和凭证保存在本机，不依赖云端托管。

双击 `OmniDispatch.exe` 或 `Start.cmd`。关闭窗口收进系统托盘；托盘可重新打开或退出桌面窗口，后台任务继续。已有后台会复用，不重复初始化账号。新目录首次运行会初始化本地数据库和节点。完整目录包含 Python、生产依赖、浏览器运行时和引擎；不要只复制 EXE。

本机安装位置：`E:\xxm\OmniDispatch\release`。源码在 `dev`，备份在 `backups`。`release\state` 保存真实数据和密钥，禁止加入分发包。桌面浏览器缓存位于当前用户 `%LOCALAPPDATA%\OmniDispatch\WebView2`。

## 使用

1. 账号页建立固定发布账号。X 填用户 OAuth 令牌与用户 ID；YouTube 导入官方 OAuth 客户端 JSON、令牌 JSON 和频道 ID。
2. 通道页选择已安装版本，接入本机引擎。B站、小红书与视频号可从桌面扫码；选择具体账号，再导入登录态。每个账号使用独立目录，禁止按平台随机选账号。
3. 素材页上传图片或视频；重新选择同一文件可恢复分块上传。
4. 通道页点击「首次核验发布」，选择素材和必需平台参数后提交。首次核验允许明确指定尚未启用的通道，不绕过账号、节点、版本与素材检查。
5. 引擎返回真实作品 ID 才自动计成功。上游只返回“成功”但没有 ID 时，任务停在待核验；核对平台后填真实 ID 或明确确认未发布。未知结果不会自动重发。
6. 核验通过后启用通道，正常任务进入队列，支持定时、重试、取消和审计。

X 当前支持纯文本；小红书支持图片和单视频，其余已集成 CLI 使用单视频。注册表中的未实现候选不等于已接入。扫码、平台开发者授权和作品发布权限必须由真实账号完成，运行包不含这些凭证。

## 维护与恢复

本机后台任务名 `OmniDispatch-Hub-Agent`，Hub 仅监听回环 8791；桌面不会创建公网网站。退出桌面不终止正在处理的发布任务。配置通道不需要手工编辑 agent.json，节点自动重新读取配置。

更新前备份源码；升级保留 state。数据库备份使用内置 Python 执行 `-m omnidispatch.cli --state state backup`，vault.key 单独安全保管。不要通过删除状态目录解决普通故障。

开发：`dev\run-dev.cmd`；前端：`node apps\web\build.mjs`；测试：`dev\run-tests.cmd`；桌面编译：`desktop\build-desktop.ps1`。构建命令与依赖摘要见 desktop 目录及技能索引。真实发布验收与隔离测试结果分别记录。

## 平台扩展与评论

已登记 23 个平台，首页使用“原有平台／短视频／长视频／文字社区／写作平台”分组，仍是一屏来源树。贴吧、知乎、豆瓣、微博、公众号、头条号、简书、掘金、CSDN、百家号已加入；视频增加抖音、快手、西瓜、好看、腾讯视频、优酷、爱奇艺和搜狐视频。

任务可选择发布、评论原帖或回复指定评论。评论必须填写本平台原帖链接，回复还须指定评论 ID／楼层；不会把评论误发成独立文章。公众号没有泛化的“评论别人文章”通道，界面与后端会拒绝这种任务。

通道页明确区分“社区引擎执行”与“本机桌面确认”。后者打开账号独立的可见浏览器，辅助填入文字与素材，由你在真实平台网页确认提交，再记录作品链接；不是无人值守自动发布。没有编辑器或网页不提供评论功能时，软件不能凭空补出平台接口。所有新增通道默认未核验、未启用，真实账号许可与作品验收需要实际完成。

Spreado 与 social-auto-upload 用于已实现的视频上传路径，后者使用单独的 Python 3.12.10。X 与小红书的评论接口分别按实际 API 接入；小红书若只返回“成功”而没有评论 ID，仍会停在待核验。保存草稿记为 drafted，不会计为已发布；“继续编辑这份草稿”打开原稿链接，不新建另一篇。

社区选型的源码依据、版本、许可证与未采用原因见 DESIGN.md 的 2026-11-01 节。
