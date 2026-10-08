// Coalesce pointer bursts without adding a unit-switch timer.
export function createHoverScheduler(paint,{requestFrame=globalThis.requestAnimationFrame,cancelFrame=globalThis.cancelAnimationFrame}={}){
 let frame=null,latest=null;
 return {
  show(...args){latest=args;if(frame!==null)return;frame=requestFrame(()=>{frame=null;const args=latest;latest=null;if(args)paint(...args)})},
  cancel(){if(frame!==null)cancelFrame(frame);frame=null;latest=null}
 };
}
