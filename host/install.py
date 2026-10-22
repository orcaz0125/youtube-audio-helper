import json, re, shlex, shutil, subprocess, sys, hashlib, base64
from pathlib import Path
SOURCE=Path(__file__).resolve().parent
if sys.version_info<(3,12): raise SystemExit('需要 Python 3.12 或更新版本。')
if sys.platform!='darwin': raise SystemExit('此安装包目前支持 macOS。')
if len(sys.argv)>1:
    identifier=sys.argv[1].strip()
else:
    extension=SOURCE.parent/'extension/manifest.json'
    manifest_data=json.loads(extension.read_text()) if extension.is_file() else {}
    if manifest_data.get('key'):
        fingerprint=hashlib.sha256(base64.b64decode(manifest_data['key'])).hexdigest()[:32]
        identifier=''.join(chr(ord('a')+int(char,16)) for char in fingerprint)
        print('正在自动配置本扩展连接，无需填写扩展 ID。')
    else:
        identifier=input('粘贴 Chrome 扩展 ID 后按回车：').strip()
if not re.fullmatch('[a-p]{32}',identifier): raise SystemExit('扩展 ID 格式不正确。')
BASE=Path.home()/'Library/Application Support/YouTube Audio'
host=BASE/'host';host.mkdir(parents=True,exist_ok=True)
for name in ('native_host.py','analysis.py','metadata.py','keyfinder_backend.py','build_keyfinder.py','requirements.txt'):
    if (SOURCE/name).resolve()!=(host/name).resolve(): shutil.copy2(SOURCE/name,host/name)
if (SOURCE/'keyfinder').resolve()!=(host/'keyfinder').resolve(): shutil.copytree(SOURCE/'keyfinder',host/'keyfinder',dirs_exist_ok=True)
subprocess.run([sys.executable,str(host/'build_keyfinder.py')],check=True)
venv=host/'.venv'
if not (venv/'bin/python').exists(): subprocess.run([sys.executable,'-m','venv',str(venv)],check=True)
subprocess.run([str(venv/'bin/python'),'-m','pip','install','--disable-pip-version-check','-r',str(host/'requirements.txt')],check=True)
python=str(venv/'bin/python')
subprocess.run([python,'-c','import yt_dlp, librosa, imageio_ffmpeg'],check=True)
node=shutil.which('node')
if not node: print('提示：建议安装 Node.js 22 或更新版本，以支持 YouTube 解析。')
output=Path.home()/'Music/YouTube Audio';output.mkdir(parents=True,exist_ok=True)
launcher=host/'launch.sh'
launcher.write_text('#!/bin/sh\nexport YOUTUBE_AUDIO_DOWNLOADS='+shlex.quote(str(output))+'\nexec '+shlex.quote(python)+' -u '+shlex.quote(str(host/'native_host.py'))+' "$@" 2>>'+shlex.quote(str(host/'native.log'))+'\n')
launcher.chmod(0o755)
folder=Path.home()/'Library/Application Support/Google/Chrome/NativeMessagingHosts';folder.mkdir(parents=True,exist_ok=True)
manifest=folder/'com.local.youtube_audio.json'
origins=[f'chrome-extension://{identifier}/']
if manifest.exists():
    try: origins+=json.loads(manifest.read_text()).get('allowed_origins',[])
    except (ValueError,OSError): pass
origins=sorted(set(x for x in origins if re.fullmatch(r'chrome-extension://[a-p]{32}/',x)))
manifest.write_text(json.dumps({'name':'com.local.youtube_audio','description':'YouTube audio download helper','path':str(launcher),'type':'stdio','allowed_origins':origins},indent=2))
print('安装完成。请在 chrome://extensions 重新加载扩展，再刷新 YouTube 页面。')
print('音频保存位置：'+str(output))
