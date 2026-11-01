# 开发环境

本项目**不需要联网安装任何东西**。仓库自带一份可移植的 Python 运行时和全部依赖，
前端是零依赖的静态文件，`node build.mjs` 一条命令就能出包。

---

## 一、已经配好的东西

| 位置 | 是什么 |
| --- | --- |
| `dev\.runtime\` | 可移植 Python 3.14.10（84 MB）。`Lib\site-packages` 里是 `requirements-runtime.lock.txt` 的全部依赖 |
| `dev\.runtime\python314._pth` | 已把 `..`（也就是 `dev\`）和 `..\validation-tools` 加进搜索路径，所以 `import omnidispatch` 直接拿到**本目录的源码**，pytest 也在 |
| `dev\validation-tools\` | 仓库自带的 pytest 9.1.1（不打进发布包） |
| `dev\.state\` | 开发用的独立数据库，和 `release\state` 完全隔离 |
| `apps\web\` | 零依赖前端，`build.mjs` 只做文件拷贝 |

系统里的 `python` 是微软商店的占位符，`py -0p` 列出的 3.11 / 3.14 路径都已失效——
所以**不要用系统 Python**，一律走 `dev\.runtime\python.exe`。

## 二、三条命令

```bat
dev\run-dev.cmd        :: 起开发服务器 → http://127.0.0.1:8793（状态在 dev\_state）
dev\run-tests.cmd      :: 跑测试（当前 19 passed）
dev\build-web.cmd      :: 重新构建前端到 omnidispatch\static
```

第一次 `run-dev.cmd` 会自动 `init` 出管理员凭据，写在 `dev\_state\ADMIN-CREDENTIALS.private.txt`。
本机直连免口令（`/api/bootstrap`），所以通常用不到它。

## 三、手动跑

```bat
cd /d E:\xxm\OmniDispatch\dev
set PYTHONUTF8=1
set OMNI_STATE=E:\xxm\OmniDispatch\dev\_state
.runtime\python.exe -m omnidispatch.cli --state %OMNI_STATE% init
.runtime\python.exe -m omnidispatch.cli --state %OMNI_STATE% serve --port 8793
```

其它子命令：`status`、`backup`、`reset-admin`、`register-agent`。

## 四、前端

```bat
cd apps\web
node build.mjs
```

把 `index.html` / `app.css` / `app.js` 拷进 `omnidispatch\static\`，FastAPI 以
`StaticFiles(html=True)` 挂在 `/`，**不需要重启服务**，刷新浏览器即可。

需要 Node ≥ 18（本机 v26.4.0）。没有 `npm install`，没有 `node_modules`。

## 五、端口与状态

| 用途 | 端口 | 状态目录 |
| --- | --- | --- |
| 发布实例（`release\`） | 8791 | `release\state\hub.db` |
| 开发实例（`dev\`） | 8793 | `dev\_state\hub.db` |
| supervisor 锁 | 8792 | — |

两个实例的数据库完全独立，开发时怎么折腾都不会碰到线上那条。

## 六、依赖变更

改 `pyproject.toml` → 重新锁版本 → 重装。没有 pip 可用，做法是把 wheel 解包进
`.runtime\Lib\site-packages`（发布包的构建脚本 `scripts\build-portable.py` 就是这么做的）。
改完记得同步 `requirements-runtime.lock.txt`。

## 七、不要提交的

`.gitignore` 已排除 `.runtime/`、`_state/`、`validation-tools/`、`*.private*`、`*.pem`、`state/` 等。
`release\state` 里有私钥和令牌，永远不进仓库。
