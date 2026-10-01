// Send only the newest uncommitted destination after the in-flight move finishes.
export function createLatestMovement(){
  let pending=null;
  return {
    remember(command,context){pending={command:{...command},context}},
    peek(context){return pending?.context===context?{...pending.command}:null},
    take(context){const entry=pending;pending=null;return entry?.context===context?entry.command:null},
    clear(){pending=null},
  };
}
