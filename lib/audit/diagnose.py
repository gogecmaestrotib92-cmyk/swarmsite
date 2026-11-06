"""AUDIT · diagnose.py — turns an inventory.json into findings + a transformation plan.
Rules are the ones measured across 16 Awwwards SOTD winners (see dna/DNA-REPORT-round2-CONCLUSIONS.md).
Usage: python3 diagnose.py inventory.json > audit.json
"""
import json, re, sys

BANNED_WORDS = ["unlock", "seamless", "elevate", "revolutioni", "supercharge", "next-level", "cutting-edge", "game-changer", "effortless", "empower", "leverage", "synergy", "world-class", "best-in-class", "innovative solution"]
GENERIC_CTAS = {"get started", "learn more", "sign up", "submit", "click here", "read more", "contact us", "start now"}
DEFAULT_FONTS = {"inter", "arial", "helvetica", "roboto", "open sans", "system-ui", "-apple-system", "segoe ui", "lato", "montserrat", "poppins"}

INDUSTRY_HINTS = {
    "data_product": ["analysis", "model", "prediction", "odds", "record", "dashboard", "api", "data", "track record", "probability"],
    "saas": ["pricing", "free trial", "sign up", "plan", "features", "integrat", "workspace"],
    "restaurant": ["menu", "reservation", "book a table", "chef", "dinner", "lunch"],
    "agency": ["portfolio", "our work", "case stud", "clients", "studio"],
    "ecommerce": ["add to cart", "shop", "checkout", "collection", "shipping"],
    "services": ["consult", "lawyer", "attorney", "clinic", "appointment", "our services"],
    "nonprofit": ["donate", "volunteer", "mission", "community"],
}

# Concept fit per industry (from the DNA table). Ordered best→ok.
CONCEPTS_BY_INDUSTRY = {
    "data_product": ["C1 blueprint", "C7 dark-infra", "C2 swiss-grid"],
    "saas": ["C5 calm-saas", "C1 blueprint", "C7 dark-infra"],
    "restaurant": ["C8 themed-world", "C3 flat-colour", "C6 black-luxury"],
    "agency": ["C2 swiss-grid", "C6 black-luxury", "C4 pastel-editorial"],
    "ecommerce": ["C3 flat-colour", "C6 black-luxury", "C4 pastel-editorial"],
    "services": ["C2 swiss-grid", "C4 pastel-editorial", "C1 blueprint"],
    "nonprofit": ["C3 flat-colour", "C4 pastel-editorial", "C2 swiss-grid"],
    "unknown": ["C5 calm-saas", "C2 swiss-grid", "C1 blueprint"],
}


def _norm(inv):
    inv.setdefault("copy", {}); c = inv["copy"]; c.setdefault("text", ""); c.setdefault("totalWords", 0); c.setdefault("h1Words", 0); c.setdefault("h1", None); c.setdefault("buttons", []); c.setdefault("headings", [])
    inv.setdefault("typography", {}); t = inv["typography"]; t.setdefault("fonts", []); t.setdefault("h1", None); t.setdefault("samples", [])
    if t["h1"] and "size" not in t["h1"]: t["h1"] = None
    inv.setdefault("colors", {}); col = inv["colors"]
    for k in ("bg", "text", "buttons"):
        col.setdefault(k, []); col[k] = [({"c": x, "n": 1} if isinstance(x, str) else x) for x in col[k]]
    inv.setdefault("brand", {}); b = inv["brand"]; b.setdefault("nav", []); b.setdefault("navCount", len(b["nav"])); b.setdefault("footerLinks", 0); b.setdefault("logo", None); b.setdefault("hasFooter", True); b.setdefault("footerWords", 0)
    inv.setdefault("media", {}); m = inv["media"]; m.setdefault("bigImgs", []); m.setdefault("imgCount", 0); m.setdefault("video", len(m.get("videos", [])) if isinstance(m.get("videos"), list) else 0)
    inv.setdefault("url", ""); inv.setdefault("sections", []); inv.setdefault("sectionCount", len(inv["sections"]))
    for s in inv["sections"]:
        for k, v in (("heading", None), ("words", 0), ("numbers", []), ("ctas", []), ("images", 0), ("bg", ""), ("i", 0)): s.setdefault(k, v)
    inv.setdefault("tech", {"libs": [], "anim": {}}); inv["tech"].setdefault("anim", {}); inv["tech"].setdefault("libs", [])
    return inv

def classify(inv):
    inv = _norm(inv)
    text = (inv["copy"]["text"] + " " + " ".join(inv["brand"]["nav"])).lower()
    scores = {k: sum(text.count(w) for w in ws) for k, ws in INDUSTRY_HINTS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "unknown", scores


def diagnose(inv):
    inv = _norm(inv)
    f = []  # findings: (severity, code, message, evidence)
    plan = []  # transformation operations
    c = inv["copy"]; t = inv["typography"]; col = inv["colors"]; b = inv["brand"]; m = inv["media"]; secs = inv["sections"]

    # --- D3 words / beats ---
    if c["totalWords"] > 800:
        f.append(("high", "too_many_words", f'{c["totalWords"]} words on the page; winners run 80–850.', None))
        plan.append({"op": "cut", "target": "copy", "to": "≤ 700 words", "how": "keep every number and claim; cut explanations, repeated CTAs, FAQ to 4 items"})
    if inv["sectionCount"] > 8:
        f.append(("high", "too_many_sections", f'{inv["sectionCount"]} sections; winners use 5–7 beats.', [s["heading"] for s in secs]))
        plan.append({"op": "merge", "target": "sections", "to": "6–7 beats", "how": "merge duplicate stats/record sections; fold methodology into record; one pricing beat"})
    dup = {}
    for s in secs:
        if s["heading"]:
            k = re.sub(r"\W+", " ", s["heading"].lower())[:40]; dup.setdefault(k, []).append(s["i"])
    for k, ids in dup.items():
        if len(ids) > 1: f.append(("med", "duplicate_section", f'Section "{k}" appears {len(ids)}×', ids))
    if c["h1Words"] > 8:
        f.append(("med", "long_h1", f'H1 has {c["h1Words"]} words; winners ≤ 8 (often 2–4).', c["h1"]))
        plan.append({"op": "rewrite", "target": "h1", "to": "≤ 6 words, concrete", "how": "lead with the artefact or the promise; move explanation to sub"})
    long_heads = [h for h in c["headings"] if (h.get("words") or len(str(h.get("text","")).split())) > 8]
    if long_heads: f.append(("low", "long_headings", f'{len(long_heads)} headings over 8 words', [h["text"] for h in long_heads[:5]]))

    # --- copy hygiene ---
    low = c["text"].lower()
    hits = [w for w in BANNED_WORDS if w in low]
    if hits: f.append(("med", "banned_words", "Marketing filler found", hits)); plan.append({"op": "rewrite", "target": "copy", "to": "concrete nouns/verbs", "how": f"replace: {', '.join(hits)}"})
    gen = [x for x in c["buttons"] if x.lower().strip(" →") in GENERIC_CTAS]
    if gen: f.append(("low", "generic_ctas", "Generic CTA labels", gen)); plan.append({"op": "rewrite", "target": "ctas", "to": "verb + object ('Check my next bet')", "how": "one primary CTA repeated, rest as text links"})

    # --- D2 typography ---
    fonts = [x.lower() for x in t["fonts"]]
    if any(x in DEFAULT_FONTS for x in fonts): f.append(("high", "default_font", "Default/system font detected — winners never use Inter/Arial/Roboto", t["fonts"])); plan.append({"op": "replace", "target": "font", "to": "display + body pair from concept", "how": "keep brand font only if it has character (condensed, serif, mono)"})
    if len(set(fonts)) > 3: f.append(("med", "too_many_fonts", f'{len(set(fonts))} families', t["fonts"]))
    h1 = t.get("h1")
    if h1:
        if h1["size"] < 56: f.append(("high", "small_h1", f'H1 is {h1["size"]}px; winners 56–140px desktop', h1))
        if float(h1["lh"]) > 1.15: f.append(("med", "loose_h1", f'H1 line-height {h1["lh"]}; winners 0.8–1.05', h1))
        body = [s for s in t["samples"] if s["tag"] == "P"]
        if body and h1["size"] / body[0]["size"] < 3.5: f.append(("med", "low_type_contrast", f'display:body ratio {h1["size"]/body[0]["size"]:.1f}×; winners ≥ 4×', None))
    mono_labels = [s for s in t["samples"] if s["size"] <= 13 and s["tt"] == "uppercase"]
    if not mono_labels: f.append(("low", "no_label_system", "No small uppercase label layer (winners use 10–13px uppercase/mono labels for meta)", None)); plan.append({"op": "add", "target": "labels", "to": "mono 11–12px uppercase layer", "how": "section numbers, eyebrows, table headers, captions"})

    # --- colour ---
    btn = [x for x in col["buttons"] if not re.search(r" a0?\.\d|#ffffff|#000000", x["c"])]
    if len(btn) > 2: f.append(("med", "many_accents", f'{len(btn)} button colours; winners use 1 accent', btn))
    if len(col["bg"]) > 5: f.append(("low", "many_backgrounds", f'{len(col["bg"])} large background colours', col["bg"][:6]))

    # --- D4 hero artefact ---
    hero = secs[0] if secs else None
    if hero and hero["images"] == 0 and hero["svg"] < 2: f.append(("high", "no_hero_artefact", "Hero has no product artefact (screenshot/data/object); winners put the real thing in the hero", None)); plan.append({"op": "add", "target": "hero", "to": "real artefact", "how": "ledger/data card, product UI, or product photo — rendered as a design object, not a device mockup"})
    if m["imgCount"] and m["bigImgs"] == []: f.append(("med", "small_images_only", "No image ≥ 400px wide — nothing carries visual weight", None))
    if m["imgCount"] == 0 and m["video"] == 0: f.append(("high", "no_imagery", "No images or video at all", None)); plan.append({"op": "ask", "target": "assets", "to": "3 photos + logo + 3 numbers", "how": "onboarding must collect assets; else use 2-colour generated illustration + grain"})

    # --- nav / footer ---
    if b["navCount"] > 6: f.append(("med", "nav_overload", f'{b["navCount"]} nav links; winners ≤ 5 + 1 CTA', b["nav"])); plan.append({"op": "cut", "target": "nav", "to": "≤ 4 links + 1 CTA", "how": "rest into a Menu"})
    if b["hasFooter"] and b["footerLinks"] > 12: f.append(("low", "footer_link_dump", f'{b["footerLinks"]} footer links; winners make the footer a brand moment', None)); plan.append({"op": "rebuild", "target": "footer", "to": "giant wordmark + 4-6 links + forward pointer", "how": "legal in one line"})

    # --- motion ---
    a = inv["tech"]["anim"]
    if a["transitions"] < 30 and a["animations"] < 5: f.append(("med", "no_motion", "Almost no motion; winners choreograph 3–6 scroll moves", a)); plan.append({"op": "add", "target": "motion", "to": "3–5 moves from vocabulary", "how": "masked reveal on headlines, number scramble on stats, text scrub on manifesto, one pinned section"})
    if a["transitions"] > 400: f.append(("low", "motion_noise", "Very many transitions — check it is choreography, not noise", a))

    # --- content conflicts ---
    prices = re.findall(r"\$(\d+(?:\.\d+)?)\s*/\s*month", c["text"], re.I)
    if len(set(prices)) > 2: f.append(("high", "price_conflict", "Different monthly prices stated on the same page — must be resolved before redesign", sorted(set(prices), key=float))); plan.append({"op": "ask", "target": "pricing", "to": "one source of truth", "how": f"page states $/month: {sorted(set(prices), key=float)}"})

    # --- assets to keep (never lose) ---
    keep = {"numbers": sorted({n for s in secs for n in s["numbers"]})[:40], "h1": c["h1"], "logo": b["logo"] or ("svg" if b.get("logoSvg") else None), "brandButtonColour": btn[0]["c"] if btn else None, "fonts": t["fonts"], "nav": b["nav"], "bigImages": [x.get("src") for x in m["bigImgs"][:8]]}

    industry, scores = classify(inv)
    concepts = CONCEPTS_BY_INDUSTRY.get(industry, CONCEPTS_BY_INDUSTRY["unknown"])
    sev = {"high": 3, "med": 2, "low": 1}
    score = max(0, 100 - sum({3: 12, 2: 6, 1: 3}[sev[x[0]]] for x in f))
    return {
        "url": inv["url"], "industry": industry, "industryScores": scores, "designScore": score,
        "findings": [{"severity": s, "code": c_, "message": m_, "evidence": e} for s, c_, m_, e in sorted(f, key=lambda x: -sev[x[0]])],
        "keep": keep, "conceptCandidates": concepts, "plan": plan,
        "beats_proposal": propose_beats(inv, industry),
    }


def propose_beats(inv, industry):
    """Collapse the existing sections into ≤7 beats, each with one register."""
    secs = inv["sections"]
    beats = []
    registers = ["hero/artefact", "proof/numbers", "how it works", "product/features", "trust/record", "pricing/offer", "ending"]
    # naive: keep first, the biggest-number section, the section with most CTAs, pricing-like, faq-like, last
    def pick(pred, label):
        for s in secs:
            if s["i"] in used: continue
            if pred(s): used.add(s["i"]); beats.append({"beat": label, "from": s["i"], "heading": s["heading"], "words": s["words"]}); return
    used = set()
    pick(lambda s: True, "hero/artefact")
    # proof = the section with the most distinct numbers (not the hero)
    cand = sorted([s for s in secs if s["i"] not in used], key=lambda s: -len(s["numbers"]))
    if cand and len(cand[0]["numbers"]) >= 4: used.add(cand[0]["i"]); beats.append({"beat": "proof/numbers", "from": cand[0]["i"], "heading": cand[0]["heading"], "words": cand[0]["words"]})
    pick(lambda s: s["heading"] and re.search(r"how|way|work|what you get|everything", s["heading"], re.I), "how it works")
    pick(lambda s: s["heading"] and re.search(r"record|trust|method|public|audit", s["heading"], re.I), "trust/record")
    pick(lambda s: (s["heading"] and re.search(r"\bplans?\b|pricing|member|lifetime|subscri", s["heading"], re.I) and not re.search(r"purchase", s["heading"], re.I)) and sum("$" in n for n in s["numbers"]) >= 2, "pricing/offer")
    pick(lambda s: s["heading"] and re.search(r"question|faq|answer", s["heading"], re.I), "faq (optional, ≤4)")
    beats.append({"beat": "ending", "from": None, "heading": "giant wordmark + forward pointer", "words": 20})
    return beats


if __name__ == "__main__":
    inv = json.load(open(sys.argv[1]))
    print(json.dumps(diagnose(inv), indent=1, ensure_ascii=False))
