"""把 v1 单文件课程重排成 v2：新外壳 + 新 CSS/JS，内容原样保留。"""
import re, pathlib, html as htmllib

SRC = pathlib.Path(r"D:\hermes-course\content.html")
OUT = pathlib.Path(r"D:\hermes-course\index.html")
BAK = pathlib.Path(r"D:\hermes-course\index-v1.html")
s = SRC.read_text(encoding="utf-8")

# ---- 抽取原有内容 ----
hero = re.search(r'<header class="hero">.*?</header>', s, re.S).group(0)
secs = re.findall(r'<section id="([^"]+)">(.*?)</section>', s, re.S)
assert len(secs) == 16, len(secs)
titles = {}
for sid, body in secs:
    m = re.search(r'<h2><span class="num">([^<]*)</span>(.*?)</h2>', body, re.S)
    assert m, sid
    titles[sid] = (m.group(1).strip(), m.group(2).strip())

GROUPS = [
    ("第一部分 · 心智模型", ["c0", "c1", "c2"]),
    ("第二部分 · 四个入口", ["c3", "c4", "c5", "c6"]),
    ("第三部分 · 采购与编排", ["c7", "c8", "c9", "c10"]),
    ("第四部分 · 外观与工作台", ["c11", "c12"]),
    ("附录", ["a1", "a2", "a3"]),
]
LABEL = {"c0": "起点诊断", "c1": "Agent 到底是什么", "c2": "五层配置地图",
         "c3": "SOUL.md 性格", "c4": "memory 事实", "c5": "AGENTS.md 项目",
         "c6": "SKILL.md 技能", "c7": "采购学", "c8": "编排姿势",
         "c9": "三个场景配方", "c10": "越用越懂你",
         "c11": "外观与桌宠", "c12": "工作台",
         "a1": "命令速查", "a2": "30 天路线", "a3": "参考资料"}

# ---- 给每章补"预计阅读时间"和前后翻页 ----
order = [sid for _, ids in GROUPS for sid in ids]
for i, sid in enumerate(order):
    body = dict(secs)[sid]
    plain = re.sub(r'<[^>]+>', '', body)
    mins = max(1, round(len(plain) / 500))
    rt = f'<div class="rt">约 {mins} 分钟 · {len(plain)} 字</div>'
    body2 = re.sub(r'(</h2>)', r'\1\n  ' + rt, body, count=1)

    prev_id = order[i - 1] if i else None
    next_id = order[i + 1] if i + 1 < len(order) else None
    pn = ['<nav class="pn">']
    if prev_id:
        pn.append(f'<a class="pv" href="#{prev_id}"><span>← 上一章</span><b>{LABEL[prev_id]}</b></a>')
    if next_id:
        pn.append(f'<a class="nx" href="#{next_id}"><span>下一章 →</span><b>{LABEL[next_id]}</b></a>')
    pn.append('</nav>')
    body2 = body2.rstrip() + "\n  " + "".join(pn)
    secs = [(sid2, body2 if sid2 == sid else b) for sid2, b in secs]

nav = []
for gname, ids in GROUPS:
    nav.append(f'<div class="grp">{gname}</div><ol>')
    for sid in ids:
        num, t = titles[sid]
        nav.append(f'<li><a href="#{sid}" data-s="{sid}"><span class="n">{num}</span>{LABEL[sid]}</a></li>')
    nav.append('</ol>')
NAV = "".join(nav)

CSS = """
:root{
  --paper:#faf7f2; --card:#fffdf9; --sunk:#f2ede4; --ink:#1d1b18; --muted:#57503f;
  --line:#e3dbcd; --acc:#a8402a; --acc-soft:#f4e8e3; --ok:#2f6b52; --ok-soft:#e8f0ec;
  --warn:#8a6420; --warn-soft:#f7f0e0;
  --serif:"Source Han Serif SC","Noto Serif SC","Songti SC",SimSun,"Times New Roman",serif;
  --sans:"PingFang SC","Microsoft YaHei","Source Han Sans SC",-apple-system,"Segoe UI",sans-serif;
  --mono:"JetBrains Mono","Cascadia Code",Consolas,ui-monospace,monospace;
  --maxw:790px;
}
html[data-theme="dark"]{
  --paper:#16150f; --card:#1d1b14; --sunk:#221f17; --ink:#eae4d7; --muted:#b3aa96;
  --line:#332e23; --acc:#e07a5f; --acc-soft:#2a1d18; --ok:#7bbfa1; --ok-soft:#17251f;
  --warn:#d9ab52; --warn-soft:#26200f;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:30px;-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink);font:16.5px/1.85 var(--sans);
  font-feature-settings:"kern" 1;text-rendering:optimizeLegibility}
::selection{background:var(--acc);color:var(--paper)}

/* 顶部阅读进度 */
#topbar{position:fixed;top:0;left:0;height:2px;background:var(--acc);width:0;z-index:60;transition:width .1s linear}

/* 左栏 */
#rail{position:fixed;inset:0 auto 0 0;width:272px;background:var(--card);border-right:1px solid var(--line);
  padding:26px 18px 60px;overflow-y:auto;z-index:40}
#rail .ttl{font-family:var(--serif);font-size:17px;font-weight:600;letter-spacing:.5px;margin:0 0 2px 6px}
#rail .sub2{font-size:11.5px;color:var(--muted);margin:0 0 18px 6px;letter-spacing:.6px}
#q{width:100%;padding:8px 11px;border:1px solid var(--line);border-radius:5px;background:var(--sunk);
  color:var(--ink);font:13px var(--sans);margin-bottom:6px}
#q:focus{outline:none;border-color:var(--acc)}
#qmsg{font-size:11px;color:var(--muted);margin:0 0 12px 2px;min-height:14px}
#rail .grp{font-size:10.5px;letter-spacing:1.6px;color:var(--muted);margin:18px 0 6px 6px}
#rail ol{list-style:none;margin:0;padding:0}
#rail li{margin:0}
#rail a{display:flex;gap:9px;align-items:baseline;padding:6px 8px;border-radius:5px;
  color:var(--muted);text-decoration:none;font-size:13.5px;line-height:1.5;transition:background .12s,color .12s}
#rail a:hover{background:var(--sunk);color:var(--ink)}
#rail a.on{background:var(--acc-soft);color:var(--acc);font-weight:600}
#rail a .n{font:11px var(--mono);opacity:.6;min-width:16px}
#rail.hide{display:none}
#rail .foot{margin-top:20px;padding-top:14px;border-top:1px solid var(--line);display:flex;
  justify-content:space-between;align-items:center;font-size:11.5px;color:var(--muted)}
#prog{font-variant-numeric:tabular-nums}
#prog b{color:var(--acc);font-size:13px}
#themebtn{background:none;border:1px solid var(--line);color:var(--muted);border-radius:4px;
  padding:3px 8px;font-size:11px;cursor:pointer;font-family:var(--sans)}
#themebtn:hover{color:var(--acc);border-color:var(--acc)}

/* 正文 */
main{margin-left:272px}
.wrap{max-width:var(--maxw);margin:0 auto;padding:0 40px}
.hero{padding:96px 0 52px}
.hero .eyebrow{font:11.5px var(--mono);letter-spacing:2.4px;color:var(--acc);margin:0 0 18px}
.hero h1{font-family:var(--serif);font-size:clamp(30px,4.4vw,44px);line-height:1.22;
  margin:0 0 20px;letter-spacing:-.2px;font-weight:600}
.hero p{color:var(--muted);font-size:17px;margin:0;max-width:640px}
.hero p strong{color:var(--ink);font-weight:600}
.hero .meta{margin-top:26px;font-size:12.5px;color:var(--muted);letter-spacing:.3px}
.hero .meta span{margin-right:16px;display:inline-block}
.hero .tags{margin-top:22px;display:flex;gap:7px;flex-wrap:wrap}
.hero .tag{font-size:11.5px;padding:3px 10px;border-radius:99px;background:var(--sunk);
  color:var(--muted);border:1px solid var(--line)}

section{padding:58px 0 26px;border-top:1px solid var(--line)}
h2{font-family:var(--serif);font-size:clamp(22px,2.8vw,28px);line-height:1.35;margin:0 0 4px;
  font-weight:600;letter-spacing:-.2px;scroll-margin-top:24px}
h2 .num{font:12px var(--mono);color:var(--acc);margin-right:11px;vertical-align:2px;letter-spacing:1px}
.rt{font:11.5px var(--mono);color:var(--muted);letter-spacing:.6px;margin:0 0 24px}
h3{font-family:var(--serif);font-size:18.5px;margin:38px 0 10px;font-weight:600}
h4{font-size:14.5px;margin:24px 0 8px;color:var(--ok);letter-spacing:.3px}
p{margin:14px 0}
ul,ol{padding-left:24px;margin:14px 0}
li{margin:7px 0}
strong{font-weight:600}
code{font-family:var(--mono);font-size:.86em;background:var(--sunk);padding:1.5px 5px;
  border-radius:3px;color:var(--ink)}
a{color:var(--acc);text-decoration:none;border-bottom:1px solid color-mix(in srgb,var(--acc) 35%,transparent)}
a:hover{border-bottom-color:var(--acc)}
hr{border:0;border-top:1px solid var(--line);margin:32px 0}

/* 代码 */
.code{position:relative;margin:20px 0;border:1px solid var(--line);border-radius:6px;
  overflow:hidden;background:var(--card)}
.code .hd{display:flex;justify-content:space-between;align-items:center;padding:7px 13px;
  background:var(--sunk);border-bottom:1px solid var(--line);font:10.5px var(--mono);
  color:var(--muted);letter-spacing:1px;text-transform:uppercase}
.code pre{margin:0;padding:15px 17px;overflow-x:auto;font:13px/1.7 var(--mono);tab-size:2}
.code pre code{background:none;padding:0;font-size:inherit}
.cp{background:none;border:1px solid var(--line);color:var(--muted);font:10.5px var(--sans);
  padding:2px 9px;border-radius:99px;cursor:pointer;letter-spacing:.5px}
.cp:hover{color:var(--acc);border-color:var(--acc)}

/* 提示块：用顶部细线而非左侧色条 */
.box{margin:22px 0;padding:16px 20px;background:var(--card);border:1px solid var(--line);
  border-top:2px solid var(--acc);border-radius:0 0 6px 6px}
.box p:last-child{margin-bottom:0}
.box.warn{border-top-color:var(--warn);background:var(--warn-soft)}
.box.bad{border-top-color:var(--acc);background:var(--acc-soft)}
.box.ok{border-top-color:var(--ok);background:var(--ok-soft)}
.box>b:first-child{display:block;font-size:13px;letter-spacing:.6px;margin-bottom:6px;color:var(--acc)}
.box.warn>b:first-child{color:var(--warn)}
.box.ok>b:first-child{color:var(--ok)}
.box p:first-of-type{margin-top:0}

/* 类比 */
.analogy{margin:22px 0;padding:16px 20px;background:var(--sunk);border-radius:6px;
  font-size:15.5px;line-height:1.8;color:var(--muted)}
.analogy b{color:var(--ink);font-weight:600}

/* 表格 */
table{width:100%;border-collapse:collapse;margin:20px 0;font-size:13.8px}
th,td{text-align:left;padding:11px 13px;border-bottom:1px solid var(--line);vertical-align:top;line-height:1.7}
th{font-size:10.5px;letter-spacing:1.4px;text-transform:uppercase;color:var(--muted);
  font-weight:600;border-bottom:1.5px solid var(--line)}
tbody tr:hover td{background:var(--card)}
td code{font-size:.85em}

/* 实操块 */
.lab{margin:26px 0;padding:22px 22px 20px;background:var(--card);border:1px solid var(--line);border-radius:8px}
.lab-h{display:inline-block;font:10.5px var(--mono);letter-spacing:1.6px;color:var(--paper);
  background:var(--ok);padding:3px 10px;border-radius:99px;margin-bottom:14px}
.lab h4{margin-top:18px;color:var(--ink)}
.lab h4:first-of-type{margin-top:6px}
.lab>:last-child{margin-bottom:0}

/* 自检 */
.check{list-style:none;padding:0;margin:16px 0}
.check li{padding-left:24px;position:relative;color:var(--muted);font-size:14.5px}
.check li::before{content:"—";position:absolute;left:0;color:var(--acc)}

/* 完成勾选 */
.done{display:flex;gap:10px;align-items:center;margin:34px 0 0;padding:13px 16px;
  border:1px solid var(--line);border-radius:6px;font-size:13.5px;color:var(--muted);
  cursor:pointer;background:var(--card);transition:border-color .15s}
.done input{accent-color:var(--ok);width:15px;height:15px;cursor:pointer;flex:none}
.done:has(input:checked){border-color:var(--ok);color:var(--ok);background:var(--ok-soft)}

details{margin:18px 0;border:1px solid var(--line);border-radius:6px;background:var(--card);padding:0 18px}
summary{cursor:pointer;padding:13px 0;font-size:14px;font-weight:600;list-style:none}
summary::-webkit-details-marker{display:none}
summary::before{content:"▸ ";color:var(--acc)}
details[open] summary::before{content:"▾ "}
details[open]{padding-bottom:14px}

/* 上一章 / 下一章 */
.pn{display:flex;gap:14px;margin:44px 0 0;padding-top:22px;border-top:1px solid var(--line)}
.pn a{flex:1;display:block;padding:13px 16px;border:1px solid var(--line);border-radius:6px;
  text-decoration:none;border-bottom:1px solid var(--line);background:var(--card);transition:border-color .15s}
.pn a:hover{border-color:var(--acc)}
.pn a span{display:block;font-size:10.5px;letter-spacing:1.2px;color:var(--muted);margin-bottom:4px}
.pn a b{font-weight:600;font-size:14px;color:var(--ink)}
.pn .nx{text-align:right}

#menu{display:none;position:fixed;top:14px;left:14px;z-index:70;background:var(--card);
  border:1px solid var(--line);border-radius:6px;padding:8px 12px;color:var(--ink);cursor:pointer;font-size:15px}
#toTop{position:fixed;right:26px;bottom:26px;z-index:50;width:38px;height:38px;border-radius:50%;
  border:1px solid var(--line);background:var(--card);color:var(--muted);cursor:pointer;
  opacity:0;pointer-events:none;transition:opacity .2s;font-size:15px}
#toTop.show{opacity:1;pointer-events:auto}
#toTop:hover{color:var(--acc);border-color:var(--acc)}

@media(max-width:960px){
  #rail{transform:translateX(-100%);transition:transform .22s;width:290px}
  #rail.open{transform:none;box-shadow:0 0 50px rgba(0,0,0,.25)}
  main{margin-left:0}
  #menu{display:block}
  .wrap{padding:0 22px}
  .hero{padding-top:80px}
  .pn{flex-direction:column}
}

/* 打印成纸质/PDF */
@media print{
  #rail,#menu,#toTop,#topbar{display:none}
  main{margin:0}
  .wrap{max-width:none;padding:0}
  body{background:#fff;color:#000;font-size:11pt;line-height:1.7}
  section{page-break-before:always;border-top:none;padding-top:0}
  .hero{page-break-after:always}
  .code{border:1px solid #999;background:#fff}
  .code .hd{background:#eee;color:#333}
  .cp{display:none}
  .box,.lab,.analogy,.done{background:#fff;border:1px solid #999}
  details{display:block}
  details>summary{list-style:none}
  a{color:#000;border:none}
  .pn{display:none}
}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{transition:none!important}}
"""

JS = """
const KEY_T='hermes-course-theme', KEY_P='hermes-course-v1';

// —— 主题 ——
const root=document.documentElement;
const savedT=localStorage.getItem(KEY_T);
root.dataset.theme = savedT || (matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light');
const tb=document.getElementById('themebtn');
const paintTb=()=>tb.textContent = root.dataset.theme==='dark'?'☀ 亮色':'☾ 暗色';
paintTb();
tb.onclick=()=>{root.dataset.theme = root.dataset.theme==='dark'?'light':'dark';
  localStorage.setItem(KEY_T,root.dataset.theme);paintTb();};

// —— 复制 ——
document.querySelectorAll('.cp').forEach(b=>{
  b.onclick=async()=>{
    const pre=b.closest('.code').querySelector('pre');
    try{await navigator.clipboard.writeText(pre.innerText);b.textContent='已复制';}
    catch(e){b.textContent='失败';}
    setTimeout(()=>b.textContent='复制',1400);
  };
});

// —— 进度勾选 ——
const boxes=[...document.querySelectorAll('.done input')];
let saved={};
try{saved=JSON.parse(localStorage.getItem(KEY_P)||'{}')}catch(e){}
boxes.forEach(cb=>{
  if(saved[cb.dataset.k])cb.checked=true;
  cb.onchange=()=>{saved[cb.dataset.k]=cb.checked;
    localStorage.setItem(KEY_P,JSON.stringify(saved));paint();};
});
function paint(){
  const n=boxes.filter(b=>b.checked).length;
  const p=boxes.length?Math.round(n/boxes.length*100):0;
  document.getElementById('pct').textContent=p+'%';
}
paint();

// —— 滚动：顶部进度条 + 章节高亮 + 回到顶部 ——
const secs=[...document.querySelectorAll('section')];
const links=[...document.querySelectorAll('#rail a[data-s]')];
const tot=document.getElementById('toTop');
function onScroll(){
  const h=document.documentElement;
  const max=h.scrollHeight-h.clientHeight;
  document.getElementById('topbar').style.width=(max>0?h.scrollTop/max*100:0)+'%';
  tot.classList.toggle('show',h.scrollTop>600);
  let cur=secs[0];
  for(const s of secs){ if(s.getBoundingClientRect().top<=120) cur=s; }
  links.forEach(a=>a.classList.toggle('on',a.dataset.s===cur?.id));
}
addEventListener('scroll',onScroll,{passive:true});onScroll();
tot.onclick=()=>scrollTo({top:0,behavior:'smooth'});

// —— 搜索：按章节正文匹配 ——
const q=document.getElementById('q'), qmsg=document.getElementById('qmsg');
const index=secs.map(s=>({id:s.id,el:s,text:s.textContent.replace(/\\s+/g,' ')}));
q.oninput=()=>{
  const v=q.value.trim().toLowerCase();
  links.forEach(a=>{
    if(!v){a.style.display='';a.querySelector('.n').textContent=a.dataset.orig||a.querySelector('.n').textContent;return;}
    const hit=index.find(i=>i.id===a.dataset.s);
    a.style.display = hit && hit.text.includes(v) ? '' : 'none';
  });
  const shown=links.filter(a=>a.style.display!=='none').length;
  qmsg.textContent=v? (shown?`${shown} 章命中 · 回车跳到第一处`:'没有匹配') : '';
};
q.onkeydown=e=>{
  if(e.key!=='Enter')return;
  const first=links.find(a=>a.style.display!=='none');
  if(first){first.click();q.blur();}
};

// —— 键盘左右翻章 ——
const order=[...document.querySelectorAll('.pn a')];
addEventListener('keydown',e=>{
  if(/^(INPUT|TEXTAREA)$/.test(document.activeElement.tagName))return;
  if(e.key!=='ArrowRight'&&e.key!=='ArrowLeft')return;
  const cur=secs.find(s=>s.getBoundingClientRect().top<=120&&s.getBoundingClientRect().bottom>120)||secs[0];
  const pn=cur.querySelector('.pn');
  if(!pn)return;
  const a=pn.querySelector(e.key==='ArrowRight'?'.nx':'.pv');
  if(a){location.hash=a.getAttribute('href');}
});

// —— 移动端菜单 ——
const rail=document.getElementById('rail');
document.getElementById('menu').onclick=()=>rail.classList.toggle('open');
links.forEach(a=>a.addEventListener('click',()=>{if(innerWidth<960)rail.classList.remove('open')}));
"""

def build():
    body_sections = "\n\n".join(
        f'<section id="{sid}">\n  {body}\n</section>' for sid, body in secs
    )
    dark_attr = ""
    return f"""<!doctype html>
<html lang="zh-CN"{dark_attr}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Hermes 实操课 · 从"装了"到"会用"</title>
<meta name="description" content="面向初学者的 Hermes Agent 实操课程：分层配置、技能编写、编排与自进化。">
<style>{CSS}</style>
</head>
<body>
<div id="topbar"></div>
<button id="menu">☰ 目录</button>
<nav id="rail">
  <div class="ttl">Hermes 实操课</div>
  <div class="sub2">从"装了"到"会用"</div>
  <input id="q" type="search" placeholder="搜索全课内容…" autocomplete="off">
  <div id="qmsg"></div>
  {NAV}
  <div class="foot"><span id="prog">完成 <b id="pct">0%</b></span><button id="themebtn">☾ 暗色</button></div>
</nav>
<main>
<div class="wrap">
{hero}

{body_sections}

</div>
</main>
<button id="toTop" title="回到顶部">↑</button>
<script>{JS}</script>
</body>
</html>
"""

if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if not BAK.exists():
        BAK.write_text(s, encoding="utf-8")
    OUT.write_text(build(), encoding="utf-8")
    print("written:", OUT, OUT.stat().st_size, "bytes")
