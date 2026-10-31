# -*- coding: utf-8 -*-
"""样板页自动检查：三档宽度 + 字号 / 点击区 / 表格滑动提示。

做法：生成 iframe 测试页（iframe 宽度 = 320/390/430），
用 Edge --allow-file-access-from-files + --dump-dom 读取每个 iframe 内 DOM 的度量。
任一项失败 -> 退出码 1；不修改 site/ 产物。
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
SHOTS = ROOT / "shots"
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
PROFILE = SHOTS / "_edgeprofile_layout"

PAGES = [
    ("index", "index.html"),
    ("event", "event.html"),
    ("schedule", "schedule.html"),
    ("match", "matches/s2-first.html"),
    ("player", "players/fangshan-de-qiu.html"),
    ("sources", "sources.html"),
]
WIDTHS = [320, 390, 430]

WRAPPER = """<!DOCTYPE html><html><head><meta charset="utf-8">
<style>html,body{margin:0;background:#111;color:#fff;font:14px monospace}iframe{border:0;height:900px;display:block}</style>
</head><body><pre id="out">pending</pre><script>
const pages=%PAGES%, widths=%WIDTHS%, results=[];
let pending=pages.length*widths.length;
pages.forEach(function(p){ widths.forEach(function(w){
  const f=document.createElement('iframe'); f.style.width=w+'px'; f.src=p; f.title=p+' '+w;
  f.onload=function(){
    const fails=[];
    try {
      const win=f.contentWindow, doc=f.contentDocument;
      const de=doc.documentElement;
      if(de.scrollWidth > win.innerWidth+1) fails.push('page-overflow '+de.scrollWidth+'>'+win.innerWidth);
      // 正文字号
      doc.querySelectorAll('.small,.notice,.note').forEach(function(el){
        const fs=parseFloat(win.getComputedStyle(el).fontSize);
        if(fs<14) fails.push('body-font '+fs.toFixed(1)+' '+el.className);
      });
      // 辅助字号
      doc.querySelectorAll('.status,.src,.badge,.tag,.breadcrumb,.footer,.brand span,.mobile-nav a').forEach(function(el){
        const fs=parseFloat(win.getComputedStyle(el).fontSize);
        if(fs<12) fails.push('aux-font '+fs.toFixed(1)+' '+el.className);
      });
      // 关键点击区：宽高均 >=44（隐藏元素跳过）
      doc.querySelectorAll('.btn,.nav a,.mobile-nav a,.src').forEach(function(el){
        const r=el.getBoundingClientRect();
        if(r.width>0 && r.height>0 && (r.height<44 || r.width<44)) {
          fails.push('tap-size '+r.width.toFixed(0)+'x'+r.height.toFixed(0)+' '+el.className);
        }
      });
      // 表格：溢出时必须有滑动提示，且能滚到最后一列
      doc.querySelectorAll('.table-wrap').forEach(function(wrap){
        if(wrap.scrollWidth>wrap.clientWidth+1){
          const hint=wrap.parentElement.querySelector('.scroll-hint');
          const ok=hint && win.getComputedStyle(hint).display!=='none';
          if(!ok) fails.push('table-hint');
          wrap.scrollLeft=wrap.scrollWidth;
          const last=wrap.querySelector('tr:last-child td:last-child, tr:last-child th:last-child');
          if(!last){ fails.push('table-last-cell'); }
          else {
            const wr=wrap.getBoundingClientRect(), lr=last.getBoundingClientRect();
            if(lr.right>wr.right+1) fails.push('table-last-not-reachable');
          }
          wrap.scrollLeft=0;
        }
      });
    } catch(e) { fails.push('ERR '+e.message); }
    results.push(p+'|'+w+'|'+(fails.length?('FAIL '+fails.join('; ')):'OK'));
    if(--pending===0){ document.getElementById('out').textContent=results.join('\\n');
      de.setAttribute('data-done','1'); }
  };
  document.body.appendChild(f);
});});
</script></body></html>"""


def main() -> None:
    imports = "[" + ",".join(f'"{p}"' for _, p in PAGES) + "]"
    wrapper = WRAPPER.replace("%PAGES%", imports).replace("%WIDTHS%", str(WIDTHS))
    path = SITE / "_layout_check.html"
    path.write_text(wrapper, encoding="utf-8")
    try:
        cmd = [str(EDGE), "--headless", "--disable-gpu",
               f"--user-data-dir={PROFILE}", "--no-first-run", "--no-default-browser-check",
               "--allow-file-access-from-files", "--virtual-time-budget=8000",
               "--dump-dom", path.resolve().as_uri()]
        out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                             errors="replace", timeout=120).stdout
        import re
        m = re.search(r'<pre id="out">(.*?)</pre>', out, re.S)
        text = m.group(1) if m else ""
        if not text or text == "pending":
            print("FAIL: check did not finish")
            sys.exit(1)
        print(text.replace("&quot;", '"').replace("&amp;", "&"))
        sys.exit(0 if "FAIL" not in text else 1)
    finally:
        path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
