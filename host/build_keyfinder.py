"""Build the GPL-3.0-or-later streaming adapter against Homebrew libkeyfinder."""
import os, shutil, subprocess
from pathlib import Path
BASE=Path(__file__).resolve().parent

def build():
    brew=shutil.which('brew') or next((p for p in ('/opt/homebrew/bin/brew','/usr/local/bin/brew') if Path(p).is_file()),None)
    if not brew: raise RuntimeError('需要先安装 Homebrew，再运行安装程序以配置 libkeyfinder。')
    env={**os.environ,'HOMEBREW_NO_AUTO_UPDATE':'1','HOMEBREW_NO_INSTALL_CLEANUP':'1'}
    result=subprocess.run([brew,'--prefix','libkeyfinder'],capture_output=True,text=True,env=env)
    prefix=Path(result.stdout.strip()) if result.returncode==0 else None
    if prefix is None or not (prefix/'include/keyfinder/keyfinder.h').exists():
        subprocess.run([brew,'install','libkeyfinder'],env=env,check=True)
        prefix=Path(subprocess.check_output([brew,'--prefix','libkeyfinder'],text=True,env=env).strip())
    compiler=shutil.which('clang++')
    if not compiler: raise RuntimeError('需要安装 Xcode Command Line Tools（clang++）。')
    output=BASE/'bin/keyfinder-audio';output.parent.mkdir(exist_ok=True)
    version=prefix.resolve().name
    temporary=output.with_suffix('.building')
    try:
        subprocess.run([compiler,'-std=c++11','-O2','-I'+str(prefix/'include'),str(BASE/'keyfinder/keyfinder_audio.cpp'),'-L'+str(prefix/'lib'),'-lkeyfinder','-DKEYFINDER_LIBRARY_VERSION="'+version+'"','-o',str(temporary)],check=True)
        subprocess.run([str(temporary),'--version'],check=True)
        temporary.replace(output)
    finally: temporary.unlink(missing_ok=True)
    return output
if __name__=='__main__': print('测调程序已安装：'+str(build()))
