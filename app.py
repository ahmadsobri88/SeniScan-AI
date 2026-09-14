import os, json, re, urllib.request, urllib.error
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

PORT=int(os.environ.get("PORT","8000"))
MODEL="@cf/moondream/moondream3.1-9B-A2B"
CF_ACCOUNT_ID=os.environ.get("CLOUDFLARE_ACCOUNT_ID","")
CF_API_TOKEN=os.environ.get("CLOUDFLARE_API_TOKEN","")

HTML="""<!doctype html><html lang="ms"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SeniScan AI</title><style>
*{box-sizing:border-box}body{margin:0;font-family:system-ui;background:#f4f6ff;color:#24294d}.app{max-width:520px;margin:auto;min-height:100vh;background:white}.hero{padding:24px 18px;background:linear-gradient(135deg,#6528d7,#168cf0);color:white;text-align:center}.hero h1{font-size:36px;margin:0}.hero p{letter-spacing:3px;font-size:11px}.main{padding:16px}.card{background:white;border:1px solid #e5e8f5;border-radius:20px;padding:16px;margin-bottom:14px;box-shadow:0 7px 20px #4250a010}.btn{width:100%;border:0;border-radius:16px;padding:14px;font-weight:800;margin-top:9px}.primary{background:linear-gradient(90deg,#6a42e8,#2488ef);color:white}.secondary{background:#eeeaff;color:#5547c8}#preview{width:100%;border-radius:18px;display:none;margin-top:12px}.result{display:none}.item{background:#f7f8ff;border:1px solid #e4e7f7;border-radius:15px;padding:12px;margin-top:9px}.item h3{margin:0 0 6px;font-size:15px}.item p{margin:5px 0;color:#646b86;font-size:13px;line-height:1.5}.tag{font-size:11px;background:#ebe8ff;color:#5748c9;border-radius:99px;padding:4px 7px;font-weight:800}.mut{color:#737b94;font-size:13px;line-height:1.5}.status{display:none;padding:10px;background:#eef2ff;border-radius:12px;margin-top:9px;color:#5059bd;font-size:13px;font-weight:700}.foot{text-align:center;padding:20px;color:#8b91a5;font-size:11px}</style></head>
<body><div class="app"><div class="hero"><h1>SeniScan AI</h1><p>IMBAS • KENAL • FAHAM • INGAT</p></div><main class="main">
<div class="card"><h2>📷 Imbas Seni Sekeliling</h2><p class="mut">Ambil gambar objek di sekeliling. AI akan membantu menerangkan unsur seni dan prinsip rekaan yang benar-benar kelihatan.</p>
<input id="file" type="file" accept="image/*" capture="environment" hidden><button class="btn primary" onclick="file.click()">📷 Scan Sekarang</button><button class="btn secondary" onclick="file.removeAttribute('capture');file.click()">🖼️ Pilih dari Galeri</button><img id="preview"><button id="go" class="btn primary" style="display:none">✦ Analisis Sekarang</button><div id="status" class="status">🔎 AI sedang menganalisis gambar...</div></div>
<div id="result" class="result"><div class="card"><h2>🤖 Apa yang AI nampak?</h2><h3 id="obj"></h3><p id="desc" class="mut"></p><span id="conf" class="tag"></span></div><div class="card"><h2>🎨 Unsur Seni</h2><div id="els"></div></div><div class="card"><h2>⚖️ Prinsip Rekaan</h2><div id="prs"></div></div><div class="card"><h2>🧠 Ingat Mudah</h2><p id="tip" class="mut"></p><h3>Rumusan</h3><p id="sum" class="mut"></p></div></div>
</main><div class="foot">SeniScan AI • Pembelajaran Seni Visual Berbantu AI</div></div>
<script>
let imageData="";const file=document.getElementById("file"),preview=document.getElementById("preview"),go=document.getElementById("go"),statusEl=document.getElementById("status"),resultEl=document.getElementById("result"),obj=document.getElementById("obj"),desc=document.getElementById("desc"),conf=document.getElementById("conf"),els=document.getElementById("els"),prs=document.getElementById("prs"),tip=document.getElementById("tip"),sum=document.getElementById("sum");
file.onchange=()=>{const f=file.files[0];if(!f)return;const r=new FileReader();r.onload=()=>{imageData=r.result;preview.src=imageData;preview.style.display="block";go.style.display="block"};r.readAsDataURL(f)};
const esc=s=>String(s||"").replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[m]));
go.onclick=async()=>{if(!imageData)return;statusEl.style.display="block";go.disabled=true;try{const r=await fetch("/api/analyze",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({image:imageData})});const d=await r.json();if(!r.ok)throw Error(d.error||"Analisis gagal");obj.textContent=d.object_name||"";desc.textContent=d.object_description||"";conf.textContent="Keyakinan: "+(d.overall_confidence||"");els.innerHTML=(d.elements||[]).map(x=>'<div class="item"><h3>'+esc(x.name)+'</h3><span class="tag">'+esc(x.confidence)+'</span><p>'+esc(x.explanation)+'</p>'+(x.types?.length?'<p><b>Jenis/Kategori:</b> '+esc(x.types.join(", "))+'</p>':"")+(x.examples?.length?'<p><b>Contoh:</b> '+esc(x.examples.join("; "))+'</p>':"")+(x.color_details?'<p><b>Analisis warna:</b> '+esc(x.color_details)+'</p>':"")+'<p><b>👀 Bukti:</b> '+esc(x.evidence)+'</p></div>').join("")||'<p class="mut">Tiada unsur yang cukup jelas.</p>';prs.innerHTML=(d.principles||[]).map(x=>'<div class="item"><h3>'+esc(x.name)+'</h3><span class="tag">'+esc(x.confidence)+'</span><p>'+esc(x.explanation)+'</p><p><b>👀 Bukti:</b> '+esc(x.evidence)+'</p></div>').join("")||'<p class="mut">Tiada prinsip yang cukup jelas.</p>';tip.textContent=d.memory_tip||"";sum.textContent=d.learning_summary||"";resultEl.style.display="block";resultEl.scrollIntoView({behavior:"smooth"})}catch(e){alert(e.message)}finally{statusEl.style.display="none";go.disabled=false}};
</script></body></html>"""

PROMPT="""Anda ialah enjin pembelajaran SeniScan AI. Analisis imej dalam Bahasa Melayu untuk membantu orang awam dan pelajar memahami seni visual.
Unsur dibenarkan: Garisan, Rupa, Bentuk, Jalinan, Warna, Ruang, Nilai.
Prinsip dibenarkan: Harmoni, Kontra, Penegasan, Kepelbagaian, Imbangan, Kesatuan, Irama & Pergerakan.
Hanya pilih yang mempunyai bukti visual. Jangan paksa semua kategori. Jangan beri markah.
Untuk Warna, nyatakan warna dominan, kategori primer/sekunder/tertier jika sesuai, panas/sejuk/neutral dan hubungan komplementari/analogus/monokromatik hanya jika disokong imej.
Untuk Jalinan nyatakan sifat permukaan; Garisan nyatakan jenis dan lokasi; Rupa geometri/organik; Bentuk kesan 3D; Ruang kedalaman/pertindihan/perspektif; Nilai terang-gelap/cahaya-bayang.
Setiap keputusan mesti menyebut bukti yang boleh dilihat.
Pulangkan JSON sahaja:
{"object_name":"","object_description":"","overall_confidence":"Jelas | Berkemungkinan | Tidak cukup jelas","elements":[{"name":"","confidence":"Jelas | Berkemungkinan","explanation":"","evidence":"","types":[],"examples":[],"color_details":""}],"principles":[{"name":"","confidence":"Jelas | Berkemungkinan","explanation":"","evidence":""}],"memory_tip":"","learning_summary":""}"""

def analyze(image):
    if not CF_ACCOUNT_ID or not CF_API_TOKEN:
        raise RuntimeError("Cloudflare belum dikonfigurasi. Semak CLOUDFLARE_ACCOUNT_ID dan CLOUDFLARE_API_TOKEN di Render.")
    payload={
        "task":"query",
        "image":image,
        "question":PROMPT,
        "reasoning":False,
        "temperature":0.1,
        "max_tokens":1000,
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
    print("[SeniScan] result type:", type(result).__name__, flush=True)
    # Cloudflare may wrap the model output as:
    # result -> {result: {answer: "...", usage: {...}}}
    # Unwrap nested result dictionaries before reading answer.
    while isinstance(result, dict) and "result" in result and not any(
        k in result for k in ("answer","response","caption","description","text")
    ):
        print("[SeniScan] result keys:", list(result.keys()), flush=True)
        result=result.get("result")
    if isinstance(result, dict):
        print("[SeniScan] final result keys:", list(result.keys()), flush=True)
        text=(result.get("answer") or result.get("response") or result.get("caption")
              or result.get("description") or result.get("text") or "")
    elif isinstance(result, str):
        text=result
    else:
        text=""
    if not text:
        print("[SeniScan] unreadable result:", json.dumps(result, ensure_ascii=False)[:800], flush=True)
        raise RuntimeError("Respons Cloudflare AI diterima tetapi formatnya belum dikenali.")
    text=re.sub(r"^\`\`\`(?:json)?|\`\`\`$","",str(text).strip()).strip()
    try:return json.loads(text)
    except:
        m=re.search(r"\{.*\}",text,re.S)
        if not m:raise RuntimeError("AI berjaya melihat imej tetapi respons belum dalam format SeniScan. Cuba sekali lagi.")
        return json.loads(m.group())

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
