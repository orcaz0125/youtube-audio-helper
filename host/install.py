"""Install the same Chrome native host on macOS or Windows x64."""
import base64,hashlib,json,os,platform,re,shlex,shutil,struct,subprocess,sys
from pathlib import Path
from platform_config import install_base,manifest_path,register_windows,default_downloads
from process_utils import find_node,spawn_options
SOURCE=Path(__file__).resolve().parent


def extension_id(argument=None):
    if argument:return argument.strip()
    extension=SOURCE.parent/'extension/manifest.json'
    data=json.loads(extension.read_text(encoding='utf-8')) if extension.is_file() else {}
    if data.get('key'):
        fingerprint=hashlib.sha256(base64.b64decode(data['key'])).hexdigest()[:32]
        return ''.join(chr(ord('a')+int(char,16)) for char in fingerprint)
    return input('粘贴 Chrome 扩展 ID 后按回车：').strip()


def verify_windows_binaries(directory):
    sums=directory/'SHA256SUMS.txt'
    if not sums.is_file():raise RuntimeError('缺少 Windows 程序校验文件，请使用完整 Windows 分享包。')
    expected={name:digest for digest,name in (line.split() for line in sums.read_text(encoding='utf-8').splitlines() if line.strip())}
    for name in ('keyfinder-audio.exe','native-host.exe'):
        binary=directory/name
        if not binary.is_file() or hashlib.sha256(binary.read_bytes()).hexdigest()!=expected.get(name):
            raise RuntimeError('Windows 程序不完整或已损坏：'+name+'，请重新解压完整安装包。')


def install(identifier):
    if sys.version_info<(3,12):raise RuntimeError('需要 Python 3.12 或更新版本。')
    if sys.platform not in {'darwin','win32'}:raise RuntimeError('当前支持 macOS 与 Windows 10/11 x64。')
    if not re.fullmatch('[a-p]{32}',identifier):raise RuntimeError('扩展 ID 格式不正确。')
    if sys.platform=='win32':
        if struct.calcsize('P')!=8 or platform.machine().upper() not in {'AMD64','X86_64'}:
            raise RuntimeError('Windows 分享版需要 x64 Windows 和 x64 Python，不支持 32 位或原生 ARM64 Python。')
        verify_windows_binaries(SOURCE/'windows-x64')
    node=find_node()
    if not node:raise RuntimeError('请先安装 Node.js 22 或更新版本：https://nodejs.org/，安装后重新运行本程序。')
    version=subprocess.check_output([node,'--version'],text=True,**spawn_options()).strip()
    if int(version.lstrip('v').split('.')[0])<22:raise RuntimeError('Node.js 版本过旧，需要 22 或更新版本。')
    base=install_base();host=base/'host';host.mkdir(parents=True,exist_ok=True)
    files=('native_host.py','analysis.py','metadata.py','keyfinder_backend.py','process_utils.py','platform_config.py','build_keyfinder.py','install.py','requirements.txt')
    for name in files:
        if (SOURCE/name).resolve()!=(host/name).resolve():shutil.copy2(SOURCE/name,host/name)
    if (SOURCE/'keyfinder').resolve()!=(host/'keyfinder').resolve():shutil.copytree(SOURCE/'keyfinder',host/'keyfinder',dirs_exist_ok=True)
    if sys.platform=='win32':
        if (SOURCE/'windows-x64').resolve()!=(host/'windows-x64').resolve():shutil.copytree(SOURCE/'windows-x64',host/'windows-x64',dirs_exist_ok=True)
        (host/'bin').mkdir(exist_ok=True)
        shutil.copy2(host/'windows-x64/native-host.exe',host/'bin/native-host.exe')
    else:subprocess.run([sys.executable,str(host/'build_keyfinder.py')],check=True)
    venv=host/'.venv';python=venv/('Scripts/python.exe' if sys.platform=='win32' else 'bin/python')
    if not python.exists():subprocess.run([sys.executable,'-m','venv',str(venv)],check=True)
    subprocess.run([str(python),'-m','pip','install','--disable-pip-version-check','-r',str(host/'requirements.txt')],check=True)
    subprocess.run([str(python),'-c','import yt_dlp,librosa,imageio_ffmpeg;from keyfinder_backend import check_available;print(check_available())'],cwd=host,check=True,**spawn_options())
    output=default_downloads();output.mkdir(parents=True,exist_ok=True)
    if sys.platform=='win32':launcher=host/'bin/native-host.exe'
    else:
        launcher=host/'launch.sh'
        launcher.write_text('#!/bin/sh\nexport YOUTUBE_AUDIO_DOWNLOADS='+shlex.quote(str(output))+'\nexec '+shlex.quote(str(python))+' -u '+shlex.quote(str(host/'native_host.py'))+' "$@" 2>>'+shlex.quote(str(host/'native.log'))+'\n',encoding='utf-8')
        launcher.chmod(0o755)
    manifest=manifest_path(base);manifest.parent.mkdir(parents=True,exist_ok=True)
    origins=[f'chrome-extension://{identifier}/']
    if manifest.exists():
        try:origins+=json.loads(manifest.read_text(encoding='utf-8')).get('allowed_origins',[])
        except (ValueError,OSError):pass
    origins=sorted(set(x for x in origins if re.fullmatch(r'chrome-extension://[a-p]{32}/',x)))
    manifest.write_text(json.dumps({'name':'com.local.youtube_audio','description':'YouTube audio download helper','path':str(launcher.resolve()),'type':'stdio','allowed_origins':origins},ensure_ascii=False,indent=2),encoding='utf-8')
    if sys.platform=='win32':register_windows(manifest)
    print('安装完成。请在 chrome://extensions 重新加载扩展，再刷新 YouTube 页面。')
    print('音频保存位置：'+str(output))

if __name__=='__main__':
    try:install(extension_id(sys.argv[1] if len(sys.argv)>1 else None))
    except Exception as error:print('安装失败：'+str(error),file=sys.stderr);raise SystemExit(1)
