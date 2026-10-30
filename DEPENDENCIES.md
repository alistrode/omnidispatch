# 依赖清单

## 运行分发包 `omnidispatch-v0.1.0-win-x64.zip`

包内已含官方 Python 运行时与全部生产依赖，不需要系统 Python、不需要 pip 联网安装。

| 依赖 | 是否必须 | 说明 |
|---|---|---|
| Windows x64 | 必须 | 运行时为官方 CPython 3.14.10 embeddable x64 |
| 系统 Python | 不需要 | 包内 `runtime\python.exe`，`Start.cmd` 固定使用它 |
| .NET / Node | 不需要（运行期） | 前端已构建为静态产物 `omnidispatch\static\assets\` |
| 浏览器 | 必须 | 访问 `http://127.0.0.1:8791` |
| 外部发布引擎 | **按通道需要** | 见下节，不随包分发，需用 `scripts\engine-install.py` 安装 |
| 互联网 | 按功能需要 | 引擎安装、平台发布、更新源 |

## 一、内置 Python 运行时

| 项 | 值 |
|---|---|
| 版本 | CPython **3.14.10** embeddable amd64 |
| 来源 | `https://www.python.org/ftp/python/3.14.10/python-3.14.10-embed-amd64.zip` |
| 落位 | `runtime\`（1745 个文件，约 84.1 MB） |
| 许可证 | 保留官方 `runtime\LICENSE.txt` |
| 生产依赖 | 33 个 wheel，逐个列在 `BUILD.json` 的 `wheel_files` 字段 |

wheel 覆盖：FastAPI、Starlette、Uvicorn、Pydantic、SQLAlchemy、httpx、cryptography、argon2-cffi、pyotp、psycopg、python-multipart、pytest 等。
各 wheel 保留自身 dist-info 许可证。版本另见 `requirements.lock.txt` 与 `requirements-runtime.lock.txt`。

## 二、外部发布引擎（不随包分发，必须按清单安装）

这些是第三方可执行文件，**不放进本仓库与 Release**，因为上游许可各不相同（见 `THIRD-PARTY.md`）。
用 `runtime\python.exe scripts\engine-install.py` 按 `engines.lock.json` 锁定的版本安装。

| 引擎 | 锁定版本 | 包内相对路径（安装后） | 大小 | 上游 |
|---|---|---|---|---|
| ffprobe | 5.1.0 | `engines\ffprobe\5.1.0\ffprobe.exe` | 77.24 MB | FFmpeg |
| resin | v1.3.0 | `engines\resin\v1.3.0\resin.exe` | 36.51 MB | Resin 网关 |
| spreado | v1.2.0 | `engines\spreado\v1.2.0\spreado-windows-x64.exe` | 44.77 MB | dreammis/social-auto-upload |
| xhsmcp | v2.5.5 | `engines\xhsmcp\v2.5.5\xiaohongshu-mcp-windows-amd64.exe` | 14.89 MB | xpzouying/xiaohongshu-mcp |
| ytuploader | v1.25.5 | `engines\ytuploader\v1.25.5\youtubeuploader.exe` | 21.69 MB | youtubeuploader |

合计约 195.1 MB。完整来源仓库、Release 标签、published_at、每个资产的官方 URL 与字节数，全部记录在
仓库根的 `engines.lock.json`（`observed_date: 2026-10-27`）。

**许可证提示（摘自 THIRD-PARTY.md）**：外部引擎不属于自有源码，许可核验未完成的项目不得作为商业可用承诺；
biliup 上游 README 明确禁止商业用途，未确认前不启用；Spreado 实际许可证以其锁定发行版为准；
Postiz（AGPL-3.0）、MatrixMedia（GPL）分别处理。

## 三、构建期依赖（仅在从源码构建时需要）

| 依赖 | 版本/要求 |
|---|---|
| Python | 3.11+（构建）；运行时锁定 3.14.10 |
| Node.js + npm | 用于 `apps/web`（Vue 3 + Vite + Element Plus） |
| 后端依赖 | `pip install -r requirements.lock.txt` |
| 前端依赖 | `cd apps/web && npm ci` |

## 四、端口

| 端口 | 用途 |
|---|---|
| 8791 | Hub HTTP 服务（`Start.cmd` 打开 `http://127.0.0.1:8791`） |

## 五、环境变量

| 变量 | 用途 |
|---|---|
| `PYTHONUTF8` | `Start.cmd` 置 1，保证 UTF-8 |
| `OMNI_UPDATE_PUBLIC_KEY` | 部署侧 Ed25519 公钥；缺失时禁止安装更新包 |
| `OMNI_UPDATE_FEED_URL` | 同源 HTTPS 签名更新源 |
| `OMNI_AUTO_PROMOTE` | 置 1 仅自动提升策略允许且观察通过的补丁 |
| 数据库 URL | 默认 SQLite；正式并发节点可配 PostgreSQL |

## 六、不随包分发的内容（明确排除）

| 内容 | 原因 |
|---|---|
| `state\` | 含管理员凭证、resin 密钥、`vault.key`、`hub.db`，README 明确禁止打包 |
| `logs\` | 运行日志，可能含敏感信息 |
| `engines\` | 第三方二进制，许可各异，改由 `engines.lock.json` 清单按需安装 |
| `validation-tools\`（源码内） | vendored pytest/colorama/pygments 等测试工具，属第三方可下载内容 |
| `__pycache__` / `.pytest_cache` / `bin` / `obj` | 构建缓存 |
