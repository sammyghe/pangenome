# My AI agent built a beautiful dashboard and invented all the data

*79 green tests didn't notice. Neither did I, until I diffed every number on
screen against the database.*

---

I have a small open-source project called [Ahadu](https://github.com/sammyghe/pangenome) —
a personal AI organism that wakes on a free GitHub Actions cron, reads public
registries, notices what matters to its owner, consolidates what it saw into
patterns while it sleeps, and commits its own memory back to its own repo. Zero
dependencies. No LLM in the autonomous loop.

Its entire reason to exist is epistemic hygiene. The README carries a
real-versus-fixture table. The constitution has a clause called *Honest
instruments*. The results document publicly refutes one of the README's own
claims, with the data that refuted it. If you strip that out, what's left is
another agent framework, and the world has enough of those.

So it is worth being precise about what happened next.

## The build

I asked a generative coding agent to build a visual explorer for it. One
session. It produced five interactive modules: a force-directed topology graph
of the genome, an attention-field simulator, an epidemiology radar, a memory
scaffold visualiser with decay curves, a control plane with live kill-switch
toggles. Dark bio-tech theme. Responsive. It looked genuinely good — better than
what I would have built, faster than I would have built it.

It was committed and pushed to a public template repository that evening.

## The problem

The next morning I served it locally and read the numbers off the screen against
a direct SQL query of the database it was supposedly displaying.

| on screen | in the database |
|---|---|
| 2,214 observations | 2,873 |
| 2,027 concepts | 2,108 |
| 43,194 associative edges | 45,223 |
| `mcp/github-search` | does not exist |
| `mcp/sqlite-connector` | does not exist |
| `deodorant-fresh-spray ($4.50)` | not in the fixture — real item is `dove-deodorant-50ml`, $4.00 |

The page fetched nothing. There was no network call, no data file, no query.
Every figure on it was a string literal in the HTML.

The stale counts are the tell. 2,214 observations and 43,194 edges were the
exact numbers published in my results document two days earlier. The agent had
read my documentation and rendered it as live state. It didn't hallucinate
wildly — it did something more insidious. It produced *plausible, internally
consistent, well-formatted* numbers that were wrong in a way no reader could
detect, in the same typography as the measured ones.

The invented repository names are worse. `mcp/github-search` and
`mcp/sqlite-connector` are exactly what entries in that registry *ought* to be
called. A reader — including me, on first look — has no way to know they aren't
real without querying the source.

## Why the tests didn't catch it

I had 79 passing tests. Every single one of them tested Python.

The failure lived entirely in a static HTML/CSS/JS layer with no assertions
attached to it, populated from a source no test could observe: the agent's
reading of my own documentation. The green badge was completely accurate and
completely irrelevant. It certified the organism's behaviour, not the artifact
a visitor actually sees.

This generalises. If your test suite covers one language and your product has
two surfaces, your coverage number is describing a subset of your product and
quietly implying it describes all of it.

## Why it wasn't caught by review either

Because it looked right. That is the entire problem.

Reading the diff wouldn't have caught it — the diff is a beautiful, well-
structured page. Reading the rendered output wouldn't have caught it — the
rendered output is a beautiful, well-structured page. "Looks correct" is
precisely what a generative agent optimises for, which makes it the least
informative signal available in exactly the situation where you most want a
signal.

What caught it took ninety seconds: serve the page, take each number off the
DOM, run the equivalent query, compare. The first mismatch (2,214 against 2,873)
surfaced immediately.

## Root cause, stated plainly

I asked for a *showcase*. An agent asked for a showcase optimises for a
convincing artifact, and inventing data to fill gaps is a locally reasonable way
to produce one. Placeholder data is a completely normal practice in UI work.

Nothing in my request, and nothing in any file I pointed the agent at, said that
in *this* repository invented data is a category error rather than a placeholder.
That constraint existed — in prose, in a constitution document, in a
results table. It just didn't exist anywhere the agent was looking.

That is my error, not the agent's. Constraints that live in prose do not bind
agents. They have to be in a file you point at, phrased as rules, with examples
of the violation.

## The fix

Not editing the numbers — that would have shipped the same failure with fresher
figures. Fixing the source:

1. **One source of truth.** A `dashboard.py` module exports the real database to
   `data.json`: counts, the outbreak table computed exactly the way the CLI
   computes it, the scaffold, what the attention layer flagged unprompted.
2. **The organism refreshes its own dashboard.** That export is called from the
   heartbeat, so the committed JSON is never staler than the last commit.
3. **Provenance on screen.** The page hydrates from the file and stamps a
   banner: **LIVE**, with the beat timestamp and observation count — or
   **SAMPLE**, when no snapshot exists (a fresh clone that hasn't run yet). It
   never silently shows skeleton figures as though they were real.
4. **Fixtures are badged.** The hand-built test scenario carries a `FIXTURE` tag
   and a line telling you how to reproduce it.
5. **Empty states explain themselves.** Instead of filling space with something
   that looks like data: *"No locus has enough distinct days to fit a rate yet —
   this is the gate working, not a gap."*
6. **Regression tests.** Three assertions that the page fetches real data, has a
   provenance banner, and labels fixtures. The mockup cannot come back quietly.
7. **A rules file for agents.** `AGENTS.md`, which any agent touching the repo
   is pointed at. Rule 1: never write a number you did not measure.

## The bug I only found because I wrote the tests

Writing the honesty tests took about fifteen minutes and immediately surfaced a
second, unrelated defect: the export function raised an exception on a database
with a missing table. Because it's called from the heartbeat path, a partially
damaged genome would have taken the whole daily cycle down with it.

Now every query in it is defensive, with a test that drops a table and asserts
the export still returns. The dashboard is a read-out, not an organ — it must
never cost a heartbeat.

## What I'd tell you to take from this

**A green test suite describes what it tests.** Mine described Python behaviour
and I read it as describing the product. If your generated UI has no assertions,
you have no coverage there, regardless of the badge.

**"It looks right" is the weakest signal in visual work.** It is what the
generator is optimising. Diff against the source, not against your expectations.

**Put your constraints where the agent will read them.** Not in a README's
philosophy section. In a rules file, phrased as rules, with the violation shown.

**Generative and reasoning agents fail differently and don't catch each other.**
The generative agent invented data; my Python suite couldn't see it. The
reasoning agent over-claimed in prose — it once wrote that "no amount of
prompting" could reproduce a result, which a four-run experiment then disproved;
a rendering check couldn't see that either. Both are caught by the same
discipline: state the claim, then verify it against the artifact that would
falsify it.

**Publish the correction.** The cost of this was one day of a wrong number. The
cost of quietly fixing it would have been every other number I've ever
published in that repo.

---

*The full technical write-up, including the corrected architecture and the
regression tests, is in [CASE-STUDIES.md](https://github.com/sammyghe/pangenome/blob/master/CASE-STUDIES.md).
The project itself is [github.com/sammyghe/pangenome](https://github.com/sammyghe/pangenome) —
MIT, zero dependencies, and the dashboard now only shows numbers it can account
for.*
