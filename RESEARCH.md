# Research basis

What this architecture is built on, what it deliberately diverges from, and
where the claimed gap actually is. Everything below was checked; anything I could
not verify is marked as such rather than dropped.

---

## 1. The biology

### Horizontal gene transfer and mobile elements
The mechanism the whole architecture is named for. Plasmids, transposons and
integrons move genes *sideways* between organisms with no shared ancestry, which
is why antibiotic resistance spread across species and continents on a timescale
no lineage could match. The pan-genome concept — core genome (in every strain) +
accessory genome (in some, largely horizontally acquired) — is the direct source
for `chromosome.py` / `plasmid.py`.

**Taken:** the accessory/core split; transfer as the unit of adaptation.
**Rejected:** the idea that transfer implies descent. It does not, which is why
provenance here is cryptographic rather than genealogical.

### Conjugation and restriction–modification
Conjugation separates *transfer* from *admission*: DNA crosses the pilus, and the
recipient's restriction enzymes inspect it before it can be expressed. This is
the single most important borrowed detail in the repository, because the live
agent ecosystem collapses those two steps into one.

**Taken:** the gate between transfer and expression (`pilus.py`).

### CRISPR–Cas adaptive immunity
A stored array of spacers taken from past invaders, used to recognise and cut
them on re-encounter. Strictly stronger than self/non-self because it learns.
Historically notable that the defence mechanism turned out more valuable than
anything it defended.

**Taken:** the spacer array (`crispr.py`).
**Added, not from biology:** the anti-autoimmunity rule — biology has no
equivalent of "refusing a stranger is not an injury", and without it the array
blacklists every legitimate capability the host has not yet been told to trust.

### Lambda phage: the lysis/lysogeny switch
The CI/Cro bistable circuit — mutual repression, cooperative positive
autoregulation of CI, CII as the activator that triggers it. Decision depends on
multiplicity of infection: lysis at low MOI, lysogeny at high MOI, with a genuine
bifurcation in between (single lytic steady state → two coexisting stable states
→ single lysogenic state as MOI rises from 1 to ≥3). Induction comes from CI
cleavage under the SOS response.

- *Design Principles of Lambda's Lysis/Lysogeny Decision vis-a-vis Multiplicity of Infection* — [bioRxiv 146308](https://www.biorxiv.org/content/10.1101/146308v12.full)
- *Revisiting Bistability in the Lysis/Lysogeny Circuit of Bacteriophage Lambda* — [PLOS One](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0100876)
- *From Bench to Keyboard and Back Again: A Brief History of Lambda Phage Modeling* — [PMC8590857](https://pmc.ncbi.nlm.nih.gov/articles/PMC8590857/)

**Taken:** the bistable switch with hysteresis, and MOI-dependence, implemented
as coupled Hill dynamics in `lysogeny.py` rather than as a threshold.

### Quasispecies theory
Eigen (1971) and Eigen–Schuster: populations as mutant swarms at
mutation–selection balance, with an error threshold bounding how much information
can be maintained at a given error rate. Domingo's caution is built into the code:
the consensus sequence is a minimal and often insufficient description, and the
field's own stated challenge is shifting from consensus-centred to
mutant-spectrum-centred understanding.

- *Viral quasispecies* — [PLOS Genetics](https://journals.plos.org/plosgenetics/article?id=10.1371%2Fjournal.pgen.1008271)
- *Quasispecies theory and emerging viruses* — [npj Viruses](https://www.nature.com/articles/s44298-024-00066-w)
- *A general and biomedical perspective of viral quasispecies* — [PMC11874995](https://pmc.ncbi.nlm.nih.gov/articles/PMC11874995/)

**Taken:** identity as a distribution; `mu_max ~ 1/L`; diversity reported next to
consensus so a monoculture reads as fragile rather than healthy.

### Quorum sensing
Autoinducer secretion at constant rate, response on ambient concentration, no
addressing and no ballot. Cooperative binding gives a sharp but non-brittle
switch.

**Taken:** the medium, the Hill response, and — the piece usually skipped —
decay, which is what makes concentration mean *now*.

### Epidemiological estimation
Standard outbreak machinery, applied to adoption: log-linear `r`, the
Wallinga–Lipsitch relation `R0 = 1 + r·Tg` for an exponentially distributed
generation interval, three-point logistic for carrying capacity. Reference
implementations consulted for method, not code: EpiModel, tsiR, epidemia,
`incidence`.

**Divergence stated plainly:** in a real outbreak you count infections. Here the
signal is an adoption proxy (stars, dependents, listing presence) and the
susceptible population is unobserved, so `K` is inferred rather than counted, and
an R₀ built on a proxy inherits that proxy's biases. The series is the asset; the
estimator is replaceable.

---

## 2. The AI/CS side

### Digital evolution — the real ancestor
Tom Ray's **Tierra** (1991): self-replicating programs competing for memory and
CPU in a virtual machine. Parasites that skipped the copy loop, then resistant
hosts, then hyper-parasites, then cheats inside cooperative groups — none of it
designed in, all of it emergent from replication plus selection. Then Avida, and
Core War before both.

- Ray, *Evolution, Ecology and Optimization of Digital Organisms* — [PDF](https://faculty.cc.gatech.edu/~turk/bio_sim/articles/tierra_thomas_ray.pdf)
- *Digital Red Queen: Adversarial Program Evolution in Core War with LLMs* — [arXiv 2601.03335](https://arxiv.org/pdf/2601.03335) — the closest live reconnection of this lineage to LLMs, and it keeps the purely competitive framing.

**Gap:** 35 years of prior art, almost none of it reconnected to LLM-era agents,
and none of it using prokaryotic *sociality* (conjugation, quorum, biofilms)
rather than pure competition.

### Open-world artificial life
**OpenLife** — Masumori, Doi, Maruyama, Takata, Ikegami, submitted 30 June 2026.
[arXiv:2606.31046](https://arxiv.org/abs/2606.31046). A stateless LLM surrounded
by asynchronous processes for memory, perception, evaluation and a budget-based
metabolism that makes persistence normative; open-vocabulary LLM appraisal
instead of scalar reward. Six agents run in the open world for ~12 weeks,
reporting a shift from reactive to spontaneous activity, individuation, emergent
social structure, and a first self-earned external income.

*(Verified — this was flagged as possibly confabulated in an earlier session. It
is real.)*

**Relation:** OpenLife establishes that the organism thesis is experimentally
viable. It is a research posture; this is an infrastructure one. Its budget-based
metabolism is the direct counterpoint to the lysogenic answer here — pay to
persist, versus cost nothing while dormant.

### Self-evolving agents — the field this repo defines itself against
- *Darwin Gödel Machine: Open-Ended Evolution of Self-Improving Agents* — [arXiv 2505.22954](https://arxiv.org/abs/2505.22954)
- *A Survey of Self-Evolving Agents* (TMLR, Jan 2026); [Awesome-Self-Evolving-Agents](https://github.com/EvoAgentX/Awesome-Self-Evolving-Agents)
- *Red Queen Gödel Machine: Co-Evolving Agents and Their Evaluators* — [arXiv 2606.26294](https://arxiv.org/pdf/2606.26294)
- *MOSS: Self-Evolution through Source-Level Rewriting* — [arXiv 2605.22794](https://arxiv.org/pdf/2605.22794)
- *PACE: Anytime-Valid Acceptance Tests for Self-Evolving Agents* — [arXiv 2606.08106](https://arxiv.org/pdf/2606.08106)

Every one of these is **vertical**: an agent (or its lineage) improving itself,
retained by benchmark score. Tree-structured, generation-gated.

**The nearest thing to horizontal transfer**, and the paper this repo is closest
to: *Group-Evolving Agents: Open-Ended Self-Improvement via Experience Sharing* —
Weng, Antoniades, Nathani, Zhang, Pu, Wang (UCSB, Feb 2026),
[arXiv 2602.04837](https://arxiv.org/abs/2602.04837), [code](https://github.com/UCSB-AI/GEA).
GEA makes a *group* the evolutionary unit with explicit experience sharing,
explicitly to escape the isolated-branch inefficiency of tree-structured
evolution (71.0% vs 56.7% on SWE-bench Verified).

**Divergence:** GEA shares experience inside one designed system among agents
that share an ancestor and a codebase. Horizontal transfer means capability
crossing between hosts that were never designed together and share no ancestry —
which is precisely where the verification problem appears, and GEA does not have
to solve it because inside one system there are no strangers.

### The memory line — the nearest neighbours to the salience layer
This is the field that has to be engaged honestly, because it is adjacent and it
is moving fast.

- **AdaMem: Learning What to Remember for Personalized Long-Horizon LLM Agents** —
  Chen, Wang, Tu, Bo. [arXiv 2606.21144](https://arxiv.org/abs/2606.21144).
  Learns a *personalised memory-write policy*: what is worth keeping for this
  particular user, refined from feedback, explicitly to cut memory bloat.
- **Eywa: Provenance-Grounded Long-Term Memory for AI Agents** — Joshi.
  [arXiv 2605.30771](https://arxiv.org/abs/2605.30771). Separates source
  evidence, extracted facts and retrieval so memory is auditable across models —
  the same instinct as this repo's append-only genome, applied to recall.
- **LightMem: Lightweight and Efficient Memory-Augmented Generation** —
  [arXiv 2510.18866](https://arxiv.org/abs/2510.18866), ICLR 2026. And, in the
  spirit of this file, its reproduction: *Reproducing LightMem: Naive RAG Is
  Just as Good for Memory Management*
  ([arXiv 2607.29104](https://arxiv.org/abs/2607.29104)). A field where the
  headline results are already failing to reproduce is a field to make narrow,
  checkable claims in.

**Divergence, stated carefully.** AdaMem personalises what an agent **keeps**.
The salience layer personalises what an agent **looks at**, before retrieval
happens at all — perception rather than storage, upstream of the write policy
rather than inside it. That is adjacent, not identical, and the README says so
in the same words. An earlier draft of both files claimed nobody was
personalising memory at all, which was wrong and is corrected here.

### Decentralised coordination
AgentNet (DAG-routed, RAG-based, no predefined workflow), DecentLLMs
(Byzantine-robust voting), SwarmBench ([arXiv 2505.04364](https://arxiv.org/pdf/2505.04364)) —
which finds current LLMs show rudimentary coordination but struggle with
long-range planning under decentralised uncertainty. Stigmergy work is
substantial but sits mostly in swarm robotics ([Nature Comms Eng](https://www.nature.com/articles/s44172-024-00175-7)),
not LLM ecosystems.

**Divergence:** all of these still transmit messages *about the decision*. Quorum
sensing transmits no decision at all.

### Agent supply chain — why the immune system is not hypothetical
The horizontal transfer layer already exists in production, without a restriction
system. Agent skills, plugins and MCP servers are executable third-party code,
not passive configuration; most organisations have no inventory of what they have
installed; packages execute with full host-agent privileges on installation,
without sandboxing or signature verification. A 2026 survey of 1,800+ deployed
MCP servers reported over 30% with at least one exploitable vulnerability, and
the ClawHavoc kill chain ran from a poisoned skill manifest to persistent
compromise across 42,900 exposed instances in 82 countries.

- [Agent Supply Chain Security: MCP Servers, Skill Registries, and Tool Poisoning](https://techjacksolutions.com/ai/agentic-ai/secure/agent-supply-chain-security/)
- [The New Supply Chain Frontier: Securing MCP Security and Agent Skills](https://obot.ai/blog/mcp-security-agent-skills-supply-chain/)
- [The State of MCP Security in 2026](https://nimblebrain.ai/mcp/mcp-security/state-of-mcp-security/)

One finding is load-bearing for the whole thesis: more capable models better
recognise and resist injection attempts, but once compromised they execute
payloads with *higher* precision — model capability does not reduce architectural
risk. That is a direct argument that the answer is ecological rather than
model-scale.

### The self-propagating attack literature — the naming trap
Morris II, Prompt Infection, AgentWorm: malicious prompts that self-replicate
across interconnected agents, propagating through exactly the communication paths
that make multi-agent systems useful. This vocabulary is taken. Anything named
"virus", "infection" or "contagion" will be read as a worm by every technical
reader — which is why this project is named for the pan-genome, and why
[`safety.py`](pangenome/safety.py) exists as code rather than as a paragraph.

**Taken:** the observed motifs, as restriction sites in `crispr.py`.

---

## 3. The gap, in one paragraph

Vertical self-evolution is crowded and well-funded. Open-world ALIFE is real but
small and research-shaped. Decentralised coordination is inherited from robotics
and still message-passing. The adversarial-viral camp owns the vocabulary and is
purely descriptive. **Nobody is at the intersection of prokaryotic sociality, the
live LLM agent ecosystem, and epidemiological measurement of it** — and the
ecosystem is already a Tierra soup running horizontal transfer at scale, with
real economic selection pressure instead of simulated CPU cycles, that nobody is
instrumenting.

## 4. What is verified, and what is not

**Verified 2026-08-16, by reading the sources directly:**

- The **Artificial Life in the Wild** workshop is real: ALIFE 2026, Thu 20 Aug
  2026, Waterloo, Canada — [alife-in-the-wild.github.io](https://alife-in-the-wild.github.io/).
  Its subject is ALIFE systems deployed in real environments rather than in
  simulation, which is the exact shape of this repo. Previously listed here as
  unconfirmed; it is confirmed.
- **Spore in the Wild** is real: *A Case Study of Spore.fun as an
  Open-Environment Evolution Experiment with Sovereign AI Agents on TEE-Secured
  Blockchains*, Botao Amber Hu and Helena Rong,
  [arXiv 2506.04236](https://arxiv.org/abs/2506.04236), accepted by ALIFE 2025
  (ISAL / MIT Press proceedings). Previously listed here as possibly
  confabulated; it is not.
- AdaMem, Eywa and LightMem (and LightMem's reproduction study) — all four
  checked against arXiv metadata; see the memory line above.

**Still not verified:**

- Claimed R₀ figures for capability spread: none exist yet anywhere, including
  here. This repo starts collecting; it does not start knowing.
- The Agensi marketplace revenue-split figure cited in an earlier session was not
  re-verified here and is not relied on by anything in the code.
