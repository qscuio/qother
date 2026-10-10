const fs=require('fs'),sharp=require('sharp');const {createCanvas,loadImage}=require('@napi-rs/canvas');const {options,validateImage}=require('../cli.cjs');const opt=options(),D=opt.output;
(async()=>{if(opt.host)await validateImage(opt.host);const host=opt.host?await loadImage(opt.host):null;let manifest=[];
for(const q of [
{id:'H09-R1-cloud',src:'eso1303a',yf:.255,title:'恒星诞生的气尘云',status:'Lupus 3 观测图 · 同类环境，不是太阳出生云',credit:'ESO/F. Comeron',focus:'审阅重点：暗云轮廓、细丝与背景恒星的遮挡关系'},
{id:'H10-R2-disk',src:'eso1436f',yf:.052,title:'原行星盘的空间层次',status:'ESO艺术示意 · 非太阳形成历史的观测记录',credit:'ESO/L. Calçada',focus:'审阅重点：斜视盘面、近远层次与中央区域'}]){
const p=opt.input+'/'+q.src+'.jpg',m=await sharp(p).metadata(),w=m.width,h=Math.round(w*9/16),top=Math.min(Math.round(m.height*q.yf),m.height-h);let img=await sharp(p).extract({left:0,top,width:w,height:h}).resize(1920,1080).png().toBuffer();fs.writeFileSync(D+'/'+q.id+'-crop.png',img);
const c=createCanvas(1920,1080),x=c.getContext('2d');x.drawImage(await loadImage(img),0,0);
let g=x.createLinearGradient(0,0,0,280);g.addColorStop(0,'rgba(0,0,0,.72)');g.addColorStop(1,'rgba(0,0,0,0)');x.fillStyle=g;x.fillRect(0,0,1920,280);
g=x.createLinearGradient(0,850,0,1080);g.addColorStop(0,'rgba(0,0,0,0)');g.addColorStop(1,'rgba(0,0,0,.72)');x.fillStyle=g;x.fillRect(0,850,1920,230);
function text(t,a,b,z,col='#f2eee8',weight='normal'){x.font=`${weight} ${z}px "Noto Sans CJK SC"`;x.fillStyle=col;x.strokeStyle='rgba(9,8,8,.8)';x.lineWidth=2;x.lineJoin='round';x.strokeText(t,a,b);x.fillText(t,a,b);}
text('形成历史 · 构图参考候选',64,61,24,'#d4c7b8');text(q.title,62,126,46,'#faf6ef','bold');text(q.status,64,175,28,'#e4d9c9');x.textAlign='right';text(q.credit,1856,55,23);text('来源 ESO · CC BY 4.0',1856,91,20,'#d1cbc3');text('裁切与叠字，源图未重绘',1856,125,19,'#c7c0b8');x.textAlign='left';text(q.focus,64,985,32);text(q.id+' · 静态参考，不代表同一对象的连续演化',64,1033,23,'#cac4bb');if(host)x.drawImage(host,0,0);else text('无主持人测试',64,215,23);
fs.writeFileSync(D+'/'+q.id+'.png',c.toBuffer('image/png'));await sharp(D+'/'+q.id+'.png').resize(480,270).toFile(D+'/'+q.id+'-thumb.png');manifest.push({...q,width:m.width,height:m.height,crop:{left:0,top,width:w,height:h},output:[1920,1080],host_supplied:!!host,transform:'crop resize only; independent text gradient and optional unchanged host overlay',not_new_3d_render:true});}
fs.writeFileSync(D+'/reference-manifest.json',JSON.stringify(manifest,null,2));})().catch(e=>{console.error(e.message);process.exitCode=1;});
