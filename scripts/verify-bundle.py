"""单文件夹自检：把已解压的运行包当作全新机器，验证它能自己启动。

用法：<解压目录>/runtime/python.exe scripts/verify-bundle.py <解压目录>/OmniDispatch [端口]

只做本机检查，不访问任何平台、不发布、不写真实账号状态：
  1. 必需文件齐全，且包内不含 state/logs/cookies.json；
  2. 包内解释器导入 omnidispatch 并创建 app，确认模块来自包内；
  3. 首次运行初始化数据库（写到包内 state/）；
  4. 用包内解释器在指定端口启动本机 Hub，检查 /api/health、工作台 HTML、app.js、app.css；
  5. 独立 Python 3.12 社区引擎 CLI 能列出平台；
  6. 随包标准 Chromium 能在 data: 本地页面启动。

输出一份 JSON 报告，全部通过才返回 0。参数与检查项和 CI/人工验收使用同一套。
"""
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

argv = sys.argv[1:]
root = Path(argv[0]).resolve()
port = int(argv[1]) if len(argv) > 1 else 8795
report = {"bundle": str(root), "port": port, "checks": {}, "failures": []}


def record(name, ok, detail):
    report["checks"][name] = {"ok": bool(ok), "detail": detail}
    if not ok:
        report["failures"].append(name)
    print(("PASS " if ok else "FAIL ") + name + ": " + str(detail), flush=True)


REQUIRED = [
    "OmniDispatch.exe",
    "Start.cmd",
    "WebView2Loader.dll",
    "Microsoft.Web.WebView2.Core.dll",
    "runtime/python.exe",
    "runtime/python314.zip",
    "runtime/python314._pth",
    "runtime/Lib/site-packages",
    "desktop/webview2-runtime/msedgewebview2.exe",
    "omnidispatch/app.py",
    "omnidispatch/static/index.html",
    "omnidispatch/static/app.js",
    "omnidispatch/static/app.css",
    "engines.lock.json",
    "engines/sau/runtime/python.exe",
    "engines/sau/runtime/python312.zip",
    "engines/sau/source/omni_sau_cli.py",
    "engines/browser/chromium-cft/chrome-win64/chrome.exe",
    "engines/xhsmcp/v2.5.5-omni/xiaohongshu-mcp.exe",
    "engines/xhsmcp/v2.5.5-omni/xiaohongshu-login.exe",
    "engines/xhsmcp/v2.5.5-omni/omni-browser-smoke.exe",
    "THIRD-PARTY.md",
]

missing = [p for p in REQUIRED if not (root / p).exists()]
record("required_files", not missing, f"missing={missing}" if missing else f"{len(REQUIRED)}/{len(REQUIRED)} present")

shipped = [name for name in ("state", "logs", "cookies.json") if (root / name).exists()]
record("no_private_state_shipped", not shipped, f"unexpected={shipped}" if shipped else "no state/, logs/ or cookies.json in the archive")

env = {**os.environ, "PYTHONUTF8": "1"}

probe = subprocess.run(
    [str(root / "runtime/python.exe"), "-c",
     "import sys,json,omnidispatch;from omnidispatch.app import create_app;"
     "print(json.dumps({'exe':sys.executable,'version':sys.version.split()[0],"
     "'package':str(omnidispatch.__file__),'app':bool(create_app)}))"],
    cwd=str(root), capture_output=True, text=True, timeout=180, env=env,
)
if probe.returncode:
    record("bundled_python_import", False, probe.stderr.strip()[-800:])
else:
    info = json.loads(probe.stdout.strip().splitlines()[-1])
    inside = Path(info["package"]).resolve().is_relative_to(root)
    record("bundled_python_import", inside and info["exe"].lower().startswith(str(root).lower()),
           {"python": info["version"], "interpreter": info["exe"], "imported_from_bundle": inside})

state = root / "state"
if state.exists():
    shutil.rmtree(state)
init = subprocess.run([str(root / "runtime/python.exe"), "-m", "omnidispatch.cli", "--state", str(state), "init"],
                      cwd=str(root), capture_output=True, text=True, timeout=240, env=env)
record("first_run_init", init.returncode == 0 and (state / "hub.db").exists(),
       {"returncode": init.returncode, "hub_db": (state / "hub.db").exists(), "stderr": init.stderr.strip()[-400:]})

log = open(root / "verify-hub.log", "wb")
server = subprocess.Popen([str(root / "runtime/python.exe"), "-m", "omnidispatch.cli", "--state", str(state), "serve", "--host", "127.0.0.1", "--port", str(port)],
                          cwd=str(root), env=env, stdout=log, stderr=subprocess.STDOUT)


def fetch(path, timeout=3):
    with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=timeout) as response:
        return response.status, response.read()


health = None
for _ in range(90):
    if server.poll() is not None:
        break
    try:
        status, body = fetch("/api/health")
        health = json.loads(body)
        break
    except (urllib.error.URLError, ConnectionError, OSError, ValueError):
        time.sleep(1)

if health is None:
    log.close()
    tail = (root / "verify-hub.log").read_text("utf-8", "replace")[-800:]
    server.kill()
    record("hub_boots", False, f"no /api/health answer; log={tail}")
else:
    record("hub_boots", health.get("ok") is True and health.get("product") == "omnidispatch", health)
    paths = ["/?desktop=1", "/app.js", "/app.css"]
    detail = {}
    ok = True
    for path in paths:
        try:
            status, body = fetch(path)
            detail[path] = {"status": status, "bytes": len(body)}
            ok = ok and status == 200 and len(body) > 500
        except Exception as error:  # noqa: BLE001
            detail[path] = repr(error)
            ok = False
    record("hub_serves_workbench", ok, detail)
    server.terminate()
    try:
        server.wait(timeout=30)
    except subprocess.TimeoutExpired:
        server.kill()
    log.close()

sau = subprocess.run([str(root / "engines/sau/runtime/python.exe"), str(root / "engines/sau/source/omni_sau_cli.py"), "--help"],
                     cwd=str(root), capture_output=True, timeout=180, env={**env, "OMNI_SAU_WORK": str(root / "state" / "sau-check")})
out = sau.stdout.decode("utf-8", "replace")
record("community_engine_cli", sau.returncode == 0 and "zhihu" in out and "douyin" in out,
       {"returncode": sau.returncode, "stderr": sau.stderr.decode("utf-8", "replace")[-400:]})

smoke = subprocess.run([str(root / "engines/xhsmcp/v2.5.5-omni/omni-browser-smoke.exe")], cwd=str(root), capture_output=True, timeout=180,
                       env={**env, "OMNI_XHS_BROWSER": str(root / "engines/browser/chromium-cft/chrome-win64/chrome.exe")})
sout = smoke.stdout.decode("utf-8", "replace")
record("bundled_chromium_smoke", smoke.returncode == 0 and '"bundled_standard_chromium":true' in sout.replace(" ", ""),
       {"returncode": smoke.returncode, "stdout": sout.strip()[-400:], "stderr": smoke.stderr.decode("utf-8", "replace")[-600:]})

report["ok"] = not report["failures"]
Path(os.environ.get("OMNI_VERIFY_REPORT", str(root / "verify-report.json"))).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"ok": report["ok"], "failures": report["failures"]}, ensure_ascii=False))
sys.exit(0 if report["ok"] else 1)
