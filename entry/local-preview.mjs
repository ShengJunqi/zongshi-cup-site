import http from "node:http";
import {DatabaseSync} from "node:sqlite";
import {readFile} from "node:fs/promises";
import worker from "./dist/server/index.js";
const db=new DatabaseSync(":memory:");db.exec("PRAGMA foreign_keys=ON");db.exec(await readFile(new URL("./drizzle/0000_entry.sql",import.meta.url),"utf8"));
const binding={prepare(sql){return {bind(...args){return {
 async first(){return db.prepare(sql).get(...args)||null;},
 async all(){return {results:db.prepare(sql).all(...args)};},
 async run(){return {meta:{changes:db.prepare(sql).run(...args).changes}};}
 };}};},async batch(operations){db.exec("BEGIN");try{const out=[];for(const op of operations)out.push(await op.run());db.exec("COMMIT");return out;}catch(e){db.exec("ROLLBACK");throw e;}}};
const env={DB:binding,OPS_ADMIN_TOKEN:process.env.ZS_PREVIEW_ADMIN};
const port=Number(process.argv[2]||8791),host="127.0.0.1";
http.createServer(async(req,res)=>{
 try{const chunks=[];for await(const b of req)chunks.push(b);const method=req.method,headers=new Headers(req.headers);
 for(const name of ["oai-authenticated-user-id","oai-authenticated-user-email"])headers.delete(name);
 const request=new Request("http://"+host+":"+port+req.url,{method,headers,body:["GET","HEAD"].includes(method)?undefined:Buffer.concat(chunks)});
 const r=await worker.fetch(request,env);res.writeHead(r.status,Object.fromEntries(r.headers));res.end(Buffer.from(await r.arrayBuffer()));}catch{res.writeHead(500);res.end();}
}).listen(port,host,()=>console.log("Local synthetic QA only: http://"+host+":"+port));
