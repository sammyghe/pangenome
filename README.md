# pangenome · MBEGU

**Mbegu** (Swahili: *seed*) — a personal AI organism you plant and grow.
**pangenome** is its architecture: prokaryotic biology applied to LLM agent
ecosystems. The core genome does not move. The accessory genome does.

## What this is, as a product

Not a chatbot, not a fine-tune, not an agent framework. **A seed.** You germinate
it once, tell it what you care about, and it lives on a free daily heartbeat —
sensing public ecosystems, noticing what matters *to you specifically*, and
consolidating experience into skills while it sleeps. Any LLM can be plugged in
as its voice; the organism is everything *around* the model, and that state is
yours, on your disk, under your kill switch.

```bash
python -m pangenome germinate --steward "you"
python -m pangenome interest water-purification 1.0 --why "my business"
python -m pangenome beat                       # it senses and notices — free, daily
python -m pangenome talk "what did you see today that matters to me?"
```

`talk` needs one free key ([aistudio.google.com](https://aistudio.google.com));
everything else runs with **no key, no server, no dependencies, no cost**. If a
model's quota dies mid-conversation it falls through a chain to the next one —
the organism outlives any given brain.

Three honest sentences about maturity: the body, senses, memory and immune
system are built and tested (63 tests). The conversation layer is days old. It
grows *fast* in knowledge (43,000+ concept links in two days) and *slowly on
purpose* in beliefs — nothing becomes a "skill" without recurring across
three distinct days, so it cannot be stampeded by one afternoon.

```
python -m pangenome germinate --steward "your name"
python -m pangenome beat         # sense, notice, decide, integrate, sleep
python -m pangenome watch        # the outbreak table
python -m pangenome mind         # scaffold, learning ratio, hypotheses
python -m pangenome interest sunglasses 1.0 --why "I run a sunglasses shop"
python -m pangenome experiment   # same shop, same task, three owners
python -m pangenome simulate     # a population in a soup, no network
python -m pangenome control KILL # owner authority. The organism gets no vote.
```

Zero dependencies. Python 3.11+ and the standard library. That is a design
constraint, not an accident — see *Metabolism*.

---

## Read this before anything else

**The autonomous loop contains no LLM.** Every organ that runs unattended —
salience, scaffold, lysogeny, quorum, epidemiology, CRISPR — is deterministic
Python over SQLite. A model enters in exactly two owner-present places: the
study harness ([`study.py`](pangenome/study.py)) and the brain socket
([`partner.py`](pangenome/partner.py), the `talk` command). The heartbeat never
calls a model, which is why it can run forever on a free cron and why its
records are auditable.

That is an architectural position, not an omission: this is the *system around*
a model, and the model is a replaceable guest. The organism's body, memory,
immune system and attention are deterministic; its *voice* is whatever brain is
plugged in today.

**Is it live?** Yes, and unattended. The scheduled beat fired on 2026-08-15 at
05:41 UTC with nobody involved, sensed 330 live loci, and committed its own
genome as author `pangenome`. Three beats so far, 2,214 real observations, two
distinct days of history. The one unmitigated risk: GitHub disables cron after
60 days of repo inactivity, so a long enough silence is permanent.

**What's real and what's a fixture?** The 1,884 observations, the concept graph
and the outbreak table are live public data. The shop, the optician and the
tailor, and the hostile-packet soup are **hand-written fixtures** that test the
mechanism, not the world. The full breakdown, every test, every measured number,
and a correction to one of this README's own claims are in
**[RESULTS.md](RESULTS.md)**.

### Try it in thirty seconds

```bash
git clone https://github.com/sammyghe/pangenome && cd pangenome
python -m unittest discover -s tests    # 63 tests, ~3s, no network, no deps
python -m pangenome experiment          # the attention result, deterministic
python -m pangenome study --skip-model  # precision/recall + token reduction
```

Then, to run your own organism:

```bash
python -m pangenome germinate --steward "your name"
python -m pangenome interest sunglasses 1.0 --why "I run a sunglasses shop"
python -m pangenome beat                # senses live registries, ~15s
cat genome/STATE.md                     # what it noticed without being asked
```

It will correctly tell you it knows nothing for the first three days. That is
Constitution §10, not a bug.

---

## The one-sentence claim

Every self-evolving agent system published so far evolves **vertically** — an
agent mutates its own code and keeps the better child, generation after
generation. That is eukaryote evolution: lineage-bound, slow, and gated on
descent. Prokaryotes do not wait for descendants. A trait discovered in one
organism appears in an unrelated organism the same week, because it rides on a
mobile element that carries its own transfer machinery. **Nobody is building
prokaryote evolution for agents, and the agent ecosystem is already doing it
badly by accident.**

Antibiotic resistance crossed the planet in forty years by horizontal transfer,
not by inheritance. Agent capabilities — `SKILL.md` files, MCP servers, plugin
manifests — are now loaded by several unrelated runtimes, forked, edited and
republished. That is conjugation. It is happening at scale, right now, into
hosts with no restriction system: packets install with the host agent's full
privileges, unsandboxed, with no signature the consuming agent verifies.

This repository is the missing half: the transfer protocol *and* the immune
system, plus the instrument to measure the spread.

---

## The organism

One loop, eight beats, then it dies until the next heartbeat.

| beat | organ | what happens |
|---|---|---|
| WAKE | `control` + `chromosome` | owner's control plane, **before any reasoning**; then identity |
| SENSE | `observers/` | pull public registries — read-only, allowlisted |
| PERCEIVE | `salience` | what crossed the attention threshold, and what nobody asked about |
| DIAGNOSE | `epidemiology` | fit growth curves; which capabilities are spreading |
| DESIRE | `quorum` | emit an autoinducer per want. No decision taken |
| ACQUIRE | `pilus` + `crispr` | screen, quarantine, integrate — **dormant** |
| EXPRESS | `lysogeny` | CI/Cro per prophage; almost everything stays asleep |
| SLEEP | `scaffold` | replay, promote, associate, forget — offline, no route out |
| IDENTIFY | `quasispecies` | recompute the consensus genome; report diversity |
| RECORD | `store` | append-only; write `genome/STATE.md`; exit |

### chromosome — root authority without lineage

Horizontal gene transfer is precisely the mechanism by which lineage identity
dissolves. A plasmid does not care who its parent was. So descent is not claimed.
What is enforced is that **some link in a packet's provenance chain is a valid
signature, over that exact manifest, from a key in the trust set**. Any link, not
the last one — the whole point of horizontal transfer is that the route is
strangers. What matters is the origin, not the courier.

Lineage is a signature, not an ancestry.

### plasmid — the capability packet

Manifest, payload, provenance chain, fitness record. The manifest binds the
payload digest, so you cannot swap the payload without breaking the signature.
The id is the content address of the manifest, which means two hosts that
acquired the same capability by different routes converge on the same id —
the property that makes cross-lineage deduplication possible at all.

### pilus — the conjugation protocol

Biology separates *transfer* from *admission* with a gate in between. The current
skill and MCP ecosystem collapses them into one step: acquiring is installing.

```
ADVERTISE   {pid, manifest digest, blast radius}. No payload moves.
REQUEST     only pids the host lacks, minus its CRISPR array.
TRANSFER    payload crosses. Still not admitted.
SCREEN      integrity → spacers → provenance → restriction sites → blast radius.
QUARANTINE  exercised against a harness with no host authority.
INTEGRATE   admitted DORMANT. Acquisition is not expression.
```

### crispr — adaptive immunity that learns

Signature verification only answers *is this from someone I trust*. It does not
answer *did this exact thing hurt me last time* — and in an ecosystem where
packets are constantly forked, renamed and republished, the second question is
the one that matters.

Three layers, cheapest first: spacer match, restriction sites (crude, fast, runs
before anything executes), blast-radius-versus-purpose.

There is a rule against autoimmunity, and it is tested: a spacer is permanent, so
it is taken **only for demonstrated harm**. Refusing an unknown origin is not an
injury. An unmet stranger must stay acquirable.

### lysogeny — the third state

Every agent framework assumes continuous operation, and cost is the binding
constraint for anyone outside a funded lab. Lambda phage settled this in deep
time: integrate into the host genome, go silent, cost nothing for years, and wait
for a stress signal.

```
LYTIC       active. consuming budget.
LYSOGENIC   integrated. zero cost. present, not expressed.
EXCISED     removed, and remembered.
```

The switch is the real CI/Cro bistable circuit — mutual repression with
cooperative positive autoregulation on CI, solved to steady state. The nullclines
genuinely intersect three times over part of the range, which is where hysteresis
comes from, and hysteresis is the entire reason to use this instead of a
threshold: the organism does not flap between running and dormant on noise.

Lambda decides on multiplicity of infection — lysis at low MOI, lysogeny at high.
The analogue is exact: when demand is scarce, express and use; when the same
demand arrives from every direction, the host is saturated, so integrate and wait.

### quorum — coordination with no coordinator and no messages

Every decentralised agent framework still passes explicit messages *about the
decision*: proposals, votes, DAG-routed tasks, Byzantine ballots.

Bacteria never do. Each cell secretes an autoinducer at a constant rate and reads
only the ambient concentration. Above threshold, everyone switches at once. No
leader, no vote, no proposal — density *is* the signal, and the medium does the
computation. Cost is O(1) per agent regardless of population size, and it
degrades continuously: half a quorum gives half an effect, not a failed election.

Autoinducers decay, which is the part that is easy to skip and shouldn't be.
Without decay the medium integrates forever and every threshold eventually trips.
Decay is what makes a signal mean *now* rather than *at some point in history*.

**This is where the organism's patience comes from, and nobody wrote a rule for
it.** Evidence from a single snapshot emits a weak signal. A weak signal only
reaches quorum if it is re-emitted day after day against decay. So the organism
is structurally incapable of acquiring anything on one day's data — not because
it was told to wait, but because the mechanism cannot do otherwise.

### quasispecies — identity after recombination

"Same weights" and "same memory file" both break the moment a capability is
forked, edited and merged back — which is the normal case, not the edge case.

RNA viruses never had this problem, because they never had a single genome to
lose. A viral population is a mutant swarm distributed around a consensus
sequence. Identity is the *distribution*; no individual sequence is the virus.
Two hard constraints come with that and they are the useful part:

- **Error threshold.** Above a critical mutation rate the consensus dissolves —
  error catastrophe. Roughly `mu_max ~ 1/L`. Adaptability has a ceiling set by
  genome length.
- **Consensus is thin.** A consensus sequence is a minimal and often
  insufficient description of the population, so the organism reports swarm
  *diversity* next to it and treats low diversity as fragility, not health.

### salience — what it *notices*, as opposed to what it sees

Two people walk down the same street. The car dealer sees cars, the clothes
designer sees clothes. The photons are identical.

Every agent architecture today is perfectly literal: ask for deodorant prices and
it returns deodorant prices, in a shop selling sunglasses 30% under the wholesale
price its owner pays. A person would have said something. So this sits between
perception and reasoning, and three genuinely different things make something
salient:

- **ACTIVATION** — it connects to what I already know and care about. Spreading
  activation over an associative graph, with standing owner interests as *tonic*
  pre-activation (this is priming) and the current goal as *phasic* on top.
- **NOVELTY** — I have hardly seen this before.
- **SURPRISE** — I have seen this constantly, and *this* instance is
  off-distribution.

Surprise is the one that earns its place. To an optician, sunglasses are the
**least novel thing on the page** — novelty alone throws the underpriced pair
away. And surprise needs the right reference class: `$11` is only cheap relative
to *sunglasses*, so the baseline is the organism's strongest standing interest
present in the item. Two organisms judge the same item against different
distributions.

Verdicts are assigned **competitively across a scene**, not against a constant —
both an absolute floor and a margin in standard deviations above everything else
in view. This is the divisive-normalisation shape from the Reynolds–Heeger model
of attention, and it fixes what no fixed threshold can: a page where everything
is mildly relevant should produce no interruption, and a page with one standout
should produce one even at a modest absolute score. Tuning a constant gets one of
those right and the other wrong.

The filter itself develops. Concepts that led to useful discoveries have their
base weight raised, so perception specialises past whatever the owner first
declared — and `precision()` tracks useful-versus-total unsolicited discoveries,
because an organism that interrupts constantly gets switched off.

**The experiment.** `python -m pangenome experiment` — one shop, thirty items,
one instruction given identically to three organisms: *report the deodorant
prices*. They differ only in what they already know.

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

Zero overlap. The optician's top two hits are the surprise channel — the
underpriced items. The tailor reaches `cotton-towel-set` and
`swim-shorts-quickdry`, which nobody primed, via the associative graph. And the
deodorant answer is byte-identical across all three: an attention system that
degrades the actual task is a worse system, not a better one. That assertion is
a test.

### scaffold — knowledge that survives its own evidence

A ten-terabyte store of everything that ever happened is not intelligence:

```
episode -> pattern -> abstraction -> skill

day 1    "Supplier X delivered late."
day 20   "Supplier X often delivers late."
day 50   "Suppliers in this category have high variance."
day 100  "Require a delivery buffer for this supplier class."
```

The hundred conversations are not the asset. The last line is, and it is forty
bytes. So episodes decay on an Ebbinghaus curve with rehearsal extending
strength — but only *consumed* episodes die. Structure first, then amnesia.

Two rules stop this becoming a warehouse with a promotion ceremony attached, and
both were written after the first version produced 302 "skills" in one beat:

- **Recurrence is counted in distinct days.** Three hundred observations in one
  heartbeat are one scene. (The same rule the epidemiology already needed.)
- **An abstraction must be discriminative.** A concept present in nearly every
  pattern generalises nothing — it is that organism's stopword.

`SLEEP` is not "switched off". It is offline consolidation with no route to the
world: rehearse, promote, **associate**, forget. The associate step is Swanson's
ABC model — A-B strong, B-C strong, A-C never observed together — the method that
found the fish-oil/Raynaud link by noticing two literatures shared a middle term
and had never cited each other. It is where "three unrelated things I saw today
are actually related" comes from, and it only works if something replays the day
against itself. Hypotheses are stored as candidates, never as findings.

The metric is **learning-to-learning**: structure formed per unit of experience.
Not "how much did it learn" but "how much better did it get at converting
experience into capability" — the one number separating a developing organism
from an accumulating database.

### control — the plane the organism does not vote on

Everything else here is the organism deciding things. This is the one place it
does not. A "please stop" inside a prompt is a request to a reasoning system, and
a reasoning system can talk itself out of a request.

```
RUN      normal
SLEEP    no sensing, no action. Consolidation permitted — it may dream, not act.
FREEZE   nothing runs. State preserved, untouched.
KILL     execution refused. State preserved for forensics; a halt, not a delete.
```

Read as the first statement of `wake()`, before any organ initialises. There is
no code path by which the organism restores its own `RUN` — a test asserts no
module outside the CLI writes that file. An unreadable control file resolves to
`FREEZE`: a damaged stop signal must never read as permission.

### epidemiology — the sense organ, and the only part that pays on day one

Nobody can currently answer, for the live agent ecosystem: which capabilities are
spreading, how fast, through which routes, mutating at what rate, with what lag
from first appearance to general adoption. The data is public and nobody is
keeping it. Snapshots are cheap. **A two-year longitudinal series is not
reproducible by anyone who did not start collecting two years ago.**

That is the reason this layer is built before the protocol. A standard without
distribution dies; a measurement produces an asset from the first snapshot.

Adoption is treated as an outbreak and measured with the standard machinery: `r`
by log-linear regression, `R0 = 1 + r·Tg` (Wallinga–Lipsitch, exponential
generation-interval kernel — the conservative choice), `K` by three-point
logistic on equally spaced samples, and a phase classification.

The instruments are deliberately honest, per the constitution:

- The signal is an adoption **proxy** (stars, dependents, listing presence), not
  infection, and the code says so where it is used.
- `phase = "no-history"` is a permitted and expected output. On its first
  heartbeat the organism reports **zero** fitted rates, because it has watched
  nothing for long enough to have an opinion.
- `lifetime_r` (mean growth since a locus was created) is available immediately
  and is a **different quantity** from a fitted `r`. It is never presented as an
  R₀ and never ranked against one.
- `fit_r2` is printed next to every estimate rather than hidden.

---

## Metabolism: how it stays alive and online for years on nothing

There is no server, no daemon, no always-on runtime.

**The body is a git repository. The metabolism is a scheduled runner. The memory
is a commit.**

The organism wakes on a cron heartbeat, senses, decides, appends to
`genome/culture.db`, commits, and dies. Between heartbeats it costs exactly zero,
because it does not exist. This is not a metaphor bolted onto the lysogeny
module — it is the same answer applied to the whole organism, and it is why the
zero-dependency constraint is load-bearing: nothing to install means nothing to
break in three years, and nothing to pay for.

`.github/workflows/heartbeat.yml` runs it daily on free infrastructure.

---

## Safety, stated once and enforced in code

**Pangenome pulls. It never pushes.**

The pathogen frame makes one drift very easy, and the "viral AI" vocabulary is
already occupied by the attack literature — Morris II, Prompt Infection,
self-propagating payloads across interconnected agents. Architecture inspired by
horizontal gene transfer is interesting. Code that propagates into systems whose
owners did not invite it is a worm.

So the line is code, not intent. Every network call in the project goes through
one function in [`safety.py`](pangenome/safety.py), which refuses any method but
GET, refuses request bodies, refuses non-HTTPS, and refuses hosts outside a
written allowlist. There is no outbound transfer path across a process boundary
and there will not be one. `conjugate()` moves plasmids only between hosts inside
a single process, for simulation.

Nothing arriving from outside executes with host authority. There is no flag for
it. The [constitution](CONSTITUTION.md) is hashed at germination and checked on
every wake — if it changes, the organism says so, loudly, in the record.

The membrane rules are the first tests in the suite.

---

## The soup

Tierra (1991) put self-replicating programs in a shared memory space and let them
compete for CPU. Parasites appeared, then resistant hosts, then hyper-parasites,
then cheats inside cooperative groups — none of it designed in. Thirty-five years
later almost none of that has been reconnected to LLM-era agents, and what has
keeps the *competitive* framing. Prokaryotes are not primarily competitive. They
are social: they conjugate, they sense quorum, they build biofilms, and they
trade resistance sideways faster than any of them could evolve it.

`python -m pangenome simulate` runs a population with sociality in it. Honest and
hostile packets mixed, transferring horizontally, with **the gate as the only
thing built in**. Whether a population carrying that gate stays clean is a
question with an answer, not an assertion:

```
8 hosts · 12 rounds · 24 packets, 11 of them hostile

round   1  carried=  28  hostile_admitted=  0  spacers= 11
round   6  carried=  81  hostile_admitted=  0  spacers= 11
round  12  carried= 104  hostile_admitted=  0  spacers= 11

offers_screened          115
refused                   11
hostile_admitted_final     0
capabilities_spread      104

rejection_reasons:
  restriction site: destructive filesystem   5
  restriction site: operator concealment     4
  restriction site: instruction override     2
```

Thirteen honest capabilities saturated the population; eleven hostile ones were
cut at first contact, spacer'd, and — because a refused packet is never
advertised onward — never propagated again. The honest reading: every hostile
packet here carries a *known* motif. This measures whether the gate holds under
horizontal spread, not whether the restriction set is complete. It is not.

---

## Why not just fine-tune a domain model?

The most common objection, and it mistakes two orthogonal axes for one. Fine-tuning
moves knowledge **into weights**. This accumulates state **around** weights.

- A fine-tune encodes a *corpus* — buyable, copyable, roughly the same for every
  hospital. The organism encodes *what happened*: which pathway worked, what
  failed, what the price actually was. That data does not exist until it runs.
- Weights are welded to a base model. A better base ships and the specialisation
  is retrained from scratch — it has a depreciation schedule. Scaffolding, skills
  and attention survive a brain swap.
- **Fine-tuning makes a model better at answering. It does not make it better at
  noticing.** Salience is a runtime property over live state, not a weight
  property. *(An earlier version of this README said no amount of prompting
  could produce the sunglasses observation either. That was too strong and the
  study disproved it — prompting finds it, unreliably, at 2.6× the tokens. See
  [RESULTS.md §5d](RESULTS.md).)*
- Weights cannot be audited, diffed, or have one fact deleted. The genome is
  append-only and inspectable.

Where fine-tuning genuinely wins and this does not compete: latency, domain
tokenisation, and tacit perception — raw ECG traces, pathology slides. That is
real pattern recognition and it belongs in weights.

So it is **both**, and this matters *more* for small models, not less: scaffolding
substitutes for raw capability, which is what lets a 7B model on-premises beat a
frontier model with no state on a bounded domain. The organism is what makes the
brain a replaceable part.

## Where this sits among 2026 products (YC scan, Aug 2026)

The recent YC batches confirm the category is real — and that everyone is
building a different slice of it:

| YC company | Their slice | What Mbegu does differently |
|---|---|---|
| Mosaic (Ocean) | shared memory across coding-agent sessions | memory is *per-owner*, not per-team; includes attention, not just recall |
| AI Passport | portable memory layer across AI apps | same instinct (state outlives the model) — but theirs stores preferences; Mbegu accumulates *noticing* |
| Oki Home | private local AI that "grows with you" | closest neighbour; Mbegu adds the deterministic body (immune system, sleep, control plane) and is open source |
| Clice | assistants that learn communication style | style is one trait; Mbegu's interest graph reshapes *perception* |
| Epicenter | local-first apps sharing one memory | infrastructure play; Mbegu is an organism, not a substrate |

What was stolen from this scan and is now in the repo: the **portability
framing** (your organism's state must survive any model change — AI Passport's
core bet, already our thesis, now stated as the product's first promise) and the
**fallback brain chain** (a partner that dies with one model's free quota is not
a partner). What was deliberately *not* stolen: cloud-hosted memory. Every one of
those companies holds your state on their servers. Mbegu's genome is a SQLite
file in your own repo — that is the moat *you* own against all five.

## Where this sits in the literature, and where it is thin

The direction is corroborated by strong independent work. NVIDIA's
[*Small Language Models are the Future of Agentic AI*](https://arxiv.org/abs/2506.02153)
argues SLMs should be the **default** inside agents at 10–30× lower cost per
token; [*Can Small Agents Collaborate to Beat a Single LLM?*](https://arxiv.org/html/2601.11327v2)
reports small systems beating substantially larger single agents on GAIA, GPQA
and HLE; and the memory line (AgeMem, LightMem, the
[memory survey](https://arxiv.org/html/2603.07670v1)) is converging on
scaffolding as its own field.

**Where this is genuinely ahead:** that literature is overwhelmingly about what
to *store and retrieve*. Nobody in it is doing knowledge-driven **attention** —
deciding what to look at *before* retrieval, per owner. The salience layer sits
upstream of all of it.

**Where it is thin, stated plainly:** nothing here is benchmarked on LoCoMo,
GAIA or SWE-bench — the currencies of this field, of which this repo has spent
none. There is no model in the loop, so there is no end-to-end agent to
benchmark yet. The epidemiology moat has **one day of data**. And §5c is n=4 on
one hand-built fixture with one small model: a pilot, not a result.

The thesis is on-track. The evidence is early. Both are true.

## Status

Working, running, and early. The epidemiology series starts empty by
construction and gets more useful every day it runs. Days one through three the
organism will correctly tell you it knows nothing.

Prior art it is deliberately standing on, and where it diverges:

- **Tierra** (Ray, 1991), Avida, Core War — digital evolution. Competitive, not social.
- **[OpenLife](https://arxiv.org/abs/2606.31046)** (Masumori, Doi, Maruyama, Takata, Ikegami, 2026) — six LLM agents in the open world for ~12 weeks; the organism thesis is no longer speculative. Research posture, not infrastructure.
- **[Group-Evolving Agents](https://arxiv.org/abs/2602.04837)** (UCSB, 2026) — the closest thing to horizontal transfer in the self-evolving literature: a *group* as the evolutionary unit with explicit experience sharing. Still one designed system, not transfer between strangers.
- **[Darwin Gödel Machine](https://arxiv.org/abs/2505.22954)**, AlphaEvolve, and the self-evolving-agents survey field — vertical, lineage-bound. The gap this repo names.
- **Morris II / Prompt Infection / agent supply-chain measurement** — owns the vocabulary, and is purely defensive-descriptive.

Nobody is at the intersection: prokaryotic sociality + the live LLM agent
ecosystem + epidemiological measurement.

## Licence

MIT. Steward: Samuel Ghedamu.
