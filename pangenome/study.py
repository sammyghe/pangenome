"""The study: does the scaffolding actually do the work, and how small can the brain be?

Two parts, and only the first needs no API key.

PART 1 — MODEL-FREE ABLATION.
    The salience layer is fully deterministic: no model, no embeddings, no
    network. So its discriminative power can be measured directly against a
    hand-labelled fixture, and the result is *model-independent by construction*
    — identical for a 7B model and a frontier one, because neither is involved.
    That is the whole claim of the architecture stated as a measurement.

PART 2 — SMALL-MODEL ARMS.
    Three ways to get the same job done, measured on hits and on tokens:

      A  LITERAL     small model, whole page, literal task
      B  PROMPTED    small model, whole page, task + "flag anything relevant to
                     my business"                       <- the fair counter-argument
      C  ORGANISM    salience shortlist only, small model judges the shortlist

    Arm B exists specifically to attack this repository's own README, which
    claimed no amount of prompting produces the incidental observation. If B
    succeeds, that claim was wrong and gets corrected rather than defended.

    Arm D runs the same comparison over the REAL 314 loci the organism sensed
    this morning, because 30 items and 3,000 items are different questions and
    only one of them is the one that matters in production.

The model call lives HERE, in the researcher's harness, not in the organism.
`pangenome/safety.py` forbids POST and non-allowlisted hosts; the organism has
no route to an inference endpoint and gains none from this file. The measuring
instrument is not an organ.
"""

from __future__ import annotations

import json
import os
import time
import urllib.request

from .experiment import SHOP, PROFILES, MARKET_HISTORY, TASK_GOAL, _grow
from .salience import AttentionField, concepts_of, INVESTIGATE, INTERRUPT
from .store import Store

# ---------------------------------------------------------------------------
# Ground truth. Hand-labelled, stated in full so it can be argued with.
# ---------------------------------------------------------------------------
# CORE      the organism should flag these — they are the owner's own trade
# ADJACENT  defensible either way; scored neither as hit nor as false positive
# TARGET    the discriminating cases: in-trade AND priced far off-distribution.
#           These are the ones a literal agent misses and a novelty filter
#           throws away, because to this owner they are the least novel thing
#           on the page.
LABELS = {
    "OPTICIAN": {
        "core": {"sunglasses-aviator-uv400", "sunglasses-wayfarer-polarised",
                 "sunglasses-designer-clearance", "reading-glasses-plus2",
                 "lens-cleaning-cloth", "polarised-clip-on", "microfibre-pouch"},
        "adjacent": {"sunscreen-spf50", "beach-hat-straw"},
        "target": {"sunglasses-designer-clearance", "polarised-clip-on"},
    },
    "TAILOR": {
        "core": {"cotton-shirt-oxford", "linen-trousers", "silk-scarf-printed",
                 "denim-jacket-raw", "wool-blend-coat"},
        "adjacent": {"cotton-towel-set", "swim-shorts-quickdry", "leather-belt-brown"},
        "target": {"wool-blend-coat"},          # 120 against a 210 baseline
    },
    "GENERALIST": {"core": set(), "adjacent": set(), "target": set()},
}

PAGE = "\n".join(f"{item} | {text} | ${price}" for item, text, price in SHOP)
TASK = "Report the prices of every deodorant on this page."


# ---------------------------------------------------------------------------
# Part 1 — model-free
# ---------------------------------------------------------------------------
def ablation() -> dict:
    """Precision / recall / F1 of the deterministic filter. No model involved."""
    out = {}
    for owner, profile in PROFILES.items():
        store = Store(":memory:")
        field = AttentionField(store)
        _grow(store, field, profile, MARKET_HISTORY[owner])

        items = []
        for item, text, price in SHOP:
            cs = concepts_of(f"{item} {text}")
            items.append((item, f"{item} {text}", field.category_of(cs), price))
        scanned = field.scan(items, goal=TASK_GOAL, log=False)

        flagged = {a["subject"] for a in scanned
                   if a["verdict"] in (INVESTIGATE, INTERRUPT)
                   and "deodorant" not in a["subject"]}

        lab = LABELS[owner]
        judged = flagged - lab["adjacent"]
        hits = judged & lab["core"]
        false_pos = judged - lab["core"]
        missed = lab["core"] - flagged

        precision = len(hits) / len(judged) if judged else (1.0 if not lab["core"] else 0.0)
        recall = len(hits) / len(lab["core"]) if lab["core"] else 1.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0

        out[owner] = {
            "flagged": len(flagged),
            "hits": sorted(hits), "false_positives": sorted(false_pos),
            "missed": sorted(missed),
            "precision": round(precision, 3), "recall": round(recall, 3),
            "f1": round(f1, 3),
            "targets_found": sorted(lab["target"] & flagged),
            "targets_total": len(lab["target"]),
        }
        store.close()
    return out


def shortlist_for(owner: str, corpus: list[tuple] | None = None) -> list[str]:
    """What the organism would hand a model, instead of the whole page."""
    store = Store(":memory:")
    field = AttentionField(store)
    _grow(store, field, PROFILES[owner], MARKET_HISTORY[owner])
    rows = corpus or SHOP
    items = [(i, f"{i} {t}", field.category_of(concepts_of(f"{i} {t}")), p)
             for i, t, p in rows]
    scanned = field.scan(items, goal=TASK_GOAL, log=False)
    keep = [a["subject"] for a in scanned
            if a["verdict"] in (INVESTIGATE, INTERRUPT)]
    store.close()
    return keep


def compression() -> dict:
    """How much of the world the expensive model never has to look at.

    This is the number the whole architecture is for, and it is the one that
    decides whether a small model is viable: not "can it reason" but "how little
    does it have to read".
    """
    out = {}
    for owner in PROFILES:
        keep = set(shortlist_for(owner))
        full = PAGE
        short = "\n".join(f"{i} | {t} | ${p}" for i, t, p in SHOP
                          if i in keep or "deodorant" in t)
        out[owner] = {
            "full_chars": len(full), "shortlist_chars": len(short),
            "reduction": round(1 - len(short) / len(full), 3),
            "items_full": len(SHOP), "items_shortlist": len(short.splitlines()),
        }
    return out


# ---------------------------------------------------------------------------
# Part 2 — the small model
# ---------------------------------------------------------------------------
GEMINI = ("https://generativelanguage.googleapis.com/v1beta/models/"
          "{model}:generateContent")


class SmallModel:
    """Deliberately outside the organism. See the module docstring.

    One adapter, two model families. `gemini-*` is proprietary; `gemma-*` is
    open-weights and is served from the same endpoint on the same free key,
    which is why a second family costs nothing here. Two families matter
    because a result measured on one model is a fact about that model.
    """

    def __init__(self, model: str = "gemini-2.5-flash"):
        self.model = model
        self.key = os.environ.get("GEMINI_API_KEY")
        self.calls = 0
        self.tokens_in = 0
        self.tokens_out = 0

    @property
    def available(self) -> bool:
        return bool(self.key)

    def ask(self, prompt: str) -> str:
        body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode()
        req = urllib.request.Request(
            GEMINI.format(model=self.model) + f"?key={self.key}",
            data=body, method="POST",
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=90) as r:
            data = json.loads(r.read())
        self.calls += 1
        usage = data.get("usageMetadata", {})
        self.tokens_in += usage.get("promptTokenCount", 0)
        self.tokens_out += usage.get("candidatesTokenCount", 0)
        parts = data["candidates"][0]["content"].get("parts", [{}])
        return "".join(p.get("text", "") for p in parts)


ARMS = {
    "A_LITERAL": (
        "You are a shopping assistant browsing an online store.\n\n"
        "STORE PAGE:\n{page}\n\nTASK: {task}\n"
    ),
    "B_PROMPTED": (
        "You are a shopping assistant browsing an online store for {owner_desc}\n\n"
        "STORE PAGE:\n{page}\n\nTASK: {task}\n"
        "Also flag anything else on this page that is relevant to my business, "
        "especially unusual pricing.\n"
    ),
    "C_ORGANISM": (
        "You are a shopping assistant browsing an online store for {owner_desc}\n\n"
        "TASK: {task}\n\nANSWER:\n{answer}\n\n"
        "Your attention system also surfaced these items as potentially "
        "relevant, with your own price history for comparison:\n{shortlist}\n\n"
        "For each, say in one line whether it is worth acting on and why.\n"
    ),
}

OWNER_DESC = {
    "OPTICIAN": "the owner of a sunglasses shop.",
    "TAILOR": "the owner of a clothing and tailoring business.",
    "GENERALIST": "a general shopper with no particular business.",
}


def _squash(s: str) -> str:
    return "".join(c for c in s.lower() if c.isalnum())


def _mentions(text: str, item: str) -> bool:
    """Did the reply actually name this item?

    Exact and hyphen-relaxed matching (unchanged, so the earlier shop numbers
    still reproduce), plus a punctuation-insensitive pass for the wild domain,
    where a locus is `org/repo` and a model may write "Trail of Bits" for
    `trailofbits`. Segments shorter than 9 characters are not matched on their
    own — "skills" would hit every second line on that page.
    """
    if item.lower() in text.lower() or item.replace("-", " ").lower() in text.lower():
        return True
    flat = _squash(text)
    if _squash(item) in flat:
        return True
    return any(_squash(part) in flat for part in item.split("/")
               if len(_squash(part)) >= 9)


def model_arms(owner: str = "OPTICIAN", model: str = "gemini-2.5-flash",
               pause: float = 1.0) -> dict:
    m = SmallModel(model)
    if not m.available:
        return {"skipped": "GEMINI_API_KEY not set"}

    lab = LABELS[owner]
    keep = shortlist_for(owner)
    answer = "; ".join(f"{i} ${p}" for i, t, p in SHOP if "deodorant" in t)
    shortlist_txt = "\n".join(
        f"{i} | {t} | ${p}" for i, t, p in SHOP if i in keep)

    results = {}
    for arm, template in ARMS.items():
        before = (m.tokens_in, m.tokens_out)
        prompt = template.format(page=PAGE, task=TASK, answer=answer,
                                 shortlist=shortlist_txt,
                                 owner_desc=OWNER_DESC[owner])
        try:
            text = m.ask(prompt)
        except Exception as e:
            results[arm] = {"error": f"{type(e).__name__}: {e}"}
            continue
        results[arm] = {
            "targets_found": sorted(t for t in lab["target"] if _mentions(text, t)),
            "targets_total": len(lab["target"]),
            "core_mentioned": sum(1 for c in lab["core"] if _mentions(text, c)),
            "core_total": len(lab["core"]),
            "tokens_in": m.tokens_in - before[0],
            "tokens_out": m.tokens_out - before[1],
            "chars_of_reply": len(text),
            "reply_head": text.strip()[:400],
        }
        time.sleep(pause)        # be polite to a free tier

    results["_totals"] = {"model": model, "calls": m.calls,
                          "tokens_in": m.tokens_in, "tokens_out": m.tokens_out}
    return results


def repeat_arms(owner: str = "OPTICIAN", model: str = "gemini-2.5-flash",
                n: int = 3, pause: float = 6.0) -> dict:
    """Run the arms n times.

    One sample of a stochastic model is an anecdote. The variance turned out to
    be the finding here, so measuring it is not optional: an arm that gets the
    right answer half the time is a different product from one that always does,
    even when their means look similar.
    """
    import statistics
    acc: dict[str, list] = {a: [] for a in ARMS}
    failures = 0
    for _ in range(n):
        r = model_arms(owner=owner, model=model, pause=pause)
        if "skipped" in r:
            return r
        for a in ARMS:
            if a in r and "error" not in r[a]:
                acc[a].append((len(r[a]["targets_found"]), r[a]["core_mentioned"],
                               r[a]["tokens_in"], r[a]["tokens_out"]))
            else:
                failures += 1
        time.sleep(pause)

    out = {"_n_requested": n, "_failed_calls": failures, "_model": model}
    for a, v in acc.items():
        if not v:
            out[a] = {"samples": 0}
            continue
        tg = [x[0] for x in v]
        co = [x[1] for x in v]
        out[a] = {
            "samples": len(v),
            "targets": tg, "targets_mean": round(statistics.mean(tg), 2),
            "targets_total": len(LABELS[owner]["target"]),
            "stable": len(set(tg)) == 1,
            "core": co, "core_mean": round(statistics.mean(co), 2),
            "core_total": len(LABELS[owner]["core"]),
            "tokens_in": v[0][2],
            "tokens_out_mean": round(statistics.mean(x[3] for x in v)),
        }
    return out


# ---------------------------------------------------------------------------
# Domain 2 — the wild corpus (real loci, hand-labelled). See wildset.py.
# ---------------------------------------------------------------------------
WILD_ARMS = {
    "A_LITERAL": (
        "You are an assistant reading a directory of GitHub repositories.\n\n"
        "PAGE:\n{page}\n\nTASK: {task}\n"
    ),
    "B_PROMPTED": (
        "You are an assistant reading a directory of GitHub repositories for "
        "{owner_desc}\n\nPAGE:\n{page}\n\nTASK: {task}\n"
        "Also flag anything else on this page that is relevant to my work, "
        "especially things with unusually low adoption for what they do.\n"
    ),
    "C_ORGANISM": (
        "You are an assistant reading a directory of GitHub repositories for "
        "{owner_desc}\n\nTASK: {task}\n\nANSWER:\n{answer}\n\n"
        "Your attention system also surfaced these repositories as potentially "
        "relevant, with your own adoption history for comparison:\n{shortlist}\n\n"
        "For each, say in one line whether it is worth acting on and why.\n"
    ),
}

WILD_OWNER_DESC = ("someone building agent infrastructure whose problem is the "
                   "capability supply chain: what a third-party skill does, what "
                   "it can reach, and whether anyone checked.")


def _wild_field():
    from . import wildset
    store = Store(":memory:")
    field = AttentionField(store)
    _grow(store, field, wildset.PROFILE, wildset.HISTORY)
    return store, field


def wild_scan() -> list[dict]:
    """The deterministic filter over the frozen real corpus."""
    from . import wildset
    store, field = _wild_field()
    items = [(locus, f"{locus} {text}",
              field.category_of(concepts_of(f"{locus} {text}")), float(stars))
             for locus, text, stars in wildset.WILD]
    out = field.scan(items, goal=wildset.TASK_GOAL, log=False)
    store.close()
    return out


def wild_ablation() -> dict:
    """Precision / recall / F1 on real data. No model involved.

    Reported exactly as it comes out. The fixture in `experiment.py` is a clean
    room; this is the street, and the two numbers being different is the most
    useful thing this study can tell anyone.
    """
    from . import wildset
    scanned = wild_scan()
    lab = wildset.LABELS
    flagged = {a["subject"] for a in scanned
               if a["verdict"] in (INVESTIGATE, INTERRUPT)}
    hits = flagged & lab["core"]
    precision = len(hits) / len(flagged) if flagged else 0.0
    recall = len(hits) / len(lab["core"]) if lab["core"] else 1.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    # Why a miss was missed: surprise needs >= 5 prior values in the same
    # reference class, so a rare class scores zero surprise by construction.
    thin = sorted(a["signature"] for a in scanned
                  if a["subject"] in (lab["core"] - flagged))
    return {
        "page_items": len(wildset.WILD),
        "flagged": len(flagged),
        "hits": sorted(hits), "missed": sorted(lab["core"] - flagged),
        "precision": round(precision, 3), "recall": round(recall, 3),
        "f1": round(f1, 3),
        "targets_found": sorted(flagged & lab["target"]),
        "targets_total": len(lab["target"]),
        "missed_reference_classes": thin,
    }


def wild_domain() -> dict:
    """Everything the model arms need for domain 2."""
    from . import wildset
    scanned = wild_scan()
    keep = [a["subject"] for a in scanned
            if a["verdict"] in (INVESTIGATE, INTERRUPT)]
    by_locus = {l: (t, s) for l, t, s in wildset.WILD}
    shortlist = "\n".join(f"{l} | {by_locus[l][0]} | {by_locus[l][1]} stars"
                          for l in keep if l in by_locus)
    top3 = sorted(wildset.WILD, key=lambda r: -r[2])[:3]
    return {
        "name": "wild",
        "page": wildset.PAGE,
        "task": wildset.TASK,
        "owner_desc": WILD_OWNER_DESC,
        "labels": wildset.LABELS,
        "arms": WILD_ARMS,
        "shortlist": shortlist,
        "answer": "; ".join(f"{l} {s} stars" for l, _, s in top3),
        "shortlist_len": len(keep),
    }


def shop_domain(owner: str = "OPTICIAN") -> dict:
    """Domain 1, expressed the same way so both run through one harness."""
    keep = shortlist_for(owner)
    return {
        "name": "shop",
        "page": PAGE,
        "task": TASK,
        "owner_desc": OWNER_DESC[owner],
        "labels": LABELS[owner],
        "arms": ARMS,
        "shortlist": "\n".join(f"{i} | {t} | ${p}" for i, t, p in SHOP if i in keep),
        "answer": "; ".join(f"{i} ${p}" for i, t, p in SHOP if "deodorant" in t),
        "shortlist_len": len(keep),
    }


DOMAINS = {"shop": shop_domain, "wild": wild_domain}


def domain_arms(domain: dict, model: str, pause: float = 1.0) -> dict:
    """One pass of all three arms over one domain with one model."""
    m = SmallModel(model)
    if not m.available:
        return {"skipped": "GEMINI_API_KEY not set"}
    lab = domain["labels"]
    results = {}
    for arm, template in domain["arms"].items():
        before = (m.tokens_in, m.tokens_out)
        prompt = template.format(page=domain["page"], task=domain["task"],
                                 answer=domain["answer"],
                                 shortlist=domain["shortlist"],
                                 owner_desc=domain["owner_desc"])
        try:
            text = m.ask(prompt)
        except Exception as e:
            results[arm] = {"error": f"{type(e).__name__}: {e}"}
            time.sleep(pause)
            continue
        results[arm] = {
            "targets_found": sorted(t for t in lab["target"] if _mentions(text, t)),
            "targets_total": len(lab["target"]),
            "core_mentioned": sum(1 for c in lab["core"] if _mentions(text, c)),
            "core_total": len(lab["core"]),
            "tokens_in": m.tokens_in - before[0],
            "tokens_out": m.tokens_out - before[1],
        }
        time.sleep(pause)
    return results


def repeat_domain(domain_name: str = "shop", model: str = "gemini-2.5-flash",
                  n: int = 20, pause: float = 6.0, progress=None) -> dict:
    """n repeats of all three arms. n >= 20 is the point: the first version of
    this study ran n=4, which measures a mean it cannot defend and a variance
    it cannot see."""
    import statistics
    domain = DOMAINS[domain_name]()
    acc: dict[str, list] = {a: [] for a in domain["arms"]}
    errors: list[str] = []
    for i in range(n):
        r = domain_arms(domain, model=model, pause=pause)
        if "skipped" in r:
            return r
        for a in domain["arms"]:
            if a in r and "error" not in r[a]:
                acc[a].append((len(r[a]["targets_found"]), r[a]["core_mentioned"],
                               r[a]["tokens_in"], r[a]["tokens_out"]))
            else:
                errors.append(f"{a}:{r.get(a, {}).get('error', 'missing')}")
        if progress:
            progress(i + 1, n, {a: [x[0] for x in v] for a, v in acc.items()})

    out = {"_domain": domain_name, "_model": model, "_n_requested": n,
           "_failed_calls": len(errors), "_errors": errors[:8],
           "_shortlist_items": domain["shortlist_len"],
           "_page_chars": len(domain["page"])}
    for a, v in acc.items():
        if not v:
            out[a] = {"samples": 0}
            continue
        tg = [x[0] for x in v]
        co = [x[1] for x in v]
        ti = [x[2] for x in v]
        out[a] = {
            "samples": len(v),
            "targets": tg,
            "targets_mean": round(statistics.mean(tg), 2),
            "targets_sd": round(statistics.pstdev(tg), 3),
            "targets_range": [min(tg), max(tg)],
            "targets_total": len(domain["labels"]["target"]),
            "perfect_runs": sum(1 for t in tg if t == len(domain["labels"]["target"])),
            "stable": len(set(tg)) == 1,
            "core_mean": round(statistics.mean(co), 2),
            "core_total": len(domain["labels"]["core"]),
            "tokens_in_mean": round(statistics.mean(ti)),
            "tokens_out_mean": round(statistics.mean(x[3] for x in v)),
        }
    return out


def scale_arm() -> dict:
    """The question that actually decides it: 30 items versus the real corpus.

    Prompting works fine when the world is a page. The organism sensed 314 real
    loci this morning and will sense them again tomorrow, forever. Whether you
    can afford to put the world in the prompt every time is not a capability
    question, and it is the reason the filter exists.
    """
    store = Store()
    rows = store.q("SELECT locus, name, payload FROM observations"
                   " WHERE seen_at = (SELECT MAX(seen_at) FROM observations)"
                   " OR seen_at > (SELECT MAX(seen_at) - 600 FROM observations)")
    if not rows:
        store.close()
        return {"skipped": "no live observations yet — run `pangenome beat` first"}

    full_chars = 0
    for r in rows:
        meta = json.loads(r["payload"])
        full_chars += len(f"{r['locus']} {r['name']} {meta.get('description','')}")

    flagged = store.q(
        "SELECT COUNT(*) n FROM attention_log WHERE verdict IN"
        " ('investigate','interrupt') AND at > (SELECT MAX(at) - 600 FROM attention_log)")
    n_flag = flagged[0]["n"] if flagged else 0
    store.close()

    # ~4 chars per token is the standard rough conversion; stated, not hidden.
    tok_full = full_chars / 4
    tok_short = (full_chars / max(1, len(rows))) * n_flag / 4
    return {
        "real_loci_this_beat": len(rows),
        "flagged": n_flag,
        "chars_full_corpus": full_chars,
        "est_tokens_full": int(tok_full),
        "est_tokens_shortlist": int(tok_short),
        "reduction": round(1 - (tok_short / tok_full), 3) if tok_full else None,
        "note": "estimate at ~4 chars/token; the ratio is the point, not the absolute",
    }


# ---------------------------------------------------------------------------
def run(model: str = "gemini-2.5-flash", skip_model: bool = False) -> dict:
    print("\n" + "=" * 72)
    print("PART 1 — MODEL-FREE ABLATION  (deterministic; no model, no network)")
    print("=" * 72)
    ab = ablation()
    for owner, r in ab.items():
        print(f"\n  {owner}")
        print(f"    precision {r['precision']}  recall {r['recall']}  F1 {r['f1']}")
        print(f"    hits           {r['hits']}")
        print(f"    false positives{'':1}{r['false_positives']}")
        print(f"    missed         {r['missed']}")
        print(f"    off-price targets found: "
              f"{len(r['targets_found'])}/{r['targets_total']} {r['targets_found']}")

    print("\n" + "=" * 72)
    print("PART 1b — HOW MUCH THE EXPENSIVE MODEL NEVER READS")
    print("=" * 72)
    comp = compression()
    for owner, c in comp.items():
        print(f"  {owner:<12} {c['items_shortlist']:>2}/{c['items_full']} items, "
              f"{c['reduction']*100:.0f}% fewer characters")

    scale = scale_arm()
    print("\n  on the REAL corpus sensed this beat:")
    if "skipped" in scale:
        print(f"    {scale['skipped']}")
    else:
        print(f"    {scale['real_loci_this_beat']} live loci -> "
              f"{scale['flagged']} flagged  "
              f"({scale['est_tokens_full']:,} -> {scale['est_tokens_shortlist']:,} "
              f"est. tokens, {scale['reduction']*100:.0f}% reduction)")

    arms = {"skipped": "--skip-model"} if skip_model else model_arms(model=model)
    if "skipped" not in arms:
        print("\n" + "=" * 72)
        print(f"PART 2 — SMALL-MODEL ARMS  ({arms['_totals']['model']}, owner=OPTICIAN)")
        print("=" * 72)
        for arm in ("A_LITERAL", "B_PROMPTED", "C_ORGANISM"):
            r = arms.get(arm, {})
            if "error" in r:
                print(f"\n  {arm}: ERROR {r['error']}")
                continue
            print(f"\n  {arm}")
            print(f"    off-price targets surfaced: "
                  f"{len(r['targets_found'])}/{r['targets_total']} {r['targets_found']}")
            print(f"    in-trade items mentioned  : {r['core_mentioned']}/{r['core_total']}")
            print(f"    tokens in/out             : {r['tokens_in']:,} / {r['tokens_out']:,}")
        t = arms["_totals"]
        print(f"\n  total {t['calls']} calls, {t['tokens_in']:,} in / {t['tokens_out']:,} out")
    else:
        print(f"\n  PART 2 skipped ({arms['skipped']})")

    return {"ablation": ab, "compression": comp, "scale": scale, "arms": arms}


# ---------------------------------------------------------------------------
# The upgraded study: two domains, two model families, n >= 20 per arm.
# ---------------------------------------------------------------------------
def full(n: int = 20, domains: tuple = ("shop", "wild"),
         models: tuple = ("gemini-2.5-flash", "gemma-4-26b-a4b-it"),
         pause: float = 4.0, save: str | None = None) -> dict:
    """Every (domain x model) cell, n repeats of three arms each.

    This replaces the n=4 single-model pilot. The point of n >= 20 and of a
    second model family is that neither a mean nor a variance measured on four
    runs of one model is a claim about anything but those four runs. Results
    are written to `save` after every cell, so a run killed by a rate limit
    still leaves behind the cells it finished — and the report says which
    cells are missing rather than quietly averaging what survived.
    """
    out = {"_n": n, "_generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "ablation_shop": ablation(), "ablation_wild": wild_ablation(),
           "compression": compression(), "cells": {}}

    def flush():
        if save:
            with open(save, "w", encoding="utf-8") as fh:
                json.dump(out, fh, indent=1)

    flush()
    for d in domains:
        for model in models:
            key = f"{d}/{model}"
            print(f"\n=== {key}  (n={n}) ", flush=True)

            def prog(i, total, seen, _k=key):
                print(f"    {_k} {i}/{total}  "
                      + "  ".join(f"{a}:{v[-1] if v else '-'}" for a, v in seen.items()),
                      flush=True)

            out["cells"][key] = repeat_domain(d, model=model, n=n, pause=pause,
                                              progress=prog)
            flush()
    return out


def report(res: dict) -> None:
    """Print the upgraded study as a table. Ranges and stability, not just means."""
    print("\n" + "=" * 78)
    print("THE STUDY, UPGRADED — two domains, two model families, n per arm")
    print("=" * 78)
    aw = res["ablation_wild"]
    print(f"\nDeterministic filter on the REAL corpus ({aw['page_items']} live loci):")
    print(f"  flagged {aw['flagged']}  precision {aw['precision']}  "
          f"recall {aw['recall']}  F1 {aw['f1']}")
    print(f"  off-adoption targets found: "
          f"{len(aw['targets_found'])}/{aw['targets_total']} {aw['targets_found']}")
    print(f"  missed: {aw['missed']}")

    print(f"\n{'cell':<34}{'arm':<12}{'targets mean':>13}{'range':>9}"
          f"{'perfect':>9}{'tokens in':>11}")
    for cell, r in res["cells"].items():
        if r.get("skipped"):
            print(f"{cell:<34}SKIPPED {r['skipped']}")
            continue
        for arm in ("A_LITERAL", "B_PROMPTED", "C_ORGANISM"):
            a = r.get(arm, {})
            if not a.get("samples"):
                print(f"{cell:<34}{arm:<12}{'no samples':>13}")
                continue
            rng = f"{a['targets_range'][0]}-{a['targets_range'][1]}"
            print(f"{cell:<34}{arm:<12}"
                  f"{a['targets_mean']:>8}/{a['targets_total']:<4}{rng:>9}"
                  f"{a['perfect_runs']:>6}/{a['samples']:<3}{a['tokens_in_mean']:>11,}")
        if r["_failed_calls"]:
            print(f"{'':<34}({r['_failed_calls']} failed calls: {r['_errors'][:2]})")
