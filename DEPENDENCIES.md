# 运行与开发依赖

## 免安装运行包

`OmniDispatch-Desktop-Windows-x64.zip`（约 1.0 GB）作为 GitHub Release 附件发布，不进 Git 对象；直链与摘要见 `packages/DOWNLOAD.md`、`packages/OmniDispatch-Desktop-Windows-x64.sha256`。下载后解压出整个 OmniDispatch 文件夹，再运行其中的 OmniDispatch.exe 或 Start.cmd；`Start-Packaged.cmd` 会自动下载、校验、解压并启动。原生 Windows x64，当前实机记录为 Windows 11；不冒充 Windows 10 或 Linux 验收。

包内包含 CPython 3.14.10、生产 Python 依赖、独立 CPython 3.12.10 社区环境、Microsoft WebView2 Fixed Runtime 156.0.4314.58、Chrome for Testing 156.0.8078.4 与当前实际接入的引擎。正常运行不要求系统另外安装 Python、浏览器、Go 或 Node。

Windows 自带的 .NET Framework 4.x / WinForms 和系统 DLL 属于操作系统基线。程序首次运行创建本机状态；已有账号凭证、数据库和私钥不分发。

版本、来源、摘要和许可：packages/manifests、desktop/*dependencies.json、engines.lock.json、vendor/*/BUILD.json、vendor/lucide/SOURCE.json、THIRD-PARTY.md。Spreado v1.2.0、SAU 3847fff 与小红书 v2.5.5-omni 的采用源码均保留。Lucide SVG 内嵌于前端，界面不依赖在线字体或图标 CDN。

## 开发环境

`scripts/delivery/start-packaged-app.ps1 -PrepareDevelopment` 从同一个完整运行包恢复 .runtime，并恢复 development/test-tools 中现有的原始测试依赖。它公开记录 python314._pth 所需的验证目录，不依赖未公开手工补丁；不会复制真实账号状态。

`run-dev.cmd`：隔离开发状态、8793 端口。`run-tests.cmd`：现有 Windows 测试。前端只需 Node 执行 `node apps/web/build.mjs`，不需要 npm 下载 UI 框架。原生外壳编译需要 Windows .NET Framework csc 与 desktop/vendor 中固定 WebView2 SDK 1.0.3537.50 DLL。社区源码重建另需 Go 1.24.13；当前预构建二进制已在运行包内，正常使用不需 Go。

历史 xhs-delta 补丁保留在 _build/xhs-delta，只用于对应旧摘要的回溯；当前运行包已包含修复，不要反复套用。当前引擎构建文件可从包内 engines/xhsmcp/v2.5.5-omni 恢复。

## 验证边界

当前包 SHA-256 见同目录 .sha256。Windows 现有 56 项后端测试、原生 13 路由、三种窗口的新界面检查通过；同一 ZIP 已从 GitHub 下载回验：单一解压文件夹内主 Python、首启数据库、本机 Hub、SAU 社区引擎、随包 Chromium 与原生窗口全部通过（记录见 VERIFICATION.md）。没有真实对外平台发帖；新通道仍需账号授权与真实核验。上传本身不重新赋予历史包验收结论。
