"""Pinned source entry point, so PyInstaller's missing dynamic plugins cannot hide adapters."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(root/'engines'/'spreado'/'v1.2.0'/'source'))
if __name__=='__main__':
    from spreado.cli.cli import main
    raise SystemExit(main())
