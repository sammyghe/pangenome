# Rules for any AI agent working on this repo

Applies to Antigravity, Claude Code, Cursor, Codex — anything that edits these
files. Read this before writing code. These rules exist because each one was
broken once and cost something.

---

## RULE 1 — Never write a number you did not measure

This is the whole project. Ahadu's only durable advantage over prettier
competitors is that it does not print plausible figures. Break this and nothing
else here is worth reading.

**Banned, always:**
- Hardcoding counts, metrics, scores, IDs, or names into a UI, README, or doc.
- Inventing example data that *looks* like real data (`mcp/github-search`,
  `deodorant-fresh-spray`) — a reader cannot tell it apart from a measurement.
- Copying a number from an older doc into a new one. It is stale the moment
  the organism beats again.

**Required instead:**
- Read from `genome/culture.db` via `pangenome/dashboard.py` or `store.py`.
- If data is unavailable, render an empty state that says *why* it is empty.
  "No locus has enough distinct days to fit a rate yet (Constitution §10)" is a
  correct, useful screen. A fake table is not.
- Anything illustrative gets a visible `FIXTURE` or `SAMPLE` badge in the UI
  and a one-line pointer to how to reproduce it.

**This was violated on 2026-08-17** (commit `3f77b7c`): the explorer shipped
displaying 2,214 observations and 43,194 edges (counts from two days earlier),
loci that do not exist, and shop items not in the fixture. It fetched nothing.
It was public for a day. See `RESULTS.md` for the full correction.

## RULE 2 — Verify visuals in a browser against the data source

"It renders and looks right" is not evidence. Before claiming a UI works:
1. Serve it.
2. Open it.
3. Pick every number on screen and diff it against a direct query of the DB.
4. Check the console for errors.

If you cannot open a browser, say so plainly and do not claim the UI is
verified.

## RULE 3 — The autonomous loop calls no model, ever

`organism.heartbeat()` and everything it touches must stay deterministic Python
over SQLite. A model may only be called from owner-present commands
(`partner.py` / `talk`, `study.py`). This is why the heartbeat can run free
forever on a cron and why its records are auditable. Do not "improve" a beat by
adding inference to it.

## RULE 4 — Zero third-party dependencies

Stdlib only, in the Python package and in `explorer/` (no CDN, no npm, no build
step). If a task seems to need a dependency, it needs a different design.

## RULE 5 — Read-outs must not cost a heartbeat

Anything called from `_write_state()` or the beat path wraps its own failures.
A dashboard, an export, a log — these degrade one panel; they never take down
the organism. Every query in `dashboard.py` is defensive for this reason.

## RULE 6 — The safety properties are not refactorable

- **Membrane** (`safety.py`): GET-only, HTTPS-only, host allowlist. No POST, no
  request bodies, ever. It pulls; it never pushes.
- **Control plane** (`control.py`): read before any organ initialises. No code
  path may let the organism write its own `RUN`.
- **Acquisition ≠ expression**: acquired packets integrate dormant. There is no
  flag to execute them.
- **Constitution §10**: recurrence counted in distinct days AND wall-clock span.

Tests assert all of these. If a test in `TestMembrane`, `TestControlPlane` or
`TestScaffold` fails, the fix is your code, not the test.

## RULE 7 — Correct in public, do not quietly patch

When you find an error in this repo's own claims, append a dated correction to
`RESULTS.md` saying what was wrong and for how long. The self-correcting record
is a feature, and it is the reason the project survives scrutiny. Silently
editing a wrong number is worse than the wrong number.

## RULE 8 — Tests before commit

`python -m unittest discover -s tests` must be green. Add a regression test for
every bug fixed. Current baseline: **88 tests**.

---

## Fast orientation

| file | what it is |
|---|---|
| `AHADU-DIRECTIVE.md` | full context + strategy + roadmap. Read first. |
| `CONSTITUTION.md` | the rules enforced in code. Non-negotiable. |
| `RESULTS.md` | every measured number, real-vs-fixture table, corrections log. |
| `USING.md` | how a stranger runs their own organism. |
| `RESEARCH.md` | prior art, what was taken, what diverges. |
| `pangenome/dashboard.py` | the ONLY source of numbers for the explorer. |

Product name **Ahadu**; package/repo name **pangenome**. Keep the split.
