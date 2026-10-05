// Coalesce provisional destinations, then deliver one committed action.
export function createLatestMovement(){
  let pending=null, action=null;
  return {
    remember(command,context){if(!action)pending={command:{...command},context}},
    peek(context){return pending?.context===context?{...pending.command}:null},
    take(context){const entry=pending;pending=null;return entry?.context===context?entry.command:null},
    commit(command,context,nextMode=null){
      if(action)return false;
      action={command:{...command},context,nextMode};return true;
    },
    hasAction(context){return action?.context===context},
    takeAction(context){const entry=action;action=null;return entry?.context===context?{command:entry.command,nextMode:entry.nextMode}:null},
    clear(){pending=null;action=null},
  };
}
