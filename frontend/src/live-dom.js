// Retain map cells, decoded portraits, focus, scroll positions and active animations.
const keys=['data-hotbar-slot','data-battle-cell','data-battle-unit','data-battle-object','data-battle-terrain','data-combat-mode','data-combat-action','data-tile-action','data-context-action','data-prep-unit','data-prep-defense','data-prep-remove','data-battle-zoom','data-roster','data-roster-page','data-roster-collection','data-building','data-char'];
const transient=['is-walking','is-attacking','is-hit'];
const rendered=new WeakMap();
const trackedAnimations=new WeakMap();
function key(node){
  if(node.nodeType!==1)return null;
  if(node.id)return `id:${node.id}`;
  if(node.hasAttribute('data-x')&&node.hasAttribute('data-y'))return `grid:${node.getAttribute('data-x')},${node.getAttribute('data-y')}`;
  for(const name of keys)if(node.hasAttribute(name))return `${name}:${node.getAttribute(name)}`;
  const cls=node.classList[0];return cls?`${node.tagName}:${cls}`:null;
}
function compatible(a,b){return a?.nodeType===b.nodeType&&(b.nodeType!==1||a.tagName===b.tagName)}
function attributes(node,fresh){
  for(const attr of [...node.attributes])if(!fresh.hasAttribute(attr.name)&&!(node.tagName==='DIALOG'&&attr.name==='open'))node.removeAttribute(attr.name);
  for(const attr of fresh.attributes){
    let value=attr.value;
    if(attr.name==='class')for(const cls of transient)if(node.classList.contains(cls)&&!fresh.classList.contains(cls))value+=` ${cls}`;
    if(node.getAttribute(attr.name)!==value)node.setAttribute(attr.name,value);
  }
}
function children(parent,fresh){
  const old=[...parent.childNodes],used=new Set(),indexed=new Map();
  for(const node of old){const k=key(node);if(k){if(!indexed.has(k))indexed.set(k,[]);indexed.get(k).push(node)}}
  let cursor=parent.firstChild;
  for(const incoming of [...fresh.childNodes]){
    const k=key(incoming);
    let node=k?indexed.get(k)?.find(n=>!used.has(n)&&compatible(n,incoming)):old.find(n=>!used.has(n)&&!key(n)&&compatible(n,incoming));
    if(!node)node=incoming.cloneNode(true);
    used.add(node);
    if(node!==cursor)parent.insertBefore(node,cursor);
    if(node.nodeType===1){attributes(node,incoming);children(node,incoming)}
    else if(node.nodeValue!==incoming.nodeValue)node.nodeValue=incoming.nodeValue;
    cursor=node.nextSibling;
  }
  for(const node of old)if(!used.has(node)&&!node.hasAttribute?.('data-live-overlay'))node.remove();
}
export function patchLiveHTML(root,html){
  const previous=rendered.get(root);
  if(previous?.html===html&&previous.first===root.firstChild)return;
  const template=root.ownerDocument.createElement('template');template.innerHTML=html;
  children(root,template.content);
  root.dispatchEvent(new CustomEvent('portrait-framing-update',{bubbles:true}));
  rendered.set(root,{html,first:root.firstChild});
}
export function captureMovingPositions(field){
  const positions=new Map();
  for(const token of field?.querySelectorAll('.battle-token.is-walking')||[]){
    const rect=token.getBoundingClientRect();positions.set(token.dataset.battleUnit,{x:rect.x+rect.width/2,y:rect.y+rect.height/2});
  }
  return positions;
}
export function restartWalking(token,position){
  for(const animation of token.getAnimations())animation.cancel();
  if(!position)return null;
  const rect=token.getBoundingClientRect();return {x:position.x-rect.x-rect.width/2,y:position.y-rect.y-rect.height/2};
}
export function trackBattleAnimation(token,animation,className,onFinish=()=>{}){
  let active=trackedAnimations.get(token);
  if(!active){active=new Map();trackedAnimations.set(token,active)}
  active.set(className,animation);token.classList.add(className);
  const finish=()=>{
    if(active.get(className)!==animation)return;
    active.delete(className);token.classList.remove(className);onFinish();
  };
  animation.addEventListener('finish',()=>{finish();animation.cancel()},{once:true});
  animation.addEventListener('cancel',finish,{once:true});
}
