import './lighting-lab.css';
import {lightingAtMinute,arrivalMinute,createMapLighting} from './battle-lighting.js';
export {lightingAtMinute} from './battle-lighting.js';

export function previewLights(view) {
  const sources=[...(view.terrain||[]),...(view.decorations||[]),...Object.values(view.objects||{})];
  const unique=new Map();
  for(const item of sources){
    const art=String(item.sprite||item.kind||'');
    if(!Number.isFinite(item.x)||!Number.isFinite(item.y)||item.destroyed||item.hp===0)continue;
    if(art.includes('campfire_lit')||item.kind==='cookfire')unique.set(`${item.x},${item.y}`,{x:item.x,y:item.y});
  }
  return [...unique.values()].slice(0,16);
}

export function createLightingLab({openBattleLab}) {
  let panel=null,field=null,view=null,enabled=false,minute=12,timer=null,lights=true,shadows=true,allowed=false;
  let clock=null,receivedAt=0,tick=null;
  const illumination=createMapLighting();
  function stop(){if(timer)clearInterval(timer);timer=null;panel?.querySelector('[data-light-play]')?.setAttribute('aria-pressed','false');}
  function paint(){
    if(!field?.isConnected||!view)return;
    const preview=allowed&&panel&&!panel.hidden;
    const current=preview?minute:arrivalMinute(clock,(clock?.server_now||0)+(performance.now()-receivedAt)/1000);
    const state=illumination.paint(field,current,{neutral:preview&&!enabled,shadows});
    const {night}=state;
    if(lights&&!(preview&&!enabled)&&night>0){
      const glow=field.querySelector('.lighting-preview-lights')||document.createElement('div');glow.className='lighting-preview-lights';glow.setAttribute('aria-hidden','true');
      glow.style.opacity=String(Math.min(1,night));
      glow.style.background=previewLights(view).map(p=>`radial-gradient(ellipse at ${(p.x+.5)/view.width*100}% ${(p.y+.5)/view.height*100}%, #ffc07565 0%, #ed8d282a 5%, transparent 15%)`).join(',')||'none';
      if(!glow.isConnected)field.append(glow);
    }else field.querySelector('.lighting-preview-lights')?.remove();
  }
  function update(){
    paint();if(!panel)return;
    panel.querySelector('[data-light-time]').value=minute;
    const state=lightingAtMinute(minute);
    panel.querySelector('output').textContent=!enabled?'Original map':state.phase[0].toUpperCase()+state.phase.slice(1);
    panel.querySelector('[data-light-status]').textContent=allowed&&field?'Previewing this test map. Close to restore its saved arrival lighting.':'Choose a Battle Lab map to preview lighting.';
    panel.querySelector('[data-light-enable]').checked=enabled;
  }
  return {
    mount(nextField,nextView,previewAllowed){
      if(field!==nextField)field?.querySelector('.lighting-preview-lights')?.remove();
      field=nextField;view=nextView;allowed=previewAllowed;
      if(!allowed){stop();if(panel)panel.hidden=true;enabled=false;shadows=true;lights=true;}
      if(clock?.server_now!==nextView?.lighting?.server_now||clock?.arrived_at!==nextView?.lighting?.arrived_at)receivedAt=performance.now();
      clock=nextView?.lighting;
      illumination.mount(field,view);update();
      if(!tick)tick=setInterval(()=>{if(!timer&&field?.isConnected&&!document.hidden&&!document.getElementById('mission-modal')?.classList.contains('hidden'))paint();},2000);
    },
    open(){
      if(!panel){
        panel=document.createElement('section');panel.className='lighting-lab-panel';panel.setAttribute('aria-label','Battle Lab lighting');
        panel.innerHTML=`<header><div><small>DEVELOPMENT PREVIEW</small><h3>Battle Lab Lighting</h3></div><button data-light-close aria-label="Close lighting preview">×</button></header><p data-light-status></p><div class="lighting-presets"><button data-light-preset="12">Day</button><button data-light-preset="29">Dusk</button><button data-light-preset="42">Night</button><button data-light-preset="59">Dawn</button></div><label>Time in the 60-minute cycle <output></output><input data-light-time type="range" min="0" max="60" step="0.1" aria-label="Preview time"></label><div class="lighting-options"><label><input data-light-enable type="checkbox"> Apply lighting</label><label><input data-light-lamps type="checkbox" checked> Campfire glow</label></div><footer><button data-light-map>Choose test map</button><button data-light-play aria-pressed="false">Play cycle · 30s</button></footer><small>Day: 30 min · Night: 30 min. This tester runs faster and changes no gameplay.</small>`;
        document.body.append(panel);
        const shadowLabel=document.createElement('label');shadowLabel.innerHTML='<input data-light-shadows type="checkbox" checked> Directional shadows';panel.querySelector('.lighting-options').append(shadowLabel);
        panel.querySelector('[data-light-shadows]').onchange=e=>{shadows=e.target.checked;update();};
        panel.querySelector('[data-light-close]').onclick=()=>{stop();enabled=false;panel.hidden=true;paint();};
        panel.querySelector('[data-light-map]').onclick=()=>openBattleLab();
        panel.querySelector('[data-light-time]').oninput=e=>{stop();minute=Number(e.target.value);enabled=true;update();};
        panel.querySelectorAll('[data-light-preset]').forEach(button=>button.onclick=()=>{stop();minute=Number(button.dataset.lightPreset);enabled=true;update();});
        panel.querySelector('[data-light-enable]').onchange=e=>{enabled=e.target.checked;update();};
        panel.querySelector('[data-light-lamps]').onchange=e=>{lights=e.target.checked;update();};
        panel.querySelector('[data-light-play]').onclick=e=>{if(timer){stop();return;}enabled=true;e.currentTarget.setAttribute('aria-pressed','true');const start=performance.now(),from=minute;timer=setInterval(()=>{minute=(from+(performance.now()-start)/500)%60;update();},250);};
        const header=panel.querySelector('header');
        header.onpointerdown=e=>{if(e.target.closest('button'))return;const rect=panel.getBoundingClientRect(),dx=e.clientX-rect.left,dy=e.clientY-rect.top;header.setPointerCapture(e.pointerId);header.onpointermove=ev=>{panel.style.left=`${Math.max(0,Math.min(innerWidth-panel.offsetWidth,ev.clientX-dx))}px`;panel.style.top=`${Math.max(0,Math.min(innerHeight-panel.offsetHeight,ev.clientY-dy))}px`;panel.style.right='auto';};header.onpointerup=header.onpointercancel=()=>{header.onpointermove=null;};};
      }
      panel.hidden=false;enabled=true;update();
    },
  };
}
