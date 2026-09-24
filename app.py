import os, json, re, urllib.request, urllib.error
PWA_MANIFEST="{\"name\":\"SeniScan AI\",\"short_name\":\"SeniScan\",\"description\":\"Imbas, kenal, faham dan ingat Unsur Seni serta Prinsip Rekaan.\",\"lang\":\"ms\",\"start_url\":\"/\",\"scope\":\"/\",\"display\":\"standalone\",\"background_color\":\"#215bf1\",\"theme_color\":\"#4d20c8\",\"icons\":[{\"src\":\"/icon.svg\",\"sizes\":\"any\",\"type\":\"image/svg+xml\",\"purpose\":\"any maskable\"}]}"
PWA_ICON="<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 512 512\"><defs><linearGradient id=\"g\" x2=\"1\" y2=\"1\"><stop stop-color=\"#4d20c8\"/><stop offset=\"1\" stop-color=\"#168de8\"/></linearGradient></defs><rect width=\"512\" height=\"512\" rx=\"112\" fill=\"url(#g)\"/><rect x=\"105\" y=\"164\" width=\"302\" height=\"218\" rx=\"58\" fill=\"#fff\"/><rect x=\"151\" y=\"131\" width=\"87\" height=\"44\" rx=\"15\" fill=\"#fff\"/><circle cx=\"256\" cy=\"272\" r=\"79\" fill=\"#6639dc\"/><circle cx=\"256\" cy=\"272\" r=\"48\" fill=\"#243267\"/><circle cx=\"274\" cy=\"253\" r=\"15\" fill=\"#fff\"/><circle cx=\"358\" cy=\"210\" r=\"16\" fill=\"#ffcf4d\"/></svg>"
PWA_SW="const CACHE='seniscan-shell-v1';const SHELL=['/','/icon.svg','/manifest.webmanifest'];self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(SHELL)));self.skipWaiting()});self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))));self.clients.claim()});self.addEventListener('fetch',e=>{const u=new URL(e.request.url);if(e.request.method!=='GET'||u.origin!==self.location.origin||u.pathname.startsWith('/api/'))return;if(e.request.mode==='navigate'){e.respondWith(fetch(e.request).then(r=>{if(r.ok){const copy=r.clone();caches.open(CACHE).then(c=>c.put('/',copy))}return r}).catch(()=>caches.match('/')));return}e.respondWith(caches.match(e.request).then(cached=>cached||fetch(e.request)))});"
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

PORT=int(os.environ.get("PORT","8000"))
MODEL="@cf/moondream/moondream3.1-9B-A2B"
CF_ACCOUNT_ID=os.environ.get("CLOUDFLARE_ACCOUNT_ID","")
CF_API_TOKEN=os.environ.get("CLOUDFLARE_API_TOKEN","")

HTML="""<!doctype html><html lang="ms"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SeniScan AI</title><meta name="theme-color" content="#4d20c8"><meta name="apple-mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-status-bar-style" content="default"><meta name="apple-mobile-web-app-title" content="SeniScan"><link rel="manifest" href="/manifest.webmanifest"><link rel="icon" type="image/svg+xml" href="/icon.svg"><style>
*{box-sizing:border-box}body{margin:0;font-family:Inter,ui-sans-serif,system-ui,-apple-system,sans-serif;background:linear-gradient(180deg,#0b79f3 0%,#215bf1 48%,#173bbd 100%);color:#202442}.app{max-width:560px;margin:auto;min-height:100vh;background:radial-gradient(circle at 15% 14%,#49b4ff55 0 18%,transparent 19%),radial-gradient(circle at 86% 20%,#6e46ff55 0 20%,transparent 21%),linear-gradient(180deg,#0b79f3 0%,#215bf1 48%,#173bbd 100%);overflow:hidden}.hero{position:relative;overflow:hidden;padding:34px 22px 46px;background:linear-gradient(135deg,#4d20c8 0%,#6734e4 48%,#168de8 100%);color:#fff;text-align:center;border-radius:0 0 34px 34px;box-shadow:0 14px 35px #5b42bb35}
.hero:before,.hero:after{content:"";position:absolute;border-radius:50%;background:#ffffff14}
.hero:before{width:210px;height:210px;right:-90px;top:-95px}
.hero:after{width:150px;height:150px;left:-70px;bottom:-85px}
.brandmark{position:relative;z-index:1;width:88px;height:88px;margin:0 auto 16px;border-radius:26px;background:#ffffff18;border:1px solid #ffffff40;display:grid;place-items:center;box-shadow:inset 0 0 0 1px #ffffff12,0 10px 28px #2a1c7b33;backdrop-filter:blur(8px)}
.brandmark svg{width:58px;height:58px}
.heroTitle{position:relative;z-index:1;font-size:38px;line-height:1;margin:0;font-weight:950;letter-spacing:-1.2px;background:linear-gradient(90deg,#ffffff 0%,#dff7ff 38%,#79e8ff 70%,#ffffff 100%);-webkit-background-clip:text;background-clip:text;color:transparent;text-shadow:0 5px 18px #132e8a33}
.heroTag{position:relative;z-index:1;margin:12px 0 0;font-size:11px;font-weight:900;letter-spacing:3.6px}
.heroSub{position:relative;z-index:1;margin:10px auto 0;max-width:420px;font-size:13px;line-height:1.55;opacity:.92}.main{padding:0 15px 24px;margin-top:-22px;position:relative}.features{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:14px 0}.feature{background:#ffffff26;border:1px solid #ffffff3d;border-radius:18px;padding:14px 8px;text-align:center;color:#fff;backdrop-filter:blur(8px)}.feature b{display:block;font-size:12px;margin-top:7px}.feature small{display:block;font-size:10px;line-height:1.35;opacity:.9;margin-top:4px}.feature .ficon{font-size:28px}.how{color:#fff;margin:18px 2px 6px}.how h3{font-size:17px;margin:0 0 12px}.steps{display:grid;grid-template-columns:1fr auto 1fr auto 1fr;align-items:start;gap:6px}.step{text-align:center}.num{width:28px;height:28px;margin:0 auto 6px;border-radius:50%;display:grid;place-items:center;background:#ffffff25;border:1px solid #ffffff66;font-weight:900}.step .big{font-size:28px}.step b{font-size:12px;display:block}.step small{font-size:10px;line-height:1.3;display:block;margin-top:3px;opacity:.9}.arrow{padding-top:31px;font-size:22px;opacity:.8}.card{background:#fff;border:1px solid #e7e6f3;border-radius:24px;padding:18px;margin-bottom:14px;box-shadow:0 9px 28px #3f467010}.scan{border:0;padding:16px 18px 17px}.scan .mut{margin:8px 0 10px}.eyebrow{font-size:11px;font-weight:900;letter-spacing:1.2px;color:#6b4ad8;text-transform:uppercase}.card h2{margin:5px 0 8px;font-size:20px}.card h3{color:#30355c}.btn{width:100%;border:0;border-radius:15px;padding:14px;font-weight:850;margin-top:9px;font-size:14px;cursor:pointer}.primary{background:linear-gradient(90deg,#6639dc,#2589ee);color:#fff;box-shadow:0 8px 18px #594bd52b}.secondary{background:#f0edff;color:#5543c8;border:1px solid #e3dcff}#preview{width:100%;max-height:420px;object-fit:cover;border-radius:19px;display:none;margin-top:14px;border:3px solid #f0edff}.result{display:none}.sectionHead{display:flex;align-items:center;gap:10px;margin-bottom:10px}.ico{width:38px;height:38px;border-radius:12px;display:grid;place-items:center;background:#f0edff;font-size:20px}.item{background:linear-gradient(180deg,#fafaff,#f7f8ff);border:1px solid #e5e6f4;border-radius:17px;padding:14px;margin-top:10px}.item h3{margin:0 0 7px;font-size:16px}.item p{margin:6px 0;color:#626a85;font-size:13px;line-height:1.55}.tag{display:inline-block;font-size:10px;background:#e9f8ef;color:#197044;border-radius:99px;padding:5px 8px;font-weight:900}.mut{color:#707892;font-size:13px;line-height:1.6}.status{display:none;padding:12px;background:#eef3ff;border:1px solid #dde7ff;border-radius:13px;margin-top:10px;color:#4f5dbc;font-size:13px;font-weight:800}.tipcard{background:linear-gradient(135deg,#fff9e9,#fffdf7);border-color:#f5e8b8}.refcard{background:#fbfbfe}.foot{text-align:center;padding:18px 20px 30px;color:#dbe8ff;font-size:11px}.restart{background:#222846;color:#fff}.divider{height:1px;background:#ececf4;margin:16px 0}</style></head>
<body><div class="app"><div class="hero">
  <div class="brandmark" aria-label="Logo SeniScan AI">
    <svg viewBox="0 0 64 64" role="img" aria-hidden="true">
      <defs>
        <linearGradient id="g1" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="#ffffff"/>
          <stop offset="1" stop-color="#d7ecff"/>
        </linearGradient>
      </defs>
      <rect x="8" y="17" width="48" height="32" rx="9" fill="url(#g1)"/>
      <rect x="16" y="12" width="13" height="8" rx="3" fill="#ffffff"/>
      <circle cx="32" cy="33" r="10" fill="#6639dc"/>
      <circle cx="32" cy="33" r="6" fill="#1f2c4f"/>
      <circle cx="35.5" cy="29.5" r="2" fill="#ffffff"/>
      <circle cx="48" cy="24" r="3" fill="#ffcf4d"/>
      <path d="M12 47c8-7 16-6 24-1s13 5 17 1v4H12z" fill="#25a3ff" opacity=".55"/>
    </svg>
  </div>
  <h1 class="heroTitle">SeniScan AI</h1>
  <p class="heroTag">IMBAS • KENAL • FAHAM • INGAT</p>
  <p class="heroSub">Pembelajaran Seni Visual Berbantu AI</p>\n</div><main class="main">
<div class="card scan"><div class="eyebrow">Pembelajaran Seni Visual Berbantu AI</div><h2>📷 Imbas Seni Sekeliling</h2><p class="mut">Ambil gambar objek di sekeliling. SeniScan membantu mengenal pasti unsur seni dan prinsip rekaan yang kelihatan.</p>
<input id="file" type="file" accept="image/*" capture="environment" hidden><button class="btn primary" onclick="file.setAttribute('capture','environment');file.click()">📷 Scan Sekarang</button><button class="btn secondary" onclick="file.removeAttribute('capture');file.click()">🖼️ Pilih dari Galeri</button><img id="preview"><button id="go" class="btn primary" style="display:none">✨ Analisis Sekarang</button><div id="status" class="status">🔎 SeniScan sedang melihat dan menganalisis gambar...</div></div>
<section class="features">
      <div class="feature"><div class="ficon">🎨</div><b>Unsur Seni</b><small>Kenal pasti elemen visual</small></div>
      <div class="feature"><div class="ficon">📐</div><b>Prinsip Rekaan</b><small>Fahami prinsip yang digunakan</small></div>
      <div class="feature"><div class="ficon">🧠</div><b>Nota Mudah</b><small>Penjelasan ringkas untuk diingat</small></div>
    </section>
    <section class="how"><h3>❓ Cara Menggunakan</h3><div class="steps">
      <div class="step"><div class="num">1</div><div class="big">📷</div><b>Imbas</b><small>Ambil gambar atau pilih dari galeri</small></div><div class="arrow">→</div>
      <div class="step"><div class="num">2</div><div class="big">🤖</div><b>AI Kenal Pasti</b><small>Analisis unsur dan prinsip rekaan</small></div><div class="arrow">→</div>
      <div class="step"><div class="num">3</div><div class="big">📘</div><b>Faham & Ingat</b><small>Dapatkan penerangan dan nota ringkas</small></div>
    </div></section>
    <div id="result" class="result"><div class="card"><div class="sectionHead"><div class="ico">🤖</div><h2>Apa yang AI nampak?</h2></div><h3 id="obj"></h3><p id="desc" class="mut"></p><span id="conf" class="tag"></span></div>
<div class="card"><div class="sectionHead"><div class="ico">🎨</div><h2>Unsur Seni</h2></div><div id="els"></div></div>
<div class="card"><div class="sectionHead"><div class="ico">⚖️</div><h2>Prinsip Rekaan</h2></div><div id="prs"></div></div>
<div class="card tipcard"><div class="sectionHead"><div class="ico">🧠</div><h2>Ingat Mudah</h2></div><p id="tip" class="mut"></p><div class="divider"></div><h3>📚 Nota Seni</h3><div id="notes"></div><div class="divider"></div><h3>Rumusan</h3><p id="sum" class="mut"></p></div>
<div class="card refcard"><div class="sectionHead"><div class="ico">📖</div><h2>Rujukan</h2></div><div id="refs" class="mut"></div></div>
<button class="btn restart" onclick="window.scrollTo({top:0,behavior:'smooth'});file.value='';preview.style.display='none';go.style.display='none';resultEl.style.display='none'">↻ Scan Objek Lain</button></div>
</main><div class="foot">SeniScan AI • Belajar seni melalui dunia di sekeliling anda</div></div>
<script>
let imageData="";const file=document.getElementById("file"),preview=document.getElementById("preview"),go=document.getElementById("go"),statusEl=document.getElementById("status"),resultEl=document.getElementById("result"),obj=document.getElementById("obj"),desc=document.getElementById("desc"),conf=document.getElementById("conf"),els=document.getElementById("els"),prs=document.getElementById("prs"),tip=document.getElementById("tip"),notes=document.getElementById("notes"),refs=document.getElementById("refs"),sum=document.getElementById("sum");
file.onchange=()=>{const f=file.files[0];if(!f)return;const r=new FileReader();r.onload=()=>{imageData=r.result;preview.src=imageData;preview.style.display="block";go.style.display="block"};r.readAsDataURL(f)};
const esc=s=>String(s||"").replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[m]));
go.onclick=async()=>{if(!imageData)return;statusEl.style.display="block";go.disabled=true;try{const r=await fetch("/api/analyze",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({image:imageData})});const d=await r.json();if(!r.ok)throw Error(d.error||"Analisis gagal");obj.textContent=d.object_name||"";desc.textContent=d.object_description||"";conf.textContent="Keyakinan: "+(d.overall_confidence||"");els.innerHTML=(d.elements||[]).map(x=>'<div class="item"><h3>'+esc(x.name)+'</h3><span class="tag">'+esc(x.confidence)+'</span><p>'+esc(x.explanation)+'</p>'+(x.types?.length?'<p><b>Jenis/Kategori:</b> '+esc(x.types.join(", "))+'</p>':"")+(x.examples?.length?'<p><b>Contoh:</b> '+esc(x.examples.join("; "))+'</p>':"")+(x.color_details?'<p><b>Analisis warna:</b> '+esc(x.color_details)+'</p>':"")+'<p><b>👀 Bukti:</b> '+esc(x.evidence)+'</p></div>').join("")||'<p class="mut">Tiada unsur yang cukup jelas.</p>';prs.innerHTML=(d.principles||[]).map(x=>'<div class="item"><h3>'+esc(x.name)+'</h3><span class="tag">'+esc(x.confidence)+'</span><p>'+esc(x.explanation)+'</p><p><b>👀 Bukti:</b> '+esc(x.evidence)+'</p></div>').join("")||'<p class="mut">Tiada prinsip yang cukup jelas.</p>';tip.textContent=d.memory_tip||"";notes.innerHTML=(d.learning_notes||[]).map(x=>'<div class="item"><h3>'+esc(x.title)+'</h3><p>'+esc(x.note)+'</p></div>').join("")||'<p class="mut">Tiada nota tambahan.</p>';refs.innerHTML=(d.references||[]).map(x=>'<p>• '+esc(x)+'</p>').join("");sum.textContent=d.learning_summary||"";resultEl.style.display="block";resultEl.scrollIntoView({behavior:"smooth"})}catch(e){alert(e.message)}finally{statusEl.style.display="none";go.disabled=false}};
</script><script>if("serviceWorker" in navigator){window.addEventListener("load",()=>navigator.serviceWorker.register("/sw.js").catch(()=>{}))}</script></body></html>"""

PROMPT="""Lihat imej ini. Senaraikan objek dan unsur seni yang benar-benar kelihatan.
Pulangkan JSON sahaja, dengan SEMUA nilai teks dalam Bahasa Melayu:
{"object_name":"nama ringkas objek atau gubahan", "object_description":"penerangan ringkas imej", "overall_confidence":"Berdasarkan pemerhatian AI", "visual":{"lines":[],"shapes":[],"forms":[],"textures":[],"colors":[],"space":[],"values":[]}}
Isi setiap senarai seperti berikut, maksimum 4 item setiap kategori:
lines, shapes, forms, textures: {"type":"jenis", "location":"objek dan lokasi"}.
colors: {"name":"nama warna", "location":"objek dan lokasi"}.
space, values: {"observation":"bukti khusus pada imej"}.
Garisan: menegak, mendatar, diagonal atau melengkung.
Rupa ialah kawasan 2D: bulatan, segi tiga, segi empat atau organik.
Bentuk ialah isipadu 3D: hanya jika objek mempunyai kedalaman yang jelas. Segi empat rata BUKAN kubus. Bulatan rata BUKAN sfera. Imej geometri rata boleh mempunyai forms kosong.
Jalinan: hanya sifat permukaan yang kelihatan, jangan anggap semua objek licin atau kasar.
Warna: senaraikan semua warna utama yang jelas berserta lokasinya.
Ruang: hanya pertindihan atau kedalaman sebenar. Nilai: hanya bukti ton terang-gelap.
Jika tidak kelihatan, gunakan []. Jangan mereka ciri. Jangan analisis Prinsip Rekaan dalam langkah ini.
Gunakan nama Melayu: kiri, kanan, atas, bawah, tengah, merah, hijau, biru, bulatan, segi tiga, segi empat sama.
"""

def _list(v):
    return v if isinstance(v,list) else []

def _text(v):
    return str(v or "").strip()

def _join_obs(items, key="observation"):
    vals=[]
    for x in _list(items):
        if isinstance(x,dict):
            a=_text(x.get(key))
            if a: vals.append(a)
    return "; ".join(vals)

def _join_pairs(items, akey, bkey):
    vals=[]
    for x in _list(items):
        if not isinstance(x,dict): continue
        a=_text(x.get(akey)); b=_text(x.get(bkey))
        if a and b: vals.append(f"{a} pada {b}")
        elif a: vals.append(a)
        elif b: vals.append(b)
    return "; ".join(vals)

BM_MAP={
"straight":"lurus","versus":"berbanding","vs":"berbanding","left":"kiri","right":"kanan","edges":"tepi","edge":"tepi","corners":"penjuru","corner":"penjuru","central":"tengah","position":"kedudukan","positions":"kedudukan","row":"baris","rows":"baris","across":"merentasi","along":"sepanjang","around":"di sekeliling","between":"di antara","below":"di bawah","above":"di atas","at":"di","on":"pada","in":"di dalam","the":"","is":"ialah","are":"ialah","of":"","and":"dan","with":"dengan",
"visual weight":"berat visual","focal point":"tumpuan utama","focal":"tumpuan","contrast":"kontra","contrasting":"berkontra","colors":"warna","colours":"warna","color":"warna","colour":"warna","similar":"serupa","same":"sama","sizes":"saiz","size":"saiz","pattern":"corak","patterns":"corak","elements":"unsur","element":"unsur","arranged":"disusun","arrangement":"susunan","horizontal row":"baris mendatar","evenly spaced":"berjarak sekata","spaced":"berjarak","spacing":"jarak","small":"kecil","larger":"lebih besar","smaller":"lebih kecil","large":"besar","two":"dua","three":"tiga","four":"empat","five":"lima","no":"tiada","none":"tiada","not visible":"tidak kelihatan","not evident":"tidak kelihatan",
"object":"objek","objects":"objek","triangle":"segi tiga","triangles":"segi tiga","square":"segi empat sama","squares":"segi empat sama","circles":"bulatan","rectangles":"segi empat tepat",
"repetition":"pengulangan","repeated":"berulang","repeating":"berulang","repeat":"berulang","rhythm":"irama","movement":"pergerakan","direction":"arah","directs":"mengarahkan","leading":"mengarah",
"balanced":"seimbang","balance":"imbangan","symmetrical":"simetri","symmetric":"simetri","symmetry":"simetri","stability":"kestabilan",
"unity":"kesatuan","unified":"bersatu","cohesive":"bersatu","variety":"kepelbagaian","variation":"variasi","different":"berbeza","harmony":"harmoni","harmonious":"harmoni","compatible":"serasi","consistent":"selaras",
"vertical":"menegak","horizontal":"mendatar","curved":"melengkung","wavy":"beralun","zigzag":"zigzag",
"smooth":"licin","slightly rough":"agak kasar","rough":"kasar","glossy":"berkilat","ribbed":"beralur",
"cylindrical":"silinder","cylinder":"silinder","circular":"bulatan","circle":"bulatan",
"rectangular":"segi empat tepat","rectangle":"segi empat tepat","geometric":"geometri","organic":"organik",
"blue":"biru","green":"hijau","white":"putih","black":"hitam","red":"merah","yellow":"kuning","orange":"jingga","gold":"keemasan","golden":"keemasan","beige":"kuning air","cream":"krim","cyan":"biru sian","teal":"biru kehijauan","navy":"biru tua","lime":"hijau muda","maroon":"merah tua",
"purple":"ungu","grey":"kelabu","gray":"kelabu","pink":"merah jambu","brown":"coklat","high":"Jelas","medium":"Berkemungkinan","low":"Tidak cukup jelas"
}
def _bm(s):
    s=_text(s)
    # Istilah lokasi/objek lazim supaya bahagian bukti kekal dalam Bahasa Melayu.
    phrase_map={
      "floral arrangement":"gubahan bunga","flower arrangement":"gubahan bunga","asymmetrical":"tidak simetri","asymmetric":"tidak simetri","composition":"komposisi","foliage":"dedaunan","chrysanthemum":"bunga kekwa","calla lilies":"bunga kala","pandanus":"pandan","dynamic":"dinamik","featuring":"yang menampilkan","and":"dan","with":"dengan","create":"mewujudkan","includes":"merangkumi","left side":"bahagian kiri","right side":"bahagian kanan","top":"bahagian atas","bottom":"bahagian bawah","lid":"penutup","base":"bahagian dasar","handle":"pemegang","stem":"batang","stems":"batang","branch":"ranting","branches":"ranting","petal":"kelopak","petals":"kelopak","flower":"bunga","flowers":"bunga","arrangement":"gubahan","vibrant":"terang",
      "middle left":"bahagian tengah kiri","middle right":"bahagian tengah kanan","upper left":"bahagian atas kiri","upper right":"bahagian atas kanan","lower left":"bahagian bawah kiri","lower right":"bahagian bawah kanan","extending diagonally":"memanjang secara diagonal","subtle shadows":"bayang lembut","subtle highlights":"pantulan cahaya lembut","leaves":"daun","shapes":"rupa","shape":"rupa","forms":"bentuk","form":"bentuk","lines":"garisan","line":"garisan","against":"berkontra dengan","variety of":"kepelbagaian","main body":"badan utama","body":"badan objek","label background":"latar label","background":"latar belakang",
      "text color":"warna tulisan","text":"tulisan","logo leaf":"logo daun","leaf accents":"hiasan daun",
      "leaf graphics":"grafik daun","bottle surface":"permukaan botol","bottle":"botol","label":"label",
      "upper section":"bahagian atas","lower section":"bahagian bawah","centre":"tengah","center":"tengah",
      "foreground":"bahagian hadapan","background area":"kawasan latar","behind":"di belakang","in front":"di hadapan",
      "bright":"terang","dark":"gelap","light":"cerah","shadow":"bayang","shadows":"bayang",
      "highlight":"pantulan cahaya","highlights":"pantulan cahaya","surface":"permukaan",
      "dominant":"dominan","dominant color":"warna dominan","main color":"warna utama",
      "petal cluster":"kelompok kelopak","flower cluster":"kelompok bunga","leaf":"daun",
      "frog":"katak","large":"besar","round":"bulat","eyes":"mata","eye":"mata","triangular":"segi tiga","snout":"muncung","an":"sebuah","a":"sebuah","curving":"melengkung","curved lines":"garisan melengkung","vertical lines":"garisan menegak",
      "horizontal lines":"garisan mendatar","diagonal lines":"garisan diagonal","organic shapes":"rupa organik",
      "geometric shapes":"rupa geometri","organic forms":"bentuk organik","cylindrical form":"bentuk silinder"
    }
    for en,ms in sorted(phrase_map.items(),key=lambda x:-len(x[0])):
        s=re.sub(r"\b"+re.escape(en)+r"\b",ms,s,flags=re.I)
    for en,ms in sorted(BM_MAP.items(),key=lambda x:-len(x[0])):
        s=re.sub(r"\b"+re.escape(en)+r"\b",ms,s,flags=re.I)
    return re.sub(r"[ \t]+", " ", s).strip()

PRINCIPLE_KEYS=("focal_points","contrasts","repetitions","balance","unity","variety","harmony","movement")

def _principle_observations(items):
    if isinstance(items,str): items=[items]
    if isinstance(items,dict): items=[items]
    out=[]
    for item in _list(items):
        raw=item if isinstance(item,str) else item.get("observation",item.get("evidence","")) if isinstance(item,dict) else ""
        s=_bm(raw)
        if len(s)<24 or re.search(r"\b(tiada|tidak kelihatan|tidak jelas|tidak cukup|no|none|not evident|not visible|cannot|unclear)\b",s,re.I):
            continue
        out.append({"observation":s})
    return out

def _valid_pairs(items,kind):
    out=[]
    allowed={
      "line":("menegak","mendatar","melengkung","beralun","zigzag","putus-putus","diagonal"),
      "shape":("bulatan","segi empat","segi tiga","bujur","oval","geometri","organik"),
      "form":("silinder","sfera","kubus","kon","piramid","prisma","organik"),
      "texture":("licin","kasar","agak kasar","berkilat","beralur","berbulu","berduri")
    }[kind]
    for x in _list(items):
        if not isinstance(x,dict): continue
        typ=_bm(x.get("type")); loc=_bm(x.get("location"))
        # Repair common 2D/3D model confusion rather than displaying it.
        if kind=="shape" and typ=="silinder": continue
        if kind=="form" and typ in ("bulatan","segi empat tepat","segi tiga","bujur","oval"): continue
        if typ and any(a in typ.lower() for a in allowed) and loc:
            out.append({"type":typ,"location":loc})
    return out

def _valid_obs(items,kind):
    out=[]
    reject={
      "space":("texture","jalinan","licin","kasar","label sahaja","atas label","bawah label"),
      "value":("clear water","clear text","clear logo","transparent","translucent","lutsinar","jernih"),
    }.get(kind,())
    require={
      "space":("hadapan","belakang","pertindih","jarak","kedalaman","ruang positif","ruang negatif","foreground","background"),
      "value":("terang","gelap","ton","cahaya","bayang","highlight","shadow"),
    }.get(kind,())
    for x in _list(items):
        if not isinstance(x,dict): continue
        s=_bm(x.get("observation")); low=s.lower()
        if s and not any(r in low for r in reject) and (not require or any(r in low for r in require)):
            out.append({"observation":s})
    return out

ART_NOTES={
"Garisan":"Garisan ialah kesan titik yang bergerak dan boleh menunjukkan arah, pergerakan, sempadan atau karakter sesuatu objek.",
"Rupa":"Rupa ialah kawasan dua dimensi yang mempunyai panjang dan lebar. Rupa boleh bersifat geometri atau organik.",
"Bentuk":"Bentuk mempunyai tiga dimensi, iaitu panjang, lebar dan kedalaman, serta mempunyai isi padu.",
"Jalinan":"Jalinan merujuk sifat permukaan sesuatu objek seperti licin, kasar, berkilat atau beralur.",
"Warna":"Warna terhasil daripada tindak balas cahaya pada objek dan boleh mewujudkan suasana, penegasan serta perbezaan visual.",
"Ruang":"Ruang merujuk jarak atau kawasan di antara, di sekeliling, di hadapan atau di belakang objek dan boleh menghasilkan kesan kedalaman.",
"Nilai":"Nilai ialah darjah terang dan gelap pada sesuatu warna atau objek yang membantu menunjukkan cahaya, bayang dan bentuk.",
"Penegasan":"Penegasan menjadikan satu bahagian visual sebagai tumpuan utama melalui perbezaan saiz, warna, kedudukan atau kontras.",
"Kontra":"Kontra ialah perbezaan ketara antara unsur seperti warna, nilai, saiz, rupa atau bentuk.",
"Irama & Pergerakan":"Irama dan pergerakan terhasil melalui pengulangan atau susunan unsur yang mengarahkan pergerakan mata.",
"Imbangan":"Imbangan ialah pengagihan berat visual yang mewujudkan kestabilan dalam sesuatu susunan.",
"Kesatuan":"Kesatuan berlaku apabila unsur-unsur visual saling berkaitan dan kelihatan sebagai satu keseluruhan.",
"Kepelbagaian":"Kepelbagaian ialah penggunaan variasi unsur visual untuk mengelakkan kebosanan dan menambah daya tarikan.",
"Harmoni":"Harmoni berlaku apabila unsur-unsur visual kelihatan serasi, selaras dan saling melengkapi."
}

REFERENCES=[
"Buku Teks Pendidikan Seni Visual KSSM, Kementerian Pendidikan Malaysia (rujukan konsep Unsur Seni dan Prinsip Rekaan).",
"Ocvirk, O. G. et al. — Art Fundamentals: Theory and Practice (rujukan asas formal elements dan principles of design)."
]

def build_art_result(obs):
    if not isinstance(obs,dict):
        raise RuntimeError("Format pemerhatian AI tidak sah.")

    vis=obs.get("visual") if isinstance(obs.get("visual"),dict) else {}
    # Lapisan penapis PSV: jangan percaya kategori mentah model secara terus.
    vis=dict(vis)
    vis["lines"]=_valid_pairs(vis.get("lines"),"line")
    vis["shapes"]=_valid_pairs(vis.get("shapes"),"shape")
    vis["forms"]=_valid_pairs(vis.get("forms"),"form")
    vis["textures"]=_valid_pairs(vis.get("textures"),"texture")
    vis["space"]=_valid_obs(vis.get("space"),"space")
    vis["values"]=_valid_obs(vis.get("values"),"value")
    for k in PRINCIPLE_KEYS:
        vis[k]=_principle_observations(vis.get(k))
    # Prinsip rekaan perlu lebih ketat: penegasan hanya satu fokus dominan, pengulangan mesti nyata,
    # dan kesatuan/kepelbagaian tidak dipaparkan daripada istilah umum semata-mata.
    if len(vis["focal_points"]) != 1:
        vis["focal_points"]=[]
    vis["repetitions"]=[x for x in vis["repetitions"] if re.search(r"ulang|berulang|pengulangan|repet",x["observation"],re.I)]
    vis["balance"]=[x for x in vis["balance"] if re.search(r"seimbang|imbang|simetri|stabil|kiri.*kanan|kanan.*kiri",x["observation"],re.I)]
    vis["unity"]=[x for x in vis["unity"] if re.search(r"kesatuan|bersatu|serasi|selaras|harmoni|cohes",x["observation"],re.I)]
    vis["variety"]=[x for x in vis["variety"] if re.search(r"pelbagai|kepelbagaian|variasi|berbeza|variety",x["observation"],re.I)]
    vis["harmony"]=[x for x in vis["harmony"] if re.search(r"harmoni|serasi|selaras|sepadan",x["observation"],re.I)]
    vis["movement"]=[x for x in vis["movement"] if re.search(r"arah|gerak|menghala|mengarah|laluan|diagonal|melengkung",x["observation"],re.I)]
    vis["colors"]=[{"name":_bm(x.get("name")),"location":_bm(x.get("location"))} for x in _list(vis.get("colors")) if isinstance(x,dict) and _text(x.get("name")) and _text(x.get("location"))]
    # Normalisasi nama warna dan buang pendua.
    color_syn={"oren":"jingga","orange":"jingga","pink":"merah jambu","grey":"kelabu","gray":"kelabu","purple":"ungu","brown":"coklat","navy":"biru tua","lime":"hijau muda"}
    clean_colors=[]
    seen=set()
    for x in vis["colors"]:
        nm=color_syn.get(x["name"].lower(),x["name"].lower()).strip()
        loc=x["location"].strip() or "bahagian objek yang jelas kelihatan"
        if nm and nm not in seen:
            clean_colors.append({"name":nm,"location":loc});seen.add(nm)
    vis["colors"]=clean_colors
    # Fallback bukti: jika model menghuraikan ciri dengan jelas tetapi terlupa mengisi kategori JSON,
    # pulihkan hanya kategori yang boleh disokong oleh penerangan visualnya.
    desc=_bm(obs.get("object_description"))
    dl=desc.lower()
    if not vis["colors"]:
        # Imbas keseluruhan respons model kerana ada model yang menyebut warna di bahagian lain
        # tetapi terlupa mengisi array colors.
        raw_blob=_bm(json.dumps(obs,ensure_ascii=False)).lower()
        known=("merah jambu","merah","jingga","kuning","hijau","biru tua","biru","ungu","putih","hitam","kelabu","coklat","krim","keemasan")
        cols=[]
        for x in known:
            if re.search(r"\b"+re.escape(x)+r"\b",raw_blob):
                cols.append(x)
        if "merah jambu" in cols and "merah" in cols:
            cols.remove("merah")
        if "biru tua" in cols and "biru" in cols:
            cols.remove("biru")
        if cols:
            vis["colors"]=[{"name":x,"location":"bahagian objek utama yang jelas kelihatan"} for x in cols[:5]]
    if not vis["lines"]:
        ls=[x for x in ("menegak","mendatar","melengkung","beralun","diagonal","zigzag") if x in dl]
        if ls: vis["lines"]=[{"type":x,"location":"bahagian objek yang jelas kelihatan"} for x in ls]
    if not vis["forms"]:
        fs=[x for x in ("silinder","sfera","kubus","kon","piramid","prisma") if x in dl]
        if fs:
            vis["forms"]=[{"type":x,"location":"bentuk utama objek"} for x in fs]
        elif re.search(r"bunga|daun|dedaunan|kelopak|gubahan",dl):
            vis["forms"]=[{"type":"organik","location":"bunga dan daun yang mempunyai isi padu"}]
    if not vis["shapes"] and re.search(r"daun|dedaunan|kelopak|bunga",dl):
        vis["shapes"]=[{"type":"organik","location":"daun atau kelopak yang kelihatan"}]
    if not vis["shapes"] and re.search(r"geometri|bulat|segi tiga|bulatan|segi empat",dl):
        recovered_shapes=[]
        if re.search(r"bulat|bulatan",dl):
            recovered_shapes.append({"type":"bulatan","location":"bahagian objek yang berbentuk bulat"})
        if re.search(r"segi tiga|triang",dl):
            recovered_shapes.append({"type":"segi tiga","location":"bahagian objek yang berbentuk segi tiga"})
        if not recovered_shapes and "geometri" in dl:
            recovered_shapes.append({"type":"geometri","location":"bahagian objek yang dibina daripada rupa geometri"})
        vis["shapes"]=recovered_shapes
    if not vis["lines"] and ("geometri" in dl or len(vis["shapes"]) >= 2):
        vis["lines"]=[
            {"type":"diagonal","location":"sempadan antara rupa geometri"},
            {"type":"melengkung","location":"kontur pada bahagian objek yang berbentuk bulat"}
        ]
    if not vis["textures"]:
        ts=[x for x in ("licin","kasar","berkilat","beralur","berbulu","berduri") if x in dl]
        if ts: vis["textures"]=[{"type":x,"location":"permukaan objek yang jelas kelihatan"} for x in ts]
    if not vis["space"] and re.search(r"bertindih|pertindihan|di hadapan|di belakang|kedalaman|gubahan|komposisi",dl):
        vis["space"]=[{"observation":"Susunan bahagian objek yang saling berada di hadapan dan belakang menghasilkan kesan ruang dan kedalaman."}]
    if not vis["values"] and re.search(r"terang.*gelap|gelap.*terang|cahaya|bayang|ton|berkilat",dl):
        vis["values"]=[{"observation":"Perbezaan cahaya dan bayang pada permukaan objek menghasilkan nilai terang dan gelap."}]
    # Jangan cipta imbangan daripada huraian umum komposisi.
    # Dua warna sahaja tidak membuktikan kontra yang ketara.
    elements=[]
    principles=[]

    line_ev=_join_pairs(vis.get("lines"),"type","location")
    if line_ev:
        elements.append({"name":"Garisan","confidence":"Jelas","explanation":"Garisan dapat dikenal pasti melalui arah, lengkungan atau sempadan visual pada objek.","evidence":line_ev,"types":[_text(x.get("type")) for x in _list(vis.get("lines")) if isinstance(x,dict) and _text(x.get("type"))],"examples":[],"color_details":""})

    shape_ev=_join_pairs(vis.get("shapes"),"type","location")
    if shape_ev:
        elements.append({"name":"Rupa","confidence":"Jelas","explanation":"Rupa merujuk kawasan dua dimensi yang dapat dilihat pada permukaan objek.","evidence":shape_ev,"types":[_text(x.get("type")) for x in _list(vis.get("shapes")) if isinstance(x,dict) and _text(x.get("type"))],"examples":[],"color_details":""})

    form_ev=_join_pairs(vis.get("forms"),"type","location")
    if form_ev:
        elements.append({"name":"Bentuk","confidence":"Jelas","explanation":"Bentuk merujuk sifat tiga dimensi dan isi padu objek.","evidence":form_ev,"types":[_text(x.get("type")) for x in _list(vis.get("forms")) if isinstance(x,dict) and _text(x.get("type"))],"examples":[],"color_details":""})

    tex_ev=_join_pairs(vis.get("textures"),"type","location")
    if tex_ev:
        elements.append({"name":"Jalinan","confidence":"Jelas","explanation":"Jalinan menunjukkan sifat permukaan yang dapat dilihat seperti licin, berkilat, kasar atau beralur.","evidence":tex_ev,"types":[_text(x.get("type")) for x in _list(vis.get("textures")) if isinstance(x,dict) and _text(x.get("type"))],"examples":[],"color_details":""})

    # Warna ialah unsur asas yang penting. Jika model tidak memulangkan array colors tetapi
    # warna jelas disebut pada pemerhatian/prinsip, pulihkan nama warna yang dapat disokong.
    if not vis["colors"]:
        evidence_blob=_bm(json.dumps(obs,ensure_ascii=False)).lower()
        known=("merah jambu","merah","jingga","kuning","hijau","biru","ungu","putih","hitam","kelabu","coklat")
        recovered=[]
        for col in known:
            if re.search(r"\\b"+re.escape(col)+r"\\b",evidence_blob):
                recovered.append({"name":col,"location":"bahagian objek yang jelas kelihatan"})
        if recovered:
            names0=[x["name"] for x in recovered]
            if "merah jambu" in names0:
                recovered=[x for x in recovered if x["name"]!="merah"]
            vis["colors"]=recovered

    color_ev=_join_pairs(vis.get("colors"),"name","location")
    if color_ev:
        names=[_text(x.get("name")) for x in _list(vis.get("colors")) if isinstance(x,dict) and _text(x.get("name"))]
        elements.append({"name":"Warna","confidence":"Jelas","explanation":"Warna membantu membezakan bahagian objek dan mewujudkan kesan visual tertentu.","evidence":color_ev,"types":[],"examples":[],"color_details":", ".join(names)})

    space_ev=_join_obs(vis.get("space"))
    if space_ev:
        elements.append({"name":"Ruang","confidence":"Jelas","explanation":"Ruang merujuk jarak, kedalaman atau kawasan di sekeliling dan antara bahagian objek.","evidence":space_ev,"types":[],"examples":[],"color_details":""})

    value_ev=_join_obs(vis.get("values"))
    if value_ev:
        elements.append({"name":"Nilai","confidence":"Jelas","explanation":"Nilai ialah perbezaan terang dan gelap yang terhasil daripada cahaya, bayang atau ton.","evidence":value_ev,"types":[],"examples":[],"color_details":""})

    def add_principle(name, items, explanation):
        ev=_join_obs(items)
        if ev:
            principles.append({"name":name,"confidence":"Berdasarkan pemerhatian AI","explanation":explanation+" Bukti visual: "+ev,"evidence":ev})

    add_principle("Penegasan",vis.get("focal_points"),"Penegasan berlaku apabila satu bahagian menjadi tumpuan utama.")
    add_principle("Kontra",vis.get("contrasts"),"Kontra terhasil melalui perbezaan yang ketara seperti warna, nilai, saiz atau rupa.")
    add_principle("Irama & Pergerakan",vis.get("repetitions")+vis.get("movement"),"Pengulangan unsur visual boleh mewujudkan irama dan mengarahkan pergerakan mata.")
    add_principle("Imbangan",vis.get("balance"),"Imbangan mewujudkan kestabilan visual melalui susunan unsur.")
    add_principle("Kesatuan",vis.get("unity"),"Kesatuan berlaku apabila unsur visual kelihatan saling berkaitan sebagai satu keseluruhan.")
    add_principle("Kepelbagaian",vis.get("variety"),"Kepelbagaian wujud melalui variasi unsur seperti warna, rupa, bentuk atau jalinan.")

    add_principle("Harmoni",vis.get("harmony"),"Harmoni terhasil apabila unsur visual kelihatan serasi dan saling melengkapi.")

    names=[x["name"] for x in elements]
    pnames=[x["name"] for x in principles]
    memory=[]
    if names: memory.append("Unsur yang jelas: "+", ".join(names)+".")
    if pnames: memory.append("Prinsip yang jelas: "+", ".join(pnames)+".")
    tip=" ".join(memory) or "Fokus pada apa yang benar-benar dapat dilihat pada objek."

    obj_name=_bm(obs.get("object_name"))
    if re.search(r"gubahan|arrangement",obj_name,re.I):
        obj_name="Gubahan bunga"
    desc_parts=[]
    if names: desc_parts.append("Imej menunjukkan "+(obj_name.lower() or "objek")+" dengan unsur "+", ".join(names)+".")
    if pnames: desc_parts.append("Prinsip rekaan yang dapat dikenal pasti ialah "+", ".join(pnames)+".")
    bm_description=_bm(" ".join(desc_parts) or obs.get("object_description"))
    bm_description=re.sub(r"^(sebuah|an)\s+","",bm_description,flags=re.I)

    return {
        "object_name":obj_name,
        "object_description":bm_description,
        "overall_confidence":_bm(obs.get("overall_confidence")) or "Berkemungkinan",
        "elements":elements,
        "principles":principles,
        "memory_tip":tip,
        "learning_summary":"Analisis dibuat berdasarkan bukti visual pada imej. Unsur Seni dan Prinsip Rekaan hanya dipaparkan apabila mempunyai bukti yang mencukupi.",
        "learning_notes":[{"title":n,"note":ART_NOTES[n]} for n in names+pnames if n in ART_NOTES],
        "references":REFERENCES
    }

PRINCIPLE_PROMPT='''Teliti keseluruhan imej untuk Prinsip Rekaan sahaja, termasuk objek kecil dan susunan kiri-kanan.
Pulangkan JSON sahaja dengan kunci focal_points, contrasts, repetitions, balance, unity, variety, harmony, movement.
Setiap nilai ialah [] jika tiada bukti, atau [{"observation":"ayat Bahasa Melayu yang menyatakan objek, ciri visual dan lokasi khusus"}].
repetitions: nyatakan motif yang berulang, bilangannya dan lokasi.
balance: nyatakan objek di kiri dan kanan yang mengimbangkan berat visual.
contrasts: nyatakan dua ciri yang benar-benar berkontra dan lokasi.
harmony: nyatakan warna, rupa atau jalinan yang serasi pada objek tertentu.
movement: nyatakan susunan atau garisan yang mengarahkan mata.
unity: nyatakan ciri khusus yang menyatukan objek.
variety: nyatakan rupa atau saiz yang berbeza.
focal_points: satu objek paling dominan sahaja.
Jangan mereka bukti. Elakkan ayat umum seperti "susunan simetri" tanpa menyebut objek. Imej kosong boleh mempunyai semua nilai [].
WAJIB Bahasa Melayu: kiri, kanan, atas, bawah, bulatan, segi tiga, segi empat, merah, hijau, biru. Jangan gunakan perkataan Inggeris dalam observation.'''

def query_visual(image,question,reasoning=False):
    if not CF_ACCOUNT_ID or not CF_API_TOKEN:
        raise RuntimeError("Cloudflare belum dikonfigurasi. Semak CLOUDFLARE_ACCOUNT_ID dan CLOUDFLARE_API_TOKEN di Render.")
    payload={
        "task":"query",
        "image":image,
        "question":question,
        "reasoning":reasoning,
        "temperature":0,
        "max_tokens":1800,
        "stream":False
    }
    url=f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/{MODEL}"
    req=urllib.request.Request(url,data=json.dumps(payload).encode(),headers={"Authorization":"Bearer "+CF_API_TOKEN,"Content-Type":"application/json"},method="POST")
    try:
        with urllib.request.urlopen(req,timeout=90) as r:
            data=json.loads(r.read())
    except urllib.error.HTTPError as e:
        detail=e.read().decode(errors="replace")
        print(f"[SeniScan] Cloudflare HTTP {e.code}: {detail[:500]}", flush=True)
        if e.code==401: raise RuntimeError("Token Cloudflare tidak sah atau permission Workers AI tidak mencukupi.")
        if e.code==403: raise RuntimeError("Akses Workers AI ditolak. Semak permission token dan Account ID.")
        if e.code==429: raise RuntimeError("Kuota/limit Workers AI telah dicapai. Cuba semula kemudian.")
        raise RuntimeError("Ralat Cloudflare AI: "+detail[:500])

    result=data.get("result")
    while isinstance(result,dict) and "result" in result and not any(k in result for k in ("answer","response","caption","description","text")):
        result=result.get("result")

    if isinstance(result,dict):
        text=(result.get("answer") or result.get("response") or result.get("caption") or result.get("description") or result.get("text") or "")
    elif isinstance(result,str):
        text=result
    else:
        text=""

    if not text:
        raise RuntimeError("Respons Cloudflare AI diterima tetapi tidak mengandungi pemerhatian yang boleh dibaca.")

    text=re.sub(r"^\`\`\`(?:json)?|\`\`\`$","",str(text).strip()).strip()
    try:
        obs=json.loads(text)
    except Exception:
        m=re.search(r"\{.*\}",text,re.S)
        if not m:
            raise RuntimeError("AI berjaya melihat imej tetapi respons pemerhatian belum dapat dibaca. Cuba sekali lagi.")
        obs=json.loads(m.group())

    if not isinstance(obs,dict):
        raise RuntimeError("Format pemerhatian AI tidak sah. Cuba sekali lagi.")
    return obs

def analyze(image):
    if not isinstance(image,str) or not image.startswith("data:image/") or ";base64," not in image:
        raise ValueError("Sila pilih fail gambar yang sah.")
    obs=query_visual(image,PROMPT,reasoning=False)
    result=build_art_result(obs)
    if not result["principles"]:
        try:
            focused=query_visual(image,PRINCIPLE_PROMPT,reasoning=False)
            visual=focused.get("visual",focused)
            if isinstance(visual,dict):
                combined=dict(obs.get("visual") or {})
                combined.update({k:visual[k] for k in PRINCIPLE_KEYS if k in visual})
                obs=dict(obs,visual=combined)
                result=build_art_result(obs)
            print("[SeniScan] Focused principle check: "+str(len(result["principles"]))+" supported principles",flush=True)
        except (RuntimeError,ValueError,urllib.error.URLError,TimeoutError) as e:
            print("[SeniScan] Focused principle check unavailable: "+type(e).__name__,flush=True)
            result["learning_summary"]+=" Semakan tambahan Prinsip Rekaan tidak dapat diselesaikan. Sila cuba semula."
    if not result["elements"] and not result["principles"]:
        result["overall_confidence"]="Tidak cukup jelas"
    return result

class H(BaseHTTPRequestHandler):
    def send(self,n,b,t="application/json; charset=utf-8"):
        if isinstance(b,dict):b=json.dumps(b,ensure_ascii=False)
        b=b.encode();self.send_response(n);self.send_header("Content-Type",t);self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
    def do_GET(self):
        if self.path in ("/","/index.html"):self.send(200,HTML,"text/html; charset=utf-8")
        elif self.path=="/manifest.webmanifest":self.send(200,PWA_MANIFEST,"application/manifest+json; charset=utf-8")
        elif self.path=="/icon.svg":self.send(200,PWA_ICON,"image/svg+xml; charset=utf-8")
        elif self.path=="/sw.js":
            self.send_response(200);b=PWA_SW.encode();self.send_header("Content-Type","application/javascript; charset=utf-8");self.send_header("Cache-Control","no-cache");self.send_header("Service-Worker-Allowed","/");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
        elif self.path=="/health":self.send(200,{"ok":True,"provider":"cloudflare","model":MODEL,"cloudflare_configured":bool(CF_ACCOUNT_ID and CF_API_TOKEN),"revision":os.environ.get("RENDER_GIT_COMMIT","")})
        else:self.send(404,{"error":"Tidak dijumpai"})
    def do_POST(self):
        if self.path!="/api/analyze":return self.send(404,{"error":"Tidak dijumpai"})
        try:
            n=int(self.headers.get("Content-Length","0"))
            if n>12000000:raise ValueError("Gambar terlalu besar.")
            d=json.loads(self.rfile.read(n));self.send(200,analyze(d.get("image","")))
        except Exception as e:self.send(400,{"error":str(e)})
    def log_message(self,*a):pass
print(f"[SeniScan] Starting with Cloudflare Workers AI: {MODEL}", flush=True)
ThreadingHTTPServer(("0.0.0.0",PORT),H).serve_forever()
