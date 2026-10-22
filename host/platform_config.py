"""Keep OS paths, registry registration and file revealing in one place."""
import os,sys,subprocess
from pathlib import Path
HOST_NAME='com.local.youtube_audio'
REGISTRY_KEY='\\'.join(('Software','Google','Chrome','NativeMessagingHosts',HOST_NAME))

def install_base():
    if sys.platform=='win32':
        local=os.environ.get('LOCALAPPDATA')
        if not local:raise RuntimeError('未找到 Windows LOCALAPPDATA 用户目录。')
        return Path(local)/'YouTube Audio'
    if sys.platform=='darwin':return Path.home()/'Library/Application Support/YouTube Audio'
    raise RuntimeError('当前支持 macOS 与 Windows 10/11 x64。')

def default_downloads():
    return Path.home()/'Music/YouTube Audio'

def manifest_path(base):
    if sys.platform=='win32':return base/(HOST_NAME+'.json')
    return Path.home()/'Library/Application Support/Google/Chrome/NativeMessagingHosts'/(HOST_NAME+'.json')

def register_windows(manifest):
    import winreg
    # Current-user key: no administrator access and no browser profile edits.
    with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER,REGISTRY_KEY,0,winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key,'',0,winreg.REG_SZ,str(manifest.resolve()))

def reveal_audio(path):
    if sys.platform=='win32':os.startfile(str(path.parent))
    elif sys.platform=='darwin':subprocess.run(['/usr/bin/open','-R',str(path)],check=True)
    else:raise RuntimeError('当前系统无法打开文件夹。')
