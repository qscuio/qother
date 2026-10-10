const {execFileSync}=require('child_process'),fs=require('fs'),path=require('path');
for(const name of ['cli.cjs','original-protoplanetary-disk/compose_review.cjs','reference-layouts/compose_eso.cjs','reference-layouts/compose_gaia.cjs']){
 const file=path.join(__dirname,name);execFileSync(process.execPath,['--check',file]);
 if(name!=='cli.cjs')execFileSync(process.execPath,[file,'--help']);
 const text=fs.readFileSync(file,'utf8');if(text.includes('/work'+'space/')||/data:image\/\w+;base64,[A-Za-z0-9+/]{100}/.test(text))throw Error('Embedded private path/image: '+name);
}
console.log('4 syntax checks, 3 CLI help checks and public-source scans passed');
