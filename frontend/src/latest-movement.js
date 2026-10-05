// Coalesce provisional destinations, then deliver one committed action.
export function createLatestMovement(){
  let pending=null, action=null, intent=null;
  return {
    remember(command,context){if(!action){intent={command:{...command},context};pending={command:{...command},context}}},
    destination(context){return intent?.context===context?{x:intent.command.x,y:intent.command.y}:null},
    peek(context){return pending?.context===context?{...pending.command}:null},
    take(context){const entry=pending;pending=null;return entry?.context===context?entry.command:null},
    commit(command,context,nextMode=null){
      if(action)return false;
      action={command:{...command},context,nextMode};return true;
    },
    hasAction(context){return action?.context===context},
    takeAction(context){const entry=action;action=null;return entry?.context===context?{command:entry.command,nextMode:entry.nextMode}:null},
    clear(){pending=null;action=null;intent=null},
  };
}
