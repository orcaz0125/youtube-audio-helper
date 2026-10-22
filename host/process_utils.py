"""Platform-specific process flags and Node lookup shared by the host."""
import os,shutil,subprocess,sys
from pathlib import Path

def spawn_options():
    return {'creationflags':getattr(subprocess,'CREATE_NO_WINDOW',0x08000000)} if sys.platform=='win32' else {}

def find_node():
    found=shutil.which('node')
    if found:return found
    if sys.platform=='win32':
        candidates=[Path(os.environ.get(name,''))/'nodejs/node.exe' for name in ('ProgramFiles','ProgramW6432') if os.environ.get(name)]
        if os.environ.get('LOCALAPPDATA'):candidates.append(Path(os.environ['LOCALAPPDATA'])/'Programs/nodejs/node.exe')
    else:candidates=[Path('/opt/homebrew/bin/node'),Path('/usr/local/bin/node')]
    return next((str(p) for p in candidates if p.is_file()),None)
