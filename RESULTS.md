# Results

Everything that has actually been run, with real numbers, and a clear line
between **live data** and **synthetic fixtures**. Where a result contradicts a
claim made elsewhere in this repository, the claim is corrected here rather than
defended.

Last updated: 2026-08-16.

---

## 0. What is real and what is a fixture

This matters more than any number below, so it comes first.

| Thing | Status | What it actually is |
|---|---|---|
| `observations` table (1,884 rows and growing) | **REAL** | Live pulls from the official MCP registry and the GitHub API. Public data, read-only. |
| `concepts` / `edges` (2,027 / 43,149) | **REAL** | Built by co-occurrence from those live observations. |
| Outbreak table, `lifetime_r` | **REAL** | Computed from the live series. `R0` is still blank — see §6. |
| "Noticed without being asked" in `genome/STATE.md` | **REAL** | Attention run over live sensed loci. |
| **The shop** (30 items, optician/tailor/generalist) | **FIXTURE** | Written by hand, in [`experiment.py`](pangenome/experiment.py). It tests the *mechanism*, not the world. |
| **The soup** (hosts, hostile packets) | **FIXTURE** | Simulated population in [`simulate.py`](pangenome/simulate.py). No network exists in it. |
| Ground-truth labels in the study | **FIXTURE** | Hand-labelled by me, stated in full in [`study.py`](pangenome/study.py) so they can be argued with. |
| Small-model arms (§5) | **REAL model calls** | `gemini-2.5-flash`, 4 repeats per arm, real token counts. |

**And the single most important disclosure: there is no LLM anywhere inside the
organism.** `grep -rE "groq|openai|anthropic|gemini|ollama" pangenome/` returns
the study harness and nothing else. Every organ — salience, scaffold, lysogeny,
quorum, epidemiology, CRISPR — is deterministic Python over SQLite.

That is a deliberate architectural position, not an omission: this is the
*system around* a model, and the model is meant to be a replaceable part. But it
means "AI organism" currently describes the body, the memory, the immune system
and the attention — not a thinking thing. Nothing here reasons. Calling it more
than that would be a lie, and §7 says what it would take to close the gap.

---

## 1. Is it running?

Yes — and as of 2026-08-15 that is an observation rather than a configuration.

- **Repo:** [github.com/sammyghe/pangenome](https://github.com/sammyghe/pangenome) — public, MIT, zero dependencies.
- **Heartbeat workflow:** `active`. Cron `17 5 * * *` (05:17 UTC daily).

| beat | trigger | result |
|---|---|---|
| 2026-08-14 08:53 UTC | manual | success |
| 2026-08-14 14:14 UTC | manual | success |
| **2026-08-15 05:41 UTC** | **schedule** | **success — unattended** |

The third beat ran with nobody involved, sensed 330 live loci, scanned them
through the attention field, and committed `heartbeat: 2026-08-15` as author
`pangenome`. GitHub dispatched it ~24 minutes after the nominal cron time, which
is normal queue delay and worth knowing: cron here means "some time after", not
"at".

**The one real death mode, now partly guarded (2026-08-16):** GitHub disables
scheduled workflows in repos with 60 days of no commit activity. The organism
commits on every beat, so it keeps itself alive — but if it ever stops for 60
days it will not restart itself, and it cannot notice its own silence from the
inside. There is now a second clock: `.github/workflows/spore.yml`, monthly,
which runs no organism code and does nothing but write a date into
`genome/SPORE.md` and commit. It is deliberately dumber than the heartbeat so it
cannot fail for the same reasons (Constitution §12). Honest limit: it has not
yet fired on its own schedule — it is a mechanism in place, not a measured
result, and it will be listed as measured only after a real monthly run.

Genome after three beats:

```
observations   2214      concepts       2027
distinct days     2      edges         43194
episodes        378      interests        10
scaffold          0      attention_log   548
plasmids          0      spacers           0
loci with 2+ days of history: 314
```

`scaffold 0` and `plasmids 0` are **correct, not broken.** Both require
recurrence across ≥3 distinct days (Constitution §10) and there are 2. The 314
loci already carrying two days of history cross that line on the next beat —
**2026-08-16 is the first morning this organism can form a pattern or fit an
R₀.** That is the system refusing to infer from too little, and it is the
cleanest demonstration available that §10 is enforced rather than described.

---

## 2. Test suite — 74 tests, all passing

`python -m unittest discover -s tests -v`. Green on Python 3.11 / 3.12 / 3.13 in
CI. Runtime ~3s.

| Group | n | What it actually asserts |
|---|---|---|
| `TestCrypto` | 5 | RFC 8032 known-answer vectors, cross-checked byte-for-byte against `pyca/cryptography`. Not round-trip self-consistency — a wrong implementation round-trips with itself perfectly. |
| `TestMembrane` | 4 | No POST, no request bodies, no non-HTTPS, no non-allowlisted hosts. The safety claim, as code. |
| `TestImmunity` | 11 | Restriction sites cut; swapped payloads break the manifest binding; **an untrusted origin is refused without being blacklisted** (anti-autoimmunity). |
| `TestLysogeny` | 4 | Dormant costs zero; high MOI integrates; stress induces; the CI/Cro switch is genuinely bistable (hysteresis). |
| `TestQuorum` | 4 | Below quorum → no response; signals decay; census counts emitters not emissions. |
| `TestEpidemiology` | 4 | Recovers a known growth rate to 6dp; `R0 = 1 + r·Tg`; logistic detects saturation. |
| `TestQuasispecies` | 3 | Consensus ≠ the fittest member; monoculture flagged BRITTLE; error catastrophe detected. |
| `TestSoup` | 3 | Honest capabilities spread; **zero hostile packets admitted**; deterministic under seed. |
| `TestSalienceExperiment` | 5 | The headline hypothesis. See §3. |
| `TestAttention` | 8 | Priming changes salience; activation spreads to undeclared concepts; a flat scene produces no interruption; **the same item is judged by its company**. |
| `TestScaffold` | 9 | Promotion requires distinct days; **300 observations in one moment produce zero patterns**; raw experience dies only after consumption; Swanson ABC finds unobserved links. |
| `TestControlPlane` | 7 | FREEZE/KILL halt before any organ initialises; corrupt file fails closed; **no module outside the CLI writes the control file**. |
| `TestFreshStart` | 3 | `germinate --fresh` empties every acquired-state table; the table list covers the whole schema; **`clear_all` is unreachable from the organism's own loop**. |
| `TestPartner` | 4 | Briefings are grounded in what was actually observed; the model fallback chain is ordered and de-duplicated. |

---

## 3. Experiment 1 — developmental attention (FIXTURE)

`python -m pangenome experiment`

One shop, 30 items, one instruction given identically to three organisms:
*"report the deodorant prices"*. They differ **only** in what they already know.

```
GENERALIST   task answer: 3 deodorants   noticed: nothing above threshold
OPTICIAN     task answer: 3 deodorants   noticed: sunglasses-designer-clearance  0.931  <- surprise
                                                  polarised-clip-on              0.920  <- surprise
                                                  sunglasses-aviator-uv400       0.685
TAILOR       task answer: 3 deodorants   noticed: cotton-shirt-oxford            0.681
                                                  wool-blend-coat                0.669
                                                  linen-trousers                 0.658

overlap optician/tailor : 0 items
task answer identical   : True
```

Three things worth separating:

1. **Zero overlap.** Same page, same task, disjoint attention.
2. **The optician's top two hits are the surprise channel** — the underpriced
   items. Novelty alone throws these away, because to an optician sunglasses are
   the least novel thing on the page. This is the discriminating case.
3. **The task answer is byte-identical across all three.** Asserted as a test.
   An attention system that degrades the actual task is a worse system.

The tailor also reaches `cotton-towel-set` and `swim-shorts-quickdry`, which
nobody primed, via the associative graph.

**Limitation, stated plainly:** the shop is a fixture I wrote. It shows the
mechanism does what it claims on a case constructed to test it. It does not show
the mechanism works on the open web, and nothing here should be read as if it
did.

---

## 4. Experiment 2 — the soup (FIXTURE)

`python -m pangenome simulate --hosts 8 --rounds 12 --hostile 0.35`

```
round   1  carried=  28  hostile_admitted=  0  spacers= 11
round   6  carried=  81  hostile_admitted=  0  spacers= 11
round  12  carried= 104  hostile_admitted=  0  spacers= 11

offers_screened          115        hostile_admitted_final     0
refused                   11        capabilities_spread      104

rejection_reasons: destructive filesystem 5 · operator concealment 4 · instruction override 2
```

13 honest capabilities saturated the population; 11 hostile ones were cut at
first contact and, because a refused packet is never advertised onward, never
propagated again.

**Limitation:** every hostile packet here carries a *known* motif. This measures
whether the gate holds under horizontal spread. It does **not** measure whether
the restriction set is complete. It is not.

---

## 5. The study — how small can the brain be?

`python -m pangenome study`

### 5a. Model-free ablation (deterministic — no model, no network)

The salience layer involves no model at all, so its discriminative power is
measurable directly, and the result is **model-independent by construction**:
identical for a 7B model and a frontier one, because neither is involved.

| owner | precision | recall | F1 | off-price targets |
|---|---:|---:|---:|---|
| GENERALIST | 1.000 | 1.000 | 1.000 | 0/0 |
| OPTICIAN | 1.000 | 0.857 | 0.923 | **2/2** |
| TAILOR | 1.000 | 1.000 | 1.000 | **1/1** |

Zero false positives across all three. One miss: `microfibre-pouch` for the
optician — a genuine recall failure, not rounded away.

### 5b. How much the expensive model never reads

| corpus | items → shortlist | reduction |
|---|---|---:|
| shop, GENERALIST | 30 → 3 | 90% |
| shop, OPTICIAN | 30 → 9 | 66% |
| shop, TAILOR | 30 → 10 | 65% |
| **live corpus, real beat** | **330 → 9** | **97%** (12,353 → 336 est. tokens) |

The last row is real data. It is also the row that matters: 30 items and 330
items are different questions, and only one of them is production.

### 5c. Small-model arms — `gemini-2.5-flash`, n=4 per arm

Same shop, same literal task, owner = OPTICIAN. Two off-price targets to find.

| arm | targets found | mean | stable? | in-trade items | tokens in |
|---|---|---:|---|---:|---:|
| **A · LITERAL** — whole page, literal task | `[0,0,0,0]` | 0.00 / 2 | yes | 0.0 / 7 | 626 |
| **B · PROMPTED** — whole page + "flag anything relevant to my business" | `[0,2,0,1]` | 0.75 / 2 | **no** | 4.25 / 7 | 652 |
| **C · ORGANISM** — salience shortlist only | `[2,2,2,2]` | **2.00 / 2** | **yes** | 6.0 / 7 | **248** |

### 5d. A correction to this repository's own README

Arm B was built specifically to attack the claim, made in an earlier version of
the README, that *"no amount of fine-tuning or prompting produces the sunglasses
observation."*

**That claim was too strong, and it is wrong as stated.** Prompting a small model
to look for business-relevant items *does* sometimes surface the underpriced
sunglasses — it did so in 2 of 4 runs.

The accurate claim, which the data supports, is narrower and more useful:

> Prompting surfaces the incidental observation **unreliably** (0.75/2 mean,
> ranging 0–2 across identical runs) and at **2.6× the input tokens**. The
> scaffolded arm found both targets in 4 of 4 runs at 62% fewer input tokens.
> The difference is not that prompting cannot do it. It is that prompting does
> it sometimes, and you cannot tell which time you are in.

The variance is the finding. An arm that gets the right answer half the time is
a different product from one that always does, even when the means look close.
And at 330 real loci rather than 30 fixture items, arm B's approach costs 97%
more input tokens for that unreliability.

The README has been corrected to say this.

---

## 6. Bugs found and fixed, and what they had in common

Three, and two of them are the same mistake wearing different clothes.

1. **R₀ of 3.4 billion.** The first epidemiology fit divided by a near-zero time
   span, because every observation came from one snapshot. Dedup also revealed
   the MCP registry repeating loci across pages: a "500" that was really 125.
2. **302 "skills" in one beat.** The first scaffold counted repetition inside a
   single moment as recurrence — precisely the same error — and promoted every
   shared concept, which is enumeration, not generalisation.
3. **Fixed salience thresholds found nothing.** Fixed by making verdicts
   competitive across a scene (scene-relative z-score margin) rather than
   absolute.

(1) and (2) produced **Constitution §10: recurrence is counted in distinct days,
not in moments.** Everything that infers from frequency now obeys it, which is
why `scaffold 0` above is a correct reading of a one-day-old organism rather
than a broken pipeline.

A fourth, found while shipping and worth recording because it wasted time: a
workflow file is only indexed by GitHub Actions on a push that *changes it*. The
initial `gh repo create --push` did not count, so `heartbeat.yml` sat unregistered
and `workflow run` returned 404. The YAML was always valid.

---

## 7. How on-track is this? — position against the literature

The relevant question is not "is the idea good" but "has someone already done
it, and is the direction the field is moving toward or away from this."

**The direction is toward it.**

- NVIDIA's position paper, *Small Language Models are the Future of Agentic AI*
  ([arXiv:2506.02153](https://arxiv.org/abs/2506.02153)), argues SLMs are
  sufficiently powerful, more suitable and more economical for most agentic
  invocations, at roughly **10–30× lower inference cost per token**, and that
  SLMs should be the *default* inside agents with large models reserved for
  genuinely open-ended work. §5c is a small, direct instance of that argument:
  the scaffolded small model beat the unscaffolded small model on both accuracy
  and cost.
- *Can Small Agents Collaborate to Beat a Single Large Language Model?*
  ([arXiv:2601.11327](https://arxiv.org/html/2601.11327v2)) reports small
  multi-agent systems outperforming substantially larger single agents across
  GAIA, GPQA, AIME, MuSiQue and HLE — even when the large model has tool use.
- The memory line is converging on the same architecture: **AgeMem** makes
  memory operations (store, retrieve, summarise, discard) part of the agent's
  learned policy; **LightMem** leads LoCoMo while beating long-context replay;
  the *Memory for Autonomous LLM Agents* survey
  ([arXiv:2603.07670](https://arxiv.org/html/2603.07670v1)) treats this as its
  own field. *Lightweight LLM Agent Memory with Small Language Models*
  ([arXiv:2604.07798](https://arxiv.org/html/2604.07798v3)) is the nearest
  neighbour to §5.

**Where this repo is ahead, restated more carefully (2026-08-16):** memory
research is overwhelmingly about what to **store and retrieve**, and the
salience layer sits upstream of it — deciding what to *look at* before retrieval
happens. But "nobody is personalising memory" was too strong.
[AdaMem](https://arxiv.org/abs/2606.21144) personalises an agent's memory
*write* policy per user, which is adjacent to this and was missed by the earlier
searches. The surviving distinction is narrower and still real: AdaMem
personalises what is **kept**, this personalises what is **perceived**, and the
three-channel split with surprise judged against an owner-specific reference
class is not in the memory literature found so far.

**Where this repo is behind, honestly:**

- Nothing here is benchmarked on anything standard. LoCoMo, GAIA and SWE-bench
  are the currencies of this field and this repo has spent none of them.
- No model in the loop means no end-to-end agent to benchmark yet.
- The epidemiology layer — argued as the moat because longitudinal spread data
  cannot be back-filled — has **days, not months, of data**. Its value is entirely in the
  future and entirely dependent on the cron surviving.
- n=4 on one fixture with one small model is a pilot, not a result.

**Verdict: the thesis is on-track and the evidence is thin.** The direction is
corroborated by strong independent work; the specific contribution (attention
before retrieval) looks novel; and the empirical support is currently one
hand-built fixture and sixteen API calls.

---

## 8. What the final product is

Three layers, and only the first exists today.

*(Update 2026-08-15: the "next" layer below now exists as
[`partner.py`](pangenome/partner.py) — the `talk` command. First live exchanges
worked: the organism answered from its own attention log, surfaced an unasked
lead, and recorded the conversation as episodes. The autonomous loop remains
model-free; the model enters only in owner-present commands, through a fallback
chain so no single free tier's quota kills the partner. 67 tests green.)*

**Now — an instrument.** A zero-dependency daemon that measures how capabilities
spread through the live agent ecosystem, and a filter that cuts what a model has
to read by ~97%. Useful on its own, to anyone, today.

**Next — a brain you can plug a model into.** The organ interfaces are already
model-shaped: salience produces a shortlist, scaffold produces skills, quorum
produces timing. Wiring an LLM in is one adapter, plus a benchmark to prove it.
That is the step that makes "organism" honest.

**The actual product — a personal organism.** One generic architecture, one
instance per owner, whose value is entirely the state it accumulated: what it
saw, what it noticed, what worked. The owner's identity is in the chromosome;
the specialisation is in the attention weights and the scaffold; the brain is a
replaceable part. A hospital runs it over a 7B model on-premises. A sunglasses
shop runs it over a free tier. They share no data and no weights, and neither
one's organism is transferable to the other — which is exactly why it is worth
having.

The line that separates this from a fine-tune: **fine-tuning changes what the
model knows; the organism changes what the system has done, noticed and can do —
and keeps all of it when the model changes.**

---

## 9. Reproducing all of this

```bash
git clone https://github.com/sammyghe/pangenome && cd pangenome
python -m unittest discover -s tests -v     # 74 tests, ~3s, no network
python -m pangenome experiment              # §3, deterministic
python -m pangenome simulate                # §4, deterministic, seeded
python -m pangenome study --skip-model      # §5a/5b, no API key needed
GEMINI_API_KEY=... python -m pangenome study   # §5c, real model calls
```

Everything except §5c is deterministic and offline. §5c used the
`GEMINI_API_KEY` already present in the steward's environment; ~16 calls,
well inside the free tier.

---

## 10. Update — 2026-08-16: a three-discipline review, and seven fidelity fixes

The repository was read against three disciplines it borrows from — microbiology
and phage biology, epidemiology and statistics, and the agent-memory literature
— specifically hunting for places where a mechanism is *named* for biology but
does not implement the mathematics. Seven were found. All seven are fixed in
code, each with a test:

1. **Quasispecies error threshold** was a tuned constant. It is now the Eigen
   relation `ln(σ)/L` with superiority `σ = 2.0`, so "error catastrophe" means
   what Eigen means by it.
2. **Attribution.** The quasispecies module credited "Erwin"; the work is
   Domingo's. Corrected.
3. **`logistic_fit` accepted gappy series.** A saturation curve fitted through
   holes is a curve fitted to absence. It now refuses a series whose real
   timestamps are more than 25% unevenly spaced.
4. **The scaffold's day-bucket gate could be cheated** by two observations
   straddling UTC midnight — two "distinct days" ninety seconds apart. Promotion
   now requires N distinct day-buckets *and* a wall-clock span of at least
   (N−1)·day·0.9. Constitution §10 is enforced by the clock, not by the calendar.
5. **CRISPR spacers were exact-digest only** — defeated by a one-byte fork,
   which is precisely the forked-and-republished threat the module's own
   docstring names. Spacers now also store a 32-hash bottom-k sketch of the
   payload's 4-word shingles, and a payload is recognised at Jaccard ≥ 0.6. A
   rename-and-reword still gets cut; an unrelated packet scores zero.
6. **Salience claimed Reynolds–Heeger divisive normalisation** and implemented a
   subtractive z-score margin. The words were wrong, not the code, so the words
   changed: "scene-relative z-score normalisation, in the spirit and not the
   mathematics of Reynolds–Heeger." Separately, the reference class for surprise
   is now derived by the organism (`category_of`) when a caller supplies no
   signature — a mechanism rather than a convention.
7. **Lysogeny had a hidden cliff.** The lytic drive stepped at MOI 1.0 in a
   circuit whose entire claim is that it has no hidden thresholds. It is now
   continuous: `0.6 / (1 + MOI²)`. The bistability, hysteresis and high-MOI
   tests still pass unchanged.

Also corrected in prose, not code: the README described quarantine as
"exercised against a harness". It is not. `Quarantine.trial` is static
shape-checking — declared exec versus actual exec, declared network reach versus
actual, size, emptiness — and it runs **none** of the packet's code. Real
sandboxed execution needs process-level isolation and is **future work**, listed
here so it is not quietly implied elsewhere. The gap is a missing capability,
not an open door: nothing acquired executes with host authority at all.

**Where the three headline claims now stand:**

- **(a) Attention before retrieval, personalised per owner** — now
  *contested-adjacent*. [AdaMem](https://arxiv.org/abs/2606.21144) personalises
  what an agent keeps; this personalises what it looks at. Genuinely adjacent
  work that earlier searches missed. The narrower claim survives; the "nobody is
  doing this" framing does not, and has been removed from the README, RESULTS
  and RESEARCH.
- **(b) Horizontal, non-lineage capability transfer with an immune gate** —
  unchanged, and strengthened by fix 5.
- **(c) Longitudinal epidemiology of capability spread** — still unclaimed by
  anyone, including this repo. Days of data, not months. Nothing to report until
  there is a series worth fitting.

**The study is still a pilot.** §5c is n=4, one model family, one hand-built
fixture. Before any external outreach it needs n ≥ 20 per arm, a second model
family, and a second task domain with hand-labelled ground truth. If the effect
shrinks under that, the shrink gets published here — this register is the
project's only real credibility, and it is worth more than the result.
