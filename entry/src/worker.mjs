// Single-origin Cloudflare Worker. Build injects PAGE, CSS, CLIENT, STAFF.
const FIRST = "2026-12-19", LAST = "2027-01-03", GROUP_LAST = "2026-12-27";
const encoder = new TextEncoder();
class Problem extends Error { constructor(status, message){ super(message); this.status=status; } }
function fail(status,message){throw new Problem(status,message);}
const check=(ok,status,message)=>{if(!ok) fail(status,message);};
const text=(v,max,label,min=1)=>{
  check(typeof v==="string"&&v.trim().length>=min&&v.trim().length<=max,400,"请检查"+label+"。");
  return v.trim();
};
async function digest(v){return Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256",encoder.encode(v))),x=>x.toString(16).padStart(2,"0")).join("");}
function receipt(req){
  const header=req.headers.get("Authorization")||"";
  check(/^Bearer [a-f0-9]{48}$/.test(header),401,"请输入完整的私人回执。");
  return header.slice(7);
}
function response(body,status=200,type="application/json; charset=UTF-8"){
  return new Response(type.startsWith("application/json")?JSON.stringify(body):body,{status,headers:{"Content-Type":type,"Cache-Control":"no-store","X-Content-Type-Options":"nosniff","Referrer-Policy":"no-referrer","X-Robots-Tag":"noindex, nofollow","Content-Security-Policy":"default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"}});
}
async function bodyOf(req){
  check((req.headers.get("Content-Type")||"").split(";")[0].trim()==="application/json",415,"请求格式不正确。");
  const source=req.headers.get("Origin");
  check(!source||source===new URL(req.url).origin,403,"请在赛事入口提交。");
  // Limit streamed requests even when content-length is absent.
  check(Number(req.headers.get("content-length")||0)<=12288,413,"填写内容过长。");
  const stream=req.body?.getReader();let size=0;const chunks=[];
  if(stream){while(true){const {done,value}=await stream.read();if(done)break;size+=value.byteLength;if(size>12288){await stream.cancel();fail(413,"填写内容过长。");}chunks.push(value);}}
  let data;
  try{const b=new Uint8Array(size);let i=0;for(const chunk of chunks){b.set(chunk,i);i+=chunk.length;}data=JSON.parse(new TextDecoder().decode(b));}catch{fail(400,"请检查填写内容。");}
  check(data&&typeof data==="object"&&!Array.isArray(data),400,"请检查填写内容。");return data;
}
const stmt=(db,sql,...args)=>db.prepare(sql).bind(...args);
const one=(db,sql,...args)=>stmt(db,sql,...args).first();
const all=async(db,sql,...args)=>(await stmt(db,sql,...args).all()).results;
async function self(db,h){
  const p=await one(db,"SELECT e.id,e.name,e.contact,e.route,e.team_id,t.name AS team_name, t.captain,t.join_code,t.windows,t.roster_categories,t.extras,t.members_confirmed FROM entrants e LEFT JOIN teams t ON t.id=e.team_id WHERE e.receipt=?",h);
  check(p,404,"没有找到这条报名，请核对回执。");
  let schedule=[];
  if(p.team_id){
   const opponents=await all(db,"SELECT g.rounds, pt.position, t.id,t.name FROM pool_teams me JOIN pools g ON g.id=me.pool_id JOIN pool_teams pt ON pt.pool_id=g.id JOIN teams t ON t.id=pt.team_id WHERE me.team_id=? ORDER BY pt.position",p.team_id);
   if(opponents.length===4){
     const pos=opponents.findIndex(t=>t.id===p.team_id);
     schedule=JSON.parse(opponents[0].rounds).map((w,i)=>{const pair=pairings[i].find(v=>v.includes(pos));return {...w,opponent:opponents[pair.find(x=>x!==pos)].name};});
   }
  }
  return {id:p.id,name:p.name,contact:p.contact,route:p.route,teamId:p.team_id,team:p.team_name,captain:p.captain===h,joinCode:p.captain===h?p.join_code:undefined,windows:p.captain===h?JSON.parse(p.windows):undefined,rosterCategories:p.captain===h?JSON.parse(p.roster_categories):undefined,extras:p.captain===h?JSON.parse(p.extras):undefined,confirmed:p.captain===h?!!p.members_confirmed:undefined,schedule};
}
async function enroll(db,h,data){
  const name=text(data.name,36,"参赛称呼"),contact=text(data.contact,96,"联系渠道");
  const old=await one(db,"SELECT id FROM entrants WHERE receipt=?",h);
  if(old){await stmt(db,"UPDATE entrants SET name=?,contact=?,updated_at=CURRENT_TIMESTAMP WHERE receipt=?",name,contact,h).run();return self(db,h);}
  const route=data.route;
  check(["solo","captain","member"].includes(route),400,"请选择组队方式。");
  const id="p"+(await digest("player:"+h)).slice(0,24);let teamId=null, ops=[];
  if(route==="captain"){
    const label=text(data.teamName,40,"队名");
    teamId="t"+(await digest("team:"+h)).slice(0,24);
    const code=(await digest("join:"+h)).slice(0,24).toUpperCase();
    ops.push(stmt(db,"INSERT INTO teams(id,name,join_code,captain) VALUES(?,?,?,?) ON CONFLICT(id) DO NOTHING",teamId,label,code,h));
  }
  if(route==="member"){
    const code=text(data.joinCode,24,"入队码").toUpperCase();
    const team=await one(db,"SELECT id FROM teams WHERE join_code=?",code);
    check(team,400,"无法加入该队，请向队长核对入队码。");teamId=team.id;
  }
  ops.push(stmt(db,"INSERT INTO entrants(receipt,id,name,contact,route,team_id) VALUES(?,?,?,?,?,?) ON CONFLICT(receipt) DO NOTHING",h,id,name,contact,route,teamId));
  await db.batch(ops);return self(db,h);
}
function normalize(windows){
  check(Array.isArray(windows)&&windows.length>=1&&windows.length<=48,400,"请填 1 至 48 段空档。");
  const unique=new Map();
  for(const w of windows){
    check(w&&typeof w==="object"&&typeof w.date==="string"&&/^\d{4}-\d{2}-\d{2}$/.test(w.date)&&w.date>=FIRST&&w.date<=LAST,400,"日期须在本次征集范围内。");
    const real=new Date(w.date+"T00:00:00Z");
    check(!Number.isNaN(real.getTime())&&real.toISOString().slice(0,10)===w.date,400,"日期无效。");
    check(Number.isInteger(w.start)&&Number.isInteger(w.end)&&w.start>=0&&w.end<=1440&&w.start%30===0&&w.end%30===0&&w.end-w.start>=30,400,"时段须在同一天，按半小时填写。");
    unique.set(w.date+":"+w.start+":"+w.end,{date:w.date,start:w.start,end:w.end});
  }
  const merged=[];
  for(const w of [...unique.values()].sort((a,b)=>a.date.localeCompare(b.date)||a.start-b.start)){
    const last=merged.at(-1);
    if(last&&last.date===w.date&&last.end>=w.start) last.end=Math.max(last.end,w.end);
    else merged.push(w);
  }return merged;
}
async function availability(db,h,data){
  const me=await self(db,h);check(me.captain,403,"本队可用时间由队长汇总提交。");
  const windows=normalize(data.windows);check(data.confirmed===true,400,"请先确认这份时间来自同场五人。");
  const categories=data.rosterCategories??["pending"];
  check(Array.isArray(categories)&&categories.length>0&&categories.length<=4&&categories.every(k=>["intl-high","domestic-uni","overseas","pending"].includes(k))&&(!categories.includes("pending")||categories.length===1),400,"请勾选实际出场类别，或单独选择待补。");
  const extras={};for(const k of ["practice","finals"]){const value=data.extras?.[k];if(value){check(["yes","no","uncertain"].includes(value),400,"请核对附加时段选项。");extras[k]=value;}}
  const assigned=await one(db,"SELECT pool_id FROM pool_teams WHERE team_id=?",me.teamId);
  check(!assigned,409,"已生成本组对阵，改期请联系赛事工作人员。");
  const saved=await stmt(db,"UPDATE teams SET windows=?,roster_categories=?,extras=?,members_confirmed=1,updated_at=CURRENT_TIMESTAMP WHERE id=? AND captain=? AND NOT EXISTS(SELECT 1 FROM pool_teams WHERE team_id=teams.id)",JSON.stringify(windows),JSON.stringify([...new Set(categories)]),JSON.stringify(extras),me.teamId,h).run();
  check(saved.meta.changes===1,409,"本组时段已被锁定，请重新核对。");return {windows};
}
const surveyOptions={affiliation:["intl-high","domestic-uni","overseas","exchange","other"],motivation:["competition","friends","exchange","practice","watch","other"],obstacle:["timing","team","latency","mismatch","exams","none","other"],mode:["solo","team","both","watch"]};
function surveyAnswers(d){
 const result={};
 for(const [key,opts] of Object.entries(surveyOptions)){
    if(d[key]===undefined||d[key]==="")continue;
    check(opts.includes(d[key]),400,"请选择列出的调研选项。");result[key]=d[key];
 }
 if(typeof d.note==="string"&&d.note.trim())result.note=text(d.note,240,"补充意见");
 check(Object.keys(result).length>0,400,"至少选一项或留一句意见。");
 return result;
}
async function withdraw(db,h){
 const me=await self(db,h);
 const locked=me.teamId&&await one(db,"SELECT team_id FROM pool_teams WHERE team_id=?",me.teamId);
 check(!locked,409,"本队已分组，退赛请联系赛事工作人员。");
 if(me.captain){
   const sql="NOT EXISTS(SELECT 1 FROM entrants WHERE team_id=? AND receipt<>?) AND NOT EXISTS(SELECT 1 FROM pool_teams WHERE team_id=?)";
   const res=await db.batch([stmt(db,"DELETE FROM entrants WHERE receipt=? AND "+sql,h,me.teamId,h,me.teamId),stmt(db,"DELETE FROM teams WHERE captain=? AND NOT EXISTS(SELECT 1 FROM entrants WHERE team_id=teams.id) AND NOT EXISTS(SELECT 1 FROM pool_teams WHERE team_id=teams.id)",h)]);
   check(res[0].meta.changes===1,409,"队内还有队员，请先联系赛事工作人员办理队长变更。");
 }else{
   const res=await stmt(db,"DELETE FROM entrants WHERE receipt=? AND NOT EXISTS(SELECT 1 FROM pool_teams WHERE team_id=entrants.team_id)",h).run();
   check(res.meta.changes===1,409,"队伍状态已变化，请联系赛事工作人员。");
 }
 return {withdrawn:true};
}
function suggest(teams,duration){
 // Same four teams on both simultaneous courts. Prefer 120 minutes including buffer.
 const rounds=[];
 for(const w of teams[0].windows.filter(x=>x.date<=GROUP_LAST)){
  for(let start=w.start;start+duration<=w.end;start+=30){
   if(!teams.every(t=>t.windows.some(s=>s.date===w.date&&s.start<=start&&s.end>=start+duration)))continue;
   if(rounds.some(r=>r.date===w.date&&r.start<start+duration&&r.end>start))continue;
   rounds.push({date:w.date,start,end:start+duration});if(rounds.length===3)return rounds;
  }
 }return rounds;
}
const pairings=[[[0,3],[1,2]],[[0,2],[1,3]],[[0,1],[2,3]]];
async function admin(req,env,path,data){
  const owner=String(env.OPS_OWNER_EMAIL||"").trim().toLowerCase();
  const ownerSession=owner&&req.headers.get("oai-authenticated-user-id")&&((req.headers.get("oai-authenticated-user-email")||"").trim().toLowerCase()===owner);
  const tokenSet=typeof env.OPS_ADMIN_TOKEN==="string"&&env.OPS_ADMIN_TOKEN.length>=32;
  if(!owner&&!tokenSet) fail(404,"未开放。");
  const supplied=req.headers.get("Authorization")||"";
  const tokenOk=tokenSet&&supplied.startsWith("Bearer ")&&supplied.length<=520&&await digest(supplied.slice(7))===await digest(env.OPS_ADMIN_TOKEN);
  if(!tokenOk&&!(ownerSession&&req.headers.get("Origin")===new URL(req.url).origin))fail(403,"请用主办方账号登录，或提供有效的赛务密钥。");
  const db=env.DB;
  if(path==="list"){
    const [players,teams,pools,surveys]=await Promise.all([all(db,"SELECT id,name,contact,route,team_id FROM entrants ORDER BY created_at,id"),all(db,"SELECT t.id,t.name,t.windows,t.roster_categories,t.extras,t.members_confirmed,pt.pool_id FROM teams t LEFT JOIN pool_teams pt ON pt.team_id=t.id ORDER BY t.id"),all(db,"SELECT p.id,p.rounds,pt.team_id,pt.position FROM pools p JOIN pool_teams pt ON p.id=pt.pool_id ORDER BY p.id,pt.position"),all(db,"SELECT answers FROM surveys ORDER BY updated_at")]);return {players,teams:teams.map(t=>({...t,windows:JSON.parse(t.windows),roster_categories:JSON.parse(t.roster_categories),extras:JSON.parse(t.extras)})),pools:pools.map(p=>({...p,rounds:JSON.parse(p.rounds)})),surveys:surveys.map(s=>JSON.parse(s.answers))};
  }
  if(path==="assign"){
    const ids=data.players,name=text(data.name,40,"队名");
    check(Array.isArray(ids)&&ids.length===5&&new Set(ids).size===5&&ids.every(x=>typeof x==="string"&&/^p[a-f0-9]{24}$/.test(x)),400,"请选择五名不同的散人，第一位为队长。");
    const markers=ids.map(()=>"?").join(",");
    const cap=await one(db,"SELECT receipt FROM entrants WHERE id=?",ids[0]);check(cap,409,"找不到该队长。");
    const teamId="t"+(await digest("assembly:"+ids.slice().sort().join(","))).slice(0,24);
    const code=(await digest("assembly join:"+cap.receipt+teamId)).slice(0,24).toUpperCase();
    const ops=[stmt(db,"INSERT INTO teams(id,name,join_code,captain) SELECT ?,?,?,? WHERE 5=(SELECT COUNT(*) FROM entrants WHERE id IN ("+markers+") AND team_id IS NULL AND route='solo') ON CONFLICT(id) DO NOTHING",teamId,name,code,cap.receipt,...ids),stmt(db,"UPDATE entrants SET team_id=?,updated_at=CURRENT_TIMESTAMP WHERE id IN ("+markers+") AND team_id IS NULL AND EXISTS(SELECT 1 FROM teams WHERE id=?)",teamId,...ids,teamId)];
    const out=await db.batch(ops);check(out[0].meta.changes===1,409,"队伍已组过或这些选手已进入其他队。");return {id:teamId};
  }
  if(path==="pool"||path==="suggest"){
    const ids=data.teams;check(Array.isArray(ids)&&ids.length===4&&new Set(ids).size===4&&ids.every(x=>typeof x==="string"&&/^t[a-f0-9]{24}$/.test(x)),400,"请选择四支不同的队伍。");
    const teams=await Promise.all(ids.map(id=>one(db,"SELECT t.id,t.name,t.windows,t.roster_categories,t.members_confirmed,pt.pool_id FROM teams t LEFT JOIN pool_teams pt ON pt.team_id=t.id WHERE t.id=?",id)));check(teams.every(t=>t&&t.members_confirmed&&!t.pool_id),409,"四队均须确认空档，且尚未被分组。");
    for(const t of teams)t.windows=JSON.parse(t.windows);
    const duration=data.duration??120;check([90,120].includes(duration),400,"请选择已支持的轮长。");
    const candidates=[];
    const categories=teams.map(t=>JSON.parse(t.roster_categories));
    pairings.forEach((pairs,i)=>pairs.forEach(([a,b])=>{if((categories[a].includes("intl-high")&&categories[b].includes("overseas"))||(categories[b].includes("intl-high")&&categories[a].includes("overseas")))candidates.push({round:i+1,teams:[teams[a].name,teams[b].name]});}));
    const rounds=suggest(teams,duration);if(path==="suggest")return {rounds,pairings,duration,crossGroupCandidates:candidates};
    check(Array.isArray(data.rounds)&&data.rounds.length===3,400,"请选择三轮对阵时段。");
    const blocks=data.rounds.map(input=>normalize([input])[0]).sort((a,b)=>a.date.localeCompare(b.date)||a.start-b.start);
    check(blocks.every((w,i)=>w.date<=GROUP_LAST&&w.end-w.start>=duration&&(!i||w.date>blocks[i-1].date||w.start>=blocks[i-1].end)&&teams.every(t=>t.windows.some(s=>s.date===w.date&&s.start<=w.start&&s.end>=w.end))),400,"三轮须落入四队共同空档且不重叠，并满足选定轮长。");
    const pool="g"+(await digest(ids.slice().sort().join(","))).slice(0,24);
    // One atomic transaction. Re-check all four availability documents at write time.
    const conditions=teams.map(()=>"(id=? AND windows=?)").join(" OR ");
    const create=stmt(db,"INSERT INTO pools(id,rounds) SELECT ?,? WHERE 4=(SELECT COUNT(*) FROM teams WHERE members_confirmed=1 AND ("+conditions+") AND id NOT IN (SELECT team_id FROM pool_teams)) ON CONFLICT(id) DO NOTHING",pool,JSON.stringify(blocks),...teams.flatMap(t=>[t.id,JSON.stringify(t.windows)]));
    let output;try{output=await db.batch([create,...ids.map((id,index)=>stmt(db,"INSERT INTO pool_teams(pool_id,team_id,position) SELECT ?,?,? WHERE EXISTS(SELECT id FROM pools WHERE id=?) ON CONFLICT(team_id) DO NOTHING",pool,id,index,pool))]);}catch{fail(409,"分组状态已改变，请刷新后重试。");}
    check(output[0].meta.changes===1,409,"四队空档或分组状态已变更。");return {id:pool,rounds:blocks,pairings};
  }
  fail(404,"没有这个入口。");
}
export default { async fetch(req,env){
 const url=new URL(req.url),path=url.pathname.replace(/\/+$/,"")||"/";
 try{
   if(req.method==="GET"||req.method==="HEAD"){
     if(path==="/winter-arena.webp")return new Response(req.method==="HEAD"?null:Uint8Array.from(atob(ARTWORK),c=>c.charCodeAt(0)),{headers:{"Content-Type":"image/webp","Cache-Control":"public, max-age=3600","X-Content-Type-Options":"nosniff"}});
     const routes={"/":[PAGE,"text/html; charset=UTF-8"],"/admin":[STAFF_PAGE,"text/html; charset=UTF-8"],"/entry.css":[CSS,"text/css; charset=UTF-8"],"/client.js":[CLIENT,"text/javascript; charset=UTF-8"],"/staff.js":[STAFF,"text/javascript; charset=UTF-8"]};
     const hit=routes[path];if(Array.isArray(hit))return response(req.method==="HEAD"?null:hit[0],200,hit[1]);
     return response({error:"没有这个入口。"},404);
   }
   check(req.method==="POST"&&path.startsWith("/api/"),405,"不支持此请求。");
   check(env.DB,503,"收件服务尚未就绪，请稍后再试。");
   const data=await bodyOf(req);
   if(path.startsWith("/api/admin/"))return response(await admin(req,env,path.slice(11),data));
   const h=await digest(receipt(req));
   switch(path){
    case "/api/enroll":return response(await enroll(env.DB,h,data));
    case "/api/me":return response(await self(env.DB,h));
    case "/api/availability":return response(await availability(env.DB,h,data));
    case "/api/withdraw":return response(await withdraw(env.DB,h));
    case "/api/survey":{const a=surveyAnswers(data);await stmt(env.DB,"INSERT INTO surveys(receipt,answers) VALUES(?,?) ON CONFLICT(receipt) DO UPDATE SET answers=excluded.answers,updated_at=CURRENT_TIMESTAMP",h,JSON.stringify(a)).run();return response({saved:true});}
    case "/api/survey/withdraw":{const out=await stmt(env.DB,"DELETE FROM surveys WHERE receipt=?",h).run();check(out.meta.changes===1,404,"未找到这份调研。");return response({withdrawn:true});}
    default:fail(404,"没有这个入口。");
   }
 }catch(e){return response({error:e instanceof Problem?e.message:"未能确认保存，请保留回执重试。"},e instanceof Problem?e.status:503);}
}};

