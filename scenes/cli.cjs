const fs=require('fs'),path=require('path');
exports.options=function(){
 const args=process.argv.slice(2),o={};
 if(args.includes('--help')){console.log('Required: --input DIR --output NEW_DIR [--host PNG]');process.exit(0);}
 for(let i=0;i<args.length;i+=2){if(!['--input','--output','--host'].includes(args[i])||!args[i+1])throw Error('Unknown or missing option: '+args[i]);o[args[i].slice(2)]=path.resolve(args[i+1]);}
 if(!o.input||!o.output)throw Error('--input and --output are required');
 if(fs.existsSync(o.output)&&fs.readdirSync(o.output).length)throw Error('Output must be new or empty');
 fs.mkdirSync(o.output,{recursive:true});
 console.log(o.host?'Using caller-supplied private host locally':'NO-HOST TEST: no substitute character is generated');
 return o;
};
exports.validateImage=async function(file){const m=await require('sharp')(file).metadata();if(m.width!==1920||m.height!==1080)throw Error('Expected unchanged 1920x1080 image: '+file);};
