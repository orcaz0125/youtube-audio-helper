"""Full-track key detection with libkeyfinder; librosa is used only for BPM."""
import re,subprocess
from keyfinder_backend import analyze_key

def estimate_bpm(path,ffmpeg,progress):
    import librosa
    import numpy as np
    info=subprocess.run([ffmpeg,'-hide_banner','-i',str(path)],capture_output=True,timeout=30).stderr.decode(errors='replace')
    match=re.search(r'Duration: (\d+):(\d+):(\d+(?:\.\d+)?)',info)
    if not match:return None
    h,m,s=map(float,match.groups());duration=h*3600+m*60+s
    if duration<8:return None
    window=min(24.,duration)
    starts=np.unique(np.maximum(0,np.minimum(duration-window,np.array([.2,.5,.8])*duration-window/2)))
    tempos=[]
    for number,start in enumerate(starts):
        progress(f'正在识别 BPM · {number+1}/{len(starts)} 段')
        decoded=subprocess.run([ffmpeg,'-nostdin','-hide_banner','-loglevel','error','-ss',str(start),'-i',str(path),'-t',str(window),'-vn','-ac','1','-ar','22050','-f','f32le','pipe:1'],capture_output=True,timeout=120)
        if decoded.returncode:continue
        y=np.frombuffer(decoded.stdout,dtype='<f4').copy()
        if len(y)<22050*4 or np.max(np.abs(y))<1e-5:continue
        onset=librosa.onset.onset_strength(y=y,sr=22050,hop_length=512)
        if len(onset)<=10 or np.max(onset)<1e-6:continue
        _,beats=librosa.beat.beat_track(onset_envelope=onset,sr=22050,hop_length=512,trim=True)
        if len(beats)>=6:
            times=librosa.frames_to_time(beats,sr=22050,hop_length=512)
            slope=float(np.polyfit(np.arange(len(times)),times,1)[0])
            if slope>0:tempos.append(60/slope)
    return round(float(np.median(tempos)),1) if tempos else None

def analyze(path,ffmpeg,progress=lambda message:None,need_bpm=True):
    result={'key':None,'scale':None,'bpm':None,'engine':'libkeyfinder'}
    try:result.update(analyze_key(path,ffmpeg,progress))
    except Exception as exc:result['key_error']=str(exc)[:400]
    if need_bpm:
        try:result['bpm']=estimate_bpm(path,ffmpeg,progress)
        except Exception as exc:result['bpm_error']=str(exc)[:300]
    return result
