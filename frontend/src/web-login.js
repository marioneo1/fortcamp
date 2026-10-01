const escape=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export const webSessionKey=cfg=>`fortcamp-web:${cfg.session_namespace}`;
export const activitySessionKey=(cfg,guild)=>`fortcamp-session:${cfg.session_namespace}:${guild}`;

export async function restoreWebSession(api,storage,cfg){
 let cached;try{cached=JSON.parse(storage.getItem(webSessionKey(cfg))||'null')}catch{return null}
 if(!cached?.session_token)return null;
 try{
  const current=await api('/api/state',{headers:{Authorization:`Bearer ${cached.session_token}`}});
  return {session_token:cached.session_token,identity:current.identity};
 }catch(error){
  if(error.status===403)return null;
  if(error.status!==401)throw error;
  storage.removeItem(webSessionKey(cfg));return null;
 }
}

export async function authenticateWeb(api,cfg,{storage=localStorage,location=window.location,root=document.body}={}){
 const query=new URLSearchParams(location.search);
 if(!query.has('choose_server')&&!query.has('login_error')){
  const cached=await restoreWebSession(api,storage,cfg);if(cached)return cached;
 }
 document.querySelector('#loading')?.classList.add('hidden');
 let panel=document.querySelector('#web-login');
 if(!panel){panel=document.createElement('section');panel.id='web-login';panel.className='web-login-card';root.prepend(panel)}
 return new Promise(resolve=>{
  const environment=cfg.environment==='dev'?'DEVELOPMENT · Separate test saves':'FORTCAMP WEB';
  const shell=body=>{panel.innerHTML=`<div class="eyebrow">${escape(environment)}</div><h1>Welcome to Fortcamp</h1>${body}`};
  const loginButton=()=>{
   shell(`<p>Sign in with Discord, then choose your server. Your characters and mission board are shared with the Activity in that server.</p>${query.has('login_error')?'<p class="web-login-error">Login was cancelled or expired. Please try again.</p>':''}<button id="web-signin">Sign in with Discord</button><small>Uses your Discord identity and server list. Each server has separate progress.</small>`);
   panel.querySelector('#web-signin').onclick=()=>location.assign('/api/web/login');
  };
  const load=async()=>{
   if(!cfg.web_login_enabled){shell('<p>Browser login needs this instance’s Discord application, bot and web origin configured.</p>');return}
   if(location.origin!==cfg.web_origin){shell(`<p>Open this environment’s website to sign in.</p><a class="web-origin-link" href="${escape(cfg.web_origin)}">Open ${escape(cfg.web_origin)}</a>`);return}
   shell('<p>Loading your Fortcamp servers…</p>');
   let data;
   try{data=await api('/api/web/servers')}catch(error){
    if(error.status===401){loginButton();return}
    shell(`<p class="web-login-error">${escape(error.message)}</p><button id="web-retry">Retry</button>`);
    panel.querySelector('#web-retry').onclick=load;return;
   }
   shell(`<p>Signed in as <strong>${escape(data.display_name)}</strong>. Choose where to play.</p><div class="web-server-list">${data.servers.map(g=>`<button class="web-server" data-web-guild="${escape(g.id)}">${g.icon?`<img src="${escape(g.icon)}" alt="">`:'<span class="web-server-monogram">'+escape(g.name.slice(0,1))+'</span>'}<span><strong>${escape(g.name)}</strong><small>${g.registered?'Continue or create your character':'Run /register with Fortcamp in this server first'}</small></span><b aria-hidden="true">→</b></button>`).join('')||'<p>No shared servers have this instance’s Fortcamp bot installed. Join a server with the bot, then refresh your Discord login.</p>'}</div><p id="web-login-message" class="web-login-error" role="status"></p><div class="web-login-controls"><button id="web-retry">Refresh list</button><button id="web-refresh-login">Refresh Discord login</button><button id="web-logout">Sign out</button></div><small>Changing servers never moves characters or items between them.</small>`);
   panel.querySelector('#web-retry').onclick=load;
   panel.querySelector('#web-refresh-login').onclick=()=>location.assign('/api/web/login');
   panel.querySelector('#web-logout').onclick=async()=>{try{await api('/api/web/logout',{method:'POST'});storage.removeItem(webSessionKey(cfg));loginButton()}catch(e){panel.querySelector('#web-login-message').textContent=e.message}};
   panel.querySelectorAll('[data-web-guild]').forEach(button=>button.onclick=async()=>{
    panel.querySelectorAll('[data-web-guild]').forEach(b=>b.disabled=true);
    try{
     const result=await api('/api/web/select',{method:'POST',body:JSON.stringify({guild_id:button.dataset.webGuild})});
     try{storage.setItem(webSessionKey(cfg),JSON.stringify(result))}catch{}
     if(query.has('choose_server')||query.has('login_error'))history.replaceState(null,'',location.pathname);
     panel.remove();resolve(result);
    }catch(e){panel.querySelector('#web-login-message').textContent=e.message;panel.querySelectorAll('[data-web-guild]').forEach(b=>b.disabled=false)}
   });
  };
  load();
 });
}

export function mountWebAccountControls(api,cfg){
 if(document.querySelector('#web-account-controls'))return;
 const controls=document.createElement('div');controls.id='web-account-controls';controls.className='web-account-controls';
 controls.innerHTML=`${cfg.environment==='dev'?'<strong class="web-dev-badge">DEV · Test saves</strong>':''}<button id="web-change-server">Change server</button><button id="web-sign-out">Sign out</button>`;
 document.querySelector('.topbar')?.append(controls);
 controls.querySelector('#web-change-server').onclick=()=>window.location.assign('/?choose_server=1');
 controls.querySelector('#web-sign-out').onclick=async()=>{try{await api('/api/web/logout',{method:'POST'});localStorage.removeItem(webSessionKey(cfg));window.location.assign('/')}catch(e){alert(e.message)}};
 const creator=document.querySelector('#creator');
 if(creator){const back=document.createElement('button');back.className='web-creator-back';back.textContent='Choose another server';back.onclick=()=>window.location.assign('/?choose_server=1');creator.append(back)}
}
