// Small reusable source textures made for particle effects, not edited portrait/art assets.
// Smoke has irregular density rather than the recognizable S-shaped painted mist stamp.
function hash(x,y,seed){let n=Math.imul(x,374761393)^Math.imul(y,668265263)^seed;n=Math.imul(n^(n>>>13),1274126177);return ((n^(n>>>16))>>>0)/4294967295}
function noise(x,y,seed){const ix=Math.floor(x),iy=Math.floor(y),fx=x-ix,fy=y-iy,s=fx*fx*(3-2*fx),t=fy*fy*(3-2*fy);const a=hash(ix,iy,seed),b=hash(ix+1,iy,seed),c=hash(ix,iy+1,seed),d=hash(ix+1,iy+1,seed);return (a+(b-a)*s)*(1-t)+(c+(d-c)*s)*t}
export function makeParticleTexture(name,document=globalThis.document){
  const canvas=document.createElement('canvas'),smoke=name.startsWith('fx:smoke');canvas.width=smoke?128:256;canvas.height=smoke?128:64;
  const ctx=canvas.getContext('2d');
  if(smoke){
    const seed=1949+Number(name.slice(-1))*137,data=ctx.createImageData(128,128);
    for(let y=0;y<128;y++)for(let x=0;x<128;x++){
      const nx=(x-64)/61,ny=(y-64)/61,envelope=Math.pow(Math.max(0,1-nx*nx-ny*ny),1.5);
      const density=noise(x/35,y/35,seed)*.6+noise(x/17,y/17,seed+11)*.27+noise(x/8,y/8,seed+31)*.13,i=(y*128+x)*4;
      data.data[i]=data.data[i+1]=data.data[i+2]=255;data.data[i+3]=Math.round(envelope*Math.max(0,density-.18)*290);
    }
    ctx.putImageData(data,0,0);
  }else if(name==='fx:mote'){
    canvas.width=canvas.height=64;const glow=ctx.createRadialGradient(32,32,0,32,32,31);glow.addColorStop(0,'rgba(255,255,255,1)');glow.addColorStop(.12,'rgba(255,255,255,.9)');glow.addColorStop(.4,'rgba(255,255,255,.22)');glow.addColorStop(1,'rgba(255,255,255,0)');ctx.fillStyle=glow;ctx.fillRect(0,0,64,64);
  }else{
    // Broad feathered beam for deformable meshes and short moving light streaks.
    const glow=ctx.createLinearGradient(0,0,0,64);
    if(name==='fx:flame'){
      glow.addColorStop(0,'rgba(210,57,12,0)');glow.addColorStop(.2,'rgba(240,82,15,.45)');glow.addColorStop(.4,'rgba(255,158,43,.85)');glow.addColorStop(.5,'rgba(255,226,133,1)');glow.addColorStop(.6,'rgba(255,158,43,.85)');glow.addColorStop(.8,'rgba(240,82,15,.45)');glow.addColorStop(1,'rgba(210,57,12,0)');
    }else{glow.addColorStop(0,'rgba(255,255,255,0)');glow.addColorStop(.34,'rgba(255,255,255,.04)');glow.addColorStop(.5,'rgba(255,255,255,.75)');glow.addColorStop(.66,'rgba(255,255,255,.04)');glow.addColorStop(1,'rgba(255,255,255,0)')}
    ctx.fillStyle=glow;ctx.fillRect(0,0,256,64);
    ctx.globalCompositeOperation='destination-in';const fade=ctx.createLinearGradient(0,0,256,0);fade.addColorStop(0,'rgba(255,255,255,0)');
    if(name==='fx:comet'){fade.addColorStop(.3,'rgba(255,255,255,.05)');fade.addColorStop(.7,'rgba(255,255,255,.4)');fade.addColorStop(1,'white')}
    else{fade.addColorStop(.2,'white');fade.addColorStop(.8,'white');fade.addColorStop(1,'rgba(255,255,255,0)')}
    ctx.fillStyle=fade;ctx.fillRect(0,0,256,64);
  }
  return canvas;
}
