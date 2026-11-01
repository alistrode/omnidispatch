---
name: omnidispatch-delivery
description: Publish the OmniDispatch desktop bundle and sources to GitHub, then verify the downloaded artifact in a clean folder.
---
给本仓库做发行时读这一份。它不是产品使用说明，而是"把包传上去、再把包拉下来证明能用"的操作索引。
产品本身的命令索引在 `.agents/skills/omnidispatch/SKILL.md`。

## 目标与边界

- 仓库：https://github.com/alistrode/omnidispatch ；发行附件放在 GitHub Releases（单附件上限 2 GiB）。
- 源码进 Git；1.0 GB 运行包**不进 Git**（单文件上限 100 MB，Git LFS 免费额度也不够）→ 作为 `v1.1.0` 的 Release 附件发布。
- 私钥、`state/`、Cookie、原始日志、`_state/`、`.runtime-cache/` 一律不进仓库、不进包。

## 上行（发布）

```powershell
gh auth status                                             # 必须是能写 alistrode/omnidispatch 的账号
gh repo view alistrode/omnidispatch --json defaultBranchRef
# 源码
git -C <checkout> add -A; git -C <checkout> commit -m "release: 1.1.0-desktop"
git -C <checkout> push origin main
# 附件（releases/download/v1.1.0/ 是成品链接，不要手工改名）
gh release create v1.1.0 <bundle.zip> <bundle.sha256> -R alistrode/omnidispatch --title "OmniDispatch v1.1.0" --notes-file <notes.md>
```

同名附件已存在时用 `gh release upload v1.1.0 <file> --clobber -R alistrode/omnidispatch`。
脚本入口：`scripts/delivery/prepare-desktop-upload.py`（整理本地待上传树）、`scripts/delivery/start-packaged-app.ps1`（先校验摘要再解压启动，缺包时自动从 Release 下载）。

## 下行（验收，必须先做）

交付门槛是"下载回来后，单个文件夹能直接运行"，不能靠任何未公开的人工修补。
**必须在包外的干净目录做，并且目录所在卷不能带沙箱/继承限制 ACL**（Chrome 沙箱会报
`Sandbox cannot access executable`，那是卷的 ACL 问题，不是包的问题）：

```powershell
# 1) 下载 → 摘录校验
Invoke-WebRequest -Uri https://github.com/alistrode/omnidispatch/releases/download/v1.1.0/OmniDispatch-Desktop-Windows-x64.zip -OutFile .\bundle.zip
(Get-FileHash .\bundle.zip -Algorithm SHA256).Hash.ToLower()   # 必须等于 packages/*.sha256
# 2) 全新文件夹解压（解压后自检目录必须为空）
Expand-Archive .\bundle.zip -DestinationPath .\fresh
# 3) 包内解释器跑自检（28 项必需文件 + 首启初始化 + Hub + 社区引擎 + 随包 Chromium）
.\fresh\OmniDispatch\runtime\python.exe .\fresh\OmniDispatch\..\..\scripts\verify-bundle.py .\fresh\OmniDispatch 8795
# 4) 原生窗口（WebView2 固定运行时）只读巡检：13 条路由、截图、无 JS 错误
.\fresh\OmniDispatch\OmniDispatch.exe --smoke
#    报告：%LOCALAPPDATA%\OmniDispatch\Diagnostics\desktop-check.json 与 desktop-preview.png
```

自检脚本：`scripts/verify-bundle.py`（本仓库，纯标准库，只用包内解释器）。
原生巡检脚本：`scripts/check-desktop.ps1`；比例与工作台专项：`scripts/check-proportions.py`、`scripts/check-design-workspace.py`。
验收记录写在 `VERIFICATION.md`，其中必须包含下载 URL、SHA-256、解压目录、逐项结果与未覆盖项。

## 下载链接交付格式

- 直接给成品：`https://github.com/alistrode/omnidispatch/releases/download/v1.1.0/OmniDispatch-Desktop-Windows-x64.zip`（会 302 到 objects.githubusercontent.com，带 `Content-Disposition: attachment`，点击即下载）。
- 备用镜像：Filebin（`POST https://filebin.net/{bin-id}/{file}`，正文直接发二进制，不用 multipart），失效前重新上传并更新 `packages/DOWNLOAD.md`。
- 交付前用 `curl -sI -L` 确认最终响应是 `attachment` 且 `Content-Length` 与本地一致。

## 常见拒绝项

- 把 ZIP 塞进 Git 或 Git LFS：超过 100 MB 单文件上限，LFS 免费额度 1 GB 也会被一次占满。
- 只给仓库链接、不给附件直链：用户点不到下载。
- 用 `_state`、`release/state` 里的真实数据当验收证据：那是本机私有状态，不能分发也不能当干净环境证明。
- 在带 `CodexSandboxUsers` 之类继承 ACE 的卷上跑 `omni-browser-smoke.exe`：Chromium 沙箱会拒绝启动，误判为包坏了。
