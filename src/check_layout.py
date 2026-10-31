# -*- coding: utf-8 -*-
"""检查样板页在 320/390/430 CSS 宽度下是否横向溢出。

做法：生成一个 iframe 测试页（iframe 宽度 = 目标宽度），
用 Edge --allow-file-access-from-files + --dump-dom 读取每个 iframe 的 scrollWidth。
不修改 site/ 产物；测试页用后删除。
"""
from __future__ import annotations

import subprocess
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
<style>html,body{margin:0;background:#111;color:#fff;font:14px monospace}iframe{border:0;height:600px;display:block}</style>
</head><body><pre id="out">pending</pre><script>
const pages=%PAGES%;
const widths=%WIDTHS%;
const results=[]; let pending=pages.length*widths.length;
pages.forEach(function(p){ widths.forEach(function(w){
  const f=document.createElement('iframe');
  f.style.width=w+'px'; f.src=p; f.title=p+' '+w;
  f.onload=function(){ try{
      const win=f.contentWindow, doc=f.contentDocument.documentElement;
      results.push(p+' '+w+'px inner='+win.innerWidth+' scrollW='+doc.scrollWidth+
        ' overflow='+(doc.scrollWidth>win.innerWidth+1?'YES':'NO'));
    }catch(e){ results.push(p+' '+w+'px ERR '+e.message); }
    if(--pending===0){ document.getElementById('out').textContent=results.join('\\n');
      document.documentElement.setAttribute('data-done','1'); }
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
               "--allow-file-access-from-files", "--virtual-time-budget=6000",
               "--dump-dom", path.resolve().as_uri()]
        out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                             errors="replace", timeout=90).stdout
        if '<pre id="out">pending</pre>' in out:
            print("WARN: iframe check did not finish; raw dump length", len(out))
        else:
            import re
            m = re.search(r'<pre id="out">(.*?)</pre>', out, re.S)
            print(m.group(1).replace("&quot;", '"').replace("&amp;", "&") if m else out[-1000:])
    finally:
        path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
