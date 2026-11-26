"use strict";
const get=id=>document.getElementById(id);let state=null,proposal=null;
const selected=id=>[...get(id).querySelectorAll("input:checked")].map(n=>n.value);
const time=n=>String(Math.floor(n/60)).padStart(2,"0")+":"+String(n%60).padStart(2,"0");
const label=w=>w.date+" "+time(w.start)+"–"+time(w.end);
async function api(endpoint,data={}){const headers={"Content-Type":"application/json"};const token=get("token").value.trim();if(token)headers.Authorization="Bearer "+token;
 const r=await fetch("/api/admin/"+endpoint,{method:"POST",headers,body:JSON.stringify(data)});const b=await r.json();if(!r.ok)throw Error(b.error||"操作失败。");return b;}
function line(id,s,key=null){const row=document.createElement("div");row.className="staff-row";const l=document.createElement("label");
 if(key){const cb=document.createElement("input");cb.type="checkbox";cb.value=key;l.append(cb);}
 l.append(document.createTextNode(s));row.append(l);get(id).append(row);}
function caps(){get("captain").replaceChildren();for(const id of selected("players")){const p=state.players.find(x=>x.id===id);get("captain").add(new Option(p.name,id));}}
get("players").onchange=caps;get("teams").onchange=()=>{proposal=null;get("suggestText").textContent="";get("makePool").hidden=true;};
async function load(){const d=await api("list");state=d;proposal=null;get("data").hidden=false;get("makePool").hidden=true;get("suggestText").textContent="";for(const key of ["players","teams","pools","surveys"])get(key).replaceChildren();caps();
 const team=id=>d.teams.find(t=>t.id===id)?.name||"待组队";
 d.players.forEach(p=>line("players",p.name+" · "+p.contact+" · "+team(p.team_id),p.route==="solo"&&!p.team_id?p.id:null));
 const tags={"intl-high":"国内国际高中","domestic-uni":"国内大学","overseas":"海外读书或交换","pending":"类别待补"};
 d.teams.forEach(t=>line("teams",t.name+" · "+t.roster_categories.map(k=>tags[k]).join("、")+" · "+(t.windows.map(label).join(" / ")||"未报空档")+(t.pool_id?" · 已分组":""),t.members_confirmed&&!t.pool_id?t.id:null));
 const groups=new Map();for(const row of d.pools){if(!groups.has(row.id))groups.set(row.id,[]);groups.get(row.id).push(row);}
 for(const [,rs] of groups){const sorted=rs.sort((a,b)=>a.position-b.position),names=sorted.map(r=>team(r.team_id)),pairs=[[[0,3],[1,2]],[[0,2],[1,3]],[[0,1],[2,3]]];sorted[0].rounds.forEach((r,i)=>line("pools",label(r)+" · "+pairs[i].map(([a,b])=>names[a]+" 对 "+names[b]).join(" / ")));}
 d.surveys.forEach(s=>line("surveys",Object.values(s).join(" · ")));get("status").textContent="已读取 "+d.players.length+" 条报名、"+d.teams.length+" 队和 "+d.surveys.length+" 份调研。";
}
const action=(id,fn)=>get(id).onclick=async e=>{e.target.disabled=true;try{await fn();}catch(err){get("status").textContent=err.message;}finally{e.target.disabled=false;}};
action("load",load);
action("assign",async()=>{const ids=selected("players"),cap=get("captain").value;if(ids.length!==5||!cap)throw Error("请勾选五人并选择队长。");await api("assign",{players:[cap,...ids.filter(x=>x!==cap)],name:get("teamName").value});await load();});
action("suggest",async()=>{const teams=selected("teams");const duration=Number(get("duration").value);const p=await api("suggest",{teams,duration});proposal={teams,rounds:p.rounds,duration};get("suggestText").textContent=p.rounds.map(label).join(" / ")+" · "+p.rounds.length+" / 3 轮。每轮需两间房。多个小组同时排期时请先核对房间和裁判。"+(p.crossGroupCandidates.length?" 国内国际高中与海外读书/交换的潜在交手："+p.crossGroupCandidates.map(x=>"第"+x.round+"轮 "+x.teams.join(" 对 ")).join("；")+"。":" 尚不能从队长信息确认跨群体对手。")+" 裁判需在出场名单及赛后记录中核实。";get("makePool").hidden=p.rounds.length!==3;});
action("makePool",async()=>{if(!proposal)throw Error("请先核对共同空档。");await api("pool",proposal);await load();});
action("export",async()=>{if(!state)return;const url=URL.createObjectURL(new Blob([JSON.stringify(state,null,2)],{type:"application/json"}));const a=document.createElement("a");a.href=url;a.download="宗师杯_私有赛务记录.json";a.click();setTimeout(()=>URL.revokeObjectURL(url),2000);});


get("duration").onchange=()=>{proposal=null;get("makePool").hidden=true;get("suggestText").textContent="";};
