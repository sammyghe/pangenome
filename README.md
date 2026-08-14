# pangenome

**A prokaryotic architecture for LLM agent ecosystems.**

The core genome does not move. The accessory genome does.

```
python -m pangenome germinate --steward "your name"
python -m pangenome beat        # sense the live ecosystem, decide, integrate
python -m pangenome watch       # the outbreak table
python -m pangenome simulate    # a population in a soup, no network
```

Zero dependencies. Python 3.11+ and the standard library. That is a design
constraint, not an accident — see *Metabolism*.

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
| WAKE | `chromosome` | load root identity; check the constitution's hash |
| SENSE | `observers/` | pull public registries — read-only, allowlisted |
| DIAGNOSE | `epidemiology` | fit growth curves; which capabilities are spreading |
| DESIRE | `quorum` | emit an autoinducer per want. No decision taken |
| ACQUIRE | `pilus` + `crispr` | screen, quarantine, integrate — **dormant** |
| EXPRESS | `lysogeny` | CI/Cro per prophage; almost everything stays asleep |
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
