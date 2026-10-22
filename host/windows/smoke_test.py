"""Run on an installed Windows x64 machine; test real EXEs and native pipes."""
import json,math,os,struct,subprocess,sys,tempfile,wave
from pathlib import Path
if sys.platform!='win32':raise SystemExit('此检查需要 Windows 10/11 x64。')
host=Path(os.environ['LOCALAPPDATA'])/'YouTube Audio/host'
if not (host/'bin/native-host.exe').is_file():raise SystemExit('请先运行 install-windows.cmd。')
sys.path.insert(0,str(host))
from keyfinder_backend import analyze_key
from process_utils import spawn_options
import imageio_ffmpeg
request=json.dumps({'action':'diagnose'}).encode('utf-8')
response=subprocess.run([str(host/'bin/native-host.exe')],input=struct.pack('=I',len(request))+request,capture_output=True,timeout=45,**spawn_options())
assert response.returncode==0,(response.returncode,response.stderr)
size=struct.unpack('=I',response.stdout[:4])[0]
status=json.loads(response.stdout[4:4+size]);assert status['status']=='ready' and status['platform']=='win32',status
print('Chrome 本机程序二进制通信：通过')
with tempfile.TemporaryDirectory(prefix='音频测试 空格 ') as tmp:
    sample_rate=22050;duration=16
    for key,root,minor in [('C',0,False),('A',9,True),('F#',6,True)]:
        chords=([0,3,7],[5,8,0],[7,11,2],[0,3,7]) if minor else ([0,4,7],[5,9,0],[7,11,2],[0,4,7])
        pcm=bytearray()
        for i in range(sample_rate*duration):
            time=i/sample_rate;chord=chords[int(time/2)%4];local=time%2
            envelope=min(local/.015,1)*math.exp(-local*.9)
            value=sum(.12/h*math.sin(2*math.pi*(440*2**((48+root+n-69)/12))*h*time)*envelope for n in chord for h in (1,2,3))
            value+=.12*math.sin(2*math.pi*(440*2**((36+root+chord[0]-69)/12))*time)*envelope
            pcm.extend(struct.pack('<h',int(max(-1,min(1,value))*32767)))
        path=Path(tmp)/(key.replace('#','sharp')+' 测试.wav')
        with wave.open(str(path),'wb') as audio:
            audio.setnchannels(1);audio.setsampwidth(2);audio.setframerate(sample_rate);audio.writeframes(pcm)
        result=analyze_key(path,imageio_ffmpeg.get_ffmpeg_exe())
        assert (result['key'],result['scale'])==(key,'Minor' if minor else 'Major'),result
        assert abs(result['analyzed_seconds']-duration)<.01,result
print('C 大调、A 小调、F# 小调、整曲读取、中文及空格路径：通过')
print('本机程序和测调测试通过。请再在 Chrome 中下载一个有权保存的视频验证完整流程。')
