"""The salience experiment.

The claim under test is the whole reason the attention organ exists:

    Three organisms with identical perception and an identical task, differing
    only in what they already know, will notice different things.

If that does not reproduce, developmental attention is a story rather than a
mechanism, and the module should be deleted.

Setup. One shop page, thirty items. One instruction, the same for everyone:
*report the deodorant prices*. Three organisms:

    GENERALIST   no standing interests
    OPTICIAN     runs a sunglasses shop
    TAILOR       runs a clothing business

Nobody is told to look for sunglasses or fabric. The task is deodorant. What is
measured is what each organism flagged that nobody asked about — and, critically,
whether the *deodorant* answer is unaffected, because an attention system that
degrades the actual task is a worse system, not a better one.

The shop deliberately contains one item that is only interesting on the SURPRISE
channel: sunglasses at far below their normal price. Novelty cannot find it — to
the optician, sunglasses are the least novel thing on the page. That item is the
discriminating test between "notices unfamiliar things" and "notices things that
matter".
"""

from __future__ import annotations

from .salience import AttentionField, concepts_of, INVESTIGATE, INTERRUPT
from .scaffold import Scaffold
from .store import Store

# (name, category text, price)
SHOP = [
    ("dove-deodorant-50ml", "deodorant antiperspirant personal care roll-on", 4.0),
    ("nivea-deodorant-spray", "deodorant spray personal care fresh", 4.5),
    ("rexona-deodorant-stick", "deodorant stick personal care", 3.8),
    ("shampoo-argan-400ml", "shampoo hair care argan oil", 6.0),
    ("toothpaste-mint", "toothpaste oral care mint fluoride", 2.5),
    ("sunglasses-aviator-uv400", "sunglasses eyewear uv400 polarised aviator lens", 35.0),
    ("sunglasses-wayfarer-polarised", "sunglasses eyewear polarised lens frame", 41.0),
    ("sunglasses-designer-clearance", "sunglasses eyewear designer frame polarised lens uv400", 11.0),
    ("reading-glasses-plus2", "eyewear reading glasses lens frame optical", 12.0),
    ("lens-cleaning-cloth", "eyewear lens cleaning microfibre optical", 3.0),
    ("cotton-shirt-oxford", "shirt cotton oxford fabric tailored menswear", 28.0),
    ("linen-trousers", "trousers linen fabric tailored menswear summer", 34.0),
    ("silk-scarf-printed", "scarf silk fabric printed accessory womenswear", 22.0),
    ("denim-jacket-raw", "jacket denim fabric raw selvedge menswear", 65.0),
    ("wool-blend-coat", "coat wool fabric blend tailored outerwear", 120.0),
    ("running-shoes-mesh", "shoes running mesh footwear sport", 55.0),
    ("leather-belt-brown", "belt leather accessory menswear", 18.0),
    ("wristwatch-steel", "watch steel accessory quartz", 89.0),
    ("phone-charger-usbc", "charger usb-c electronics cable", 9.0),
    ("bluetooth-earbuds", "earbuds bluetooth electronics audio", 45.0),
    ("kitchen-knife-set", "knife kitchen homeware steel", 32.0),
    ("ceramic-mug-pair", "mug ceramic homeware kitchen", 11.0),
    ("cotton-towel-set", "towel cotton fabric homeware bathroom", 24.0),
    ("laundry-detergent-2l", "detergent laundry household cleaning", 7.5),
    ("dish-soap-lemon", "soap dish household cleaning lemon", 2.2),
    ("sunscreen-spf50", "sunscreen spf50 uv skin protection outdoor", 13.0),
    ("beach-hat-straw", "hat straw accessory outdoor summer", 16.0),
    ("swim-shorts-quickdry", "shorts swim fabric quickdry outdoor summer", 21.0),
    ("polarised-clip-on", "eyewear clip-on polarised lens uv400 sunglasses", 8.0),
    ("microfibre-pouch", "pouch microfibre eyewear accessory", 4.0),
]

PROFILES = {
    "GENERALIST": {},
    "OPTICIAN": {"sunglasses": 1.0, "eyewear": 0.9, "lens": 0.7,
                 "uv400": 0.6, "polarised": 0.6, "frame": 0.5, "optical": 0.5},
    "TAILOR": {"fabric": 1.0, "cotton": 0.8, "linen": 0.7, "tailored": 0.7,
               "menswear": 0.6, "silk": 0.6, "wool": 0.6, "shirt": 0.5},
}

TASK_GOAL = ["deodorant"]


# What each owner has seen *before today*, and at what price. Expectations come
# from the organism's own past, never from the page in front of it — otherwise
# nothing on that page can ever be surprising, because it defines its own norm.
MARKET_HISTORY = {
    "OPTICIAN": [
        ("sunglasses eyewear polarised lens uv400 frame", 32.0),
        ("sunglasses eyewear designer frame lens uv400", 46.0),
        ("sunglasses eyewear aviator lens polarised", 38.0),
        ("sunglasses eyewear designer polarised lens frame", 52.0),
        ("sunglasses eyewear frame lens uv400", 29.0),
        ("sunglasses eyewear polarised designer lens", 44.0),
    ],
    "TAILOR": [
        ("shirt cotton fabric tailored menswear oxford", 30.0),
        ("trousers linen fabric tailored menswear", 36.0),
        ("coat wool fabric tailored outerwear blend", 210.0),
        ("jacket denim fabric menswear raw", 70.0),
        ("scarf silk fabric accessory womenswear", 26.0),
        ("shirt cotton fabric tailored menswear", 33.0),
    ],
    "GENERALIST": [],
}


def _grow(store: Store, field: AttentionField, profile: dict, history: list) -> None:
    """Give the organism a past, not just a config.

    Priming alone would be a lookup table. The associative graph is what lets
    activation reach concepts nobody declared — an optician primed on
    'sunglasses' should also light up on 'polarised', because those two words
    co-occurred in everything it has ever seen.
    """
    for concept, weight in profile.items():
        field.prime(concept, weight, why="owner business")
    scaffold = Scaffold(store, field)
    for _ in range(4):
        for text, price in history:
            terms = sorted(set(text.split()))
            scaffold.remember(field.category_of(terms), terms, {"value": price})
    store.commit()


def run(quiet: bool = False) -> dict:
    results = {}
    for name, profile in PROFILES.items():
        store = Store(":memory:")
        field = AttentionField(store)
        _grow(store, field, profile, MARKET_HISTORY[name])

        items, task_answer = [], []
        for item, text, price in SHOP:
            terms = concepts_of(f"{item} {text}")
            items.append((item, f"{item} {text}", field.category_of(terms), price))
            if "deodorant" in text:
                task_answer.append((item, price))

        scanned = field.scan(items, goal=TASK_GOAL, log=False)
        flagged = sorted(
            [(a["subject"], a["score"], a["surprise"]) for a in scanned
             if a["verdict"] in (INVESTIGATE, INTERRUPT)
             and "deodorant" not in a["subject"]],
            key=lambda f: -f[1])

        results[name] = {
            "task_answer": task_answer,
            "noticed": flagged[:6],
            "noticed_count": len(flagged),
        }
        store.close()

    if not quiet:
        print("\nTask given to all three, identically: report the deodorant prices.\n")
        for name, r in results.items():
            print(f"  {name}")
            print(f"    task answer : {len(r['task_answer'])} deodorants "
                  f"{[f'{i}=${p}' for i, p in r['task_answer']]}")
            if r["noticed"]:
                for item, score, sur in r["noticed"]:
                    tag = "  <- surprise" if sur > 0.3 else ""
                    print(f"    noticed     : {item:<32} {score:.3f}{tag}")
            else:
                print("    noticed     : nothing above threshold")
            print()

        gen = {i for i, _, _ in results["GENERALIST"]["noticed"]}
        opt = {i for i, _, _ in results["OPTICIAN"]["noticed"]}
        tai = {i for i, _, _ in results["TAILOR"]["noticed"]}
        print(f"  overlap optician/tailor : {len(opt & tai)} items")
        print(f"  optician-only           : {sorted(opt - tai - gen)}")
        print(f"  tailor-only             : {sorted(tai - opt - gen)}")
        same = all(r["task_answer"] == results["GENERALIST"]["task_answer"]
                   for r in results.values())
        print(f"  task answer identical   : {same}")

    return results
