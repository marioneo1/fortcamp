export function attackCommand(action,targetId,preview){
  return {action,target_id:targetId,...(preview?.move_to?{move_to:{...preview.move_to}}:{})};
}
export function nextCombatMode(action,nextMode,currentMode){
  if(nextMode)return nextMode;
  return ['attack','subdue','skill','throw','end_turn','guard','leave','use_item'].includes(action)?'move':currentMode;
}
export function approachDescription(preview){
  return preview?.move_to?`Move ${preview.movement_cost} movement point${preview.movement_cost===1?'':'s'} first · `:'';
}
