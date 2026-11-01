"""Stage current source and its existing self-contained package for GitHub Desktop.
Only local files are copied. This command never commits, pushes, or reads credentials.
"""
import argparse,datetime,hashlib,json,os,shutil,subprocess,zipfile
from pathlib import Path
ARCHIVE='OmniDispatch-Desktop-Windows-x64.zip'
SKIP_DIRS={'.git','.runtime','.runtime-cache','_state','.delivery','__pycache__','.pytest_cache','node_modules','validation-tools','.venv','state','logs','backups'}
STALE_PREFIXES=('apps/web/src/','apps/web/dist/','omnidispatch/static/assets/')
STALE_FILES={'apps/web/vite.config.ts','apps/web/tsconfig.json','apps/web/package-lock.json','scripts/delivery/reopen-github-desktop.ps1'}
def sha(path):
    with Path(path).open('rb') as file:return hashlib.file_digest(file,'sha256').hexdigest()
def allowed(rel):
    text=rel.as_posix();low=text.lower()
    if any(part in SKIP_DIRS for part in rel.parts) or text.startswith(STALE_PREFIXES) or text in STALE_FILES:return False
    if text.startswith('_build/') and not text.startswith('_build/xhs-delta/'):return False
    if '.private' in low or rel.name=='.env' or 'admin-credentials' in low:return False
    if rel.suffix.lower() in {'.pyc','.pyo','.log','.db','.sqlite','.sqlite3','.key','.pfx','.p12','.pem'}:return False
    if rel.name.lower() in {'cookies.json','agent.json','runtime-settings.json','vault.key'}:return False
    return True

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--checkout');p.add_argument('--prepare-only',action='store_true');args=p.parse_args();root=Path(args.root).resolve();source=root/'dev';release=root/'release'
    entries=[(file,file.relative_to(source)) for file in source.rglob('*') if file.is_file() and allowed(file.relative_to(source))]
    archive=release/ARCHIVE;expected=(archive.with_suffix('.sha256')).read_text().split()[0]
    if sha(archive)!=expected:raise ValueError('Current runtime package checksum mismatch')
    with zipfile.ZipFile(archive) as z:
        assert not any('/state/' in n or '/logs/' in n or 'cookies.json' in n for n in z.namelist())
    if not args.checkout:
        print(json.dumps({'source_files':len(entries),'source_bytes':sum(file.stat().st_size for file,_ in entries),'archive':ARCHIVE,'archive_bytes':archive.stat().st_size,'sha256':expected,'private_state_excluded':True}));return
    checkout=Path(args.checkout).resolve()
    if not args.prepare_only and not (checkout/'.git').exists():raise ValueError('Use an existing GitHub Desktop checkout')
    checkout.mkdir(parents=True,exist_ok=True)
    if checkout==source or not checkout.is_relative_to(source/'.delivery'):raise ValueError('Delivery checkout must be isolated under dev/.delivery')
    copied=set()
    for file,rel in entries:
        target=checkout/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(file,target);copied.add(rel.as_posix())
    # Preserve original small dependency files and licenses; omit compiled caches.
    testroot=source/'validation-tools'
    for file in testroot.rglob('*'):
        rel=file.relative_to(testroot)
        if file.is_file() and '__pycache__' not in rel.parts and file.suffix.lower() not in {'.pyc','.pyo'}:
            dest=Path('development/test-tools')/rel;target=checkout/dest;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(file,target);copied.add(dest.as_posix())
    packages=checkout/'packages';packages.mkdir(exist_ok=True)
    target=packages/ARCHIVE
    if not target.exists() or sha(target)!=expected:shutil.copy2(archive,target)
    if sha(target)!=expected:raise ValueError('Staged distribution differs')
    shutil.copy2(archive.with_suffix('.sha256'),packages/(archive.stem+'.sha256'))
    manifests=['BUILD.json','BUILD-DESKTOP.json','desktop/WEBVIEW2-RUNTIME.json','engines/browser/chromium-cft/BUILD.json','engines/sau/BUILD.json','engines/xhsmcp/v2.5.5-omni/BUILD.json']
    manifest_files=[]
    for name in manifests:
        file=release/name
        if file.is_file():
            dest=packages/'manifests'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(file,dest);manifest_files.append(dest.relative_to(checkout).as_posix())
    (checkout/'.gitattributes').write_text('packages/'+ARCHIVE+' filter=lfs diff=lfs merge=lfs -text\n',encoding='utf-8')
    (checkout/'.gitignore').write_text('''__pycache__/
*.py[cod]
.pytest_cache/
.venv/
node_modules/
.runtime/
.runtime-cache/
_state/
.delivery/
validation-tools/
state/
logs/
backups/
/engines/
*.db
*.db-*
*.sqlite*
.env
*.private*
*.pem
*.key
*.pfx
*.p12
*.log
*.zip
!packages/*.zip
_build/xhsmcp/
apps/web/dist/
''',encoding='utf-8')
    # Remove superseded tracked source, preserving old packages and Git history.
    git=Path('C:/Program Files/Git/cmd/git.exe')
    tracked=[] if args.prepare_only else subprocess.run([str(git),'-C',str(checkout),'ls-files','-z'],capture_output=True,check=True).stdout.decode('utf-8').split('\0')
    retained={'README.md','DEPENDENCIES.md','SKILL.md','BUILD.json','.gitattributes','.gitignore'}
    for name in tracked:
        if not name or name in copied or name in retained or name.startswith('packages/'):continue
        file=checkout/name
        if file.is_file():file.unlink()
    (checkout/'SKILL.md').write_text('# OmniDispatch 维护入口\n\n项目命令、修复与交付索引：`.agents/skills/omnidispatch/SKILL.md`。上传标准：`.agents/skills/workspace-backup-dev/SKILL.md`。\n',encoding='utf-8')
    build=json.loads((release/'BUILD-DESKTOP.json').read_text());build['distribution']={'path':'packages/'+ARCHIVE,'sha256':expected,'storage':'Git LFS'};build['historical_packages_are_not_revalidated']=True
    (checkout/'BUILD.json').write_text(json.dumps(build,ensure_ascii=False,indent=2),encoding='utf-8')
    test_files=[x for x in copied if x.startswith('development/test-tools/')]
    (checkout/'DEPENDENCIES.md').write_text('''# 运行与开发依赖

## 免安装运行包

`packages/OmniDispatch-Desktop-Windows-x64.zip` 采用 Git LFS；GitHub Desktop 克隆/拉取后须取得完整对象，不能拿 LFS 文本指针当运行包。解压整个 OmniDispatch 文件夹，再运行其中的 OmniDispatch.exe 或 Start.cmd。原生 Windows x64，当前实机记录为 Windows 11；不冒充 Windows 10 或 Linux 验收。

包内包含 CPython 3.14.10、生产 Python 依赖、独立 CPython 3.12.10 社区环境、Microsoft WebView2 Fixed Runtime 156.0.4314.58、Chrome for Testing 156.0.8078.4 与当前实际接入的引擎。正常运行不要求系统另外安装 Python、浏览器、Go 或 Node。

Windows 自带的 .NET Framework 4.x / WinForms 和系统 DLL 属于操作系统基线。程序首次运行创建本机状态；已有账号凭证、数据库和私钥不分发。

版本、来源、摘要和许可：packages/manifests、desktop/*dependencies.json、engines.lock.json、vendor/*/BUILD.json、vendor/lucide/SOURCE.json、THIRD-PARTY.md。Spreado v1.2.0、SAU 3847fff 与小红书 v2.5.5-omni 的采用源码均保留。Lucide SVG 内嵌于前端，界面不依赖在线字体或图标 CDN。

## 开发环境

`scripts/delivery/start-packaged-app.ps1 -PrepareDevelopment` 从同一个完整运行包恢复 .runtime，并恢复 development/test-tools 中现有的原始测试依赖。它公开记录 python314._pth 所需的验证目录，不依赖未公开手工补丁；不会复制真实账号状态。

`run-dev.cmd`：隔离开发状态、8793 端口。`run-tests.cmd`：现有 Windows 测试。前端只需 Node 执行 `node apps/web/build.mjs`，不需要 npm 下载 UI 框架。原生外壳编译需要 Windows .NET Framework csc 与 desktop/vendor 中固定 WebView2 SDK 1.0.3537.50 DLL。社区源码重建另需 Go 1.24.13；当前预构建二进制已在运行包内，正常使用不需 Go。

历史 xhs-delta 补丁保留在 _build/xhs-delta，只用于对应旧摘要的回溯；当前运行包已包含修复，不要反复套用。当前引擎构建文件可从包内 engines/xhsmcp/v2.5.5-omni 恢复。

## 验证边界

当前包 SHA-256 见同目录 .sha256。Windows 现有 56 项后端测试、原生 13 路由、三种窗口的新界面检查通过；基包曾独立解压检查主 Python、SAU CLI 和小红书浏览器，新界面包随后保持运行时字节不变并重新校验完整 ZIP 与界面文件。没有真实对外平台发帖；新通道仍需账号授权与真实核验。上传本身不重新赋予历史包验收结论。本轮并未执行“云端 Windows 全新单文件夹 GUI”验收，不能声称百分百全平台通过。
''',encoding='utf-8')
    readme=(checkout/'README.md').read_text(encoding='utf-8')
    note='''# GitHub Desktop 完整交付

目标仓库：https://github.com/alistrode/omnidispatch 。完整当前源码、有效维护脚本与补丁、开发测试依赖原文件和自包含免安装包一起交付。大文件通过 Git LFS，提交/推送由 GitHub Desktop 完成。

- 直接使用：在 packages 解压完整 Windows x64 ZIP，双击内部 OmniDispatch.exe；或使用仓库的 Start-Packaged.cmd 校验并解压启动。
- 开发：查看 DEPENDENCIES.md 与 .agents/skills/omnidispatch/SKILL.md。所有实际采用的版本、环境恢复和维护命令均有索引。
- 当前运行包的真实数据不在仓库：state、授权、Cookie、私钥、原始日志、调试截图和构建缓存均排除。当前 SHA-256 与文件清单见 packages 和 DELIVERY-MANIFEST.json。
- 旧 packages/OmniDispatch-0.1.0-windows.zip 只保留历史，不自动继承当前包的验收结论。

---

'''
    if not readme.startswith('# GitHub Desktop 完整交付'):(checkout/'README.md').write_text(note+readme,encoding='utf-8')
    files=[]
    for file in checkout.rglob('*'):
        rel=file.relative_to(checkout)
        if not file.is_file() or '.git' in rel.parts or rel.name=='DELIVERY-MANIFEST.json':continue
        if not allowed(rel) and not rel.as_posix().startswith(('development/','packages/')):continue
        # Reject obvious credential material without printing its contents.
        if file.suffix.lower() in {'.py','.ps1','.json','.md','.txt','.js','.css','.html','.cmd'} and file.stat().st_size<5*1024**2:
            text=file.read_text(encoding='utf-8',errors='ignore')
            import re
            if re.search(r'(?:gh[pousr]_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{35,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)',text):raise ValueError('Credential-like material found in '+rel.as_posix())
        files.append({'path':rel.as_posix(),'bytes':file.stat().st_size,'sha256':sha(file)})
    delivery={'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'repository':'https://github.com/alistrode/omnidispatch','publication_method':'GitHub Desktop UI','archive_sha256':expected,'archive_bytes':archive.stat().st_size,'source_files':len(entries),'test_dependency_files':len(test_files),'private_state_included':False,'cloud_windows_single_folder_gui_test':'not_run','files':files}
    (checkout/'DELIVERY-MANIFEST.json').write_text(json.dumps(delivery,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in delivery.items() if k!='files'},ensure_ascii=False))
if __name__=='__main__':main()
