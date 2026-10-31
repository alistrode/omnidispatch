# OmniDispatch 模型下载清单

**本项目不需要任何本地模型。**

OmniDispatch 是内容发布中枢，负责账号、任务账本、通道引擎与更新管理。全仓检索确认：
`omnidispatch/*.py`、`apps/web/`、`scripts/` 里**没有任何 Ollama / LLM 调用**（搜到的 `model` 全部是 `fullmatch` 正则）。

它的「本地依赖」是**内置 Python 运行时**，不是模型：

| 组件 | 位置 | 说明 |
|---|---|---|
| CPython 3.14.10 embeddable | `runtime\python.exe` | 官方 embeddable 包，见 `BUILD.json` |
| 33 个生产依赖 wheel | `runtime\Lib` | 清单见 `BUILD.json` 的 `wheel_files` |
| SQLite | `state\hub.db` | WAL 模式 |

本机 Ollama 与本项目**无关**，装了也不会被调用。
需要模型的是同组的 AgentHub / PromptLab / ResearchDesk，它们的模型清单见各自仓库的 `MODELS.md`。

## 外部引擎（非模型）

真正的「外置依赖」是发布引擎，不是模型，见 `engines.lock.json` 与 `DEPENDENCIES.md`：
ffprobe 5.1.0、resin v1.3.0、spreado v1.2.0、xhsmcp v2.5.5、ytuploader v1.25.5。
