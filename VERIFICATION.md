# 下载回验记录：1.1.0-desktop

本轮把运行包上传到 GitHub，再从 GitHub 实际下载回来，在包外的全新文件夹里解压并运行。本文只记录**实际执行过**的步骤与结果；没做的部分在最后一节列出。

## 一、交付物

| 项 | 值 |
| --- | --- |
| 仓库 | https://github.com/alistrode/omnidispatch |
| 源码提交 | `2b743f0`（release: OmniDispatch 1.1.0-desktop 完整源码与发行说明） |
| 发行版本 | tag `v1.1.0`，https://github.com/alistrode/omnidispatch/releases/tag/v1.1.0 |
| 运行包直链 | https://github.com/alistrode/omnidispatch/releases/download/v1.1.0/OmniDispatch-Desktop-Windows-x64.zip |
| 运行包 SHA-256 | `211d6534fcec9d51ecb4d9a71da400e6178dad1692c79fa2c7412b7489367a4e` |
| 运行包字节数 | `1090968422`（约 1.0 GiB） |
| GitHub 服务端摘要 | `sha256:211d6534fcec9d51ecb4d9a71da400e6178dad1692c79fa2c7412b7489367a4e`（Release API 的 `digest`） |

运行包不进入 Git 对象：GitHub 单文件上限 100 MB，Git LFS 免费额度也不够承载 1.0 GiB。它作为 Release 附件发布（单附件上限 2 GiB），仓库内保留 `packages/OmniDispatch-Desktop-Windows-x64.sha256`、`packages/manifests/` 与 `DELIVERY-MANIFEST.json`。

## 二、下载链路实测

```
curl -sSL --fail --retry 3 -o OmniDispatch-Desktop-Windows-x64.zip -D headers.txt <直链>
```

| 观测项 | 结果 |
| --- | --- |
| 状态码 | `302` → `200`（1 次重定向） |
| 重定向目标 | `release-assets.githubusercontent.com/github-production-release-asset/...` |
| 最终 `Content-Length` | `1090968422` |
| 最终 `Content-Disposition` | `attachment; filename=OmniDispatch-Desktop-Windows-x64.zip` |
| 最终 `Content-Type` | `application/octet-stream` |
| 实际下载 | 1 090 968 422 字节，用时 239 秒（约 4.5 MB/s），无重试 |
| 下载后 SHA-256 | `211d6534…67a4e`，与本地 `.sha256`、Release 服务端 `digest` 三者一致 |

点击直链即开始下载，不需要二次点击、不是 inline 预览。备用 Filebin 镜像本轮未启用（GitHub 直链可用）。

## 三、解压与运行环境

| 项 | 值 |
| --- | --- |
| 解压目标 | `E:\omniverify\unpacked`（包外新目录，解压前为空） |
| 解压结果 | 4425 个文件、约 1.8 GB，单一根目录 `OmniDispatch/` |
| 包内私有状态 | 无 `state/`、`logs/`、`cookies.json`（解压后立即确认） |
| 宿主机 | Windows 11 `10.0.26200`，x64，普通用户（非管理员） |
| 包内运行时 | CPython 3.14.10；独立 CPython 3.12.10；WebView2 固定运行时 156.0.4314.58；Chrome for Testing 156.0.8078.4 |

## 四、单文件夹自检结果（`scripts/verify-bundle.py`）

命令：

```powershell
.\OmniDispatch\runtime\python.exe repo\scripts\verify-bundle.py .\OmniDispatch 8797
```

退出码 `0`，`failures` 为空：

| 检查 | 结果 | 证据 |
| --- | --- | --- |
| `required_files` | PASS | 22/22 必需文件存在（EXE、运行时、`_pth`、site-packages、WebView2、SAU、Chromium、xhsmcp、许可） |
| `no_private_state_shipped` | PASS | 解压后包内无 `state/`、`logs/`、`cookies.json` |
| `bundled_python_import` | PASS | `python.exe` 为包内 3.14.10，`omnidispatch.__file__` 位于包内目录 |
| `first_run_init` | PASS | 首启创建 `state/hub.db` 与 `state/ADMIN-CREDENTIALS.private.txt` |
| `hub_boots` | PASS | `/api/health` → `{"ok":true,"product":"omnidispatch","version":"1.1.0-desktop","platform_count":23}` |
| `hub_serves_workbench` | PASS | `/?desktop=1` 200（5262 B）、`/app.js` 200（119 037 B）、`/app.css` 200（38 975 B） |
| `community_engine_cli` | PASS | 独立 Python 3.12 的 `omni_sau_cli.py --help` 正常，列出 zhihu/douyin |
| `bundled_chromium_render` | PASS | 随包 Chromium `--headless=new --dump-dom data:` 渲染出 `OmniLocalEngineCheck` / `local fixture` |
| `xhsmcp_engine_health` | PASS | 真实引擎 `xiaohongshu-mcp.exe` 在回环随机端口起服务，注册 18 个 MCP 工具，`/health` 200 `status: healthy` |
| `omni_browser_smoke_diagnostic` | WARN（不计入通过门槛） | 见第六节 |

## 五、原生窗口（WebView2）巡检

从下载包内直接启动原生窗口做只读巡检：

```powershell
.\OmniDispatch\OmniDispatch.exe --smoke
```

| 观测项 | 结果 |
| --- | --- |
| 退出码 / 用时 | `0` / 34 秒 |
| `desktop-check.json` | `success: true` |
| WebView2 版本 | `156.0.4314.58`（即包内固定运行时，不是系统 WebView2） |
| 路由巡检 | 13/13：`#/jobs`(15 控件)、`#/accounts`(5)、`#/assets`(1)、`#/agents`(2)、`#/updates`(5)、`#/audit`(0)、`#/settings`(5)、`#/c/biliup-bilibili`(11)、`#/?group=short|long|community|writing|core`(各 11) |
| 前端运行时错误 | `errors: []` |
| 视口 / 来源树 | 1404 × 845，"leaves": 5 |
| 截图 | 由程序写入 `%LOCALAPPDATA%\OmniDispatch\Diagnostics\desktop-preview.png`（含本机账号数量等私有状态，未入库） |
| 启动轨迹 | `boot → service-ready → browser-environment → browser-initialize → browser-ready → navigate → page-loaded` |

## 六、未计入通过门槛的项与判定

`omni-browser-smoke.exe`（go-rod 诊断程序）本轮多次返回 `panic: unexpected browser result`（退出码 2）。判定为**宿主执行环境问题，不是包或上传问题**，依据：

1. 该诊断程序在下载包内与现有生产安装 `E:\xxm\OmniDispatch\release` 内**逐字节相同**（SHA-256 `3d7fb498abdfa879ee3e232be116cb530e16e90d4df362fb0811f15879b167cb`），伴随的 Chromium 目录 306 个文件也逐个 SHA-256 相同。
2. 用现有生产安装里的同一程序、同一 Chromium 复跑，结果同样失败（2/2），与下载包表现一致。
3. Chromium 本身可用：包内 `chrome.exe` 直接渲染 `data:` 页面成功（见第四节），真实小红书引擎 `xiaohongshu-mcp.exe` 启动并 `/health` 200（18 个 MCP 工具）。
4. 失败时 Chromium 日志出现 `Sandbox cannot access executable … (0x5)` 与 `Network service crashed or was terminated`，即 Chromium 自身子进程沙箱在受限进程上下文里偶发起不来；同一会话早前多次通过、机器负载升高后连续失败，与路径、卷、工作目录无关（在 E:、D:、系统临时目录、包内包外都复现过）。

因此 `scripts/verify-bundle.py` 把它标为 informational，硬检查改用 Chromium 直接渲染与真实引擎 `/health`。人工复核方式：在正常桌面会话（不在受限/沙箱进程树里）运行 `scripts/check-xhs-engine.py`。

## 七、已知边界

- 端口 `8791` 在本机被既有安装（另一个 Windows 账户下的 `OmniDispatch-Hub-Agent`，停止需要管理员）占用，因此原生窗口巡检复用已运行的本机服务；包内后端"首次运行自行启动 Hub"这条路径由第四节在 `8797` 端口独立验证（同一套包内解释器与代码）。
- 本轮没有对任何真实平台发起发布，也没有使用真实账号授权；新通道仍需账号授权与真实核验。
- 本轮未在 Windows 10、Linux 或独立云主机上执行；宿主为 Windows 11 本机。
- `packages/OmniDispatch-0.1.0-windows.zip` 只保留历史，不继承本记录的验收结论。

## 八、复现命令

```powershell
$url='https://github.com/alistrode/omnidispatch/releases/download/v1.1.0/OmniDispatch-Desktop-Windows-x64.zip'
curl.exe -L -o OmniDispatch-Desktop-Windows-x64.zip $url
(Get-FileHash .\OmniDispatch-Desktop-Windows-x64.zip -Algorithm SHA256).Hash.ToLower()
# 211d6534fcec9d51ecb4d9a71da400e6178dad1692c79fa2c7412b7489367a4e
Expand-Archive .\OmniDispatch-Desktop-Windows-x64.zip -DestinationPath .\fresh
git clone --depth 1 https://github.com/alistrode/omnidispatch.git repo
.\fresh\OmniDispatch\runtime\python.exe repo\scripts\verify-bundle.py .\fresh\OmniDispatch 8797
.\fresh\OmniDispatch\OmniDispatch.exe --smoke
```
