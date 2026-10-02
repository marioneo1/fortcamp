const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let queue=Promise.resolve();
export function confirmAction(options){
 const result=queue.then(()=>showConfirmation(options));queue=result.catch(()=>false);return result;
}
function showConfirmation({title,message,details=[],confirmLabel='Confirm',danger=false}){
 return new Promise(resolve=>{
  const previous=document.activeElement,dialog=document.createElement('dialog');let finished=false;
  dialog.className='game-confirmation';dialog.setAttribute('aria-labelledby','confirmation-title');dialog.setAttribute('aria-describedby','confirmation-description');
  dialog.innerHTML=`<form method="dialog"><header><span>CONFIRM ACTION</span><button type="button" data-confirm-cancel aria-label="Close confirmation">×</button></header><h2 id="confirmation-title">${esc(title)}</h2><p id="confirmation-description">${esc(message)}</p>${details.length?`<dl>${details.map(([label,value])=>`<div><dt>${esc(label)}</dt><dd>${esc(value)}</dd></div>`).join('')}</dl>`:''}<footer><button type="button" data-confirm-cancel>Cancel</button><button type="submit" data-confirm-submit class="${danger?'danger':'primary'}">${esc(confirmLabel)}</button></footer></form>`;
  const finish=accepted=>{if(finished)return;finished=true;dialog.close();dialog.remove();if(previous?.isConnected)previous.focus({preventScroll:true});resolve(accepted)};
  dialog.querySelectorAll('[data-confirm-cancel]').forEach(button=>button.onclick=()=>finish(false));
  dialog.querySelector('form').onsubmit=event=>{event.preventDefault();finish(true)};
  dialog.oncancel=event=>{event.preventDefault();finish(false)};
  let backdrop=false;dialog.onpointerdown=event=>{backdrop=event.target===dialog};dialog.onpointerup=event=>{if(backdrop&&event.target===dialog)finish(false)};
  document.body.append(dialog);dialog.showModal();dialog.querySelector('footer [data-confirm-cancel]').focus();
 });
}
