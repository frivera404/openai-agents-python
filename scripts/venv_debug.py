import sys
import importlib.util
print('sys.executable:', sys.executable)
print('sys.version:', sys.version.replace('\n', ' '))
print('sys.path[0:5]:', sys.path[:5])
print("find_spec('dotenv'):", importlib.util.find_spec('dotenv'))
from pathlib import Path
venv_site = Path(sys.executable).resolve().parents[1] / 'Lib' / 'site-packages'
print('expected venv site-packages:', venv_site)
print('venv site exists:', venv_site.exists())
if venv_site.exists():
	print('venv site contents sample:', list(venv_site)[:10])
