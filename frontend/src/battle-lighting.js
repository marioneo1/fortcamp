// Shared by actual maps and the fast developer preview. No turn/stat changes.
export const PHASE_WINDOWS={day:[0,28],dusk:[28,30],night:[30,58],dawn:[58,60]};
export function phaseAt(minute){return minute<28?'day':minute<30?'dusk':minute<58?'night':'dawn';}
const clamp=(value,low,high)=>Math.max(low,Math.min(high,value));
export function arrivalMinute(lighting,serverNow){
  if(!lighting)return 12;
  const window=PHASE_WINDOWS[lighting.phase]||PHASE_WINDOWS.day;
  const elapsed=Math.max(0,serverNow-lighting.arrived_at)/60;
  return clamp(lighting.arrival_minute+elapsed,window[0],window[1]-.001);
}

// RGB multiplication and a small blue lift, preserving each pixel's alpha.
const KEYS=[
  [0,[1.03,1,.93,0,0,0]], [12,[1,1,1,0,0,0]],
  [27.999,[1.04,.91,.79,.015,.005,0]],
  [29,[.77,.76,.98,.015,.015,.04]],
  [30,[.53,.65,.96,.01,.018,.055]],
  [44,[.58,.71,1.03,.012,.022,.06]],
  [58,[.53,.64,.95,.01,.018,.045]],
  [59,[.78,.78,.99,.018,.012,.04]], [60,[1.03,1,.93,0,0,0]],
];
export function lightingAtMinute(value){
  const minute=((Number(value)||0)%60+60)%60;
  const index=KEYS.findIndex(key=>key[0]>minute),left=KEYS[Math.max(0,index-1)],right=KEYS[index];
  let blend=(minute-left[0])/(right[0]-left[0]);blend=blend*blend*(3-2*blend);
  const rgb=left[1].map((v,i)=>v+(right[1][i]-v)*blend),phase=phaseAt(minute);
  const night=phase==='night'?1:phase==='dusk'?(minute-28)/2:phase==='dawn'?(60-minute)/2:0;
  const angle=phase==='day'?(-65+minute/28*130):phase==='dusk'?65+(minute-28)*7.5:phase==='night'?(minute<33?80-(minute-30)/3*115:-35+(minute-33)/25*35):-(minute-58)/2*65;
  const shadow=phase==='day'?.55+Math.abs(minute-14)/14*.6:phase==='dusk'?1.15-(minute-28)*.5:phase==='night'?.15+Math.min(1,(minute-30)/3)*.2:.35+(minute-58)*.4;
  return {minute,phase,night,rgb,angle,shadow};
}

export function colorMatrix(rgb){
  const [r,g,b,ro,go,bo]=rgb;
  return `${r} 0 0 0 ${ro} 0 ${g} 0 0 ${go} 0 0 ${b} 0 ${bo} 0 0 0 1 0`;
}

export function largeProp(element){
  if(element.classList.contains('ground-edging')||element.classList.contains('wall-connector')||element.classList.contains('destroyed'))return false;
  const art=element.style.getPropertyValue('--battle-prop');
  return /tree|oak|pine|birch/i.test(art)||element.classList.contains('prop-structure');
}

export function propShadowKind(element){
  if(element.classList.contains('ground-edging')||element.classList.contains('wall-connector')||element.classList.contains('destroyed')||element.classList.contains('wall-cap'))return 'none';
  if(largeProp(element))return 'large';
  return /barrel|crate|chest|rack|workbench|anvil|handcart|wagon|table|stocks|cage|boulder/i.test(element.style.getPropertyValue('--battle-prop'))?'small':'none';
}
export function footprintIndoors(x,y,width,height,indoor){
  for(let yy=y;yy<y+height;yy++)for(let xx=x;xx<x+width;xx++)if(!indoor.has(`${xx},${yy}`))return false;
  return width>0&&height>0;
}

export function createMapLighting(){
  let matrix=null;
  function ensureFilter(){
    if(matrix)return;
    const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');
    svg.classList.add('map-lighting-defs');svg.setAttribute('aria-hidden','true');
    svg.innerHTML='<defs><filter id="battle-light-grade" x="-100%" y="-100%" width="300%" height="300%" color-interpolation-filters="sRGB"><feColorMatrix type="matrix"/></filter></defs>';
    document.body.append(svg);matrix=svg.querySelector('feColorMatrix');
  }
  return {
    mount(field,view){
      if(!field)return;
      const indoor=new Set((view?.lighting?.indoor_cells||[]).map(cell=>cell.join(',')));
      field.querySelectorAll('.has-prop-art').forEach(prop=>{
        // Artwork rotates in its pseudo-element; counter-rotate the offset so
        // every silhouette still casts its shadow in the same world direction.
        const rotatedArt=prop.classList.contains('multi-cell-asset');
        const rotation=(rotatedArt?parseFloat(prop.style.getPropertyValue('--asset-rotation'))||0:0)*Math.PI/180;
        const mirror=rotatedArt?parseFloat(prop.style.getPropertyValue('--asset-mirror-y'))||1:1;
        prop.style.setProperty('--prop-shadow-x',`calc(var(--sun-shadow-x) * ${Math.cos(rotation)} + var(--sun-shadow-y) * ${Math.sin(rotation)})`);
        prop.style.setProperty('--prop-shadow-y',`calc((var(--sun-shadow-y) * ${Math.cos(rotation)} - var(--sun-shadow-x) * ${Math.sin(rotation)}) * ${mirror})`);
        const kind=propShadowKind(prop),x=Number(prop.style.gridColumnStart)-1,y=Number(prop.style.gridRowStart)-1;
        const width=Number(prop.style.gridColumnEnd.replace('span','').trim())||1,height=Number(prop.style.gridRowEnd.replace('span','').trim())||1;
        prop.classList.toggle('lighting-large-prop',kind==='large');
        prop.classList.toggle('lighting-small-prop',kind==='small');
        prop.classList.toggle('lighting-indoor-prop',footprintIndoors(x,y,width,height,indoor));
      });
    },
    paint(field,minute,{shadows=true,neutral=false}={}){
      if(!field)return;
      ensureFilter();const state=lightingAtMinute(minute);
      matrix.setAttribute('values',colorMatrix(neutral?[1,1,1,0,0,0]:state.rgb));
      field.classList.toggle('map-lit',!neutral);field.classList.toggle('map-sun-shadows',!neutral&&shadows);
      field.dataset.lightPhase=state.phase;
      // Camera owns cell size. A preview redraw must not sample the temporary
      // pre-fit field width and leave its shadow at that size until the next tick.
      const radians=state.angle*Math.PI/180,length=.15*state.shadow;
      field.style.setProperty('--sun-shadow-x',`calc(var(--lighting-cell-size,72px) * ${Math.sin(radians)*length})`);
      field.style.setProperty('--sun-shadow-y',`calc(var(--lighting-cell-size,72px) * ${Math.cos(radians)*length})`);
      return state;
    },
  };
}
