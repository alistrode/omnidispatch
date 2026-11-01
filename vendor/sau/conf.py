"""OmniDispatch integration configuration; upstream code stays pinned and separate."""
import os,tempfile
from pathlib import Path
BASE_DIR=Path(os.getenv('OMNI_SAU_WORK',str(Path(tempfile.gettempdir())/'omni-sau-check'))).resolve()
BASE_DIR.mkdir(parents=True,exist_ok=True)
XHS_SERVER='http://127.0.0.1:11901'
LOCAL_CHROME_PATH=os.getenv('OMNI_BROWSER_PATH','')
LOCAL_CHROME_HEADLESS=True
DEBUG_MODE=False
YT_PROXY=None
