export function furyMarkup(unit,{compact=false}={}){
 if(!unit||unit.fury_cap!==5||unit.conscious===false||unit.alive===false)return '';
 const value=Math.max(0,Math.min(5,Number(unit.fury)||0));
 return `<span class="fury-meter ${compact?'compact':''}" role="img" aria-hidden="false" aria-label="Fury ${value} of 5" title="Fury ${value}/5. Enemy damage to HP grants 1; Bloodfury can grant 2. Spend Fury on Barbarian skills.">${compact?'':`<small>FURY <b>${value}/5</b></small>`}<span class="fury-segments">${Array.from({length:5},(_,i)=>`<i class="${i<value?'filled':''}"></i>`).join('')}</span></span>`;
}

export function comboMarkup(unit){
 if(!unit?.combo||unit.alive===false||unit.conscious===false)return '';
 const {stage,available,turns_remaining:turns}=unit.combo;
 const label={neutral:'Neutral',follow_up:'Follow-up Ready',finisher:'Finisher Ready'}[stage]||'Neutral';
 return `<span class="monk-combo stage-${stage}" role="img" aria-label="Monk combo: ${label}" title="${label}${stage==='neutral'?' · Land an opener to begin.':available?` · ${turns} personal turns remaining.`:' · Available next personal turn.'}"><span>${['neutral','follow_up','finisher'].map((s,i)=>`<em class="combo-pip ${s===stage?'lit':''}">${i+1}</em>`).join('')}</span><small>${label}${stage!=='neutral'?available?` · ${turns}t`:' · next turn':''}</small></span>`;
}
