# AHADU DIRECTIVE — master prompt for Claude Opus 5

**Paste this file's contents (or point the session at this file) to continue the
work. It is self-contained: context, mid-flight state, exact tasks in order,
acceptance criteria, and the strategy behind every choice. Steward: Samuel
(Sammy) Ghedamu. Repo: `C:\Users\user\Desktop\pangenome` →
github.com/sammyghe/pangenome (public, MIT).**

---

## 0. What this project is (read once, then act)

**Ahadu** (Amharic/Ge'ez: *the first*) — a personal AI organism. **pangenome**
is its architecture name and Python package name (keep this split: Ahadu in
prose/branding, pangenome in code/URLs/commands — decided, do not revisit).

One-line thesis: every published self-evolving agent system evolves
*vertically* (agent mutates itself — eukaryote evolution); Ahadu implements
*horizontal, prokaryotic* adaptation — capability packets with cryptographic
provenance, an immune gate, dormancy that costs zero, quorum-gated patience,
and an attention field shaped by its owner — as **deterministic Python around
a replaceable LLM**. The autonomous daily loop (GitHub Actions cron) contains
NO model call. The model is a guest (`partner.py`, `study.py` only).

Hard rules that are code, not prose (never weaken):
- **Membrane**: pulls, never pushes. One network function, GET-only, HTTPS,
  host allowlist (`safety.py`). Tested first in the suite.
- **Control plane**: owner's SLEEP/FREEZE/KILL read before any organ
  initialises; no code path lets the organism write its own RUN (`control.py`,
  tested).
- **Constitution §10**: recurrence counted in distinct days, never in moments.
- **Acquisition ≠ expression**: packets integrate dormant; nothing acquired
  ever executes with host authority.
- Zero third-party dependencies, forever. Stdlib only.

## 1. Mid-flight state (exact, verified 2026-08-16)

Committed HEAD: `d50ebaf` ("mbegu: the brain socket"). Working tree has
UNCOMMITTED changes — do not lose them, they are correct and reviewed:

| file | state | what it is |
|---|---|---|
| `README.md` | modified | Mbegu→Ahadu rename (title `# AHADU · አሐዱ`, tagline, YC table) |
| `pangenome/quasispecies.py` | modified | DONE: "Erwin"→Domingo; error threshold now Eigen-correct `ln(σ)/L` with `SUPERIORITY = 2.0` |
| `pangenome/epidemiology.py` | modified | DONE: `logistic_fit` now refuses gappy series (25% gap-equality guard on real timestamps) |
| `pangenome/scaffold.py` | modified | DONE: pattern gate now requires N distinct day-buckets AND wall-clock span ≥ (N−1)·DAY·0.9 (kills the UTC-midnight-straddle cheat) |
| `pangenome/store.py` | modified | DONE: `spacer_shingles` table + `add_spacer_shingles` / `best_spacer_similarity` (Jaccard) + `clear_all()` for `--fresh` |
| `USING.md` | untracked | Complete 3-mode usage guide (Try / Grow your own / Fleet) |

An approved plan exists at
`C:\Users\user\.claude\plans\check-this-out-and-velvet-sifakis.md` — this
directive supersedes it only in ordering and detail; the content agrees.

## 2. Remaining build tasks, in order (each small, each tested)

### 2a. Finish the CRISPR fuzzy-spacer upgrade (store half is done)
In `pangenome/crispr.py`:
- Add a module-level `shingles(payload: bytes) -> set[str]`: decode utf-8
  (errors=ignore), lowercase, collapse whitespace, split to words, take
  4-word overlapping shingles, hash each (e.g. `hashlib.md5(s).hexdigest()[:12]`),
  keep the 32 lexicographically smallest (a MinHash-style cap so long payloads
  don't bloat the array).
- `acquire_spacer`: after `add_spacer`, call
  `store.add_spacer_shingles(digest(payload), shingles(payload))`.
- `recognised`: exact-digest fast path first (unchanged); then
  `store.best_spacer_similarity(shingles(payload)) >= 0.6`.
- Rationale (biology review): exact-hash spacers are defeated by a one-byte
  fork — precisely the forked-and-republished threat the module's own
  docstring names. Update the docstring to describe the two-tier match.
- TEST: a spacer'd payload with a few words changed/reordered is still
  recognised; a genuinely different payload is not.

### 2b. Salience honesty + wiring
In `pangenome/salience.py`:
- The comment block above `FLOOR`/`MARGIN` claims Reynolds–Heeger *divisive*
  normalisation; the code is *subtractive* (z-score margin). Fix the words,
  not the code: call it "scene-relative z-score normalisation (in the spirit,
  not the mathematics, of Reynolds–Heeger)". Same fix in README's salience
  section.
- Wire `category_of()` in by default: in `scan()`, when an item's signature
  is falsy, use `self.category_of(concepts_of(text))` so reference-class
  surprise is mechanism, not caller convention.
- TEST: `scan()` with `None` signatures runs and produces category-based
  signatures.

### 2c. Lysogeny hidden threshold
In `pangenome/lysogeny.py` (~line 92): replace
`seed_cro = self.cro + (0.6 if moi < 1.0 else 0.0)` with a continuous
function, e.g. `self.cro + 0.6 / (1.0 + moi * moi)`. The bistable circuit's
whole point is no hidden cliffs. Existing tests (high-MOI→lysogeny,
stress→lytic, hysteresis) must still pass — verify, don't assume.

### 2d. Pilus/README wording
README says arriving packets are "exercised against a harness". They are not —
`Quarantine.trial` is static shape-checking, no execution. Fix the README
sentence to say exactly that (the `pilus.py` docstring already admits it).
Real sandboxed execution is future work; say so in RESULTS.md.

### 2e. Sporulation (closes the one real death mode)
- New `.github/workflows/spore.yml`: monthly cron (e.g. `23 6 1 * *`) +
  `workflow_dispatch`; checkout; append/refresh a timestamp line in
  `genome/SPORE.md`; commit+push unconditionally. Keep it dumber than
  heartbeat.yml on purpose — it must not share heartbeat's failure modes.
- Why: GitHub disables scheduled workflows after 60 days without repo
  activity. Heartbeat commits daily, so this fires only if heartbeat has
  already silently died — a second, simpler clock. (Biology review's
  endospore analogue, minimal form.)
- Add CONSTITUTION.md clause (§12, "A second clock"): the organism's defense
  against silent death is a keepalive that cannot fail for the same reason
  the heartbeat might.

### 2f. `germinate --fresh`
- `cli.py cmd_germinate`: add `--fresh` flag → when set, call
  `Store().clear_all()` (already implemented) then
  `Chromosome.germinate(..., force=True)`.
- Update USING.md Mode 2 step 2 to the single command and DELETE the manual
  `DELETE FROM` python one-liner it currently contains.
- TEST: populated store + `clear_all()` → all 12 tables empty.

### 2g. Template repository
`gh api -X PATCH repos/sammyghe/pangenome -f is_template=true` — then verify
`--jq '.is_template'` returns `true`. This makes USING.md's "Use this
template" literally true.

### 2h. Tests + suite
One test per fix above (2a–2c, 2f). Baseline 67 green; expect ~72–75. Full
suite must pass on `python -m unittest discover -s tests` before any commit.

## 3. Documentation tasks (the "clear studies" ask)

### 3a. README
- Keep the Ahadu rename as-is on disk. Read the top 60 lines once for tone:
  Ahadu = product, pangenome = architecture, consistently.
- Add a **"Personal AGI, made concrete"** section after "What this is, as a
  product": Garry Tan (YC Startup School 2026) argues for agents on your own
  infrastructure that compound your knowledge over time, skill files as
  personal assets, owning your cognition rather than renting it. Map each
  phrase to the mechanism that already exists: own infra = free Actions cron
  + SQLite genome in the owner's repo; compounding = scaffold's
  episode→pattern→abstraction→skill; skill files as assets = `scaffold` tier
  'skill' rows in the owner's own repo; agency = `control.py` (the organism
  gets no vote). Position as *one concrete, inspectable instance* of the
  pattern Tan describes — built independently, pointing the same direction.
  Do not use the phrase "AGI" for Ahadu itself (research review: invites the
  wrong fight; "personal organism" and "state that outlives the model" are
  what's demonstrated).
- Soften the novelty claim the research review contested: name **AdaMem**
  (arXiv 2606.21144) explicitly — it personalises what an agent *keeps*
  (write policy); Ahadu personalises what an agent *looks at* before
  retrieval (perception). Adjacent, not identical; say so before a reader
  finds AdaMem first.

### 3b. RESEARCH.md
Update the stale "not verified" section: the ALIFE 2026 "Artificial Life in
the Wild" workshop (Waterloo, Aug 20) and "Spore in the Wild" (ISAL/MIT Press
ALIFE 2025 proceedings) are both now verified real — cite
alife-in-the-wild.github.io and the MIT Press proceedings link. Add AdaMem,
Eywa (2605.30771), LightMem-ICLR-2026 to the memory-line prior art.

### 3c. RESULTS.md
Append a dated update (same pattern as the existing 2026-08-15 note): the
three-discipline review happened; list the seven fidelity fixes with one line
each; note claim (a) now CONTESTED-adjacent by AdaMem, claim (c) still
unclaimed, study still a pilot pending §4 below.

### 3d. USING.md
- Commit it (currently untracked), with the `--fresh` update from 2f.
- Add a short **"Where to share this"** section — the amplifier list, so it
  lives in the repo and Sammy sends things himself. Top targets from the
  research review, in order: ISAL / alife.org mailing list; ALIFE
  "Artificial Life in the Wild" workshop (alife-in-the-wild.github.io);
  awesome-artificial-life (github.com/jetnew/awesome-artificial-life — PR);
  EvoAgentX/Awesome-Self-Evolving-Agents (PR, framed as the horizontal
  alternative to vertical self-evolution); r/LocalLLaMA (lead with $0
  infra + fallback chain, skip the biology); Simon Willison (deterministic
  loop, model-as-guest, auditability angle); Hacker News (submit RESULTS.md
  itself — the self-correcting register survives HN); MCP-security outlets
  (Obot/NimbleBrain — pitch pilus+crispr as the missing gate their own
  articles describe); Latent Space (the 248-vs-652-token stable-vs-unstable
  result, once §4 strengthens it); r/selfhosted (own-your-data angle, no
  biology); Lobste.rs. SKIP: LangChain/AutoGPT-adjacent spaces — saturated,
  wrong fit.

## 4. The study upgrade (before any external push)

Current §5c evidence is n=4, one model, one hand-built fixture — a pilot, not
a result. Before HN/ALIFE/newsletter outreach, upgrade once:
- n ≥ 20 per arm; add a second model family (a small open-weights model via
  the same HTTP-adapter pattern, or a second hosted free tier); add a second
  task domain beyond the shop fixture (e.g. the live MCP-registry corpus with
  hand-labelled ground truth for one owner profile).
- Report means, ranges, and stability per arm exactly as now. If the effect
  shrinks, publish the shrink — the project's credibility IS the
  self-correction register.
This is the single highest-leverage credibility step (research review's
unanimous #1).

## 5. Commit plan (3 commits, then push, then verify)

1. `ahadu: rename + personal-AGI positioning + usage guide` — README,
   USING.md, RESEARCH.md, RESULTS.md.
2. `fidelity: seven fixes from the three-discipline review` — quasispecies,
   epidemiology, scaffold, store+crispr, salience, lysogeny, pilus wording,
   with their tests.
3. `sporulation + germinate --fresh + template repo` — spore.yml,
   CONSTITUTION §12, cli flag.
Style: narrative bodies like existing history; trailer
`Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`. After push:
`gh run list --limit 3` green; `is_template` true; heartbeat workflow
untouched and still scheduled; `git log --author=pangenome` still shows the
organism's own daily commits arriving.

## 6. Strategy frame (so future sessions decide like the steward would)

**Worth-Sammy's-time policy**: Ahadu is an *instrument and research asset*,
not a startup pivot. Maji Safi launch is the business. Ahadu's design goal is
to compound **unattended** — steward time capped at ~2–4 h/week. The moat is
the longitudinal epidemiology series: every day it runs it becomes less
reproducible by anyone who started later. Decision gate: after ~30 days of
data AND the §4 study upgrade, decide on the ALIFE/HN push. Until then, no
outreach, no marketing, just beats.

**Growth loops (how it grows, in order of activation):**
1. *Owner loop* (live): interests → noticing → talk → episodes → skills →
   sharper noticing. Deepens with use, zero marginal cost.
2. *Data loop* (live): daily beats → capability-spread series nobody else
   holds → the research asset.
3. *Distribution loop* (activates with template flag): Use-this-template →
   each user's organism commits daily in their own repo → every user's GitHub
   activity graph becomes a living advertisement → stars → forks.
4. *Research loop* (after §4): strengthened study → workshop note/arXiv →
   citations → the right audience arrives already convinced.

**Future organs, priority order (do NOT build until the above ships):**
chemotaxis (reallocate sensing toward productive sources using existing
`attention_log` yield data); toxin–antitoxin (plasmids re-earn their place
during sleep or get excised — gives `EXCISED` a driver); critical-period
plasticity (juvenile window with a 2-day gate, salience-weighted recurrence);
real sandboxed quarantine; conjugation between the steward's own organisms
across repos (the fleet, signed by keys he holds).

**Never**: outbound transmission, cloud-hosted state, a model inside the
autonomous loop, weakening the control plane, biology-washing (every
mechanism named for biology must implement the mathematics or say plainly
that it doesn't).
