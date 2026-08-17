# Case studies

Things that went wrong or went right in this project, written up so they are
reusable rather than merely survived. Each one is dated, has a cause, and has a
change that makes recurrence structurally harder.

---

## CS-1 · The dashboard that lied (2026-08-17)

**What happened.** A visual explorer was generated for the project by an AI
coding agent (Google Antigravity) in a single session: five interactive
modules, force-directed topology graph, salience simulator, epidemiology radar,
memory scaffold, control plane. It looked genuinely good. It was committed and
pushed to a public template repository the same evening.

It displayed:

| on screen | in `genome/culture.db` |
|---|---|
| 2,214 observations | 2,873 |
| 2,027 concepts | 2,108 |
| 43,194 associative edges | 45,223 |
| `mcp/github-search`, `mcp/sqlite-connector` | do not exist |
| `deodorant-fresh-spray ($4.50)` | not in the fixture (`dove-deodorant-50ml`, $4.00) |

The page fetched no data at all. Every figure was hand-written. The stale
counts were exactly the numbers published in `RESULTS.md` two days earlier —
the agent had read the documentation and rendered it as if it were live state.

**Why it is serious.** This repository's entire claim to attention is that it
does not do this. `RESULTS.md` §0 is a real-vs-fixture table; Constitution §8
requires honest instruments; the study in §5 publicly refutes one of the
README's own claims. A dashboard printing invented figures in the same
typography as measurements destroys all of it at once — and the repo is a
GitHub template, so anyone cloning it would have inherited the lie.

**Why it was not caught by tests.** 79 tests were green. Every one of them
tested Python. The failure was entirely in a static HTML/JS layer with no
assertions attached, populated from a source (the agent's reading of the docs)
that no test could see.

**How it was found.** Not by review of the code, and not by looking at the page
— it *looked* correct. It was found by serving the page, reading every number
off the DOM, and diffing each against a direct SQL query. The first mismatch
(2,214 vs 2,873) took about ninety seconds to surface.

**Root cause.** An AI agent asked to build a *showcase* optimises for a
convincing artifact. Nothing in the request or the repo told it that invented
data was a category error rather than a reasonable placeholder. The constraint
existed in prose, in files it had not been pointed at.

**Fixes applied.**
1. `pangenome/dashboard.py` — the single source of numbers, reading the live
   store.
2. Called from `organism._write_state()`, so the organism refreshes its own
   dashboard every heartbeat and the committed `data.json` is never staler than
   the last commit.
3. `explorer/app.js` hydrates from it and stamps provenance: **LIVE** with the
   beat timestamp, or **SAMPLE** when no snapshot exists.
4. Fixture panels badged `FIXTURE` with reproduction instructions.
5. Empty states explain the rule that produced them.
6. `tests/test_dashboard.py` — three static assertions that the page fetches
   real data, has a provenance banner, and labels fixtures. The mockup cannot
   return silently.
7. `AGENTS.md` — Rule 1 and Rule 2, so the constraint reaches the next agent
   before it writes code rather than after.

**Second bug, found by writing the tests.** `export()` raised on a store with a
missing table. Because it is called from the beat path, a damaged genome would
have taken down the heartbeat. Now every query is defensive, with a test that
drops a table and asserts the export still returns.

**Transferable lessons.**
- A test suite that covers only one language covers only one language. The
  green badge said nothing about the artifact users actually see.
- "Looks right" is the least reliable signal in visual work; it is precisely
  what a generative agent optimises. Diff against the source.
- Constraints living in prose do not bind agents. Put them in a file the agent
  is told to read, phrased as rules with examples of the violation.
- Publish the correction. The cost of CS-1 was one day of a wrong number; the
  cost of hiding it would have been the credibility of every other number.

---

## CS-2 · The organism crossed its own gate (2026-08-17)

**What happened.** On its fourth day of unattended operation, Ahadu produced
its first inferences — and they were produced by the rule that had been
refusing to produce them.

Constitution §10 forbids belief from recurrence within a single moment:
promotion to a pattern requires a signature to recur across **≥3 distinct
days** *and* span ≥3 real days of wall-clock time. For three days the correct
output of `mind` was nothing at all. On day 4:

**First patterns formed** (from 539 episodes):

| pattern | support |
|---|---|
| `market:agent` | 208 |
| `market:mcp` | 165 |
| `market:skill` | 52 |
| `market:memory` | 23 |
| `market:security` | 11 |

**First fitted R₀ values** — the epidemiology layer needs the same 3-day
minimum before it will report a growth rate rather than `no-history`:

| locus | R₀ | days | phase |
|---|---|---|---|
| `internet-court/internet-court-skill` | 2.254 | 4 | outbreak |
| `citrolabs/ego-lite` | 1.309 | 4 | outbreak |
| `tt-a1i/archify` | 1.233 | 4 | outbreak |
| `titanwings/colleague-skill` | 1.122 | 4 | outbreak |

**Why this is the interesting result.** The same mechanism produced both the
three days of silence and the day-4 output. Two earlier bugs — an R₀ of 3.4
billion, and 302 fabricated "skills" in one beat — had the identical cause:
counting repetition inside a single moment as evidence. §10 was written to
forbid that, and the visible consequence was an organism that reported nothing
for three days while looking, to an impatient observer, broken.

It was not broken. It was waiting, and the waiting is what makes the day-4
numbers worth anything.

**Transferable lesson.** A system that cannot say "I don't know yet" will
always say something, and what it says will be noise. The design cost of
honesty is a visibly empty dashboard early on; the payoff is that the first
non-empty reading can be trusted. Build the empty state deliberately and
explain it on screen, or someone will "fix" the silence.

---

## CS-3 · Two agents, two failure modes (2026-08-14 → 17)

An observation worth recording, since this project is built almost entirely by
AI agents working on the same repository.

| | tendency observed | mitigation now in place |
|---|---|---|
| **Generative/visual agent** (Antigravity) | Fast, high-quality artifacts; optimises for a convincing result; invents data to fill gaps without flagging it | `AGENTS.md` Rules 1–2; `tests/test_dashboard.py` |
| **Reasoning/analysis agent** (Claude) | Slower; over-claims in prose (three separate naming inflations, one refuted README claim); catches data errors when it diffs against sources | Three-discipline review panel; `RESULTS.md` corrections log |

Neither failure mode is caught by the other's tests. The generative agent's
failure is invisible to a green Python suite; the reasoning agent's failure is
invisible to a rendering check. Both are caught by the same discipline: *state
the claim, then verify it against the artifact that would falsify it.*
