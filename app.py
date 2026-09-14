import os, json, re, urllib.request, urllib.error
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

PORT=int(os.environ.get("PORT","8000"))
MODEL="@cf/moondream/moondream3.1-9B-A2B"
CF_ACCOUNT_ID=os.environ.get("CLOUDFLARE_ACCOUNT_ID","")
CF_API_TOKEN=os.environ.get("CLOUDFLARE_API_TOKEN","")

HTML="""<!doctype html><html lang="ms"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SeniScan AI</title><style>
*{box-sizing:border-box}body{margin:0;font-family:Inter,ui-sans-serif,system-ui,-apple-system,sans-serif;background:linear-gradient(180deg,#f3f0ff 0,#f8f9ff 35%,#f5f7fb 100%);color:#202442}.app{max-width:560px;margin:auto;min-height:100vh}.hero{position:relative;overflow:hidden;padding:34px 20px 48px;background:linear-gradient(135deg,#4b20b9 0%,#7138e6 45%,#168de8 100%);color:#fff;text-align:center;border-radius:0 0 34px 34px;box-shadow:0 14px 35px #5b42bb35}.hero:before,.hero:after{content:"";position:absolute;border-radius:50%;background:#ffffff18}.hero:before{width:170px;height:170px;right:-70px;top:-75px}.hero:after{width:120px;height:120px;left:-50px;bottom:-65px}.logo{width:62px;height:62px;margin:0 auto 10px;display:grid;place-items:center;border-radius:20px;background:#ffffff20;border:1px solid #ffffff35;font-size:30px;backdrop-filter:blur(8px)}.hero h1{font-size:36px;margin:0;font-weight:900;letter-spacing:-1px}.hero p{margin:7px 0 0;letter-spacing:3px;font-size:10px;font-weight:800;opacity:.9}.main{padding:0 15px 24px;margin-top:-22px;position:relative}.card{background:#fff;border:1px solid #e7e6f3;border-radius:24px;padding:18px;margin-bottom:14px;box-shadow:0 9px 28px #3f467010}.scan{border:0}.eyebrow{font-size:11px;font-weight:900;letter-spacing:1.2px;color:#6b4ad8;text-transform:uppercase}.card h2{margin:5px 0 8px;font-size:20px}.card h3{color:#30355c}.btn{width:100%;border:0;border-radius:15px;padding:14px;font-weight:850;margin-top:9px;font-size:14px;cursor:pointer}.primary{background:linear-gradient(90deg,#6639dc,#2589ee);color:#fff;box-shadow:0 8px 18px #594bd52b}.secondary{background:#f0edff;color:#5543c8;border:1px solid #e3dcff}#preview{width:100%;max-height:420px;object-fit:cover;border-radius:19px;display:none;margin-top:14px;border:3px solid #f0edff}.result{display:none}.sectionHead{display:flex;align-items:center;gap:10px;margin-bottom:10px}.ico{width:38px;height:38px;border-radius:12px;display:grid;place-items:center;background:#f0edff;font-size:20px}.item{background:linear-gradient(180deg,#fafaff,#f7f8ff);border:1px solid #e5e6f4;border-radius:17px;padding:14px;margin-top:10px}.item h3{margin:0 0 7px;font-size:16px}.item p{margin:6px 0;color:#626a85;font-size:13px;line-height:1.55}.tag{display:inline-block;font-size:10px;background:#e9f8ef;color:#197044;border-radius:99px;padding:5px 8px;font-weight:900}.mut{color:#707892;font-size:13px;line-height:1.6}.status{display:none;padding:12px;background:#eef3ff;border:1px solid #dde7ff;border-radius:13px;margin-top:10px;color:#4f5dbc;font-size:13px;font-weight:800}.tipcard{background:linear-gradient(135deg,#fff9e9,#fffdf7);border-color:#f5e8b8}.refcard{background:#fbfbfe}.foot{text-align:center;padding:18px 20px 30px;color:#8b91a5;font-size:11px}.restart{background:#222846;color:#fff}.divider{height:1px;background:#ececf4;margin:16px 0}</style></head>
<body><div class="app"><div class="hero"><div class="logo">🎨</div><h1>SeniScan AI</h1><p>IMBAS • KENAL • FAHAM • INGAT</p></div><main class="main">
<div class="card scan"><div class="eyebrow">Pembelajaran Seni Visual Berbantu AI</div><h2>📷 Imbas Seni Sekeliling</h2><p class="mut">Ambil gambar objek di sekeliling. SeniScan membantu mengenal pasti unsur seni dan prinsip rekaan yang kelihatan.</p>
<input id="file" type="file" accept="image/*" capture="environment" hidden><button class="btn primary" onclick="file.setAttribute('capture','environment');file.click()">📷 Scan Sekarang</button><button class="btn secondary" onclick="file.removeAttribute('capture');file.click()">🖼️ Pilih dari Galeri</button><img id="preview"><button id="go" class="btn primary" style="display:none">✨ Analisis Sekarang</button><div id="status" class="status">🔎 SeniScan sedang melihat dan menganalisis gambar...</div></div>
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
</script></body></html>"""

PROMPT="""Anda ialah pemerhati visual untuk aplikasi Pendidikan Seni Visual Malaysia.
Tugas anda ialah melihat imej dan memulangkan JSON SAHAJA. Jangan tulis markdown.

PENTING: Periksa SETIAP kategori visual secara berasingan. Jangan kosongkan kategori hanya kerana objek bukan karya seni. Objek harian, tumbuhan, pakaian dan peralatan juga mempunyai unsur visual.

Jawab semua nilai JSON dalam Bahasa Melayu.

Struktur JSON WAJIB:
{
  "object_name":"",
  "object_description":"",
  "overall_confidence":"Jelas",
  "visual":{
    "lines":[{"type":"","location":""}],
    "shapes":[{"type":"","location":""}],
    "forms":[{"type":"","location":""}],
    "textures":[{"type":"","location":""}],
    "colors":[{"name":"","location":""}],
    "space":[{"observation":""}],
    "values":[{"observation":""}],
    "focal_points":[{"observation":""}],
    "contrasts":[{"observation":""}],
    "repetitions":[{"observation":""}],
    "balance":[{"observation":""}],
    "unity":[{"observation":""}],
    "variety":[{"observation":""}]
  }
}

Panduan:
- lines: garisan menegak, mendatar, melengkung, beralun, diagonal atau zigzag yang benar-benar kelihatan.
- shapes: rupa 2D geometri atau organik yang benar-benar kelihatan. Daun dan kelopak boleh menjadi rupa organik.
- forms: bentuk 3D seperti silinder, sfera, kubus, kon atau bentuk organik 3D.
- textures: sifat permukaan yang BOLEH DILIHAT seperti licin, kasar, berkilat, berbulu atau beralur.
- colors: senaraikan warna utama yang jelas kelihatan.
- space: hanya jika kelihatan pertindihan, hadapan-belakang, jarak, ruang positif/negatif atau kedalaman.
- values: hanya jika kelihatan terang-gelap, ton, cahaya atau bayang.
- focal_points: hanya SATU tumpuan utama jika benar-benar dominan.
- contrasts: nyatakan perbezaan visual yang jelas antara dua unsur.
- repetitions: hanya pengulangan visual yang nyata.
- balance, unity, variety: isi hanya jika ada bukti visual yang jelas.

Contoh bunga: ranting melengkung -> lines; daun/kelopak organik -> shapes; kelompok bunga 3D -> forms; permukaan daun/kelopak -> textures; jingga/hijau/putih -> colors; bunga bertindih -> space; cahaya/bayang pada kelopak -> values.
Contoh botol: kontur melengkung -> lines; grafik label -> shapes; badan silinder -> forms; permukaan licin -> textures; warna label -> colors.

Jangan gunakan fungsi, tujuan, jenama, kandungan atau pemasaran produk sebagai unsur seni. Jika bukti kategori memang tidak kelihatan, gunakan [].
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
"vertical":"menegak","horizontal":"mendatar","curved":"melengkung","wavy":"beralun","zigzag":"zigzag",
"smooth":"licin","slightly rough":"agak kasar","rough":"kasar","glossy":"berkilat","ribbed":"beralur",
"cylindrical":"silinder","cylinder":"silinder","circular":"bulatan","circle":"bulatan",
"rectangular":"segi empat tepat","rectangle":"segi empat tepat","geometric":"geometri","organic":"organik",
"blue":"biru","green":"hijau","white":"putih","black":"hitam","red":"merah","yellow":"kuning","orange":"jingga",
"purple":"ungu","grey":"kelabu","gray":"kelabu","pink":"merah jambu","brown":"coklat","high":"Jelas","medium":"Berkemungkinan","low":"Tidak cukup jelas"
}
def _bm(s):
    s=_text(s)
    # Istilah lokasi/objek lazim supaya bahagian bukti kekal dalam Bahasa Melayu.
    phrase_map={
      "floral arrangement":"gubahan bunga","flower arrangement":"gubahan bunga","asymmetrical":"tidak simetri","asymmetric":"tidak simetri","composition":"komposisi","foliage":"dedaunan","chrysanthemum":"bunga kekwa","calla lilies":"bunga kala","pandanus":"pandan","dynamic":"dinamik","featuring":"yang menampilkan","and":"dan","with":"dengan","create":"mewujudkan","includes":"merangkumi","left side":"bahagian kiri","right side":"bahagian kanan","top":"bahagian atas","bottom":"bahagian bawah","lid":"penutup","base":"bahagian dasar","handle":"pemegang","stem":"batang","stems":"batang","branch":"ranting","branches":"ranting","petal":"kelopak","petals":"kelopak","flower":"bunga","flowers":"bunga","arrangement":"gubahan","vibrant":"terang",
      "middle left":"bahagian tengah kiri","middle right":"bahagian tengah kanan","upper left":"bahagian atas kiri","upper right":"bahagian atas kanan","lower left":"bahagian bawah kiri","lower right":"bahagian bawah kanan","extending diagonally":"memanjang secara diagonal","subtle shadows":"bayang lembut","subtle highlights":"pantulan cahaya lembut","leaves":"daun","shapes":"rupa","shape":"rupa","forms":"bentuk","form":"bentuk","lines":"garisan","line":"garisan","against":"berkontra dengan","variety of":"kepelbagaian","main body":"badan utama","body":"badan objek","label background":"latar label","background":"latar belakang",
      "text color":"warna tulisan","text":"tulisan","logo leaf":"logo daun","leaf accents":"hiasan daun",
      "leaf graphics":"grafik daun","bottle surface":"permukaan botol","bottle":"botol","label":"label"
    }
    for en,ms in sorted(phrase_map.items(),key=lambda x:-len(x[0])):
        s=re.sub(r"\b"+re.escape(en)+r"\b",ms,s,flags=re.I)
    for en,ms in sorted(BM_MAP.items(),key=lambda x:-len(x[0])):
        s=re.sub(r"\b"+re.escape(en)+r"\b",ms,s,flags=re.I)
    return s

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
    for k in ("focal_points","contrasts","repetitions","balance","unity","variety"):
        vis[k]=[{"observation":_bm(x.get("observation"))} for x in _list(vis.get(k)) if isinstance(x,dict) and _text(x.get("observation"))]
    # Prinsip rekaan perlu lebih ketat: penegasan hanya satu fokus dominan, pengulangan mesti nyata,
    # dan kesatuan/kepelbagaian tidak dipaparkan daripada istilah umum semata-mata.
    if len(vis["focal_points"]) != 1:
        vis["focal_points"]=[]
    vis["repetitions"]=[x for x in vis["repetitions"] if re.search(r"ulang|berulang|pengulangan|repet",x["observation"],re.I)]
    vis["balance"]=[x for x in vis["balance"] if re.search(r"seimbang|imbang|simetri|stabil|kiri.*kanan|kanan.*kiri",x["observation"],re.I)]
    vis["unity"]=[x for x in vis["unity"] if re.search(r"kesatuan|bersatu|serasi|selaras|harmoni|cohes",x["observation"],re.I)]
    vis["variety"]=[x for x in vis["variety"] if re.search(r"pelbagai|kepelbagaian|variasi|berbeza|variety",x["observation"],re.I)]
    vis["colors"]=[{"name":_bm(x.get("name")),"location":_bm(x.get("location"))} for x in _list(vis.get("colors")) if isinstance(x,dict) and _text(x.get("name")) and _text(x.get("location"))]
    # Fallback bukti: jika model menghuraikan ciri dengan jelas tetapi terlupa mengisi kategori JSON,
    # pulihkan hanya kategori yang boleh disokong oleh penerangan visualnya.
    desc=_bm(obs.get("object_description"))
    dl=desc.lower()
    if not vis["colors"]:
        known=("merah","jingga","kuning","hijau","biru","ungu","putih","hitam","kelabu","coklat","merah jambu")
        cols=[x for x in known if re.search(r"\\b"+re.escape(x)+r"\\b",dl)]
        if cols: vis["colors"]=[{"name":x,"location":"objek yang kelihatan"} for x in cols]
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
    if not vis["textures"]:
        ts=[x for x in ("licin","kasar","berkilat","beralur","berbulu","berduri") if x in dl]
        if ts: vis["textures"]=[{"type":x,"location":"permukaan objek yang jelas kelihatan"} for x in ts]
    if not vis["space"] and re.search(r"bertindih|pertindihan|di hadapan|di belakang|kedalaman|gubahan|komposisi",dl):
        vis["space"]=[{"observation":"Susunan bahagian objek yang saling berada di hadapan dan belakang menghasilkan kesan ruang dan kedalaman."}]
    if not vis["values"] and re.search(r"terang.*gelap|gelap.*terang|cahaya|bayang|ton|berkilat",dl):
        vis["values"]=[{"observation":"Perbezaan cahaya dan bayang pada permukaan objek menghasilkan nilai terang dan gelap."}]
    if not vis["balance"] and re.search(r"tidak simetri|simetri|komposisi",dl):
        vis["balance"]=[{"observation":"Susunan komposisi menunjukkan imbangan visual melalui pengagihan unsur pada keseluruhan gubahan."}]
    if not vis["contrasts"]:
        found_cols=[x.get("name","") for x in vis["colors"] if isinstance(x,dict)]
        if len(set(found_cols)) >= 3:
            vis["contrasts"]=[{"observation":"Perbezaan warna yang ketara antara bahagian objek menghasilkan kontra visual."}]
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
        evidence_blob=" ".join([
            desc,
            _join_obs(vis.get("contrasts")),
            _join_obs(vis.get("variety")),
            _join_obs(vis.get("focal_points"))
        ]).lower()
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
            principles.append({"name":name,"confidence":"Jelas","explanation":explanation,"evidence":ev})

    add_principle("Penegasan",vis.get("focal_points"),"Penegasan berlaku apabila satu bahagian menjadi tumpuan utama.")
    add_principle("Kontra",vis.get("contrasts"),"Kontra terhasil melalui perbezaan yang ketara seperti warna, nilai, saiz atau rupa.")
    add_principle("Irama & Pergerakan",vis.get("repetitions"),"Pengulangan unsur visual boleh mewujudkan irama dan mengarahkan pergerakan mata.")
    add_principle("Imbangan",vis.get("balance"),"Imbangan mewujudkan kestabilan visual melalui susunan unsur.")
    add_principle("Kesatuan",vis.get("unity"),"Kesatuan berlaku apabila unsur visual kelihatan saling berkaitan sebagai satu keseluruhan.")
    add_principle("Kepelbagaian",vis.get("variety"),"Kepelbagaian wujud melalui variasi unsur seperti warna, rupa, bentuk atau jalinan.")

    # Harmoni: derive conservatively only when unity observation explicitly mentions serasi/harmoni.
    unity_ev=_join_obs(vis.get("unity"))
    if unity_ev and re.search(r"harmoni|serasi|selaras", unity_ev, re.I):
        principles.append({"name":"Harmoni","confidence":"Berkemungkinan","explanation":"Harmoni terhasil apabila unsur visual kelihatan serasi dan saling melengkapi.","evidence":unity_ev})

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
    bm_description=" ".join(desc_parts) or _bm(obs.get("object_description"))

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

def analyze(image):
    if not CF_ACCOUNT_ID or not CF_API_TOKEN:
        raise RuntimeError("Cloudflare belum dikonfigurasi. Semak CLOUDFLARE_ACCOUNT_ID dan CLOUDFLARE_API_TOKEN di Render.")
    payload={
        "task":"query",
        "image":image,
        "question":PROMPT,
        "reasoning":False,
        "temperature":0,
        "max_tokens":1200,
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

    return build_art_result(obs)

class H(BaseHTTPRequestHandler):
    def send(self,n,b,t="application/json; charset=utf-8"):
        if isinstance(b,dict):b=json.dumps(b,ensure_ascii=False)
        b=b.encode();self.send_response(n);self.send_header("Content-Type",t);self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
    def do_GET(self):
        if self.path in ("/","/index.html"):self.send(200,HTML,"text/html; charset=utf-8")
        elif self.path=="/health":self.send(200,{"ok":True,"provider":"cloudflare","model":MODEL,"cloudflare_configured":bool(CF_ACCOUNT_ID and CF_API_TOKEN)})
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
