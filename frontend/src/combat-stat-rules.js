// Rank scales allocated attributes once; callers add gear/proficiency/perks after.
export function rankedAttribute(value,rank,percentages){
 const percent=percentages?.[rank]??100;
 return Math.floor((Math.max(1,Number(value)||1)*percent+50)/100);
}
