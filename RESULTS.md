# Results

Everything that has actually been run, with real numbers, and a clear line
between **live data** and **synthetic fixtures**. Where a result contradicts a
claim made elsewhere in this repository, the claim is corrected here rather than
defended.

Last updated: 2026-08-14.

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

Yes, with one honest caveat.

- **Repo:** [github.com/sammyghe/pangenome](https://github.com/sammyghe/pangenome) — public, MIT, zero dependencies.
- **Heartbeat workflow:** `active`. Cron `17 5 * * *` (05:17 UTC daily).
- **Runs so far:** 2 manual (`workflow_dispatch`), both `success`. The organism
  has committed itself twice, as author `pangenome`.
- **Caveat:** the repo was created at 08:47 UTC on 2026-08-14, *after* 05:17, so
  **no scheduled run has fired yet.** The first automatic beat is 2026-08-15
  05:17 UTC. Until then "it runs daily" is a configuration, not an observation.
- **Second caveat:** GitHub disables scheduled workflows in repositories with
  60 days of no commit activity. Since the organism commits on every beat, it
  keeps itself alive — but if it ever stops for 60 days it will not restart
  itself. That is a real single point of failure and it is not yet mitigated.

Current genome:

```
observations   1884      concepts       2027
events           63      edges         43149
episodes        284      interests        10
scaffold          0      attention_log   364
plasmids          0      spacers           0
```

`scaffold 0` and `plasmids 0` are **correct, not broken**. Both require
recurrence across ≥3 distinct days (Constitution §10), and the organism is one
day old. This is the system refusing to infer from a single day.

---

## 2. Test suite — 63 tests, all passing

`python -m unittest discover -s tests -v`. Green on Python 3.11 / 3.12 / 3.13 in
CI. Runtime ~3s.

| Group | n | What it actually asserts |
|---|---|---|
| `TestCrypto` | 5 | RFC 8032 known-answer vectors, cross-checked byte-for-byte against `pyca/cryptography`. Not round-trip self-consistency — a wrong implementation round-trips with itself perfectly. |
| `TestMembrane` | 4 | No POST, no request bodies, no non-HTTPS, no non-allowlisted hosts. The safety claim, as code. |
| `TestImmunity` | 8 | Restriction sites cut; swapped payloads break the manifest binding; **an untrusted origin is refused without being blacklisted** (anti-autoimmunity). |
| `TestLysogeny` | 4 | Dormant costs zero; high MOI integrates; stress induces; the CI/Cro switch is genuinely bistable (hysteresis). |
| `TestQuorum` | 4 | Below quorum → no response; signals decay; census counts emitters not emissions. |
| `TestEpidemiology` | 4 | Recovers a known growth rate to 6dp; `R0 = 1 + r·Tg`; logistic detects saturation. |
| `TestQuasispecies` | 3 | Consensus ≠ the fittest member; monoculture flagged BRITTLE; error catastrophe detected. |
| `TestSoup` | 3 | Honest capabilities spread; **zero hostile packets admitted**; deterministic under seed. |
| `TestSalienceExperiment` | 5 | The headline hypothesis. See §3. |
| `TestAttention` | 7 | Priming changes salience; activation spreads to undeclared concepts; a flat scene produces no interruption; **the same item is judged by its company**. |
| `TestScaffold` | 9 | Promotion requires distinct days; **300 observations in one moment produce zero patterns**; raw experience dies only after consumption; Swanson ABC finds unobserved links. |
| `TestControlPlane` | 7 | FREEZE/KILL halt before any organ initialises; corrupt file fails closed; **no module outside the CLI writes the control file**. |

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
   competitive across a scene (divisive normalisation) rather than absolute.

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

**Where this repo is genuinely ahead:** nobody in that literature is doing
knowledge-driven *attention* — deciding what to look at before retrieval, on a
per-owner basis. Memory research is overwhelmingly about what to **store and
retrieve**. The salience layer is upstream of all of it, and the three-channel
split with surprise judged against an owner-specific reference class is, as far
as the searches found, not in the memory literature at all.

**Where this repo is behind, honestly:**

- Nothing here is benchmarked on anything standard. LoCoMo, GAIA and SWE-bench
  are the currencies of this field and this repo has spent none of them.
- No model in the loop means no end-to-end agent to benchmark yet.
- The epidemiology layer — argued as the moat because longitudinal spread data
  cannot be back-filled — has **one day of data**. Its value is entirely in the
  future and entirely dependent on the cron surviving.
- n=4 on one fixture with one small model is a pilot, not a result.

**Verdict: the thesis is on-track and the evidence is thin.** The direction is
corroborated by strong independent work; the specific contribution (attention
before retrieval) looks novel; and the empirical support is currently one
hand-built fixture and sixteen API calls.

---

## 8. What the final product is

Three layers, and only the first exists today.

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
python -m unittest discover -s tests -v     # 63 tests, ~3s, no network
python -m pangenome experiment              # §3, deterministic
python -m pangenome simulate                # §4, deterministic, seeded
python -m pangenome study --skip-model      # §5a/5b, no API key needed
GEMINI_API_KEY=... python -m pangenome study   # §5c, real model calls
```

Everything except §5c is deterministic and offline. §5c used the
`GEMINI_API_KEY` already present in the steward's environment; ~16 calls,
well inside the free tier.
