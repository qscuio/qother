// Functional local Chromium playback QA, with no seeks or frame interpolation.
// This verifies playback/decode and captures actual presented frames; it is not a claim of subjective film quality.
const fs=require('fs');const path=require('path');const {pathToFileURL}=require('url');
const argv=process.argv.slice(2),opt={};
if(argv.includes('--help')){console.log('--movie MP4 --output NEW_DIR [--chromium EXECUTABLE]');process.exit(0);}
for(let i=0;i<argv.length;i+=2){if(!['--movie','--output','--chromium'].includes(argv[i])||!argv[i+1])throw Error('Invalid option');opt[argv[i].slice(2)]=path.resolve(argv[i+1]);}
if(!opt.movie||!opt.output||!fs.statSync(opt.movie).isFile())throw Error('--movie and --output required');
const {chromium}=require('playwright');
(async()=>{
 const out=opt.output,movie='source.mp4';fs.mkdirSync(out,{recursive:false});fs.copyFileSync(opt.movie,path.join(out,movie),fs.constants.COPYFILE_EXCL);
 fs.writeFileSync(path.join(out,'local-player.html'),`<!doctype html><meta charset="utf-8"><style>html,body{margin:0;background:black}video{display:block;width:1280px;height:720px}</style><video id="v" preload="auto" muted playsinline src="${movie}"></video>`);
 const browser=await chromium.launch({headless:true,...(opt.chromium?{executablePath:opt.chromium}:{}),args:['--autoplay-policy=no-user-gesture-required']});
 try {
 const page=await browser.newPage({viewport:{width:1280,height:720}});await page.goto(pathToFileURL(path.join(out,'local-player.html')).href);
 await page.evaluate(async()=>{const v=document.getElementById('v');window.presented=[];window.events=[];for(const e of ['playing','waiting','stalled','error','ended'])v.addEventListener(e,()=>window.events.push({event:e,time:v.currentTime,wall:performance.now()}));if(v.readyState<2)await new Promise((ok,no)=>{const timer=setTimeout(()=>no(new Error('Media loadeddata timeout after 10 seconds')),10000);v.addEventListener('loadeddata',()=>{clearTimeout(timer);ok()},{once:true});v.addEventListener('error',()=>{clearTimeout(timer);no(new Error('Media load failed'))},{once:true})});const cb=(now,m)=>{window.presented.push({mediaTime:m.mediaTime,presentedFrames:m.presentedFrames,expectedDisplayTime:m.expectedDisplayTime});if(!v.ended)v.requestVideoFrameCallback(cb)};v.requestVideoFrameCallback(cb);window.playStart=performance.now();await v.play()});
 for(let i=0;i<3;i++){await page.waitForTimeout(500);await page.screenshot({path:path.join(out,`actual-playback-${i+1}.png`)});}
 await page.waitForFunction(()=>document.getElementById('v').ended,null,{timeout:10000});
 const result=await page.evaluate(()=>{const v=document.getElementById('v'),q=v.getVideoPlaybackQuality();return{playback:'local unpaused playback',currentTime:v.currentTime,duration:v.duration,width:v.videoWidth,height:v.videoHeight,ended:v.ended,paused:v.paused,totalVideoFrames:q.totalVideoFrames,droppedVideoFrames:q.droppedVideoFrames,corruptedVideoFrames:q.corruptedVideoFrames,presented:window.presented,events:window.events,elapsedWallMilliseconds:performance.now()-window.playStart,subjectiveCinematicQuality:'not established by this functional playback test'}});
 result.browserVersion=browser.version();result.browserExecutable=opt.chromium||'Playwright default';
 fs.writeFileSync(path.join(out,'browser-playback-QA.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));
 if(!result.ended||result.width!==1280||result.height!==720||Math.abs(result.duration-2)>.01||result.droppedVideoFrames!==0)process.exitCode=1;
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
