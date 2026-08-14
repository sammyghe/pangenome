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
    c = Chromosome.germinate(a.name, a.steward, force=a.force)
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


def main(argv=None) -> int:
    p = argparse.ArgumentParser("pangenome", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("germinate", help="create the organism (runs once)")
    g.add_argument("--name", default="culture-01")
    g.add_argument("--steward", required=True)
    g.add_argument("--force", action="store_true")
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

    a = p.parse_args(argv)
    try:
        return a.fn(a)
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
