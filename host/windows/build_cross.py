"""Rebuild the Windows x64 binaries from pinned GPL-compatible source archives.
Run on macOS/Linux with mingw-w64, make and Python 3.12+.
No downloads: unpack source archives from ../keyfinder/sources.
"""
import hashlib,os,shutil,subprocess,tarfile
from pathlib import Path
HOST=Path(__file__).resolve().parent.parent
SOURCES=HOST/'keyfinder/sources'
EXPECTED={'libkeyfinder-2.2.8.tar.gz':'a54fc6c5ff435bb4b447f175bc97f9081fb5abf0edd5d125e6f5215c8fff4d11','fftw-3.3.11.tar.gz':'5630c24cdeb33b131612f7eb4b1a9934234754f9f388ff8617458d0be6f239a1'}

def build(work):
    work=Path(work).resolve();work.mkdir(parents=True,exist_ok=True)
    for name,digest in EXPECTED.items():
        archive=SOURCES/name
        if hashlib.sha256(archive.read_bytes()).hexdigest()!=digest:raise RuntimeError('Source checksum mismatch: '+name)
        with tarfile.open(archive) as tar:tar.extractall(work/'source',filter='data')
    triple='x86_64-w64-mingw32'
    cc=shutil.which(triple+'-gcc');cxx=shutil.which(triple+'-g++')
    if not cc or not cxx:raise RuntimeError('Install mingw-w64 first')
    prefix=work/'fftw-install';fftw_build=work/'fftw-build';fftw_build.mkdir(exist_ok=True)
    env={**os.environ,'CC':cc,'AR':triple+'-ar','RANLIB':triple+'-ranlib','CFLAGS':'-O2 -DNDEBUG -ffile-prefix-map='+str(work)+'=.'}
    if not (prefix/'lib/libfftw3.a').is_file():
        subprocess.run([str(work/'source/fftw-3.3.11/configure'),'--host='+triple,'--prefix='+str(prefix),'--disable-fortran','--disable-shared','--enable-static','--disable-threads','--disable-openmp','--disable-mpi','--enable-portable-binary','--disable-alloca','--with-our-malloc16'],cwd=fftw_build,env=env,check=True)
        subprocess.run(['make','-j4'],cwd=fftw_build,env=env,check=True)
        subprocess.run(['make','install'],cwd=fftw_build,env=env,check=True)
    output=HOST/'windows-x64';output.mkdir(exist_ok=True)
    obj=work/'objects';obj.mkdir(exist_ok=True)
    upstream=work/'source/libkeyfinder-2.2.8';objects=[]
    flags=['-std=c++11','-O2','-DNDEBUG','-D_WIN32_WINNT=0x0A00','-ffile-prefix-map='+str(work)+'=.','-ffile-prefix-map='+str(HOST)+'=host','-I'+str(prefix/'include'),'-I'+str(upstream.parent)]
    # Upstream headers live in src; the adapter includes keyfinder/*.h.
    headers=work/'include/keyfinder';headers.mkdir(parents=True,exist_ok=True)
    for header in (upstream/'src').glob('*.h'):shutil.copy2(header,headers/header.name)
    flags+=['-I'+str(work/'include')]
    for source in sorted((upstream/'src').glob('*.cpp')):
        target=obj/(source.stem+'.o')
        subprocess.run([cxx,*flags,'-c',str(source),'-o',str(target)],check=True)
        objects.append(str(target))
    subprocess.run([cxx,*flags,'-DKEYFINDER_LIBRARY_VERSION="2.2.8"',str(HOST/'keyfinder/keyfinder_audio.cpp'),*objects,str(prefix/'lib/libfftw3.a'),'-static','-static-libgcc','-static-libstdc++','-o',str(output/'keyfinder-audio.exe')],check=True)
    subprocess.run([cxx,'-std=c++17','-O2','-D_WIN32_WINNT=0x0A00','-municode',str(HOST/'windows/native_host_launcher.cpp'),'-static','-static-libgcc','-static-libstdc++','-o',str(output/'native-host.exe')],check=True)
    for path in output.glob('*.exe'):subprocess.run([triple+'-strip',str(path)],check=True)
    (output/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256((output/name).read_bytes()).hexdigest()+'  '+name+'\n' for name in ('keyfinder-audio.exe','native-host.exe')),encoding='utf-8')
    print('Windows x64 binaries built:',output,flush=True)
if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--work',required=True)
    build(parser.parse_args().work)
