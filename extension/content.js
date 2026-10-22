(() => {
 const mount=document.createElement('div'),shadow=mount.attachShadow({mode:'closed'});
 shadow.innerHTML=`<style>
 :host{position:fixed;right:24px;bottom:24px;z-index:2147483647;font:12px -apple-system,BlinkMacSystemFont,"Helvetica Neue",sans-serif;color:#1d1d1f;max-width:calc(100vw - 32px)}
 *{box-sizing:border-box}.card{width:248px;max-width:100%;padding:12px;border:1px solid #ffffffd9;border-radius:18px;background:#fffffff2;backdrop-filter:blur(24px);box-shadow:0 6px 32px #00000016,0 1px 4px #00000008}
 button{font:inherit;cursor:pointer;border:0}button:focus-visible{outline:3px solid #0071e355;outline-offset:3px}.download{display:flex;align-items:center;justify-content:center;gap:7px;width:100%;padding:11px 12px;border-radius:11px;background:#0071e3;color:#fff;font-size:13px;font-weight:550}.download:hover{background:#0077ed}.download:disabled{background:#a2c5e9;cursor:default}.status{font-size:11px;line-height:1.5;color:#86868b;margin:9px 3px 0;overflow-wrap:anywhere}.status:empty{display:none}.result{display:none;padding:12px 3px 2px}.metrics{display:flex;align-items:center;gap:8px}.chip{background:#f2f2f7;border-radius:7px;padding:5px 8px;font-size:12px;font-weight:550}.source{font-size:10px;color:#86868b;line-height:1.5;margin:8px 0}.open{background:transparent;padding:0;color:#0071e3;font-size:11px}.credit{text-align:center;color:#86868b;font-size:9px;letter-spacing:.3px;margin:10px 0 0}.spinner{display:none;width:11px;height:11px;border:1.5px solid #ffffff60;border-top-color:#fff;border-radius:50%;animation:spin .8s linear infinite}.download:disabled .spinner{display:inline-block}@keyframes spin{to{transform:rotate(360deg)}}@media(prefers-reduced-motion:reduce){.spinner{animation:none}}
 </style><div class="card"><button id="download" class="download"><i class="spinner" aria-hidden="true"></i><span id="label">↓ 下载音频</span></button><p id="status" class="status" role="status" aria-live="polite"></p><div id="result" class="result"><div class="metrics"><span class="chip" id="key"></span><span class="chip" id="bpm"></span></div><p class="source" id="source"></p><button class="open" id="open">打开所在文件夹 ↗</button></div><p class="credit">work by orcaz</p></div>`;
 document.documentElement.append(mount);
 const btn=shadow.getElementById('download'),status=shadow.getElementById('status'),label=shadow.getElementById('label'),result=shadow.getElementById('result');
 const sourceLabels={title:'视频标题',description:'视频介绍',audio:'音频分析',libkeyfinder:'libkeyfinder · 整曲'};
 let path='',ownTabId=null,previous='';
 const videoUrl=()=>{const u=new URL(location.href),id=u.searchParams.get('v')||(u.pathname.startsWith('/shorts/')?u.pathname.split('/')[2]:'');return /^[A-Za-z0-9_-]{11}$/.test(id||'')?`https://www.youtube.com/watch?v=${id}`:'';};
 function render(job){
 if(job?.status==='review')job={...job,status:'done',message:'已下载（旧版本文件）'};
  if(!job||job.url!==videoUrl())return;
  btn.disabled=job.status==='working';label.textContent=btn.disabled?'正在下载…':job.status==='done'?'↓ 再次下载':'↓ 下载音频';status.textContent=job.message||'';
  path=job.path||'';result.style.display=job.status==='done'?'block':'none';
  if(job.status==='done'){const a=job.analysis||{};shadow.getElementById('key').textContent=[a.key,a.scale].filter(Boolean).join(' ')||'Key 未识别';shadow.getElementById('bpm').textContent=a.bpm?`${a.bpm} BPM`:'BPM 未识别';shadow.getElementById('source').textContent=`调性：${sourceLabels[a.key_source]||'未识别'} · BPM：${sourceLabels[a.bpm_source]||'未识别'}`;}
 }
 async function loadState(){if(ownTabId===null)return;const k=`job_${ownTabId}`;const saved=await chrome.storage.local.get(k);render(saved[k]);}
 btn.addEventListener('click',async()=>{try{await chrome.runtime.sendMessage({action:'start',url:videoUrl(),format:'mp3'});}catch{btn.disabled=false;status.textContent='请刷新页面后重试。';}});
 shadow.getElementById('open').addEventListener('click',()=>chrome.runtime.sendMessage({action:'reveal',path}));
 chrome.storage.onChanged.addListener(changes=>{const c=changes[`job_${ownTabId}`];if(c)render(c.newValue);});
 function navigate(){const url=videoUrl();mount.style.display=url?'block':'none';if(url!==previous){previous=url;btn.disabled=false;label.textContent='↓ 下载音频';status.textContent='';result.style.display='none';loadState().catch(()=>{});}}
 chrome.runtime.sendMessage({action:'identify'}).then(x=>{ownTabId=x.tabId;loadState();}).catch(()=>{});
 document.addEventListener('yt-navigate-finish',navigate);window.addEventListener('popstate',navigate);setInterval(navigate,1500);navigate();
})();
