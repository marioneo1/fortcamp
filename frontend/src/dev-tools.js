import './lighting-lab.css';

export function createDevTools({battle,portraits,walls}) {
  let dialog;
  return {open(){
    if(!dialog){
      dialog=document.createElement('dialog');dialog.className='dev-tools-panel';dialog.setAttribute('aria-label','Developer Tools');
      dialog.innerHTML=`<header><h2>Developer Tools</h2><button data-dev-close aria-label="Close Developer Tools">×</button></header><p>Labs and visual previews in one place. Battle Lab uses temporary characters and leaves your save unchanged.</p><div class="dev-tools-grid"><button data-dev-tool="battle"><b>Battle Lab</b><span>Test missions, parties, map variations and lighting.</span></button><button data-dev-tool="portraits"><b>Portrait Lab</b><span>Review portraits and adjust their framing.</span></button><button data-dev-tool="walls"><b>Wall Kit Lab</b><span>Inspect building pieces and wall joins.</span></button></div>`;
      document.body.append(dialog);
      dialog.querySelector('[data-dev-close]').onclick=()=>dialog.close();
      const actions={battle,portraits,walls};
      dialog.querySelectorAll('[data-dev-tool]').forEach(button=>button.onclick=()=>{dialog.close();actions[button.dataset.devTool]();});
      dialog.onclick=e=>{if(e.target!==dialog)return;const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close();};
    }
    if(!dialog.open)dialog.showModal();
  }};
}
