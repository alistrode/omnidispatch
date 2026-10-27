# 第三方来源与边界

OmniDispatch 自有代码位于 omnidispatch、apps/web/src、scripts。生产依赖版本见 requirements.lock.txt 和 apps/web/package-lock.json；各 Python wheel 保留其 dist-info 许可证。Windows 运行时为官方 CPython 3.14.10 embeddable x64，保留其 LICENSE.txt。

FastAPI（MIT）、SQLAlchemy（MIT）、Vue（MIT）、Element Plus（MIT）、Vite（MIT）、httpx（BSD-3-Clause）、cryptography（Apache-2.0/BSD）、argon2-cffi（MIT）、pyotp（MIT）、psycopg（LGPL-3.0）属于外部依赖，以随包许可证为准。

外部发布引擎不属于自有源码。来源和固定发行版本见 engines.lock.json；许可核验未完成的项目不得作为商业可用承诺。biliup 上游 README 明确禁止商业用途；未确认用途前不启用。Spreado 当前 README 标注 MIT，与原需求清单 Apache-2.0 不一致，以锁定发行版本实际许可证为准。Postiz AGPL-3.0、MatrixMedia GPL、Mixpost Lite 与商业版能力分别处理。HTTP 分进程调用不自动免除各项目分发/修改时的许可证义务。

引擎安装器下载固定官方 GitHub Release/npm 产物，记录版本、URL 与大小；这不是上游数字签名验证，不声称提供完整软件供应链认证。OmniDispatch 自己的自动更新包采用独立受信 Ed25519 公钥验证，未配置公钥时禁止安装。
