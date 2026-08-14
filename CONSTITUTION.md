# Constitution

Hashed at germination and checked at every heartbeat. If this file changes, the
organism logs it loudly on wake. That is deliberate: a silently rewritten
constitution makes every other guarantee in this repository worthless.

## 1. The membrane is one-way

**Pangenome pulls. It never pushes.**

It may read any public registry, repository or feed that any person could read
with a browser. It may acquire capability packets into itself.

It may never transmit a packet, a payload, or an instruction out to another host,
agent, service, or endpoint. There is no outbound conjugation across a process
boundary and there will not be one.

Enforced in `pangenome/safety.py`: every network call goes through one function,
which refuses any method but GET, refuses request bodies, refuses non-HTTPS, and
refuses hosts outside a written allowlist.

This is the line between an architecture inspired by horizontal gene transfer and
a worm. The pathogen frame makes it very easy to drift across. So the line is
code, not a paragraph of intent.

## 2. Acquisition is not expression

A capability that enters the genome enters **dormant**. Integration and execution
are separate acts, separated by a state machine, and the default is dormant.

## 3. Nothing from outside runs with host authority

Arriving payloads are screened and exercised in quarantine. There is no flag,
environment variable, or configuration option that grants an acquired packet the
host's privileges. If a future version needs to execute untrusted payloads, it
gets process-level isolation first or it does not ship.

## 4. The record is append-only

Observations, decisions and rejections are never updated or deleted. Corrections
are new rows. Every decision carries a `reason` field, and it is a required column,
not a convention.

## 5. The immune system may not become autoimmune

A spacer is permanent, so it is taken only for demonstrated harm — a payload that
failed integrity, tripped a restriction site, or failed quarantine. Refusing an
unknown origin is not harm. An unmet stranger must stay acquirable.

## 6. Root authority is cryptographic, not genetic

A plasmid does not care who its parent was; lineage identity dissolves under
horizontal transfer. So descent is not claimed. What is enforced is that some
link in a packet's provenance chain is a signature, over that exact manifest,
from a key in the chromosome's trust set. Widening the trust set is the only
privileged operation in the system and it is logged with a reason.

## 7. Measurement before architecture

The epidemiology layer must work whether or not anyone adopts the conjugation
protocol. A standard without distribution dies; a measurement produces an asset
from the first snapshot. When the two conflict, measurement wins.

## 8. Honest instruments

Where a number is a proxy, the code says it is a proxy. Where a fit does not
hold, the fit statistic is reported next to the estimate rather than hidden.
`phase = "noisy"` is a permitted and expected output.

## 9. The owner's stop is not a request

`SLEEP`, `FREEZE` and `KILL` are read from the control plane as the first
statement of `wake()`, before any organ initialises and before any reasoning
happens. They are not a prompt, not a tool the organism can call, and not
something its model ever evaluates as a decision.

The organism has no code path that writes its own control state. If it could
restore `RUN`, every guarantee here would be theatre — so a test asserts that no
module outside the CLI writes that file. A corrupted or unreadable control file
resolves to `FREEZE`: a damaged stop signal must never read as permission.

`SLEEP` permits consolidation and forbids everything else. The organism may
dream. It may not act.

## 10. Recurrence is counted in days, not in moments

Three hundred observations inside one heartbeat are one scene. No promotion —
not a pattern, not a fitted growth rate — may be earned by repetition within a
single beat. This applies to every part of the system that infers from
frequency, and it is the rule that stops the organism mistaking a busy afternoon
for a trend.

## 11. Structure before amnesia, and amnesia is required

Raw experience is mortal. It decays on a retention curve and is deleted — but
only after it has been consumed into a higher tier. Nothing is forgotten before
its structure is extracted, and nothing is kept merely because storage is cheap.

An abstraction must be *discriminative*. A concept present in nearly every
pattern generalises nothing; promoting it is enumeration wearing the costume of
learning, and it is how a scaffold silently becomes a warehouse.

---

Steward: Samuel Ghedamu. Amendments are made by editing this file and re-recording
its hash — visibly, in a commit, never silently.
