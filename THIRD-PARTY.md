# 第三方来源与边界

OmniDispatch 自有代码位于 omnidispatch、apps/web/src、scripts。生产依赖版本见 requirements.lock.txt 和 apps/web/package-lock.json；各 Python wheel 保留其 dist-info 许可证。Windows 运行时为官方 CPython 3.14.10 embeddable x64，保留其 LICENSE.txt。

FastAPI（MIT）、SQLAlchemy（MIT）、Vue（MIT）、Element Plus（MIT）、Vite（MIT）、httpx（BSD-3-Clause）、cryptography（Apache-2.0/BSD）、argon2-cffi（MIT）、pyotp（MIT）、psycopg（LGPL-3.0）属于外部依赖，以随包许可证为准。

外部发布引擎不属于自有源码。来源和固定发行版本见 engines.lock.json；许可核验未完成的项目不得作为商业可用承诺。biliup 上游 README 明确禁止商业用途；未确认用途前不启用。Spreado 当前 README 标注 MIT，与原需求清单 Apache-2.0 不一致，以锁定发行版本实际许可证为准。Postiz AGPL-3.0、MatrixMedia GPL、Mixpost Lite 与商业版能力分别处理。HTTP 分进程调用不自动免除各项目分发/修改时的许可证义务。

引擎安装器下载固定官方 GitHub Release/npm 产物，记录版本、URL 与大小；这不是上游数字签名验证，不声称提供完整软件供应链认证。OmniDispatch 自己的自动更新包采用独立受信 Ed25519 公钥验证，未配置公钥时禁止安装。

## 桌面版新增组件

- Microsoft.Web.WebView2 1.0.3537.50，NuGet 官方包；Core/WinForms/Loader DLL。浏览器运行时来自微软官方 Fixed Version Runtime CAB，版本、下载来源与 SHA-256 在 desktop/WEBVIEW2-RUNTIME.json 记录，遵循 Microsoft 分发条款。
- Spreado v1.2.0，MIT，https://github.com/BadKid90s/Spreado ，固定源码 9c96764dca331bdea8656566a90956b6d89c1cfd；动态插件源码完整保留，examples 未分发。仅调整 Chromium sandbox 开启，移除上游 --no-sandbox 参数。上游 LICENSE 随源码与运行包保存。
- Playwright、playwright-stealth、greenlet、pyee、loguru、pytz：官方 PyPI wheel，固定版本、来源与 SHA-256 见 desktop/spreado-dependencies.json。沿用同版本的发布协议，不把插件加载检查等同真实作品发布。

- social-auto-upload，MIT，固定源码 3847fff01f5434a8a32829833163cd6723cabc59；完整采用的源代码、许可证和 Python 3.12.10 独立运行环境随项目保存。构建依赖版本、官方下载与 SHA-256 见 desktop/sau-dependencies.json、engines/sau/BUILD.json。集成 conf.py 和 omni_sau_cli.py 仅负责隔离工作目录与固定浏览器。
- Chrome for Testing 156.0.8078.4：官方分发，engines/browser/chromium-cft/BUILD.json 记录来源与摘要，用于本机可见浏览器工作流；不是浏览器扩展或云端中间站。
- Wechatsync、Postiz、aiotieba 仅用于社区选型和能力调研，本次没有把其源代码编入或分发在产品中。不能把它们的文档平台清单计为本产品已验证的发布能力。

- xiaohongshu-mcp v2.5.5-omni：上游 Apache-2.0，固定 a5c8f7799980ba1fdd501999843eb2d17e4c9a9f，自有修改与依赖 headless_browser v0.4.0 的修改源码、许可证、构建清单随 engines/xhsmcp/v2.5.5-omni/source 保存。使用标准 Chromium；不启用指纹伪装，不关闭浏览器 sandbox。

## Lucide 导航图标

Lucide static 0.468.0，来源 https://github.com/lucide-icons/lucide ，仅嵌入 15 个 SVG 图标，不依赖在线资源。固定包摘要与图标源文件见 vendor/lucide/SOURCE.json。完整 ISC 许可如下：

```text
ISC License

Copyright (c) for portions of Lucide are held by Cole Bemis 2013-2022 as part of Feather (MIT). All other copyright (c) for Lucide are held by Lucide Contributors 2022.

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

```
