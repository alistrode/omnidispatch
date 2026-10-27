import sys
from pathlib import Path
root=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(root));sys.path.insert(0,str(root/'validation-tools'))
import pytest
raise SystemExit(pytest.main(['-q',str(root/'tests')]))
