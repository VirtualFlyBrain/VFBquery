"""Compare the MCP `search_terms` query with the website's main-search query.

Both hit the same Solr `ontology` core with edismax; they differ in `q` construction
(phrase+wildcards vs per-token AND of wildcard groups), `fq` (hard-exclude Deprecated
or not) and `bq` boosts (the website floats Class/DataSet/pub). Read-only GETs.

Write-up of these results: docs/search-config-comparison.md

    python3 docs/compare_search_configs.py
"""
import requests, json
U="https://solr.virtualflybrain.org/solr/ontology/select"
COMMON=dict(**{"q.op":"OR"},defType="edismax",mm="45%",
  qf="label^110 synonym^100 label_autosuggest synonym_autosuggest shortform_autosuggest",
  pf="true", fl="short_form,label", rows="10", wt="json")
BQ_MCP=("short_form:VFBexp*^10.0 short_form:VFB*^100.0 short_form:FBbt*^100.0 "
        "short_form:FBbt_00003982^2 facets_annotation:Deprecated^0.001")
BQ_WEB=("short_form:VFBexp*^10.0 short_form:VFB*^50.0 facets_annotation:Class^200.0 "
        "short_form:FBbt*^150.0 short_form:FBbt_00003982^2 facets_annotation:Deprecated^0.001 "
        "facets_annotation:DataSet^500.0 facets_annotation:pub^100.0")
FQ_BASE="(short_form:VFB* OR short_form:FB* OR facets_annotation:DataSet OR facets_annotation:pub) AND NOT short_form:VFBc_*"

def web_q(s):
    s=s.replace("-"," ").replace("+"," ").replace("_"," ").strip()
    return " AND ".join(f"({t} OR {t}* OR *{t} OR *{t}*)" for t in s.split(" ") if t)

def run(label,q,bq,fq):
    p=dict(COMMON); p["q"]=q; p["bq"]=bq; p["fq"]=fq
    r=requests.get(U,params=p,timeout=40)
    try: r.raise_for_status()
    except Exception as e: print(label,"ERR",e,r.text[:200]); return
    d=r.json()["response"]
    print(f"\n== {label}  numFound={d['numFound']}")
    for doc in d["docs"][:6]:
        print("   ", doc.get("short_form"), "|", doc.get("label"))

for term in ["DA1 lPN","kenyon cell","MBON-a2"]:
    print("\n############", term)
    run("MCP search_terms", f"{term} OR {term}* OR *{term}*", BQ_MCP, [FQ_BASE])
    run("website main search", web_q(term), BQ_WEB, [FQ_BASE,"NOT facets_annotation:Deprecated"])

print("\n\n===== RECALL CHECK (numFound only) =====")
def nf(q,bq,fq):
    p=dict(COMMON); p["q"]=q; p["bq"]=bq; p["fq"]=fq; p["rows"]="1"
    r=requests.get(U,params=p,timeout=40); r.raise_for_status()
    d=r.json()["response"]
    top=d["docs"][0]["label"] if d["docs"] else "-"
    return d["numFound"], top
for term in ["DA1","lPN","antennal lobe DA1 projection","kenyoncell","fan-shaped body","MB247","VFB_jrchjtdb","1734350908"]:
    a=nf(f"{term} OR {term}* OR *{term}*",BQ_MCP,[FQ_BASE])
    b=nf(web_q(term),BQ_WEB,[FQ_BASE,"NOT facets_annotation:Deprecated"])
    print(f"{term:32s} MCP {a[0]:6d} top={a[1][:40]:42s} | WEB {b[0]:6d} top={b[1][:40]}")
