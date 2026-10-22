"""Decode the complete audio track and stream it through actual libkeyfinder."""
import json, subprocess, tempfile
from pathlib import Path
HELPER=Path(__file__).resolve().parent/'bin/keyfinder-audio'

def check_available():
    if not HELPER.is_file(): raise RuntimeError('libkeyfinder 尚未安装，请重新运行本机安装程序。')
    result=subprocess.run([str(HELPER),'--version'],capture_output=True,text=True,timeout=10)
    if result.returncode or not result.stdout.startswith('libkeyfinder '):
        raise RuntimeError('libkeyfinder 无法启动，请重新运行本机安装程序。'+result.stderr.strip()[:200])
    return result.stdout.strip()

def analyze_key(path,ffmpeg,progress=lambda text:None):
    version=check_available()
    progress('正在用 libkeyfinder 分析整首音频的调性…')
    # Redirect errors to an unnamed temporary stream, never to the user's folder.
    with tempfile.TemporaryFile() as decoder_error:
        decoder=subprocess.Popen([ffmpeg,'-nostdin','-hide_banner','-loglevel','error','-i',str(path),'-vn','-ac','1','-ar','44100','-f','f32le','pipe:1'],stdout=subprocess.PIPE,stderr=decoder_error)
        try:
            with subprocess.Popen([str(HELPER)],stdin=decoder.stdout,stdout=subprocess.PIPE,stderr=subprocess.PIPE) as detector:
                decoder.stdout.close()
                try: output,error=detector.communicate(timeout=1800)
                except BaseException:
                    detector.kill();detector.communicate();raise
                if detector.returncode:raise RuntimeError('libkeyfinder 分析失败：'+error.decode(errors='replace')[:300])
            if decoder.wait(timeout=15):raise RuntimeError('整曲音频解码失败')
        finally:
            if decoder.poll() is None:decoder.kill()
            decoder.wait()
    result=json.loads(output)
    if result.get('engine')!='libkeyfinder':raise RuntimeError('测调引擎返回结果异常')
    result['engine_version']=version
    result['analyzed_seconds']=round(result['frames']/result['sample_rate'],3)
    return result
