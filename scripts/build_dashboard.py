"""Generate a self-contained mobile dashboard. Never modifies management sources."""
import json, re, subprocess
from collections import Counter
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import check_project_management as pm
ROOT=Path(__file__).resolve().parents[1]

def generate(root=ROOT):
    now=datetime.now(ZoneInfo("Asia/Taipei"))
    revision=subprocess.check_output(["git","rev-parse","HEAD"],cwd=root,text=True).strip()
    cards=pm.read_json(root,"cards.json")
    live,errors=pm.machine_snapshot(root,now.date().isoformat())
    model=pm.load_model(root)
    saved={r["page_id"]:r for r in model["inventory"]}
    active=[r for r in live if r["visibility"]=="current"]
    fields=["text_status","reference_status","date_status","footer_status","jsonld_status"]
    changes=[]
    for r in live:
        old=saved.get(r["page_id"],{})
        diff=[k for k in pm.MACHINE_FIELDS if k!="checked_at" and r.get(k)!=old.get(k)]
        if diff: changes.append({"page":r["page_id"],"fields":diff})
    issues=[]
    for r in active:
        missing=[k for k in fields if r[k] not in ("machine_pass","not_applicable")]
        if missing:issues.append({"title":r["title"],"path":r["page_path"],"series":r["primary_series_id"],"issues":missing})
    groups=[]
    for sid,c in cards.items():
        groups.append({"id":sid,"title":c["title"],"count":len(set(c.get("steps",[]))),"hidden":c.get("hidden",False),"areas":c.get("topics",[]),"departments":c.get("departments",[])})
    areas=Counter(a for c in groups if not c["hidden"] for a in c["areas"])
    topics=[{"title":n["title"],"path":n["page_path"]} for n in model["topics"]["nodes"] if n.get("kind")=="topic" and n.get("page_path") and (root/n["page_path"]).is_file()]
    calc=(root/"calc.html").read_text(encoding="utf-8-sig")
    tools=[]
    for href,label in re.findall(r'<a[^>]*class="tool-card"[^>]*href="([^"]+)"[^>]*aria-label="([^"]+)"',calc):
        path=href.removeprefix("./")
        if not path.startswith("http") and (root/path).is_file():tools.append({"title":label.removeprefix("開啟"),"path":path})
    data={"generatedAt":now.isoformat(timespec="seconds"),"baseline":revision,"scope":"網站來源快照；版本 "+revision[:8], "counts":{"cards":len(active),"series":sum(not c["hidden"] for c in groups),"allSeries":len(groups),"hidden":sum(r["visibility"]=="hidden" for r in live),"retired":sum(r["visibility"]=="retired" for r in live),"areas":len(areas),"topics":len(topics),"tools":len(tools)},"areas":dict(areas),"series":groups,"issues":issues,"fields":fields,"statusCounts":{k:dict(Counter(r[k] for r in active)) for k in fields},"sync":{"pages":len(changes),"fields":sum(len(c["fields"]) for c in changes),"differences":changes,"sourceErrors":errors},"topics":topics,"tools":tools}
    if errors: raise ValueError("Dashboard source errors: "+str(errors))
    template=(root/"templates/dashboard.html").read_text(encoding="utf-8")
    payload=json.dumps(data,ensure_ascii=False).replace("<","\\u003c")
    out=root/"dashboard";out.mkdir(exist_ok=True)
    (out/"index.html").write_text(template.replace("__DATA__",payload),encoding="utf-8")
    (out/"status.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"counts":data["counts"],"syncPages":len(changes),"sourceErrors":errors},ensure_ascii=False))
    return data
if __name__=="__main__":generate()
