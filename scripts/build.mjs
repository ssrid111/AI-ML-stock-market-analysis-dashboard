import {readFile,mkdir,writeFile} from 'node:fs/promises';
const assets={};
for(const [name,type] of [['index.html','text/html'],['style.css','text/css'],['app.js','application/javascript']]) assets['/'+name]={body:await readFile(new URL('../public/'+name,import.meta.url),'utf8'),type:type+'; charset=utf-8'};
const worker=await readFile(new URL('../worker/index.js',import.meta.url),'utf8');
await mkdir(new URL('../dist/server/',import.meta.url),{recursive:true});
await mkdir(new URL('../dist/.openai/',import.meta.url),{recursive:true});
await writeFile(new URL('../dist/server/index.js',import.meta.url),'const ASSETS = '+JSON.stringify(assets)+';\n'+worker);
await writeFile(new URL('../dist/.openai/hosting.json',import.meta.url),await readFile(new URL('../.openai/hosting.json',import.meta.url)));
console.log('Built Worker with embedded dashboard assets');
