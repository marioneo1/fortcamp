export function furyMarkup(unit,{compact=false}={}){
 if(!unit||unit.fury_cap!==5||unit.conscious===false||unit.alive===false)return '';
 const value=Math.max(0,Math.min(5,Number(unit.fury)||0));
 return `<span class="fury-meter ${compact?'compact':''}" role="img" aria-hidden="false" aria-label="Fury ${value} of 5" title="Fury ${value}/5. Enemy damage to HP grants 1; Bloodfury can grant 2. Spend Fury on Barbarian skills.">${compact?'':`<small>FURY <b>${value}/5</b></small>`}<span class="fury-segments">${Array.from({length:5},(_,i)=>`<i class="${i<value?'filled':''}"></i>`).join('')}</span></span>`;
}
