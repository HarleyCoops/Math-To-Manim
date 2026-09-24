/* Orthographic 3D projection. Geometry remains 3:4:6; the camera only rotates. */
'use strict';
const canvas = document.querySelector('#space');
const ctx = canvas.getContext('2d');
const inputs = ['width', 'depth', 'height'].map(id => document.getElementById(id));
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const state = {a:3,b:4,c:6,yaw:-.7,pitch:.38,zoom:1,orbit:!reducedMotion.matches,step:3};
let w=1,h=1,last=0,drag=null,orbitPhase=0;
const colors = {teal:'#75e4d4',violet:'#b8a5ed',gold:'#f7ca77',muted:'#61738e'};
const fmt = n => Number.isInteger(n) ? String(n) : n.toFixed(2);
function syncOrbit(){const b=document.querySelector('#orbit');b.textContent=state.orbit?'Pause orbit':'Resume orbit';b.setAttribute('aria-pressed',String(state.orbit));}
function update(){
  [state.a,state.b,state.c]=inputs.map(i=>Number(i.value));
  inputs.forEach(i=>document.getElementById(`${i.id}-value`).textContent=i.value);
  const {a,b,c}=state,d2=a*a+b*b,d=Math.sqrt(d2),l2=d2+c*c,L=Math.sqrt(l2);
  document.querySelector('#length').innerHTML=`${L.toFixed(2)}<small> units</small>`;
  document.querySelector('#compare').textContent=`The edge walk is ${a+b+c} units.`;
  document.querySelector('#floor-equation').textContent=`d² = ${a}² + ${b}² = ${d2}`;
  document.querySelector('#space-equation').textContent=`L² = ${d2} + ${c}² = ${l2}`;
  document.querySelector('#result-equation').textContent=Number.isInteger(L)?`L = √${l2} = ${L}`:`L = √${l2} ≈ ${L.toFixed(2)}`;
  canvas.setAttribute('aria-label',`Box ${a} by ${b} by ${c}. Floor diagonal ${fmt(d)}. Interior diagonal ${L.toFixed(2)}. Edge walk ${a+b+c}.`);
}
function project(p){
  let [x,y,z]=[p[0]-state.a/2,p[1]-state.b/2,p[2]-state.c/2];
  const X=x*Math.cos(state.yaw)-y*Math.sin(state.yaw),Y=x*Math.sin(state.yaw)+y*Math.cos(state.yaw);
  const Z=z*Math.cos(state.pitch)-Y*Math.sin(state.pitch);
  const scale=Math.min(w*.64,h*.62)/Math.sqrt(state.a**2+state.b**2+state.c**2)*state.zoom;
  return [w/2+X*scale,h*.50-Z*scale,Y*Math.cos(state.pitch)+z*Math.sin(state.pitch)];
}
function line(p,q,color,width=1,dash=[]){const a=project(p),b=project(q);ctx.beginPath();ctx.moveTo(a[0],a[1]);ctx.lineTo(b[0],b[1]);ctx.strokeStyle=color;ctx.lineWidth=width;ctx.setLineDash(dash);ctx.stroke();ctx.setLineDash([]);}
function polygon(points,color){ctx.beginPath();points.map(project).forEach((p,i)=>i?ctx.lineTo(p[0],p[1]):ctx.moveTo(p[0],p[1]));ctx.closePath();ctx.fillStyle=color;ctx.fill();}
function label(point,text,color,dx=0,dy=0){const p=project(point);ctx.font='13px Segoe UI, sans-serif';ctx.textAlign='center';ctx.textBaseline='middle';const tw=ctx.measureText(text).width;ctx.fillStyle='#0b1322ee';ctx.fillRect(p[0]+dx-tw/2-7,p[1]+dy-12,tw+14,24);ctx.fillStyle=color;ctx.fillText(text,p[0]+dx,p[1]+dy);}
function draw(t){
  const dt=Math.min((t-last)/1000,.04);last=t;
  if(state.orbit&&!drag&&!document.hidden){orbitPhase+=dt*.15;state.yaw=-.7+.28*Math.sin(orbitPhase);}
  ctx.clearRect(0,0,w,h);
  const {a,b,c,step}=state,O=[0,0,0],X=[a,0,0],F=[a,b,0],T=[a,b,c];
  // Faint gridded floor: all points share z=0.
  for(let i=0;i<=a;i++)line([i,0,0],[i,b,0],'#28404b',.7);
  for(let j=0;j<=b;j++)line([0,j,0],[a,j,0],'#28404b',.7);
  polygon([O,X,F],'#75e4d418');
  if(step>=2)polygon([O,F,T],'#b8a5ed16');
  for(let z of [0,c]){line([0,0,z],[a,0,z],colors.muted);line([a,0,z],[a,b,z],colors.muted);line([a,b,z],[0,b,z],colors.muted);line([0,b,z],[0,0,z],colors.muted);}
  for(let x of [0,a])for(let y of [0,b])line([x,y,0],[x,y,c],colors.muted,1,[3,5]);
  line(O,X,colors.teal,2);line(X,F,colors.teal,2);line(O,F,colors.teal,2.5);
  const r=Math.min(a,b,c)*.13;
  line([a-r,0,0],[a-r,r,0],colors.teal,1.2);line([a-r,r,0],[a,r,0],colors.teal,1.2);
  if(step>=2){line(F,T,colors.violet,2.5);const d=Math.hypot(a,b),Q=[a-r*a/d,b-r*b/d,0],R=[Q[0],Q[1],r];line(Q,R,colors.violet,1.2);line(R,[a,b,r],colors.violet,1.2);}
  if(step>=3){ctx.shadowColor=colors.gold;ctx.shadowBlur=15;line(O,T,colors.gold,3);ctx.shadowBlur=0;}
  [O,T].forEach(p=>{const q=project(p);ctx.beginPath();ctx.arc(q[0],q[1],4,0,Math.PI*2);ctx.fillStyle=colors.gold;ctx.fill();});
  label([a/2,0,0],String(a),colors.teal,0,19);label([a,b/2,0],String(b),colors.teal,20,0);
  label([a*.5,b*.5,0],`d = ${fmt(Math.hypot(a,b))}`,colors.teal,0,24);
  if(step>=2)label([a,b,c/2],String(c),colors.violet,22,0);
  if(step>=3)label([a*.47,b*.47,c*.47],`L = ${Math.hypot(a,b,c).toFixed(2)}`,colors.gold,-15,-18);
  requestAnimationFrame(draw);
}
new ResizeObserver(()=>{const r=canvas.getBoundingClientRect(),dpr=Math.min(window.devicePixelRatio||1,2);w=r.width;h=r.height;canvas.width=w*dpr;canvas.height=h*dpr;ctx.setTransform(dpr,0,0,dpr,0,0);}).observe(canvas);
canvas.addEventListener('pointerdown',e=>{state.orbit=false;syncOrbit();drag=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId);});
canvas.addEventListener('pointermove',e=>{if(!drag)return;state.yaw+=(e.clientX-drag[0])*.008;state.pitch=Math.max(-.8,Math.min(1.1,state.pitch+(e.clientY-drag[1])*.006));drag=[e.clientX,e.clientY];});
for(const name of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(name,()=>{drag=null;});
canvas.addEventListener('wheel',e=>{e.preventDefault();state.zoom=Math.max(.65,Math.min(1.4,state.zoom-e.deltaY*.001));},{passive:false});
inputs.forEach(i=>i.addEventListener('input',update));
document.querySelector('#orbit').addEventListener('click',()=>{state.orbit=!state.orbit;syncOrbit();});
document.querySelector('#reset').addEventListener('click',()=>{state.yaw=-.7;state.pitch=.38;state.zoom=1;});
document.querySelector('#restore').addEventListener('click',()=>{inputs.forEach((i,n)=>i.value=[3,4,6][n]);update();});
document.querySelectorAll('.step').forEach(b=>b.addEventListener('click',()=>{state.step=Number(b.dataset.step);document.querySelectorAll('.step').forEach(s=>{const selected=s===b;s.classList.toggle('active',selected);s.setAttribute('aria-pressed',String(selected));});}));
reducedMotion.addEventListener('change',e=>{if(e.matches){state.orbit=false;syncOrbit();}});
update();syncOrbit();requestAnimationFrame(draw);
