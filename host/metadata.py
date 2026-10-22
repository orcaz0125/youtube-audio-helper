"""Read explicit musical annotations; description text is data, never instructions."""
import re

NOTE = r'[A-Ga-g](?:[#♯b♭])?'
MODE = r'(?:major|minor|maj|min|大调|小调|大調|小調|m(?![a-z]))'
FULL = re.compile(rf'(?<![A-Za-z])(?P<note>{NOTE})\s*(?P<mode>{MODE})(?![A-Za-z0-9])',re.I)
LABELED = re.compile(rf'(?:\bkey\b|调性|調性|调式|調式)\s*[:：=\-]?\s*(?P<note>{NOTE})(?P<mode>\s*{MODE})?(?![A-Za-z0-9#♯b♭])',re.I)
BPM = re.compile(r'(?:(?:\bbpm\b|\btempo\b|速度|节拍|節拍)\s*[:：=\-]?\s*(?P<before>\d{2,3}(?:\.\d+)?)|(?<![\d.])(?P<after>\d{2,3}(?:\.\d+)?)\s*bpm\b)',re.I)

def tonic(note):
    value={'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}[note[0].upper()]
    if len(note)>1:value+=1 if note[1] in '#♯' else -1
    return ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B'][value%12]

def mode(value):
    if not value:return None
    # Uppercase M is conventional major, lowercase m is minor.
    raw=value.strip()
    if raw=='M':return 'Major'
    return 'Minor' if raw.lower() in ('m','min','minor','小调','小調') else 'Major'

def read_annotations(title='',description=''):
    key_candidates=[];bpm_candidates=[]
    for source,text in [('title',title),('description',description)]:
        if not isinstance(text,str):continue
        # Remove URLs so query strings cannot masquerade as musical annotations.
        text=re.sub(r'https?://\S+','',text[:100000])
        for pattern in (FULL,LABELED):
            for match in pattern.finditer(text):
                if pattern is FULL and match['mode'] in ('m','M') and not match['note'][0].isupper():continue
                key_candidates.append({'key':tonic(match['note']),'scale':mode(match['mode']),'source':source,'text':match[0]})
        for match in BPM.finditer(text):
            value=float(match['before'] or match['after'])
            if 20<=value<=400:bpm_candidates.append({'bpm':value,'source':source,'text':match[0]})
    # Prefer a complete key annotation over its duplicate tonic-only match.
    complete=[c for c in key_candidates if c['scale']]
    pool=complete or key_candidates
    keys={(c['key'],c['scale']) for c in pool}
    tempos={c['bpm'] for c in bpm_candidates}
    result={'key':None,'scale':None,'bpm':None,'key_source':None,'bpm_source':None,
            'key_candidates':key_candidates,'bpm_candidates':bpm_candidates,
            'key_conflict':len(keys)>1,'bpm_conflict':len(tempos)>1}
    if len(keys)==1:
        chosen=next((c for c in pool if c['source']=='description'),pool[0])
        result.update(key=chosen['key'],scale=chosen['scale'],key_source=chosen['source'])
    if len(tempos)==1:
        chosen=next((c for c in bpm_candidates if c['source']=='description'),bpm_candidates[0])
        result.update(bpm=chosen['bpm'],bpm_source=chosen['source'])
    return result

def merge_analysis(annotation,analysis):
    result=dict(analysis)
    # The actual recording wins, even if an uploader's key annotation disagrees.
    if analysis.get('key') and analysis.get('scale'):
        result['key_source']='libkeyfinder'
        if annotation.get('key'):
            result['annotation_agrees']=analysis['key']==annotation['key'] and (not annotation.get('scale') or analysis['scale']==annotation['scale'])
    elif annotation.get('key'):
        result.update(key=annotation['key'],scale=annotation.get('scale'),key_source=annotation['key_source'])
    else:result['key_source']=None
    # libkeyfinder detects key, not BPM. Preserve explicit tempo annotations.
    if annotation.get('bpm') is not None:result.update(bpm=annotation['bpm'],bpm_source=annotation['bpm_source'])
    else:result['bpm_source']='audio' if analysis.get('bpm') else None
    return result
