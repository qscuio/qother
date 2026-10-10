const fs=require('fs');
const sharp=require('sharp');
const { createCanvas, loadImage }=require('@napi-rs/canvas');
const path=require('path');
const {options,validateImage}=require('../cli.cjs');const opt=options(),dir=opt.output;
const host=opt.host?fs.readFileSync(opt.host).toString('base64'):null;
(async()=>{
if(opt.host)await validateImage(opt.host);
for(const [time,name] of [['089','01-overall-reference'],['104','02-sun-reference']]){
await validateImage(path.join(opt.input,`source-${time}.png`));
const source=fs.readFileSync(path.join(opt.input,`source-${time}.png`)).toString('base64');
const svg=`<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080"><title>ESA原动画选帧 · 构图参考</title><desc>Official documentary frame at ${Number(time)} seconds; original frame unchanged beneath independent source label and private host layers.</desc><image id="official-frame" width="1920" height="1080" href="data:image/png;base64,${source}"/>${host?`<image id="private-host" width="1920" height="1080" href="data:image/png;base64,${host}"/>`:""}<g id="reference-disclosure" font-family="Noto Sans CJK SC, sans-serif" text-anchor="end" fill="#ededed" stroke="#101012" stroke-width="3" paint-order="stroke" stroke-linejoin="round"><text x="1872" y="48" font-size="24">${host?"ESA原动画选帧 · 构图参考":"ESA原动画选帧 · 无主持人测试"}</text><text x="1872" y="78" font-size="18">原片 ${Number(time)} 秒 · Gaia数据支持的艺术复原</text><text x="1872" y="105" font-size="16">ESA/Gaia/DPAC, Stefan Payne-Wardenaar</text></g></svg>`;
fs.writeFileSync(path.join(dir,name+'.svg'),svg);
const canvas=createCanvas(1920,1080); const ctx=canvas.getContext('2d');
// Render independent overlays only; composite over decoded source without color-profile conversion.
if(host)ctx.drawImage(await loadImage('data:image/png;base64,'+host),0,0);
ctx.textAlign='right'; ctx.textBaseline='alphabetic'; ctx.lineJoin='round'; ctx.strokeStyle='#101012'; ctx.fillStyle='#ededed'; ctx.lineWidth=3;
for (const [txt,size,y] of [[host?'ESA原动画选帧 · 构图参考':'ESA原动画选帧 · 无主持人测试',24,48],[`原片 ${Number(time)} 秒 · Gaia数据支持的艺术复原`,18,78],['ESA/Gaia/DPAC, Stefan Payne-Wardenaar',16,105]]) {ctx.font=`${size}px "Noto Sans CJK SC"`;ctx.strokeText(txt,1872,y);ctx.fillText(txt,1872,y);}
const raw = await sharp(path.join(opt.input,`source-${time}.png`)).raw().toBuffer({resolveWithObject:true});
await sharp(raw.data,{raw:{width:raw.info.width,height:raw.info.height,channels:raw.info.channels}}).composite([{input:canvas.toBuffer('image/png')}]).png().toFile(path.join(dir,name+'.png'));
console.log(name);
}

})().catch(e=>{console.error(e.message);process.exitCode=1;});
