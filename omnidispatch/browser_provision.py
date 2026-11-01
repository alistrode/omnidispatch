"""Resolve the immutable bundled standard Chromium for our source-patched XHS engine."""
from pathlib import Path
def bundled_xhs_browser():
    path=Path(__file__).resolve().parent.parent/'engines'/'browser'/'chromium-cft'/'chrome-win64'/'chrome.exe'
    if not path.is_file():raise ValueError('运行包缺少发布浏览器，请使用完整运行包')
    return str(path.resolve())
