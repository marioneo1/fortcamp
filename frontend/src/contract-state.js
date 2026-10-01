export function applyContractUpdate(lists,mission){
  if(!mission?.id)return lists;
  const replace=rows=>[mission,...rows.filter(row=>row.id!==mission.id)];
  const privateRows=lists.privateContracts.filter(row=>row.id!==mission.id);
  return {
    pool:lists.pool?{...lists.pool,missions:lists.pool.missions.filter(row=>row.id!==mission.id||mission.status==='available')}:lists.pool,
    privateContracts:['reserved','available'].includes(mission.status)?[mission,...privateRows]:privateRows,
    activeMissions:replace(lists.activeMissions),
  };
}
