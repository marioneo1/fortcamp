// One transform timeline per token. Delayed motions cannot overwrite earlier poses.
export function composeMotion(segments){
  const ordered=segments.slice().sort((a,b)=>a.delay-b.delay);
  const duration=Math.max(1,...ordered.map(s=>s.delay+s.duration));
  const frames=[];let last=null;
  for(const segment of ordered){
    const first=segment.frames[0];
    if(!last)frames.push({...first,offset:0});
    else frames.push({...last,offset:segment.delay/duration});
    for(let i=0;i<segment.frames.length;i++){
      const frame=segment.frames[i];
      const local=frame.offset??i/Math.max(1,segment.frames.length-1);
      frames.push({filter:'brightness(1)',opacity:1,...frame,offset:(segment.delay+local*segment.duration)/duration});
    }
    last=frames.at(-1);
  }
  return {frames,duration};
}

export function poseFrames(frames,point,unit,cw,ch){
  const x=(point.x-unit.x)*cw,y=(point.y-unit.y)*ch;
  return frames.map(frame=>({...frame,transform:`translate(${x}px,${y}px) ${frame.transform}`}));
}

export function walkingFrames(points,unit,cw,ch,scale=1,extracted=false){
  const frames=[];
  for(let i=0;i<points.length-1;i++){
    const from=points[i],to=points[i+1];
    frames.push({transform:`translate(${(from.x-unit.x)*cw}px,${(from.y-unit.y)*ch}px) scale(${scale})`,opacity:1,offset:i/(points.length-1)});
    frames.push({transform:`translate(${((from.x+to.x)/2-unit.x)*cw}px,${((from.y+to.y)/2-unit.y)*ch-3}px) scale(${scale*1.015})`,opacity:1,offset:(i+.5)/(points.length-1)});
  }
  const last=points.at(-1)||unit;
  frames.push({transform:`translate(${(last.x-unit.x)*cw}px,${(last.y-unit.y)*ch}px) scale(${scale})`,opacity:extracted?0:1,offset:1});
  return frames;
}

export function playbackDuration(timeline){
  // Floating labels can linger after control returns. Actual motion cannot.
  return Math.max(0,...timeline.filter(r=>r.event.type!=='combat_feedback').map(r=>
    r.start+Math.max(r.duration,r.event.type==='ground_impact'||r.event.type==='fighter_rally'?650:0)));
}

export function needsPlaybackLock(events,battle){
  return events.some(e=>e.type!=='movement'||e.forced||e.leap||
    battle.units?.[e.unit_id]?.team!=='player');
}

export function createPlaybackGate(now=()=>performance.now()){
  let context=null,deadline=0;
  return {
    hold(key,duration){if(key!==context){context=key;deadline=0}deadline=Math.max(deadline,now()+duration)},
    blocked(key){return key===context&&now()<deadline},
    remaining(key){return key===context?Math.max(0,deadline-now()):0},
    clear(){context=null;deadline=0},
  };
}
