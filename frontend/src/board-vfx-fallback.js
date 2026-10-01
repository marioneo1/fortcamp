import {BOARD_TEXTURES,vfxTextures} from './vfx-textures.js';
const THEMES=new Set(Object.keys(BOARD_TEXTURES));
export function createBoardVFX({document=globalThis.document,window=globalThis.window,requestFrame=fn=>window.requestAnimationFrame(fn),cancelFrame=id=>window.cancelAnimationFrame(id),random=Math.random,textures=vfxTextures}={}){
  const canvas=document.createElement('canvas');canvas.className='board-regional-backdrop';canvas.setAttribute('aria-hidden','true');document.body.prepend(canvas);
  const ctx=canvas.getContext('2d'),motion=window.matchMedia('(prefers-reduced-motion: reduce)');
  let theme=null,active=false,frame=null,last=0,time=0,width=1,height=1,disposed=false,particles=[];
  const palette={goblin:[177,202,88],undead:[206,199,215],arcane:[126,194,255],beast:[220,171,83],starfall:[185,139,250]};
  function resize(){width=Math.max(1,window.innerWidth);height=Math.max(1,window.innerHeight);const scale=Math.min(1,1920/width);canvas.width=Math.round(width*scale);canvas.height=Math.round(height*scale);ctx?.setTransform(scale,0,0,scale,0,0);particles=Array.from({length:Math.min(38,Math.max(18,Math.round(width*height/40000)))},()=>({x:random(),y:random(),speed:.6+random()*.9,size:3+random()*6,phase:random()*Math.PI*2}));if(active)draw(time)}
  function stop(){if(frame!==null)cancelFrame(frame);frame=null}
  function sprite(name,x,y,size,alpha,rotation=0){
    const image=textures.get(name);if(!image?.naturalWidth||!image.naturalHeight)return false;
    const h=size*image.naturalHeight/image.naturalWidth;
    ctx.save();ctx.translate(x,y);ctx.rotate(rotation);ctx.globalAlpha=alpha;
    ctx.drawImage(image,-size/2,-h/2,size,h);ctx.restore();return true;
  }
  function glow(x,y,radius,color,alpha){const gradient=ctx.createRadialGradient(x,y,0,x,y,radius);gradient.addColorStop(0,`rgba(${color},${alpha})`);gradient.addColorStop(1,`rgba(${color},0)`);ctx.fillStyle=gradient;ctx.fillRect(x-radius,y-radius,radius*2,radius*2)}
  function draw(t){
    if(!ctx)return;ctx.clearRect(0,0,width,height);if(!theme||!active)return;
    const color=palette[theme].join(',');
    // Large soft textures sit at the edges, leaving the readable card centers calm.
    if(theme==='undead')for(let i=0;i<3;i++)sprite(i%2?'mist_violet':'mist_gray',width*(.08+i*.43)+Math.sin(t*.09+i)*45,height*(.2+i*.3),420,.19,Math.sin(t*.05+i)*.15);
    if(theme==='beast')sprite('wind_curl',width*.88,height*.5+Math.sin(t*.08)*45,320,.09);
    if(theme==='goblin')sprite('dust_gold',width*.1,height*.7,310,.1);
    if(theme==='arcane'){
      for(let k=0;k<3;k++){
        ctx.beginPath();for(let i=0;i<=40;i++){const u=i/40,x=u*width,y=height*(.18+k*.34)+Math.sin(u*6+t*.32+k*2.3)*height*.065;i?ctx.lineTo(x,y):ctx.moveTo(x,y)}
        ctx.strokeStyle=`rgba(${color},.08)`;ctx.lineWidth=18;ctx.stroke();ctx.strokeStyle=`rgba(${color},.18)`;ctx.lineWidth=3;ctx.stroke();
      }
    }
    if(theme==='starfall'){
      for(let k=0;k<2;k++){ctx.beginPath();ctx.ellipse(width*(k?.92:.08),height*(k?.22:.76),Math.min(width,height)*(.3+k*.09),Math.min(width,height)*(.3+k*.09)*.62,t*.035*(k?-1:1),0,Math.PI*1.65);ctx.strokeStyle=`rgba(${color},.14)`;ctx.lineWidth=3;ctx.stroke()}
    }
    if(theme==='undead'){for(let i=0;i<3;i++)glow(width*(.1+i*.38)+Math.sin(t*.08+i)*70,height*(.25+i*.26),Math.min(width*.3,330),color,.12+Math.sin(t*.2+i)*.025)}
    if(theme==='arcane'){for(let i=0;i<2;i++)glow(width*(i?.87:.12),height*(.3+i*.4),220,color,.12+Math.sin(t*.5+i)*.05)}
    if(theme==='starfall'){glow(width*.18,height*.65,310,color,.14+Math.sin(t*.3)*.04);glow(width*.86,height*.2,260,'83,189,201',.075+Math.sin(t*.24)*.025);const phase=(t%14)/14;if(phase>.3&&phase<.38){const a=(phase-.3)/.08,x=width*(1.05-a*1.15),y=height*(.08+a*.6);ctx.save();const trail=ctx.createLinearGradient(x+125,y-60,x,y);trail.addColorStop(0,`rgba(${color},0)`);trail.addColorStop(1,`rgba(${color},.6)`);ctx.strokeStyle=trail;ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(x+125,y-60);ctx.lineTo(x,y);ctx.stroke();glow(x,y,6,'232,241,255',.8);ctx.restore()}}
    for(const p of particles){
      const falling=theme==='beast'||theme==='undead',travel=t*p.speed*(theme==='beast'?16:theme==='undead'?9:5),y=((p.y*height+(falling?travel:-travel))%height+height)%height,x=((p.x*width+Math.sin(t*.3+p.phase)*(theme==='beast'?34:12)+(theme==='beast'?t*p.speed*8:0))%width+width)%width;
      ctx.save();ctx.translate(x,y);ctx.globalAlpha=theme==='beast'?.4:theme==='undead'?.45:.28+.13*Math.sin(t*.5+p.phase);ctx.fillStyle=`rgb(${color})`;
      const index=particles.indexOf(p),names=BOARD_TEXTURES[theme];
      const name=theme==='beast'?names[index%6]:theme==='undead'?names[index%2]:theme==='goblin'?names[index%5===0?1:0]:null;
      const textured=name&&sprite(name,0,0,theme==='beast'?18+p.size*1.5:theme==='undead'?6+p.size*.7:12+p.size,theme==='beast'?.55:theme==='undead'?.42:.4,theme==='beast'?p.phase+t*.25:p.phase*.15);
      if(textured){ctx.restore();continue}
      if(theme==='beast'){ctx.rotate(p.phase+t*.4);ctx.beginPath();ctx.moveTo(-p.size,0);ctx.bezierCurveTo(-p.size,-p.size,p.size,-p.size,p.size,0);ctx.bezierCurveTo(p.size,p.size,-p.size,p.size,-p.size,0);ctx.fill();ctx.strokeStyle='rgba(100,65,29,.65)';ctx.beginPath();ctx.moveTo(-p.size,0);ctx.lineTo(p.size,0);ctx.stroke()}
      else if(theme==='arcane'){ctx.rotate(p.phase+t*.1);ctx.strokeStyle=`rgb(${color})`;ctx.lineWidth=1;ctx.strokeRect(-2,-2,4,4)}
      else{ctx.beginPath();ctx.ellipse(0,0,theme==='undead'?1.2:1.5,theme==='undead'?2.4:1.5,p.phase,0,Math.PI*2);ctx.fill()}
      ctx.restore();
    }
  }
  function tick(stamp){frame=null;if(!active||disposed||document.hidden||motion.matches)return;if(stamp-last>=1000/24){time+=Math.min(.1,(stamp-last)/1000);last=stamp;draw(time)}frame=requestFrame(tick)}
  function resume(){stop();if(!active||document.hidden||disposed)return;draw(time);if(!motion.matches){last=window.performance.now();frame=requestFrame(tick)}}
  function visibility(){if(document.hidden)stop();else resume()}
  function motionChange(){resume()}
  window.addEventListener('resize',resize);document.addEventListener('visibilitychange',visibility);motion.addEventListener('change',motionChange);resize();
  return {
    setEvent(event,enabled=true){const next=THEMES.has(event?.theme)&&event?.id!=='general'?event.theme:null,wanted=!!(next&&enabled);if(next===theme&&wanted===active)return;theme=next;active=wanted;canvas.dataset.theme=theme||'general';canvas.hidden=!active;document.body.classList.toggle('board-vfx-active',active);if(!active){stop();ctx?.clearRect(0,0,width,height)}else {resume();textures.load(BOARD_TEXTURES[next]).then(()=>{if(!disposed&&active&&theme===next&&!document.hidden)draw(time)})}},
    dispose(){disposed=true;stop();window.removeEventListener('resize',resize);document.removeEventListener('visibilitychange',visibility);motion.removeEventListener('change',motionChange);canvas.remove();document.body.classList.remove('board-vfx-active')},
  };
}
