"""pangenome CLI.

    python -m pangenome germinate --name culture-01 --steward "Samuel Ghedamu"
    python -m pangenome beat            # one heartbeat: sense, decide, integrate
    python -m pangenome watch           # the outbreak table, no side effects
    python -m pangenome genome          # what is in the accessory genome
    python -m pangenome immune          # the CRISPR array
    python -m pangenome simulate        # in-process population, no network
"""

from __future__ import annotations

import argparse
import json
import sys

from .chromosome import Chromosome
from .organism import Organism
from .store import Store
from . import epidemiology


def _table(rows: list[dict], cols: list[tuple[str, str]]) -> str:
    if not rows:
        return "  (nothing yet)"
    widths = {k: max(len(h), *(len(str(r.get(k, ""))) for r in rows)) for k, h in cols}
    out = ["  " + "  ".join(h.ljust(widths[k]) for k, h in cols),
           "  " + "  ".join("-" * widths[k] for k, _ in cols)]
    for r in rows:
        out.append("  " + "  ".join(str(r.get(k, "")).ljust(widths[k]) for k, _ in cols))
    return "\n".join(out)


def cmd_germinate(a) -> int:
    if a.fresh:
        # A template clone inherits the ancestor's acquired state. --fresh sheds
        # it in one step, so nobody has to hand-write DELETE statements to get a
        # an organism that is genuinely their own from beat one.
        Store().clear_all()
        print("cleared inherited state: all acquired tables emptied")
    c = Chromosome.germinate(a.name, a.steward, force=a.force or a.fresh)
    print(f"germinated: {c.name}")
    print(f"  root pubkey : {c.data['root_pubkey']}")
    print(f"  steward     : {c.data['steward']}")
    print("  secret key  : genome/root.key  (gitignored — this is the identity)")
    return 0


def cmd_beat(a) -> int:
    o = Organism()
    r = o.heartbeat()
    if a.json:
        print(json.dumps(r, indent=2, default=str))
        return 0
    print(f"\n{r['organism']} — heartbeat in {r['seconds']}s\n")
    for k, v in r["sense"].items():
        print(f"  sensed {v:>4} loci from {k}")
    print(f"  watching {r['watching']} loci · {r['fittable']} with enough days to fit")
    print(f"  wants {r['wants']} · admitted {r['acquire']['admitted']} · "
          f"refused {r['acquire']['refused']} · below quorum {r['acquire']['below_quorum']}")
    print(f"  expressed {r['express']['lytic']} / dormant {r['express']['lysogenic']} "
          f"(cost {r['express']['cost_units']} units)")
    i = r["identity"]
    print(f"  identity: {i['variants']} variants, diversity {i['diversity_nats']} nats "
          f"— {i['status']}")
    if r["outbreaks"]:
        print("\n  fastest-spreading (R0 is blank until there are several days of history):")
        print(_table([{k: ("—" if v is None else v) for k, v in o.items()}
                      for o in r["outbreaks"]],
                     [("locus", "locus"), ("R0", "R0"), ("lifetime_r", "lifetime r"),
                      ("signal", "signal"), ("distinct_days", "days"),
                      ("phase", "phase")]))
    print(f"\n  state written to genome/STATE.md")
    return 0


def cmd_watch(a) -> int:
    rows = epidemiology.outbreak_table(Store(), source=a.source, min_obs=a.min_obs)
    if a.json:
        print(json.dumps(rows, indent=2))
        return 0
    fittable = sum(1 for r in rows if r["phase"] != "no-history")
    print(f"\n{len(rows)} loci watched · {fittable} with enough distinct days to fit\n")
    print(_table([{k: ("—" if v is None else v) for k, v in r.items()}
                  for r in rows[: a.limit]],
                 [("locus", "locus"), ("source", "source"), ("R0", "R0"),
                  ("lifetime_r", "lifetime r"), ("signal", "signal"),
                  ("distinct_days", "days"), ("phase", "phase"), ("fit_r2", "r2")]))
    return 0


def cmd_genome(a) -> int:
    s = Store()
    rows = []
    for r in s.plasmids():
        m = json.loads(r["manifest"])
        rows.append({"pid": r["pid"], "name": m["name"][:44], "kind": m["kind"],
                     "state": r["state"], "trials": r["trials"], "wins": r["wins"]})
    print(f"\naccessory genome — {len(rows)} plasmids\n")
    print(_table(rows, [("pid", "pid"), ("name", "name"), ("kind", "kind"),
                        ("state", "state"), ("trials", "n"), ("wins", "won")]))
    return 0


def cmd_immune(a) -> int:
    s = Store()
    spacers = [dict(r) for r in s.q(
        "SELECT digest, locus, harm, severity FROM spacers ORDER BY at DESC")]
    for r in spacers:
        r["digest"] = r["digest"][:12]
        r["locus"] = (r["locus"] or "—")[:40]
    print(f"\nCRISPR array — {len(spacers)} spacers\n")
    print(_table(spacers, [("digest", "digest"), ("locus", "locus"),
                           ("harm", "harm"), ("severity", "sev")]))
    rej = s.q("SELECT reason, COUNT(*) n FROM events WHERE kind='reject'"
              " GROUP BY reason ORDER BY n DESC")
    if rej:
        print("\nrejection reasons\n")
        print(_table([dict(r) for r in rej], [("reason", "reason"), ("n", "count")]))
    return 0


def cmd_simulate(a) -> int:
    from .simulate import run
    run(hosts=a.hosts, rounds=a.rounds, hostile_fraction=a.hostile)
    return 0


def cmd_talk(a) -> int:
    from .partner import talk
    r = talk(" ".join(a.message), model=a.model)
    if r["reply"]:
        print(f"\n{r['reply'].strip()}\n")
        if r.get("suggestions"):
            print(f"  (it keeps hearing about: {', '.join(r['suggestions'])} — "
                  f"prime any of these with `pangenome interest <concept> 1.0`)")
    else:
        print(f"\n  {r['note']}\n")
    print(f"  learned {len(r['learned'])} concepts from this exchange")
    return 0


def cmd_study(a) -> int:
    from . import study
    if not a.full:
        study.run(a.model, a.skip_model)
        return 0
    res = study.full(n=a.n, pause=a.pause, save=a.save)
    study.report(res)
    if a.save:
        print(f"\n  raw run written to {a.save}")
    return 0


def cmd_experiment(a) -> int:
    from .experiment import run
    run()
    return 0


def cmd_interest(a) -> int:
    """Priming. This is what makes two organisms see the same page differently."""
    from .salience import AttentionField
    s = Store()
    f = AttentionField(s)
    if a.concept:
        f.prime(a.concept, a.weight, a.why or "set by owner")
        print(f"primed: {a.concept} @ {a.weight}")
    rows = s.q("SELECT concept, weight, why FROM interests ORDER BY weight DESC")
    print(f"\nstanding interests — {len(rows)}\n")
    print(_table([dict(r) for r in rows],
                 [("concept", "concept"), ("weight", "weight"), ("why", "why")]))
    return 0


def cmd_mind(a) -> int:
    from .salience import AttentionField
    from .scaffold import Scaffold
    s = Store()
    sc = Scaffold(s, AttentionField(s))
    print(f"\nscaffold: {json.dumps(sc.summary())}")
    print(f"learning: {json.dumps(sc.learning_ratio())}")
    print(f"attention precision: {json.dumps(AttentionField(s).precision())}\n")
    for tier in ("skill", "abstraction", "pattern"):
        rows = s.q("SELECT statement, support FROM scaffold WHERE tier=?"
                   " ORDER BY support DESC LIMIT ?", (tier, a.limit))
        if rows:
            print(f"{tier}s")
            for r in rows:
                print(f"  [{r['support']:>4}] {r['statement']}")
            print()
    hyp = s.q("SELECT reason FROM events WHERE kind='hypothesis'"
              " ORDER BY at DESC LIMIT ?", (a.limit,))
    if hyp:
        print("hypotheses raised during sleep (candidates, not conclusions)")
        for h in hyp:
            print(f"  - {h['reason']}")
    return 0


def cmd_control(a) -> int:
    from . import control
    if a.state:
        r = control.set_state(a.state, a.why or "set by owner")
        print(f"control plane: {r['prior']} -> {r['state']}")
        if r["state"] in (control.FREEZE, control.KILL):
            print("  the organism will refuse to run. It does not get a vote.")
        return 0
    s = control.state()
    print(f"control plane: {s}")
    for k, v in control.PERMITS[s].items():
        print(f"  {k:<12} {'permitted' if v else 'blocked'}")
    return 0


def cmd_explorer(a) -> int:
    import http.server
    import socketserver
    import webbrowser
    from pathlib import Path

    explorer_dir = Path(__file__).resolve().parent.parent / "explorer"
    if not explorer_dir.exists():
        print("error: explorer directory not found", file=sys.stderr)
        return 1

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(explorer_dir), **kwargs)

    port = a.port
    print(f"\nAHADU · Pangenome Visual Explorer starting at http://localhost:{port}/")
    print("Press Ctrl+C to stop.\n")
    webbrowser.open(f"http://localhost:{port}/")

    with socketserver.TCPServer(("", port), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nExplorer stopped.")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser("pangenome", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("germinate", help="create the organism (runs once)")
    g.add_argument("--name", default="culture-01")
    g.add_argument("--steward", required=True)
    g.add_argument("--force", action="store_true")
    g.add_argument("--fresh", action="store_true",
                   help="wipe inherited acquired state first (template clones)")
    g.set_defaults(fn=cmd_germinate)

    b = sub.add_parser("beat", help="one heartbeat")
    b.add_argument("--json", action="store_true")
    b.set_defaults(fn=cmd_beat)

    w = sub.add_parser("watch", help="outbreak table (read-only)")
    w.add_argument("--source")
    w.add_argument("--limit", type=int, default=25)
    w.add_argument("--min-obs", type=int, default=3, dest="min_obs")
    w.add_argument("--json", action="store_true")
    w.set_defaults(fn=cmd_watch)

    sub.add_parser("genome", help="the accessory genome").set_defaults(fn=cmd_genome)
    sub.add_parser("immune", help="the CRISPR array").set_defaults(fn=cmd_immune)

    s = sub.add_parser("simulate", help="in-process population, no network")
    s.add_argument("--hosts", type=int, default=6)
    s.add_argument("--rounds", type=int, default=12)
    s.add_argument("--hostile", type=float, default=0.25)
    s.set_defaults(fn=cmd_simulate)

    t = sub.add_parser("talk", help="talk to the organism (owner-present; needs a free GEMINI_API_KEY for replies)")
    t.add_argument("message", nargs="+")
    t.add_argument("--model", default=None)
    t.set_defaults(fn=cmd_talk)

    st = sub.add_parser("study", help="ablation + small-model arms (the evidence)")
    st.add_argument("--model", default="gemini-2.5-flash")
    st.add_argument("--skip-model", action="store_true", dest="skip_model")
    st.add_argument("--full", action="store_true",
                    help="the upgraded study: both domains, both model families, n per arm")
    st.add_argument("--n", type=int, default=20, help="repeats per arm (--full)")
    st.add_argument("--pause", type=float, default=4.0, help="seconds between calls")
    st.add_argument("--save", default=None, help="write the raw run to this JSON path")
    st.set_defaults(fn=cmd_study)

    sub.add_parser("experiment",
                   help="same shop, same task, three different owners"
                   ).set_defaults(fn=cmd_experiment)

    ex = sub.add_parser("explorer", help="launch the interactive visual web explorer showcase")
    ex.add_argument("--port", type=int, default=8000, help="HTTP port (default 8000)")
    ex.set_defaults(fn=cmd_explorer)

    i = sub.add_parser("interest", help="prime a standing interest (the owner model)")
    i.add_argument("concept", nargs="?")
    i.add_argument("weight", nargs="?", type=float, default=1.0)
    i.add_argument("--why")
    i.set_defaults(fn=cmd_interest)

    m = sub.add_parser("mind", help="scaffold, learning ratio, hypotheses")
    m.add_argument("--limit", type=int, default=8)
    m.set_defaults(fn=cmd_mind)

    c = sub.add_parser("control", help="owner authority: RUN / SLEEP / FREEZE / KILL")
    c.add_argument("state", nargs="?", choices=["RUN", "SLEEP", "FREEZE", "KILL",
                                                "run", "sleep", "freeze", "kill"])
    c.add_argument("--why")
    c.set_defaults(fn=cmd_control)

    a = p.parse_args(argv)
    try:
        return a.fn(a)
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
