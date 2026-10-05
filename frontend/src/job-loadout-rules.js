export function loadoutSelection(current,id,capacity=5){
  if(current.includes(id))return current.filter(key=>key!==id);
  return current.length<capacity?[...current,id]:current;
}
