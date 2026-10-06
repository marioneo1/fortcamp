// Grounded, pure top-down painted trap props; deterministic scatter per tile.
export function caltropsArtwork(cells,x,y){
 const variants=['caltrops_rust_a','caltrops_rust_b','caltrops_steel'];
 return cells.map(c=>{const px=(c.x-x)*100,py=(c.y-y)*100,name=variants[((c.x*7+c.y*13)%variants.length+variants.length)%variants.length];return `<g class="caltrop-cluster" style="transform-origin:${px+50}px ${py+50}px"><image href="/assets/tactical-props-v1/${name}.png" x="${px+14}" y="${py+14}" width="72" height="72" preserveAspectRatio="xMidYMid meet"/></g>`}).join('');
}
