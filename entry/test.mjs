import {test} from "node:test";
import assert from "node:assert/strict";
import {DatabaseSync} from "node:sqlite";
import {randomBytes} from "node:crypto";
import {mkdtemp,readFile,rm} from "node:fs/promises";
import {tmpdir} from "node:os";
import path from "node:path";
import worker from "./dist/server/index.js";
const key=()=>randomBytes(24).toString("hex");
const origin="https://example.test";
function d1(raw){return {
 prepare(sql){return {bind(...args){return {
    async first(){return raw.prepare(sql).get(...args)||null;},
    async all(){return {results:raw.prepare(sql).all(...args)};},
    async run(){return {meta:{changes:raw.prepare(sql).run(...args).changes}};}
 };}};},
 async batch(statements){raw.exec("BEGIN");try{const out=[];for(const s of statements)out.push(await s.run());raw.exec("COMMIT");return out;}catch(e){raw.exec("ROLLBACK");throw e;}}
};}
test("public forms, private receipts, organization and persistence",async t=>{
 const dir=await mkdtemp(path.join(tmpdir(),"zs-entry-test-")),file=path.join(dir,"entry.sqlite");
 let raw=new DatabaseSync(file);raw.exec("PRAGMA foreign_keys=ON");raw.exec(await readFile(new URL("drizzle/0000_entry.sql",import.meta.url),"utf8"));
 t.after(async()=>{raw.close();await rm(dir,{recursive:true,force:true});});
 const adminKey=key(),env={DB:d1(raw),OPS_ADMIN_TOKEN:adminKey,OPS_OWNER_EMAIL:"owner@example.test"};
 async function api(endpoint,bearer,payload={},expected=200,extra={}){const headers={"Content-Type":"application/json",Origin:origin,...extra};if(bearer)headers.Authorization="Bearer "+bearer;
  const r=await worker.fetch(new Request(origin+endpoint,{method:"POST",headers,body:JSON.stringify(payload)}),env);const b=await r.json();assert.equal(r.status,expected,endpoint+" "+JSON.stringify(b));return b;}
 const a=key(),survey=key(),member=key();
 await t.test("public entry lists five routes and login has no data",async()=>{
  const r=await worker.fetch(new Request(origin),env);const html=await r.text();assert.equal(r.status,200);
  for(const id of ["enroll","availability","survey","format","calendar"])assert.ok(html.includes('href="#'+id+'"'));
  assert.match(html,/zsc-arena/);assert.ok(!html.includes("<!--ARENA-->"));
  assert.equal((await worker.fetch(new Request(origin+"/api/admin/list"),env)).status,404);
  assert.equal((await worker.fetch(new Request(origin+"/winter-arena.webp"),env)).headers.get("Content-Type"),"image/webp");
  const staff=await worker.fetch(new Request(origin+"/admin"),env);assert.match(await staff.text(),/signin-with-chatgpt/);
  await api("/api/admin/list",null,{},403);await api("/api/admin/list",key(),{},403);
  await api("/api/admin/list",null,{},403,{"oai-authenticated-user-email":"owner@example.test"});
  await api("/api/admin/list",null,{},200,{"oai-authenticated-user-email":"owner@example.test","oai-authenticated-user-id":"signed-in-owner"});
  await api("/api/admin/list",null,{},403,{Origin:"https://wrong.test","oai-authenticated-user-email":"owner@example.test","oai-authenticated-user-id":"signed-in-owner"});
 });
 let captain,mem;
 await t.test("registration retry, private cross-device access and cross-origin rejection",async()=>{
  await api("/api/enroll",a,{name:"QA captain",contact:"test",route:"captain",teamName:"QA team"},403,{Origin:"https://wrong.test"});
  captain=await api("/api/enroll",a,{name:"QA captain",contact:"test",route:"captain",teamName:"QA team"});
  assert.ok(captain.captain&&captain.joinCode.length===24);
  const replay=await api("/api/enroll",a,{name:"QA captain",contact:"updated"});assert.equal(replay.id,captain.id);assert.equal(replay.joinCode,captain.joinCode);
  mem=await api("/api/enroll",member,{name:"QA member",contact:"member",route:"member",joinCode:captain.joinCode});assert.equal(mem.teamId,captain.teamId);assert.ok(!mem.joinCode);
  await api("/api/me",key(),{},404);await api("/api/me",null,{},401);await api("/api/withdraw",a,{},409);
  const list=await api("/api/admin/list",adminKey);assert.equal(list.players.length,2);assert.equal(list.teams.length,1);assert.ok(!JSON.stringify(list).includes(a));
 });
 await t.test("anonymous survey optional, retry does not duplicate, opt-out",async()=>{
  await api("/api/survey",survey,{},400);await api("/api/survey",survey,{motivation:"exchange"});await api("/api/survey",survey,{mode:"solo",note:"你好"});
  let list=await api("/api/admin/list",adminKey);assert.equal(list.surveys.length,1);assert.equal(list.surveys[0].note,"你好");assert.ok(!("name" in list.surveys[0]));
  await api("/api/survey/withdraw",survey);list=await api("/api/admin/list",adminKey);assert.equal(list.surveys.length,0);
 });
 const teams=[captain];const teamKeys=[a];const common=[{date:"2026-12-19",start:600,end:780},{date:"2026-12-20",start:600,end:900}];
 await t.test("confirmed windows saved only by captain and after a process restart",async()=>{
  await api("/api/availability",member,{confirmed:true,windows:common},403);await api("/api/availability",a,{confirmed:false,windows:common},400);
  await api("/api/availability",a,{confirmed:true,windows:[{date:"2026-12-32",start:600,end:900}]},400);
  const merged=await api("/api/availability",a,{confirmed:true,windows:[...common,common[0]]});assert.deepEqual(merged.windows,common);
  raw.close();raw=new DatabaseSync(file);raw.exec("PRAGMA foreign_keys=ON");env.DB=d1(raw);
  const persisted=await api("/api/me",a);assert.equal(persisted.contact,"updated");assert.deepEqual(persisted.windows,common);
 });
 await t.test("six group series across simultaneous pairings, owner-only assignment, lock",async()=>{
  await api("/api/availability",a,{confirmed:true,windows:common,rosterCategories:["intl-high"],extras:{finals:"yes"}});
  await api("/api/availability",a,{confirmed:true,windows:common,rosterCategories:["pending","intl-high"]},400);
  assert.equal((await api("/api/me",member)).rosterCategories,undefined);
  for(let n=1;n<4;n++){const k=key();teamKeys.push(k);teams.push(await api("/api/enroll",k,{name:"cap"+n,contact:"test",route:"captain",teamName:"队"+n}));await api("/api/availability",k,{confirmed:true,windows:common,rosterCategories:n===1?["overseas"]:["domestic-uni"]});}
  const ids=teams.map(x=>x.teamId);const s=await api("/api/admin/suggest",adminKey,{teams:ids});assert.equal(s.duration,120);assert.equal(s.rounds.length,3);assert.equal(s.rounds[0].date,"2026-12-19");
  assert.equal(s.crossGroupCandidates.length,1);assert.equal(s.crossGroupCandidates[0].round,3);
  const teamExport=(await api("/api/admin/list",adminKey)).teams.find(x=>x.id===captain.teamId);assert.deepEqual(teamExport.roster_categories,["intl-high"]);assert.equal(teamExport.extras.finals,"yes");
  const compact=await api("/api/admin/suggest",adminKey,{teams:ids,duration:90});assert.equal(compact.rounds[0].end-compact.rounds[0].start,90);
  await api("/api/admin/pool",adminKey,{teams:ids,rounds:[s.rounds[0],s.rounds[0],s.rounds[0]]},400);
  const g=await api("/api/admin/pool",adminKey,{teams:ids,rounds:s.rounds});assert.equal(new Set(g.pairings.flat().map(pair=>pair.join("-"))).size,6);
  await api("/api/admin/pool",adminKey,{teams:ids,rounds:s.rounds},409);
  await api("/api/availability",a,{confirmed:true,windows:common},409);await api("/api/withdraw",member,{},409);
  const me=await api("/api/me",member);assert.equal(me.schedule.length,3);assert.equal(new Set(me.schedule.map(x=>x.opponent)).size,3);
 });
 await t.test("staff can create five-person team from solo applicants",async()=>{
  const people=[],keys=[];for(let i=0;i<5;i++){const k=key();keys.push(k);people.push(await api("/api/enroll",k,{name:"散人"+i,contact:"synthetic",route:"solo"}));}
  const ids=people.map(x=>x.id);await api("/api/admin/assign",adminKey,{players:ids.slice(0,4),name:"散人队"},400);
  const made=await api("/api/admin/assign",adminKey,{players:ids,name:"散人队"});assert.ok(made.id);const cap=await api("/api/me",keys[0]);assert.ok(cap.captain&&cap.joinCode);
  const player=await api("/api/me",keys[1]);assert.equal(player.team,"散人队");assert.equal(player.captain,false);
  await api("/api/admin/assign",adminKey,{players:ids,name:"又组队"},409);
 });
 await t.test("test captain and survey can be removed without residue",async()=>{
  const tester=key();const p=await api("/api/enroll",tester,{name:"QA",contact:"test",route:"captain",teamName:"QA removal"});await api("/api/availability",tester,{confirmed:true,windows:common});await api("/api/withdraw",tester);
  await api("/api/me",tester,{},404);const list=await api("/api/admin/list",adminKey);assert.ok(!list.players.some(e=>e.id===p.id));assert.ok(!list.teams.some(e=>e.id===p.teamId));
 });
});
