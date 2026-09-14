import os, json, re, urllib.request, urllib.error
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

PORT=int(os.environ.get("PORT","8000"))
MODEL="@cf/moondream/moondream3.1-9B-A2B"
CF_ACCOUNT_ID=os.environ.get("CLOUDFLARE_ACCOUNT_ID","")
CF_API_TOKEN=os.environ.get("CLOUDFLARE_API_TOKEN","")

HTML="""<!doctype html><html lang="ms"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SeniScan AI</title><style>
*{box-sizing:border-box}body{margin:0;font-family:Inter,ui-sans-serif,system-ui,-apple-system,sans-serif;background:linear-gradient(180deg,#f3f0ff 0,#f8f9ff 35%,#f5f7fb 100%);color:#202442}.app{max-width:560px;margin:auto;min-height:100vh}.hero{position:relative;overflow:hidden;padding:0;background:#1f1b5b;color:#fff;text-align:center;border-radius:0 0 34px 34px;box-shadow:0 14px 35px #5b42bb35}.hero img{display:block;width:100%;height:auto;aspect-ratio:3/2;object-fit:cover;object-position:center}.main{padding:0 15px 24px;margin-top:-22px;position:relative}.card{background:#fff;border:1px solid #e7e6f3;border-radius:24px;padding:18px;margin-bottom:14px;box-shadow:0 9px 28px #3f467010}.scan{border:0}.eyebrow{font-size:11px;font-weight:900;letter-spacing:1.2px;color:#6b4ad8;text-transform:uppercase}.card h2{margin:5px 0 8px;font-size:20px}.card h3{color:#30355c}.btn{width:100%;border:0;border-radius:15px;padding:14px;font-weight:850;margin-top:9px;font-size:14px;cursor:pointer}.primary{background:linear-gradient(90deg,#6639dc,#2589ee);color:#fff;box-shadow:0 8px 18px #594bd52b}.secondary{background:#f0edff;color:#5543c8;border:1px solid #e3dcff}#preview{width:100%;max-height:420px;object-fit:cover;border-radius:19px;display:none;margin-top:14px;border:3px solid #f0edff}.result{display:none}.sectionHead{display:flex;align-items:center;gap:10px;margin-bottom:10px}.ico{width:38px;height:38px;border-radius:12px;display:grid;place-items:center;background:#f0edff;font-size:20px}.item{background:linear-gradient(180deg,#fafaff,#f7f8ff);border:1px solid #e5e6f4;border-radius:17px;padding:14px;margin-top:10px}.item h3{margin:0 0 7px;font-size:16px}.item p{margin:6px 0;color:#626a85;font-size:13px;line-height:1.55}.tag{display:inline-block;font-size:10px;background:#e9f8ef;color:#197044;border-radius:99px;padding:5px 8px;font-weight:900}.mut{color:#707892;font-size:13px;line-height:1.6}.status{display:none;padding:12px;background:#eef3ff;border:1px solid #dde7ff;border-radius:13px;margin-top:10px;color:#4f5dbc;font-size:13px;font-weight:800}.tipcard{background:linear-gradient(135deg,#fff9e9,#fffdf7);border-color:#f5e8b8}.refcard{background:#fbfbfe}.foot{text-align:center;padding:18px 20px 30px;color:#8b91a5;font-size:11px}.restart{background:#222846;color:#fff}.divider{height:1px;background:#ececf4;margin:16px 0}</style></head>
<body><div class="app"><div class="hero"><img src="data:image/webp;base64,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" alt="SeniScan AI — Imbas, Kenal, Faham, Ingat"></div><main class="main">
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
