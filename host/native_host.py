#!/usr/bin/env python3
import json, os, re, shutil, struct, subprocess, sys, time, uuid, math
from pathlib import Path
from urllib.parse import parse_qs, urlparse
BASE = Path(__file__).resolve().parent.parent
DOWNLOADS = Path(os.environ.get('YOUTUBE_AUDIO_DOWNLOADS',str(BASE / 'downloads'))).expanduser()

def send(data):
    raw=json.dumps(data,ensure_ascii=False).encode('utf-8')
    sys.stdout.buffer.write(struct.pack('=I',len(raw))+raw); sys.stdout.buffer.flush()

def receive():
    head=sys.stdin.buffer.read(4)
    if not head: return None
    if len(head)!=4: raise ValueError('消息头不完整')
    size=struct.unpack('=I',head)[0]
    if size>65536: raise ValueError('消息过大')
    data=sys.stdin.buffer.read(size)
    if len(data)!=size: raise ValueError('消息不完整')
    return json.loads(data)

def normalize(url):
    if not isinstance(url,str): raise ValueError('链接无效')
    u=urlparse(url)
    if u.scheme!='https' or u.hostname not in {'youtube.com','www.youtube.com','m.youtube.com','youtu.be'} or u.port not in (None,443):
        raise ValueError('仅支持 YouTube 视频链接')
    video=u.path.strip('/') if u.hostname=='youtu.be' else (u.path.split('/')[2] if u.path.startswith('/shorts/') else parse_qs(u.query).get('v',[''])[0])
    if not re.fullmatch(r'[A-Za-z0-9_-]{11}',video): raise ValueError('请打开一个具体的 YouTube 视频')
    return 'https://www.youtube.com/watch?v='+video

class QuietLogger:
    def debug(self,msg): pass
    def warning(self,msg): pass
    def error(self,msg): pass

def download(message):
    import yt_dlp
    url=normalize(message.get('url'))
    fmt='mp3'
    DOWNLOADS.mkdir(parents=True,exist_ok=True)
    temp=DOWNLOADS / ('.working-'+uuid.uuid4().hex)
    temp.mkdir()
    last=[0]
    def progress(info):
        if info.get('status')=='downloading' and time.monotonic()-last[0]>.7:
            last[0]=time.monotonic()
            total=info.get('total_bytes') or info.get('total_bytes_estimate')
            pct=min(100,round(info.get('downloaded_bytes',0)*100/total)) if total else None
            send({'status':'working','message':f'正在下载音频{f" · {pct}%" if pct is not None else "…"}','progress':pct})
    node=shutil.which('node') or next((p for p in ('/usr/local/bin/node','/opt/homebrew/bin/node') if Path(p).exists()),None)
    options={'format':'bestaudio[ext=m4a]/bestaudio','noplaylist':True,'outtmpl':str(temp/'audio.%(ext)s'),'quiet':True,'no_warnings':True,'logger':QuietLogger(),'progress_hooks':[progress],'socket_timeout':30,'retries':3,'windowsfilenames':True,'max_filesize':1024**3,'match_filter':lambda info,**kw: '暂不支持正在直播的视频' if info.get('is_live') else None}
    if node: options['js_runtimes']={'node':{'path':node}}
    try:
        send({'status':'working','message':'正在解析视频…'})
        with yt_dlp.YoutubeDL(options) as ydl:
            info=ydl.extract_info(url,download=True)
            if not info: raise ValueError('此视频暂时无法提取音频')
            source=Path(info['requested_downloads'][0]['filepath'])
        title=re.sub(r'[\\/:*?"<>|\x00-\x1f]','_',info.get('title') or info['id']).strip('. ').encode('utf-8')[:120].decode('utf-8',errors='ignore') or info['id']
        analysis_source=source
        suffix='mp3'
        destination=DOWNLOADS/f'{title} [{info["id"]}]-{uuid.uuid4().hex[:6]}.{suffix}'
        if fmt=='mp3':
            import imageio_ffmpeg
            send({'status':'working','message':'音频下载完成，正在转换 MP3…'})
            result=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-nostdin','-hide_banner','-loglevel','error','-i',str(source),'-vn','-codec:a','libmp3lame','-q:a','2',str(temp/'output.mp3')],capture_output=True,timeout=1800)
            if result.returncode: raise ValueError('MP3 转换失败，请重试')
            source=temp/'output.mp3'
        from metadata import read_annotations, merge_analysis
        annotations=read_annotations(info.get('title',''),info.get('description',''))
        import imageio_ffmpeg
        from analysis import analyze
        analysis=analyze(analysis_source,imageio_ffmpeg.get_ffmpeg_exe(),lambda text:send({'status':'working','message':text}),need_bpm=annotations.get('bpm') is None)
        result=merge_analysis(annotations,analysis)
        key_label=' '.join(x for x in (result.get('key'),result.get('scale')) if x) or 'Key Unknown'
        tempo_label=f'{result["bpm"]:g} BPM' if result.get('bpm') else 'BPM Unknown'
        destination=DOWNLOADS/f'{title} [{key_label}] [{tempo_label}].{suffix}'
        if destination.exists():
            destination=DOWNLOADS/f'{title} [{key_label}] [{tempo_label}] {uuid.uuid4().hex[:6]}.{suffix}'
        source.replace(destination)
        send({'status':'done','message':'下载完成','filename':destination.name,'path':str(destination),'title':info.get('title',title),'analysis':result})
    finally:
        shutil.rmtree(temp,ignore_errors=True)

def main():
    while True:
        try:
            message=receive()
            if message is None: return
            if message.get('action') in {'ping','diagnose'}:
                import importlib
                missing=[]
                for module in ('yt_dlp','librosa','imageio_ffmpeg'):
                    try: importlib.import_module(module)
                    except Exception as exc: missing.append(f'{module}: {exc}')
                try:
                    from keyfinder_backend import check_available
                    key_engine=check_available()
                except Exception as exc:missing.append(str(exc))
                if missing: send({'status':'error','message':'本机程序依赖不完整：'+'; '.join(missing)})
                else: send({'status':'ready','version':'0.3.0','key_engine':key_engine,'download_directory':str(DOWNLOADS)})
            elif message.get('action')=='download': download(message)
            elif message.get('action')=='reveal':
                path=Path(message.get('path','')).resolve()
                if not path.is_relative_to(DOWNLOADS.resolve()) or not path.is_file(): raise ValueError('找不到此音频文件')
                subprocess.run(['/usr/bin/open','-R',str(path)],check=True)
                send({'status':'done'})
            else: raise ValueError('未知操作')
        except Exception as exc:
            text=str(exc)
            if 'Sign in' in text or 'bot' in text.lower(): text='YouTube 要求登录验证，此视频暂时无法下载。可以换一个公开视频重试。'
            elif 'timed out' in text or 'Unable to download' in text: text='连接 YouTube 失败，请检查网络后重试。'
            send({'status':'error','message':text[:700]})
if __name__=='__main__': main()
