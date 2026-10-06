// Vite 6 CSS imports require these helpers even when HMR is disabled.
// Steady play intentionally has no socket, reconnect logic, or page reload.
const styles=new Map();
export function updateStyle(id,content){
 let style=styles.get(id);
 if(!style){style=document.createElement('style');style.setAttribute('data-vite-dev-id',id);document.head.append(style);styles.set(id,style)}
 style.textContent=content;
}
export function removeStyle(id){styles.get(id)?.remove();styles.delete(id)}
export function injectQuery(url,query){
 if(!url.startsWith('.')&&!url.startsWith('/'))return url;
 const parsed=new URL(url,'http://vite.local');
 return `${url.replace(/[?#].*$/,'')}?${query}${parsed.search?'&'+parsed.search.slice(1):''}${parsed.hash}`;
}
