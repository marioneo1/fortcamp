"""Actual frontend startup with synthetic browser-login API responses, no player data."""
import json
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from backend.game import new_game,public_content

source=(ROOT/'frontend/src/main.js').read_text(encoding='utf-8')
source=source.replace("from './","from '/frontend/src/").replace("import './","import '/frontend/src/").replace('import "./','import "/frontend/src/')
source=re.sub(r'import \{ DiscordSDK \} from [^;]+;','',source)
states={gid:new_game({'name':'Character in server '+gid}) for gid in ['10','20']}
fixtures=json.dumps({'states':states,'content':public_content()},ensure_ascii=True)
startup='const webFixture='+fixtures+';\n'+'''
localStorage.removeItem('fortcamp-web:qa-web-dev');
window.webRequests=[];window.unexpectedWebApi=[];let chosenGuild='10';
const realFetch=window.fetch.bind(window);
window.fetch=async(url,options={})=>{
 const path=String(url);if(!path.startsWith('/api/'))return realFetch(url,options);
 window.webRequests.push({path,body:options.body,headers:options.headers});
 let data;
 const me=()=>({guild_id:chosenGuild,user_id:'qa-user',display_name:'QA player',guild_admin:false});
 if(path==='/api/config')data={environment:'dev',session_namespace:'qa-web-dev',web_origin:location.origin,web_login_enabled:true,dev_bypass_auth:false,debug_mode:false,discord_client_id:'qa-app'};
 else if(path==='/api/web/servers')data={display_name:'QA player',servers:[{id:'10',name:'Friends <guild>',registered:true},{id:'20',name:'Second server',registered:true}]};
 else if(path==='/api/web/select'){chosenGuild=JSON.parse(options.body).guild_id;data={session_token:'fixture-'+chosenGuild,identity:me()}}
 else if(path==='/api/state')data={exists:true,identity:me(),state:webFixture.states[chosenGuild]};
 else if(path==='/api/content')data=webFixture.content;
 else if(path==='/api/missions/pool')data={rank:'E',missions:[],event:{id:'general'},next_refresh:Date.now()/1000+1000,registered_players:2};
 else if(path==='/api/private-contracts'||path==='/api/missions/active')data={missions:[]};
 else if(path==='/api/web/logout')data={ok:true};
 else {window.unexpectedWebApi.push(path);throw new Error('Unexpected fixture API: '+path)}
 return new Response(JSON.stringify(data),{status:200,headers:{'Content-Type':'application/json'}});
};
init();
'''
source=source.replace('\ninit();','\n'+startup)
folder=ROOT/'staging-ui/web-login';folder.mkdir(parents=True,exist_ok=True)
(folder/'preview.js').write_text(source,encoding='utf-8')
page=(ROOT/'frontend/index.html').read_text(encoding='utf-8')
page=re.sub(r'<script type="module" src="/src/main.js[^>]+></script>','<script type="module" src="/staging-ui/web-login/preview.js"></script>',page)
(folder/'preview.html').write_text(page,encoding='utf-8')
print(folder/'preview.html')
