const fs=require('fs');const {createCanvas,loadImage}=require('@napi-rs/canvas');const sharp=require('sharp');const {options,validateImage}=require('../cli.cjs');const opt=options(),D=opt.output;
(async()=>{await validateImage(opt.input+'/H10-original-disk-clean.png');if(opt.host)await validateImage(opt.host);const c=createCanvas(1920,1080),x=c.getContext('2d');x.drawImage(await loadImage(opt.input+'/H10-original-disk-clean.png'),0,0);
function text(t,px,py,size,color,weight='normal'){x.font=`${weight} ${size}px "Noto Sans CJK SC"`;x.fillStyle=color;x.strokeStyle='rgba(3,5,7,.8)';x.lineWidth=3;x.lineJoin='round';x.strokeText(t,px,py);x.fillText(t,px,py);}
text('约46亿年前',72,82,26,'#cab79d');text('形成中的太阳与盘',70,143,45,'#eee9e1','bold');text('原创三维艺术示意 · 非比例 · 非流体动力学模拟',73,185,23,'#aaa9a5');
text('太阳还在形成，行星的生长也已经开始。',90,1000,36,'#eee9e1');
if(opt.host)x.drawImage(await loadImage(opt.host),0,0);else text('无主持人测试 · 非最终合成',72,235,23,'#aaa9a5');
fs.writeFileSync(D+'/H10-original-disk-review.png',c.toBuffer('image/png'));await sharp(D+'/H10-original-disk-review.png').resize(960,540).toFile(D+'/H10-original-disk-preview.png');})().catch(e=>{console.error(e.message);process.exitCode=1;});
