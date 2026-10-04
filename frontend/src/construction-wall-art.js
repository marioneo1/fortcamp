import kits from './construction-wall-art.json' with {type:'json'};
import {anchors} from './construction-geometry.js';

export function wallArt(piece,kit){
 const sources=kits[kit]?.sources;if(!sources||!piece)return null;
 let source,flipX=false,flipY=false;
 if(piece.startsWith('horizontal_')){
  source=piece.includes('both_posts')?'horizontal_both_posts':piece.includes('_post')?'horizontal_one_post':'horizontal_plain';
  flipX=piece.includes('right_post');flipY=piece.endsWith('_south');
 }else if(piece.startsWith('vertical_')){
  source=piece.includes('both_posts')?'vertical_both_posts':piece.includes('_post')?'vertical_one_post':'vertical_plain';
  flipX=piece.endsWith('_west');flipY=piece.includes('bottom_post');
 }else if(piece.startsWith('corner_')){
  source='corner';flipX=piece.endsWith('_east');flipY=piece.includes('_south_');
 }else if(piece.startsWith('gate_horizontal')){source='gate_horizontal';flipY=piece.endsWith('_south')}
 else if(piece.startsWith('gate_vertical')){source='gate_vertical';flipX=piece.endsWith('_west')}
 return sources[source]?{...sources[source],source,flipX,flipY}:null;
}

export function wallArtImage(wall,kit){
 const art=wallArt(wall.piece,kit);if(!art||wall.broken||wall.open&&wall.shape==='gate')return '';
 const [ax,ay]=anchors[wall.anchor],horizontal=art.source.startsWith('horizontal')||art.source==='gate_horizontal';
 const origin=art.source==='corner'?[0,0]:horizontal?[0,.5]:[.5,0];
 const x=wall.x+ax-.5+origin[0]-art.origin[0]/art.span,y=wall.y+ay-.5+origin[1]-art.origin[1]/art.span;
 const cx=wall.x+ax,cy=wall.y+ay;
 return `<g data-wall-original="${art.source}" transform="translate(${cx} ${cy}) scale(${art.flipX?-1:1} ${art.flipY?-1:1}) translate(${-cx} ${-cy})"><image href="/assets/combat-terrain/${art.file}" x="${x}" y="${y}" width="${art.size/art.span}" height="${art.size/art.span}" preserveAspectRatio="xMidYMid meet"/></g>`;
}
