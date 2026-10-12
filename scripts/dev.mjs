import http from 'node:http';
import {readFile} from 'node:fs/promises';
const source=await readFile(new URL('../dist/server/index.js',import.meta.url),'utf8');
const worker=(await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'))).default;
http.createServer(async(req,res)=>{try{const response=await worker.fetch(new Request('http://localhost:8000'+req.url,{method:req.method}),{},{});res.writeHead(response.status,Object.fromEntries(response.headers));res.end(Buffer.from(await response.arrayBuffer()))}catch{res.writeHead(500);res.end('Server error')}}).listen(8000,'127.0.0.1',()=>console.log('Local: http://127.0.0.1:8000'));
