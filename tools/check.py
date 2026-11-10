import re, os, sys, glob
docs="docs"
files=sorted(glob.glob(docs+"/*.html"))
errs=[]; warns=[]
internal=set()
for f in files:
    internal.add(os.path.basename(f))
def strip(h): return re.sub(r"<script.*?</script>","",h,flags=re.S)

for f in files:
    h=open(f).read()
    # 1. anchor balance (rough)
    for tag in ("table","thead","tbody","tr","td","th","div","nav","main","header","footer","details","summary","ul","ol","li","p","h1","h2","h3","h4","span","a","strong","em","code","blockquote","style"):
        o=len(re.findall(rf"<{tag}[\s>]",h)); c=len(re.findall(rf"</{tag}>",h))
        if tag in ("li","p","td","th","tr") and o!=c:
            errs.append(f"{f}: <{tag}> open {o} close {c}")
        elif o!=c and tag not in ("li","p","td","th","tr","br","img","input","meta","link"):
            warns.append(f"{f}: <{tag}> open {o} close {c}")
    # 2. internal hrefs exist
    for href in re.findall(r'href="([^"#:]+)(?:#[^"]*)?"',h):
        if href.startswith(("http","mailto","//")): continue
        if href.startswith("#"): continue
        tgt=os.path.normpath(os.path.join(docs,href))
        if not os.path.exists(tgt):
            errs.append(f"{f}: broken link -> {href}")
    # 3. suspicious artifacts
    for pat,msg in [(r"\bnan\b","NaN value"),(r"\bNone\b","None literal"),
                    (r"\$\-","negative dollar format"),(r"\{[a-z_]+\}","unformatted f-string"),
                    (r"None","None"),(r"&amp;amp;","double-escaped ampersand")]:
        for mm in re.finditer(pat,h):
            seg=h[max(0,mm.start()-60):mm.end()+60].replace("\n"," ")
            warns.append(f"{f}: [{msg}] ...{seg}...")
            break
    # 4. required structural elements
    for req in ("<title>","assets/style.css","</html>"):
        if req not in h: errs.append(f"{f}: missing {req}")

print(f"files: {len(files)}")
print(f"ERRORS: {len(errs)}")
for e in errs: print("  ✗",e)
print(f"WARNINGS: {len(warns)}")
seen=set()
for w in warns:
    k=w.split(":")[1][:40] if ":" in w else w
    if k in seen: continue
    seen.add(k); print("  !",w)
sys.exit(1 if errs else 0)
