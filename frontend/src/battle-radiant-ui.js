export function radiantMarkup(b,escape){
 const e=b.radiant_encounter;
 if(e?.state!=='pending')return '';
 return `<div class="mercenary-notice-overlay"><section role="dialog" aria-modal="true" aria-label="Unexpected encounter"><div class="eyebrow">UNEXPECTED ENCOUNTER</div><h2>${escape(e.title)}</h2><p>${escape(e.text)}</p><p class="muted">${escape(e.reward)}</p><button data-radiant-choice="continue" class="primary">Enter the battlefield</button></section></div>`;
}
