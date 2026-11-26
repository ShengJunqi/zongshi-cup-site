"use strict";
const get=id=>document.getElementById(id), fields=f=>Object.fromEntries(new FormData(f)), sections=["home","enroll","survey","availability","format","calendar"];
function route(){const requested=location.hash.slice(1);const to=sections.includes(requested)?requested:"home";for(const name of sections)get(name).hidden=name!==to;get("home-back").hidden=to==="home";window.scrollTo(0,0);}
window.addEventListener("hashchange",route);route();
const store=(k,v)=>{try{if(v===null)sessionStorage.removeItem(k);else sessionStorage.setItem(k,v);}catch{}};
const read=k=>{try{return sessionStorage.getItem(k)||"";}catch{return "";}};
let entryKey=read("zs-entry"),surveyKey=read("zs-survey");
function newKey(){const bytes=crypto.getRandomValues(new Uint8Array(24));return Array.from(bytes,v=>v.toString(16).padStart(2,"0")).join("");}
function rememberEntry(v){entryKey=v;store("zs-entry",v);get("lookup").elements.key.value=v||"";get("team-lookup").elements.key.value=v||"";}
function rememberSurvey(v){surveyKey=v;store("zs-survey",v);get("survey-withdraw").elements.key.value=v||"";}
rememberEntry(entryKey);rememberSurvey(surveyKey);
function msg(id,str,err=false,secret=""){
 const node=get(id);node.replaceChildren();const p=document.createElement("p");p.className="message"+(err?" error":"");p.textContent=str;node.append(p);
 if(secret){const b=document.createElement("button");b.type="button";b.className="secondary copy";b.textContent="复制私人回执";b.onclick=async()=>{try{await navigator.clipboard.writeText(secret);b.textContent="已复制";}catch{b.textContent="请选中上方回执复制";}};node.append(b);}
}
async function post(path,key,data){const r=await fetch(path,{method:"POST",headers:{"Content-Type":"application/json","Authorization":"Bearer "+key},body:JSON.stringify(data)});let out;try{out=await r.json();}catch{throw new Error("收件状态无法确认，请保留回执重试。");}if(!r.ok)throw new Error(out.error||"服务暂不可用，请保留回执重试。");return out;}
function onForm(id,status,fn){get(id).addEventListener("submit",async e=>{e.preventDefault();const b=e.submitter;if(b)b.disabled=true;try{await fn(e.target);}catch(err){msg(status,err.message||"网络中断，请保留回执后重试。",true);}finally{if(b)b.disabled=false;}});}
function syncEnroll(){
 const f=get("enroll-form"),v=f.elements.route.value;
 get("team-name").hidden=v!=="captain";get("join-code").hidden=v!=="member";
 f.elements.teamName.required=v==="captain"&&!f.dataset.edit;f.elements.joinCode.required=v==="member"&&!f.dataset.edit;
}
get("enroll-form").addEventListener("change",syncEnroll);syncEnroll();
function showMe(me){
 const f=get("enroll-form");f.hidden=false;f.dataset.edit="yes";f.elements.name.value=me.name;f.elements.contact.value=me.contact;f.elements.route.value=me.route;
 for(const radio of f.querySelectorAll("[name=route]"))radio.disabled=true;
 f.elements.teamName.value=me.team||"";f.elements.teamName.readOnly=true;f.elements.joinCode.required=false;f.elements.joinCode.readOnly=true;
 syncEnroll();get("join-code").hidden=true;f.querySelector("button").textContent="保存报名修改";get("withdraw").hidden=false;
 let info="已保存报名。请私存回执，换设备可用它查看、修改或撤回。\n"+entryKey;
 if(me.team)info+="\n队伍："+me.team;
 if(me.captain) info+="\n给队员的入队码："+me.joinCode+"（只分享入队码）。队长可前往「队伍时段」。";
 if(me.schedule.length)info+="\n本队已排对阵（北京时间）：" + me.schedule.map(w=>"\n"+w.date+" "+hh(w.start)+"–"+hh(w.end)+" 对 "+w.opponent).join("");
 if(me.route==="solo"&&!me.team)info+="\n待赛务组队，可凭回执回来查看。";
 msg("enroll-result",info,false,entryKey);
}
onForm("enroll-form","enroll-result",async f=>{
 if(!entryKey)rememberEntry(newKey());const data=fields(f);
 // Expose the recovery key before network I/O, including when storage is disabled.
 msg("enroll-result","正在提交；请保留本次回执："+entryKey,false,entryKey);
 try{showMe(await post("/api/enroll",entryKey,data));}catch(e){msg("enroll-result",e.message+"\n本次回执："+entryKey,true,entryKey);}
});
onForm("lookup","enroll-result",async f=>{const k=f.elements.key.value.trim();const me=await post("/api/me",k,{});rememberEntry(k);showMe(me);});
get("withdraw").onclick=async e=>{if(!confirm("确定撤回你的报名吗？"))return;e.target.disabled=true;try{
 await post("/api/withdraw",entryKey,{});rememberEntry(null);location.reload();
}catch(err){msg("enroll-result",err.message,true);}finally{e.target.disabled=false;}};
onForm("survey-form","survey-result",async f=>{
 if(!surveyKey)rememberSurvey(newKey());try{await post("/api/survey",surveyKey,fields(f));msg("survey-result","已收到调研。私人回执："+surveyKey,false,surveyKey);}
 catch(e){msg("survey-result",e.message+"\n调研回执："+surveyKey,true,surveyKey);}
});
onForm("survey-withdraw","survey-result",async f=>{if(!confirm("确定撤回这份调研吗？"))return;await post("/api/survey/withdraw",f.elements.key.value.trim(),{});rememberSurvey(null);get("survey-form").reset();msg("survey-result","这份调研已撤回。");});
const hh=n=>String(Math.floor(n/60)).padStart(2,"0")+":"+String(n%60).padStart(2,"0");
function newRow(w={}){
 const row=document.createElement("div");row.className="time-row";
 const part=(caption,control)=>{const l=document.createElement("label");l.textContent=caption;l.append(control);row.append(l);};
 const day=document.createElement("input");day.type="date";day.name="date";day.required=true;day.min="2026-12-19";day.max="2027-01-03";day.value=w.date||"";part("日期",day);
 for(const [name,label,first,last,selected] of [["start","开始",0,1410,w.start??1080],["end","结束",30,1440,w.end??1200]]){
  const sel=document.createElement("select");sel.name=name;for(let n=first;n<=last;n+=30)sel.add(new Option(hh(n),String(n),false,n===selected));part(label,sel);
 }
 const b=document.createElement("button");b.type="button";b.className="secondary";b.textContent="移除";b.onclick=()=>row.remove();row.append(b);get("windows").append(row);
}
get("add-row").onclick=()=>newRow();
onForm("team-lookup","time-result",async f=>{get("time-form").hidden=true;const k=f.elements.key.value.trim();const me=await post("/api/me",k,{});rememberEntry(k);
 if(!me.captain){msg("time-result",me.team?"请队长汇总五人的共同时间后提交。":"散人组队后可回来查看队伍，由队长填统一时间。");return;}
 get("time-form").hidden=false;get("time-team").textContent=me.team;get("windows").replaceChildren();for(const w of me.windows.length?me.windows:[{}])newRow(w);
 for(const opt of get("roster-types").querySelectorAll("input"))opt.checked=me.rosterCategories.includes(opt.value);
 for(const key of ["practice","finals"])get("time-form").elements[key].value=me.extras[key]||"";
 get("time-form").elements.confirmed.checked=!!me.confirmed;msg("time-result","已打开本队记录。");
});
onForm("time-form","time-result",async f=>{const rows=[...get("windows").children];const windows=rows.map(r=>({date:r.querySelector("[name=date]").value,start:Number(r.querySelector("[name=start]").value),end:Number(r.querySelector("[name=end]").value)}));const saved=await post("/api/availability",entryKey,{windows,confirmed:f.elements.confirmed.checked,rosterCategories:[...f.querySelectorAll("[name=roster]:checked")].map(x=>x.value),extras:{practice:f.elements.practice.value,finals:f.elements.finals.value}});msg("time-result","已保存 "+saved.windows.length+" 段共同空档。这还不是最终比赛排期。");});


get("roster-types").onchange=e=>{if(!e.target.checked)return;for(const opt of get("roster-types").querySelectorAll("input"))if((e.target.value==="pending"&&opt.value!=="pending")||(e.target.value!=="pending"&&opt.value==="pending"))opt.checked=false;};
if(entryKey){
 const oldKey=entryKey;get("enroll-form").hidden=true;
 const reset=document.createElement("button");reset.type="button";reset.className="secondary";reset.textContent="为另一位选手新建报名";
 reset.onclick=()=>{if(!confirm("请先私存原回执。要在本标签页开始另一条报名吗？"))return;rememberEntry(null);location.reload();};
 get("enroll").append(reset);
 post("/api/me",oldKey,{}).then(me=>{if(entryKey===oldKey)showMe(me);}).catch(err=>{
   if(entryKey!==oldKey)return;
   if(err.message.includes("没有找到")){get("enroll-form").hidden=false;return;}
   msg("enroll-result","暂时不能读取已有报名，请在下方用回执重试。",true);
 });
}
