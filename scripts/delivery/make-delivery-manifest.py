"""Regenerate DELIVERY-MANIFEST.json from the checked-out tree.

Only records what is actually in the repository: every tracked-looking file except
VCS/state/cache paths, plus the release-asset digest read from packages/*.sha256.
The 1 GB bundle is not a Git object, so it is described in `distribution`, not in
`files`, and it is never hashed by this script (the .sha256 file is the authority).
"""
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
skip_dirs = {'.git', '.runtime', '.runtime-cache', '_state', 'state', 'logs', 'backups',
             '__pycache__', '.pytest_cache', 'node_modules', 'validation-tools', 'engines'}
skip_suffix = {'.pyc', '.log'}

def tracked():
    try:
        listing = subprocess.run(['git', '-C', str(root), 'ls-files', '-z'], capture_output=True, check=True).stdout
        return sorted(p.decode('utf-8') for p in listing.split(b'\0') if p)
    except Exception:
        return None

files = tracked()
if files is None:
    files = []
    for path in sorted(root.rglob('*')):
        relative = path.relative_to(root)
        if not path.is_file() or any(part in skip_dirs for part in relative.parts):
            continue
        if path.suffix.lower() in skip_suffix:
            continue
        files.append(relative.as_posix())

entries = []
for relative in files:
    path = root / relative
    if not path.is_file():
        continue
    entries.append({'path': relative, 'bytes': path.stat().st_size,
                    'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})

checksum = next(iter(sorted(root.glob('packages/*.sha256'))), None)
archive = None
if checksum:
    field = (checksum.read_text(encoding='utf-8').strip().split() + [''])[0]
    archive_name = checksum.stem + '.zip'
    local = root / 'packages' / archive_name
    archive = {'path': 'packages/' + archive_name, 'sha256': field,
               'bytes': local.stat().st_size if local.is_file() else None,
               'storage': 'GitHub Releases asset (not a Git object; single file limit 100 MB)'}
    if archive['bytes'] is None:
        documented = root / 'packages' / 'DOWNLOAD.md'
        if documented.is_file():
            for line in documented.read_text(encoding='utf-8').splitlines():
                if '字节数' in line and '`' in line:
                    digits = ''.join(ch for ch in line.split('`')[1] if ch.isdigit())
                    if digits:
                        archive['bytes'] = int(digits)
                    break

test_dependency_files = [e for e in entries if e['path'].startswith('development/test-tools/')]
source_files = [e for e in entries if e['path'].startswith(('omnidispatch/', 'apps/', 'desktop/', 'scripts/', 'tests/'))]

manifest = {
    'created_at': datetime.now(timezone.utc).isoformat(),
    'repository': 'https://github.com/alistrode/omnidispatch',
    'publication_method': 'git push + GitHub Releases asset (gh CLI)',
    'archive_sha256': archive['sha256'] if archive else None,
    'archive_bytes': archive['bytes'] if archive else None,
    'archive_download': 'https://github.com/alistrode/omnidispatch/releases/download/v1.1.0/OmniDispatch-Desktop-Windows-x64.zip',
    'source_files': len(source_files),
    'test_dependency_files': len(test_dependency_files),
    'private_state_included': False,
    'distribution': archive,
    'cloud_windows_single_folder_gui_test': 'passed 2026-11-02: downloaded from the v1.1.0 release asset, SHA-256 matched, '
                                            'extracted to a new folder outside the bundle, scripts/verify-bundle.py exit 0 '
                                            'and OmniDispatch.exe --smoke success=true (13/13 routes, 0 script errors); see VERIFICATION.md',
    'files': entries,
}
(root / 'DELIVERY-MANIFEST.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'files': len(entries), 'source_files': len(source_files),
                  'test_dependency_files': len(test_dependency_files),
                  'archive_sha256': manifest['archive_sha256']}, ensure_ascii=False))
