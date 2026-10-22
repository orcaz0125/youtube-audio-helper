const HOST = 'com.local.youtube_audio';
const running = new Map();
const key = id => `job_${id}`;
const save = (id, state) => chrome.storage.local.set({[key(id)]:state});
function connect() { return chrome.runtime.connectNative(HOST); }
function start(tabId, url, format) {
  try {
    const parsed = new URL(url);
    const id = parsed.searchParams.get('v') || (parsed.pathname.startsWith('/shorts/') ? parsed.pathname.split('/')[2] : '');
    if (parsed.protocol !== 'https:' || !['www.youtube.com','m.youtube.com','youtube.com'].includes(parsed.hostname) || !/^[A-Za-z0-9_-]{11}$/.test(id || '')) throw new Error();
    url = `https://www.youtube.com/watch?v=${id}`;
  } catch { save(tabId, {status:'error', message:'请打开一个具体的 YouTube 视频。'}); return; }
  if (running.has(tabId)) return;
  const port = connect(); running.set(tabId, port);
  let terminal = false;
  save(tabId, {status:'working', message:'正在解析视频…', url});
  port.onMessage.addListener(data => {
    if (data.status === 'done' || data.status === 'error' || data.status === 'review') terminal = true;
    save(tabId, {...data, url});
    if (terminal) { running.delete(tabId); port.disconnect(); }
  });
  port.onDisconnect.addListener(() => {
    const error = chrome.runtime.lastError;
    running.delete(tabId);
    if (!terminal) save(tabId, {status:'error', message: error ? '本机程序连接失败：' + error.message : '下载进程已中断，请重试。', url});
  });
  port.postMessage({action:'download', url, format});
}
chrome.runtime.onMessage.addListener((msg, sender, reply) => {
  if (sender.id !== chrome.runtime.id) return;
  if (msg.action === 'checkNative') {
    chrome.runtime.sendNativeMessage(HOST, {action:'diagnose'}, response => {
      const error=chrome.runtime.lastError;
      reply(error ? {status:'error',message:'本机程序连接失败：'+error.message} : (response || {status:'error',message:'本机程序未返回响应'}));
    });
    return true;
  }
  if (msg.action === 'identify') { reply({tabId:sender.tab?.id}); return; }
  if (msg.action === 'start') {
    const tabId = sender.tab?.id ?? msg.tabId;
    if (!Number.isInteger(tabId)) return;
    start(tabId, msg.url, 'mp3');
    reply({ok:true});
  } else if (msg.action === 'reveal') {
    const port = connect();
    port.onMessage.addListener(() => port.disconnect());
    port.onDisconnect.addListener(() => { void chrome.runtime.lastError; });
    port.postMessage({action:'reveal', path:msg.path});
    reply({ok:true});
  }
});
