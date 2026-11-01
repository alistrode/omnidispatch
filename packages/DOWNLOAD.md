# 下载：自包含免安装运行包

版本 `1.1.0-desktop` · Windows x64 · 约 1.0 GB · 解压后约 1.8 GB

## 一键直链

https://github.com/alistrode/omnidispatch/releases/download/v1.1.0/OmniDispatch-Desktop-Windows-x64.zip

- 这是 GitHub Release 附件直链；请求会 302 到 `objects.githubusercontent.com`，最终响应带 `Content-Disposition: attachment`，浏览器点击即开始下载，不需要再点第二个按钮。
- SHA-256：`211d6534fcec9d51ecb4d9a71da400e6178dad1692c79fa2c7412b7489367a4e`
- 字节数：`1090968422`
- 同目录还发布 `OmniDispatch-Desktop-Windows-x64.sha256` 附件，与仓库内同名文件内容一致。

## 下载 → 校验 → 解压 → 运行

```powershell
$url='https://github.com/alistrode/omnidispatch/releases/download/v1.1.0/OmniDispatch-Desktop-Windows-x64.zip'
Invoke-WebRequest $url -OutFile OmniDispatch-Desktop-Windows-x64.zip
(Get-FileHash .\OmniDispatch-Desktop-Windows-x64.zip -Algorithm SHA256).Hash.ToLower()
# 期望 211d6534fcec9d51ecb4d9a71da400e6178dad1692c79fa2c7412b7489367a4e
Expand-Archive .\OmniDispatch-Desktop-Windows-x64.zip -DestinationPath .
.\OmniDispatch\OmniDispatch.exe
```

等价写法：`curl.exe -L -o OmniDispatch-Desktop-Windows-x64.zip $url`。

或者直接用仓库脚本 `Start-Packaged.cmd`：缺包时从同一 Release 下载，按 `packages/OmniDispatch-Desktop-Windows-x64.sha256` 校验，再解压到 `.runtime-cache/packaged-app` 并启动。

## 运行要求

- Windows x64（本轮实机验收为 Windows 11）；系统自带 .NET Framework 4.x / WinForms。
- 解压出的 `OmniDispatch` 文件夹放在本机任意可写 NTFS 目录；不要只复制其中的 EXE。
- 不需要另装 Python、浏览器、Go 或 Node；包内自带 CPython 3.14.10、独立 CPython 3.12.10、WebView2 固定运行时 156.0.4314.58、Chrome for Testing 156.0.8078.4 与全部生产依赖。
- 首次运行在包内 `state/` 建立本机数据库，并写出 `state/ADMIN-CREDENTIALS.private.txt` 初始口令文件。
- 本机服务只监听 `127.0.0.1:8791`，不建公网站点；关闭窗口收进系统托盘，后台任务继续。

## 单文件夹自检

把包内解释器当作干净环境的唯一运行时来验证（脚本来自本仓库 `scripts/verify-bundle.py`，与运行包解压目录并列放置）：

```powershell
git clone --depth 1 https://github.com/alistrode/omnidispatch.git repo
.\OmniDispatch\runtime\python.exe repo\scripts\verify-bundle.py .\OmniDispatch 8795
```

全部通过时退出码为 0，并写出 `verify-report.json`。本轮从 GitHub 实际下载后的结果记录在 `VERIFICATION.md`。
原生窗口（WebView2 固定运行时）另用 `.\OmniDispatch\OmniDispatch.exe --smoke` 巡检，报告写入 `%LOCALAPPDATA%\OmniDispatch\Diagnostics`。

## 镜像

主下载为 GitHub Release 附件。Filebin 备用镜像仅在 GitHub 附件不可用时按需生成，生成后必须用同一 SHA-256 校验；本轮 GitHub 直链可用，未启用备用镜像。
