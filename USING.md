# Using Ahadu

Three ways in, from lightest to heaviest. Windows, Mac and Linux; Python 3.11+;
zero dependencies to install, ever.

---

## Mode 1 — Try it (2 minutes, nothing to sign up for)

```bash
git clone https://github.com/sammyghe/pangenome && cd pangenome
python -m unittest discover -s tests     # 74 tests, ~3s, no network
python -m pangenome experiment           # three owners, one shop, disjoint attention
python -m pangenome study --skip-model   # the measured evidence, no API key
python -m pangenome watch                # what the LIVE organism is tracking
```

You are looking at **Sammy's organism** — the first one, `culture-01`. Its genome
(`genome/culture.db`) ships in the repo because an organism whose history you
cannot inspect is asking for trust it has not earned.

## Mode 2 — Grow your own (10 minutes, free forever)

One repo = one organism = one owner. GitHub's template mechanism is the
distribution: your copy's cron runs **your** organism, on GitHub's free tier,
with the genome committed to **your** repo. Nobody else's server ever holds your
state.

1. **Copy the repo** — click **Use this template** on
   [github.com/sammyghe/pangenome](https://github.com/sammyghe/pangenome)
   (or fork it). Clone your copy.

2. **Germinate yours, shedding the ancestor's memories** (once, locally):

   ```bash
   python -m pangenome germinate --name my-organism --steward "Your Name" --fresh
   ```

   `--fresh` empties every acquired-state table first, so your organism starts
   blank instead of inheriting Sammy's observations, concepts and habits. It
   then writes a fresh `genome/chromosome.json` (public, commit it) and
   `genome/root.key` (**the identity — gitignored, never leaves your machine;
   back it up**).

   Use `--force` instead of `--fresh` if you deliberately want to keep the
   ancestor's memories under a new identity.

3. **Tell it who you are** — this is what makes it *yours*:

   ```bash
   python -m pangenome interest coffee-export 1.0 --why "my business"
   python -m pangenome interest addis-ababa 0.8 --why "my market"
   python -m pangenome interest logistics 0.6 --why "my bottleneck"
   ```

4. **First beat, then push:**

   ```bash
   python -m pangenome beat
   git add -A && git commit -m "germinate: my organism" && git push
   ```

5. **Switch on the heartbeat** — in your repo: Actions tab → enable workflows.
   From tomorrow it senses, notices and commits itself daily at ~05:17 UTC
   without you. `genome/STATE.md` in your repo is its daily report.

6. **Talk to it** (optional, needs one free key from
   [aistudio.google.com](https://aistudio.google.com)):

   ```bash
   export GEMINI_API_KEY=...        # setx on Windows
   python -m pangenome talk "what did you notice today that matters to me?"
   ```

It will honestly know nothing for ~3 days (Constitution §10: no belief without
recurrence across 3 distinct days). Day 4 it can form its first pattern. Week 2
it starts being worth talking to. That curve is the design, not a delay.

**Owner controls, always available, never overridable by the organism:**

```bash
python -m pangenome control SLEEP    # may dream, may not act
python -m pangenome control FREEZE   # nothing runs
python -m pangenome control KILL     # halt; state preserved for inspection
python -m pangenome control RUN      # resume
```

## Mode 3 — A fleet (several organisms, several niches)

Nothing shared, nothing central: **one template copy per organism.** A second
GitHub account, an org account, a work identity — each gets its own repo, its
own chromosome, its own interests, its own genome. They diverge the way two
people walking the same street notice different shops.

Sensible splits that work today:

| organism | interests primed | what its STATE.md becomes |
|---|---|---|
| `you/ahadu-business` | your industry, your city, competitors | a daily competitive scan nobody asked it for |
| `you/ahadu-research` | your field's methods and venues | a literature-adjacent radar |
| `org/ahadu-eng` | your stack, your dependencies | a supply-chain watchtower (CRISPR screening included) |

Cross-organism capability exchange (conjugation between YOUR organisms, signed
by keys you hold) is what the pilus protocol was built for; today it runs
in-process (`simulate`), not between repos. That is the honest current limit.

## What each command is for

| command | what it does |
|---|---|
| `germinate` | create the organism (once) |
| `beat` | one full day-cycle: sense → perceive → decide → sleep → record |
| `talk "…"` | converse; it answers from its own state and learns from yours |
| `interest` | prime what it should care about (this is priming, literally) |
| `watch` | the outbreak table — what is spreading in the wild |
| `mind` | its scaffold: patterns, skills, sleep hypotheses, learning ratio |
| `immune` | the CRISPR array — what it has refused and why |
| `genome` | acquired capability packets and their states |
| `control` | RUN / SLEEP / FREEZE / KILL — owner authority |
| `experiment` / `study` / `simulate` | the reproducible evidence |
| `study --full` | the upgraded study: two domains (hand-built shop + frozen real corpus), two model families, n=20 per arm |

## What it will never do, by construction

- Push, POST, or transmit anything to any host (membrane: GET-only, allowlisted,
  HTTPS-only — [`safety.py`](pangenome/safety.py), tested first in the suite).
- Execute anything it acquired (packets integrate **dormant**; no flag exists).
- Override your control state (no code path writes its own RUN; tested).
- Call a model unattended (the heartbeat is 100% deterministic).

## Where to share this

Kept in the repo so it is a checklist rather than a memory. Ordered by fit, best
first. The rule: no outreach until the study in
[RESULTS.md](RESULTS.md) §10 is upgraded past pilot — a thin result posted
widely is worse than no post.

| # | Where | The angle to lead with |
|---|---|---|
| 1 | **ISAL / alife.org mailing list** | The organism thesis, running unattended in the wild. This is the audience that already has the vocabulary. |
| 2 | **ALIFE "Artificial Life in the Wild" workshop** ([alife-in-the-wild.github.io](https://alife-in-the-wild.github.io/)) | Literally the workshop's subject: ALIFE deployed in a real environment rather than a simulator. |
| 3 | **[awesome-artificial-life](https://github.com/jetnew/awesome-artificial-life)** | A PR. Cheap, permanent, and it puts the repo where the ALIFE-curious already browse. |
| 4 | **[EvoAgentX/Awesome-Self-Evolving-Agents](https://github.com/EvoAgentX/Awesome-Self-Evolving-Agents)** | A PR, framed precisely: the *horizontal* alternative to the list's otherwise entirely vertical self-evolution. |
| 5 | **r/LocalLLaMA** | $0 infrastructure and the model-fallback chain. Lead with the cost and the ownership. Skip the biology entirely. |
| 6 | **Simon Willison** | Deterministic loop, model-as-guest, every decision auditable in SQLite. His exact interests. |
| 7 | **Hacker News** | Submit [RESULTS.md](RESULTS.md) itself, not the README. A self-correcting register with its own claims marked CONTESTED is the one thing that survives HN. |
| 8 | **MCP-security outlets** (Obot, NimbleBrain) | `pilus` + `crispr` are the admission gate their own articles describe as missing. Their framing, implemented. |
| 9 | **Latent Space** | The 248-vs-652-token stable-versus-unstable result — but only once §10's study upgrade strengthens it. |
| 10 | **r/selfhosted** | Own your data, own the cron, no vendor. No biology. |
| 11 | **Lobste.rs** | Same as HN, smaller and more patient. |

**Skip:** LangChain- and AutoGPT-adjacent spaces. Saturated, and the framing
there is agent-framework — the wrong fit for something whose whole claim is that
it is not a framework.
