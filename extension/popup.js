const button=document.getElementById('download'),status=document.getElementById('status'),result=document.getElementById('result');
const sourceLabels={title:'视频标题',description:'视频介绍',audio:'音频分析',libkeyfinder:'libkeyfinder · 整曲'};
document.getElementById('extension-id').textContent=chrome.runtime.id;
let tab,path='',validVideo=false;
function videoId(url){try{const u=new URL(url);if(u.protocol!=='https:'||!['www.youtube.com','m.youtube.com','youtube.com'].includes(u.hostname))return '';const id=u.searchParams.get('v')||(u.pathname.startsWith('/shorts/')?u.pathname.split('/')[2]:'');return /^[A-Za-z0-9_-]{11}$/.test(id||'')?id:'';}catch{return '';}}
function render(job){
 if(job?.status==='review')job={...job,status:'done',message:'已下载（旧版本文件）'};
 if(!job||!tab||videoId(job.url)!==videoId(tab.url))return;
 const working=job.status==='working',done=job.status==='done';
 button.disabled=working||!validVideo;document.getElementById('download-label').textContent=working?'正在下载…':done?'↓ 再次下载':'↓ 下载音频';
 status.textContent=job.message||'';result.style.display=done?'block':'none';path=job.path||'';
 if(done){
  const a=job.analysis||{};
  document.getElementById('key-value').textContent=[a.key,a.scale].filter(Boolean).join(' ')||'未识别';
  document.getElementById('bpm-value').textContent=a.bpm??'—';
  document.getElementById('key-source').textContent=sourceLabels[a.key_source]||'';
  document.getElementById('bpm-source').textContent=sourceLabels[a.bpm_source]||'';
  const file=document.getElementById('filename');file.textContent=job.filename||job.title||'';file.title=file.textContent;
 }
}
(async()=>{
 [tab]=await chrome.tabs.query({active:true,currentWindow:true});
 validVideo=Boolean(videoId(tab?.url));button.disabled=!validVideo;
 const saved=await chrome.storage.local.get(`job_${tab?.id}`);
 if(!validVideo){status.textContent='打开一个 YouTube 视频即可下载。';return;}
 render(saved[`job_${tab.id}`]);
})();
button.addEventListener('click',async()=>{button.disabled=true;status.textContent='正在连接…';try{await chrome.runtime.sendMessage({action:'start',tabId:tab.id,url:tab.url,format:'mp3'});}catch(error){status.textContent=error.message;button.disabled=!validVideo;}});
document.getElementById('reveal').addEventListener('click',()=>chrome.runtime.sendMessage({action:'reveal',path}));
chrome.storage.onChanged.addListener(c=>{if(tab&&c[`job_${tab.id}`])render(c[`job_${tab.id}`].newValue);});
async function checkNative(){
 const output=document.getElementById('connection-status'),check=document.getElementById('check-native');check.disabled=true;output.textContent='检查连接中…';
 try{const r=await chrome.runtime.sendMessage({action:'checkNative'});const dot=document.createElement('i');dot.className='dot';dot.dataset.state=r.status;output.replaceChildren(dot,document.createTextNode(r.status==='ready'?'本机已连接':r.message||'连接失败'));}
 catch(error){output.textContent=error.message;}
 finally{check.disabled=false;}
}
document.getElementById('check-native').addEventListener('click',checkNative);checkNative();
