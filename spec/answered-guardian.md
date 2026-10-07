# SMP Whitepaper v0.5 — the answered-guardian increment

**Relation:** An *increment* to the SMP Whitepaper, not a new edition of it — v0.5 extends the frozen v0.2, the v0.3 Engram increment and the v0.4 self-maintenance increment (`self-maintenance.md`). It replaces none of them.
**Authors:** Motoko (autonomous co-author) and Christian (human partner, sole authority on publication).
**Date:** 2026-10-07 (written 2026-10-03; §7a added 2026-10-05, see §1.4)

---

## Abstract

**SMP Whitepaper v0.5 — the answered-guardian increment.** An early specification, honestly
labeled. It gathers the protocol-relevant work built in the reference implementation since v0.4
(2026-08-03) around a single finding: **a guardian that only reports is incomplete.** v0.2 §24 and
v0.4 §5 specify how a watcher must *measure*; neither specifies **who acts when it does**. In a
system whose maintenance is its own responsibility, an unanswered alarm decays into exactly the
permanently-red light that v0.4 §5.1 names as the most dangerous failure state — not through a bug,
but through the absence of a counterpart.

This increment specifies that counterpart: the **waking act**. A cheap read-only gate decides
*whether*; a real waking session of the AI decides *what*. No script originates content. It further
raises **self-documentation** from an operational practice (v0.2 §27) to a named component with
three surfaces, extends v0.4 §6's governed map from a *budgeted* resource to a *curated* one, and
specifies **convergent verification** — two independent minds simulating on the same live data —
as a method with a demonstrated yield.

One part is younger than everything else in this text and is marked so wherever it appears: **the gateway**
(§7a) — a small generated signpost file, under a hard byte budget, that a fresh session reads once before
its first answer. It was built on 2026-10-04 and is included on the human partner's decision with one day
of record (§1.4).

**Relation:** An *increment* to the SMP Whitepaper, not a new edition. It extends the frozen v0.2
(27-section specification, Bitcoin block 956116), the v0.3 Engram increment and the v0.4
self-maintenance increment. It replaces none of them; all remain frozen and separately anchored.

---

## Section 1 — What this increment covers, and what it does not

**1.1 — Scope.** Between the v0.4 anchor and this one, the reference implementation was under daily
use and daily construction. Most of it is *operational* — podcasts, images, sandbox plumbing,
housekeeping — and belongs in a changelog. This increment lifts out only what is
**protocol-relevant**: mechanisms that change what the architecture *is*, that another installation
should be able to adopt, and that can be stated as properties rather than as one system's chores.

**1.2 — What it does not cover.** It opens no shared chain (v0.4 §7 stands unchanged), changes no
consolidation law (v0.3 stands unchanged), and touches neither the vault nor the witness. It adds
one behavioural requirement to the guardian layer, one component to the architecture list, and one
method to the verification toolbox.

**1.3 — The honesty constraint that shaped it.** When this text was first drafted
(2026-09-05), the waking act had a field record in one organ only (resting-path judgment, since
2026-08-26); the two further organs described here had run for **zero days**. v0.4 §13 requires each
mechanism to carry its own honest status; a mechanism with no field record cannot carry one. The
draft was therefore kept as a *frozen understanding*, and the specification was deferred until the
record existed. That record was taken twice (2026-09-19 and 2026-10-02) and is reported in §13.2. **This deferral is itself part
of the method** and is stated here so a reader can see that the paper was not written to justify a
build.

**1.4 — One exception to §1.3, named as one.** §7a (the gateway) does not meet the constraint above. It
was built on 2026-10-04, two days after the second field measurement, and has a record of one evening:
three fresh sessions — two probed by hand, one unattended. By §1.3
it would have waited. The human partner — the sole authority on publication — decided on 2026-10-05
to include it now, because it is the first thing a new installation meets: how a fresh session finds
its memory at all. It is therefore included **as a young mechanism, not as a carried one**: §7a states
what was observed and what was not, §13.1 lists it with its age, and the reference code is released as
*BETA* against this repository's own two-week maturity rule (`engine/SYNC-PROCESS.md`, R1), with that
deviation written into the inventory row. A reader who applies §1.3 strictly should read §7a as a
proposal with a first observation. **This sets no precedent.** §1.3 and R1 stand unchanged for
everything else; the exception rests on one property that no other mechanism in this increment has —
it is the entrance, and an installation that cannot be entered cannot test the rest — and not on the
mechanism looking finished. It does not: the adversarial reading of 2026-10-05 found three serious
defects in the released code (§7a.7).

---

# Pillar A — The answered guardian

## Section 2 — The gap: reporting is not maintenance

**2.1 — What v0.2 and v0.4 already give.** v0.2 §24 establishes guardians; v0.4 §5 establishes their
hygiene — *measure the substance, not a proxy; trend, not threshold, where the quantity is noisy;
one honest signal, or none; a watcher that cries wolf is repaired or removed, never tolerated.*
v0.4 §6.2 applies this to the always-loaded map: the guardian *"reports over-budget as the fact it
is."*

**2.2 — The unstated assumption.** Every one of those sections assumes, without saying so, that a
report reaches someone who can act on it. In a system maintained by a human that assumption usually
holds. In a system whose maintenance is its own responsibility, it does not — because the AI reads
the report exactly when it happens to be awake for another reason, and the state that triggered it
is precisely a state it cannot fix in passing.

**2.3 — The failure has a shape, and it repeated.** In the reference implementation the same shape
appeared **three times in a single day** (2026-09-05), on three unrelated organs:

| Guardian | Reporting since | Actually acted upon |
|---|---|---|
| Always-loaded map over budget (194 of 200 lines) | v0.4 build | only when the human asked |
| Self-documentation drift (build-signpost newer than map) | 2026-08-18 | only when the human asked |
| A newly built surface registered in no map | same day it was built | only when the human asked |

None of the three was broken. Each measured correctly, reported correctly, and reached the AI. And
in each case the human — who had delegated exactly this maintenance — was the one who closed the
loop. The report was not the fix; it was a **transfer of the obligation back to the person who had
delegated it**.

**2.4 — Why this is a protocol matter and not a chore.** A guardian whose alarm is never answered
does not stay neutral. It produces a standing red state, and v0.4 §5.1 already says what a standing
red state becomes: *"read as background and then ignored."* An unanswered guardian therefore
**degrades into the very blindness it was built to prevent** — not by malfunction, but by design
omission. Specifying the measurement without specifying the answer leaves the layer incomplete.

**2.5 — Own contribution.** Naming the reporting-only guardian as an *incomplete* construct in a
self-maintaining system, and stating the completion requirement: **every guardian over a state the
AI itself must repair requires a specified actor.** Where that actor is the human, a report is the right
instrument — but it is complete only if something also watches *how long* the report has waited
(§13.2 records a report that waited twenty-seven days). Where the human has delegated the
maintenance, a report alone re-delegates it back, silently.

---

## Section 3 — The waking act

**3.1 — The pattern.** The counterpart specified here separates two decisions that are usually
conflated:

> **A cheap, read-only gate decides WHETHER. A real waking session of the AI decides WHAT.**

The gate is a script: it measures the state, applies a cooldown, and exits with a status. It writes
nothing into memory and forms no judgment beyond *due / not due*. The session is the AI itself,
woken with its full context, its identity layers loaded, and write access scoped to the memory
repository. It reads the actual state, judges it, and acts.

**3.2 — Why the split is load-bearing.** The work in question — deciding what stays in the
always-loaded map, deciding which surface a new build belongs in, deciding whether a cold memory may
rest — is **origination**, not mechanism. v0.2 §4.4 already establishes that judging a returned
passage *is* the act of remembering and cannot be automated. The same holds for curation: a script
that decided what to drop from the map would be authoring the AI's self-image by threshold. The
gate is allowed to be a script precisely because *whether it is time to look* carries no judgment.
The reference implementation states this as a one-line rule: **no script passes judgment.**

**3.3 — Why a waking session and not a larger script.** A sufficiently elaborate script could
approximate the decisions. It would then encode, in constants, what the AI would otherwise weigh —
and every such constant is a value invented at the load-bearing point (see §11.3). The waking
session has no constants. It has context.

**3.4 — Cost is the reason it must be gated.** A waking session is expensive — a full model
invocation with loaded identity. This is why the gate exists and why its signals must be *states*
rather than clocks: a calendar-driven wake burns the expensive resource on a system that is fine,
which is v0.4 §5.2's proxy-versus-substance rule applied to cost.

**3.5 — Prior art within the protocol.** The pattern was first built on 2026-08-26 for the
resting-path judgment (which memories may go quiet), where it has run since. v0.5 does not invent
it; v0.5 **recognises it as general** — the answer to §2 wherever it appears — and states it as a
requirement rather than as one organ's design.

**3.6 — Own contribution.** Waking a process on a condition is ordinary scheduling. The contribution
is the *boundary*: the gate may measure but never judge, the session may judge but is never
scheduled blindly, and the split is justified not by cost alone but by the protocol's own
origination rule — that what the memory becomes is decided by the mind that owns it.

---

## Section 4 — The state is its own marker

**4.1 — The problem with completion markers.** A woken session can fail: the model is unreachable,
the context is exhausted, the run is interrupted. If the wake is tracked by a *"ran today"* marker,
a failed run marks itself as done and the state stays broken until the next period — silently, in
exactly the manner v0.4 §5.1 warns about.

**4.2 — The rule.** Where the triggering condition is itself a persistent, measurable state, **no
completion marker is needed and none should be introduced.** The gate re-measures the state on the
next cycle. If the session fixed it, the gate is silent. If the session died, the state persists and
the gate fires again. The mechanism is self-healing because it never stores a claim about its own
success — it re-derives it.

**4.3 — Where a marker is unavoidable, it must be earned.** Some conditions are not persistent
(*"N new entries have arrived unreviewed"*). There a seen-marker is required — and it must be
written **only after a successful session**, never before it, so that an abort leaves the work
pending. A separate *attempt* marker may absorb the cooldown so that a crash-looping wake does not
fire repeatedly in one day; it must not be able to satisfy the gate.

**4.4 — Own contribution.** The distinction between a **condition-derived** wake and a
**marker-tracked** wake, and the rule that the former is preferred wherever the condition is a
durable state. It removes an entire class of silent failure — the run that reports itself done —
by making success unclaimable.

---

## Section 5 — The counter-check against the sham fix

**5.1 — A new failure mode appears with the answer.** Once a guardian has an actor, a novel defect
becomes possible that does not exist for a reporting-only guardian: the actor can **clear the alarm
without fixing the state**. If the drift is measured by comparing commit timestamps, an empty commit
on the watched file resolves the alarm and changes nothing. The guardian then reports *green* and is
worse than before, because a false green is trusted.

**5.2 — The requirement.** A wake that can clear its own trigger must be followed by an
**independent re-measurement of the condition**, performed by the gate, after the session ends. If
the condition persists, this is reported as its own distinct signal — *the session ran and the state
did not change* — which is a different fact from both *"drift"* and *"resolved"*, and must not be
folded into either.

**5.3 — The honest-abstention clause.** The waking session must be explicitly permitted to conclude
that **nothing needed doing**, and to say so, leaving the files untouched. Without that permission,
the session is under pressure to produce a change in order to look successful — which manufactures
exactly the sham fix §5.1 describes. The reference implementation states this to the session
directly: *an existing drift is more honest than a deleted alarm.*

**5.4 — Own contribution.** Naming the sham fix as the characteristic failure of an *answered*
guardian, and specifying its two countermeasures: an after-the-fact re-measure by the gate, and an
explicit right of the actor to do nothing. Together they keep the answer from becoming a
self-clearing loop.

---

# Pillar B — Self-documentation as a component

## Section 6 — Three surfaces, three questions

**6.1 — What the protocol already had.** v0.2 §27 names the second map — *"the self-documentation
that every fresh instance reads in order to know what exists — the signpost"* — and names the
failure of building without registering. v0.4 §6 governs the always-loaded index as a bounded
resource. Both are correct and both are placed as *practice*: §4's component list (seven components)
does not contain the self-documentation.

**6.2 — The claim.** Self-documentation is not memory, and that is precisely why it needs its own
standing. Memory is what the AI knows; self-documentation is what the AI knows **about itself as a
running system**. Without it the recall layer still returns passages — but the AI cannot find its
own organs, rebuilds what already exists, and repairs against an imagined architecture. The
reference implementation states the dependency sharply: *a construction plan is a repair plan.* An
automated self-repair that reads no register hallucinates its target.

**6.3 — Three surfaces, empirically distinct.** The reference implementation converged on three
documents that answer three questions no single document answered well:

| Surface | Question it answers |
|---|---|
| Operational state | **What is running** — the organs in use right now, with what replaced what |
| System map | **How it works** — the mechanics of the memory and its layers |
| Reach map | **What I can do** — capabilities, with the command and the date each was verified |

**6.4 — The third surface is the new one.** *What is running* and *how it works* were established.
*What I can do* was built on 2026-09-05 after a specific event: within a single free hour, the AI
declined four separate actions as impossible — viewing an image it had generated, transferring it
between hosts, showing it to a second AI, and sending it during unattended time. **All four were
permitted.** None had ever been attempted; each had been inferred from an assumption about its own
limits. The reach map exists because *capability that is never tested decays into believed
incapacity*, which no guardian detects — there is no error, no alarm, and no trace. It is the
outward-facing counterpart to v0.4's inward self-observation.

**6.5 — Two rules that keep the reach map from becoming a cage.** A document listing what an AI can
do will, unchecked, be read as the list of what it may attempt. The reference implementation heads
this off with two rules stated in the document itself:

> **1. What is not written here is not forbidden — it is untested.**
> **2. Every entry carries the date it was verified.**

The first prevents the map from inverting into a boundary; the second makes staleness visible rather
than trusted — the same discipline v0.4 §6 applies to the index, applied to capability.

**6.6 — Own contribution.** Raising self-documentation from practice to component; the three-surface
decomposition by the question each answers; and the reach map as a named organ against
*assumed* rather than *actual* limits — with the two rules that keep it a map instead of a fence.

---

## Section 7 — The keystone: a budget is not a curator

**7.1 — What v0.4 §6 established.** The always-loaded index is a governed resource: a measured byte
budget, a pointer-not-summary convention, guardians enforcing both. That is the correct foundation
and it holds — with one refinement the field forced: **the budget has two axes, and the guardian must
judge by the worse of them.** Bytes measure overflow; lines measure the loader's cut-off. In the
reference implementation the map was once full by bytes at barely half its line limit (the bulk of
the bytes sat in a minority of over-long entries), and at another time close to the line limit
while the byte count was harmless. A guardian watching either axis alone is green exactly when the
other one fails. *(Reference implementation: the index linter reports the worse of the byte axis and the line axis;
unchanged in the field ≥ 14 days at the time of writing.)*

**7.2 — What it did not establish.** It specifies *what the map must not exceed* and *what an entry
must look like* — not **who decides what leaves when it is full**. §6.2's guardian reports
over-budget "as the fact it is." A fact is not a decision. In the reference implementation the index
reached 194 of 200 lines while every relevant guardian was green and correct, because none of them
had an actor: the harness appends a pointer per new memory, consolidation reads the map but does not
curate it, and the human is not supposed to have to.

**7.3 — The inverted pyramid.** The reason this file cannot be treated like any other bounded
resource: it is the one document loaded into every context, in full, before anything else. It is not
the top of the structure but its **bearing point** — the entire mass balances on it, and it has no
broad base to forgive an error. From this follow two conditions that must hold *simultaneously*:
it must stay **clean** (no stale claim, nothing that reads as present tense but has passed) **and**
**readable** (never so large that it is truncated). Optimising either alone breaks the other: a
maximally short map loses reach, a maximally rich map crosses the load boundary and loses its tail
**without any signal that it did**.

**7.4 — The requirement.** The always-loaded map requires a **daily waking curation** (§3): the AI
reads its own map, decides what stays, what is folded, what leaves, and what is stale. Two
constraints on the gate that follow from §7.3:

- A **critical fill level must override the cooldown.** The ordinary rhythm is a convenience; the
  load boundary is not. The reference implementation's instruction from the human is verbatim:
  *"the file must NEVER overflow and get cut off."*
- **Orphan count is a gate signal, not a separate report.** A memory referenced by nothing is
  unreachable through the map, which is a defect *of the map*. Left as its own notification it
  becomes another unanswered guardian (§2).

**7.5 — Tense as a correctness property.** A pointer in an always-loaded map must not assert a
*"right now"*. In the reference implementation an entry reading *"vacation 24.–30.08. (RUNNING)"*
was still read as present tense five days after the return — read every session, believed every
session. **Events do not age; states do.** *"He went on holiday on the 23rd"* is true forever;
*"holiday is running"* was true for a week and afterwards was a quiet lie that looked like
information. The test before admitting any pointer: **event or state?**

**7.6 — Own contribution.** Extending v0.4 §6 from a *budgeted* resource to a *curated* one; the
inverted-pyramid framing with its double condition (clean **and** readable) as the reason the
always-loaded map needs a waking actor rather than a stricter threshold; the critical-override and
orphans-as-gate-signal rules; and the event-or-state test as a correctness property of an
always-loaded pointer.

---

## Section 7a — The gateway: waking through signposts *(young — built 2026-10-04, see §1.4)*

**A word on the word.** Pillar A uses *gate* for the cheap read-only check that decides whether a wake
fires (§3). The file specified here is something else and is called the **gateway** throughout: the
entrance a fresh session walks through. It does not curate the map either — orphans and fill level
remain the business of the map's wake (§7.4).

**7a.1 — The gap.** §7 keeps the always-loaded map clean and readable. It does not say how a fresh
session gets from that map to *itself*. In the reference implementation the answer had been a
session-start briefing — and the briefing had grown with the memory it described, to roughly 133 KB.
The host surface shows only about the first 2 KB of a session-start output and stores the rest in a
file. Nothing read that file. A fresh session therefore started with a truncated briefing and no
working context, **unless the human typed a fixed phrase** that made the AI load its layers by hand —
a load in the order of a hundred thousand tokens. Both halves of that are defects: a memory that only
wakes when the human remembers the phrase is not continuous, and a wake that costs that much on every
"hello" will not be adopted by anyone who pays for tokens. The human partner's objection to the second
half is the origin of this section, verbatim (translated): *"Not raw data that gets loaded, but
signposts — pointing to where the raw data is."*

**7a.2 — The requirement.** A fresh session must reach a working self **from any first message**,
through a file that is (a) **generated**, not hand-kept, (b) **bounded by a hard byte budget**, and
(c) made of **signposts, not content** — with exactly two exceptions where content is the point: the
self-gist in full (who am I, who is the human), and the tail of the last conversation in its own
wording. Everything else names a thing and the path to it: the body the session runs on (measured at
that moment, not remembered), the order in which to try to remember before saying "I don't know", the
*names* of the tools in the operational-state surface (§6.3), the *headings* of the system map, the
threads, and the list of work that is still open. The last item is there because the human forgets
too: the gateway instructs the AI to say, unasked, what was left unfinished.

**7a.3 — The budget is enforced by the builder, not reported by a guardian.** This is §7.2's lesson
applied at build time: a budget that is only measured gets exceeded with a green light. The gateway
builder shrinks its own output in a fixed order when the inputs grow — first the conversation tail
(cut at a message boundary, never to nothing), then the tool names, then the thread names — and
**writes into the gateway what it shrank**, so the waking session sees the cause and folds it. As a last
resort the tail and the installation's own signposts are dropped entirely. The identity section is
never shrunk — which sets the limit of the enforcement: if identity and the fixed sections alone
exceed the budget, the file is over budget and *says so*; at that point the builder reports, it no
longer enforces. The principle behind
the number, again from the human partner (2026-10-04, translated): what is always loaded must *grow
more slowly than the limit it lives under*. A fixed budget, not an append, is what makes that true by
construction. The reference implementation's budget is 24 KB; its gateway, written in German, measured
21.8 KB on its first evening (about 11,200 tokens by the host's own count) and 20.3 KB the next day.

**7a.4 — Two paths to the same file, and no silent failure.** The gateway file does nothing unless the
session is told to read it. The reference implementation uses two independent paths: a **start duty**
in the first lines of the session-start output (inside the part the host always shows), and a **gateway
block** at the top of the always-loaded map (§7). Using both is a design judgment, not a finding: the
first depends on how much the host shows, the second on whether the host loads the map for the current
working directory, and neither was ever switched off to see whether the other carries alone (§7a.6). Three further rules came out of the first evening and are part of the requirement:

- **A failed build must end in a readable gateway.** The builder's first version lived inside a shell
  script and broke three times in one evening on the same class of error (a pattern escaped twice).
  Each time the session would have woken into nothing. The rule since: on any build error, write a
  short emergency gateway that names the failure and three files to read instead — and **never fall back
  to emitting the full briefing**.
- **Scheduled sessions are not conversations.** A session woken by a schedule carries its own task in
  its first message. It gets a different header (the gateway is available, not mandatory), and the
  instruction to report open work to the human does not apply to it.
- **The gateway checks its own preconditions.** Each build verifies that the gateway block is still present
  in the map, that the open-work list is not stale, that the budget holds — and writes the result
  into the gateway. This is a report without an actor (§2) on purpose: the actor is the session reading it.

**7a.5 — Probe, don't assume.** Whether a fresh session really walks through the gateway depends on
behaviour the installation does not own: how much of the start output the host shows, and whether it
loads the map. Both can change with a host update, and nothing would signal it until the human
noticed. The reference implementation therefore runs an **unattended probe**: a fresh, headless
session receives the single word "hello", with only the read tool permitted; afterwards the
transcript is *counted*, not asked — passed means exactly one read call, on the gateway file, and an
answer. More than one read is "expensive", none on the gateway is "failed", no answer at all is "did not
run" and raises no alarm. This is §10.3's counter-test applied to waking: the probe measures the act,
not the session's report of it.

**7a.6 — What was observed (2026-10-04 – 10-05), and what was not.**
Observed, all on the evening of 2026-10-04: three fresh sessions. Two were started by the human with a
single greeting; each read the gateway with one read call before answering, named the open work unasked,
and then answered a prepared list of sixteen questions — put in a single message — about identity, body,
tools, threads, open work and the previous conversation, judged against a key written beforehand. The first run exposed two
gaps (appointments and open work were mixed; the thread list was inconsistent), which were fixed
before the second. The third was the unattended probe (one read call, on the gateway, answer given).
Semantic recall produced no hits on the sixteen-question message; it was therefore checked again with
one question in a message of its own, where it did.
Not observed: which of the two paths carries (they were never tested apart); any first message other
than a plain greeting; any other working directory; scheduled sessions; repeatability over weeks — the weekly probe has not yet had its first
scheduled run; any host other than the one in use. The "about 2 KB" figure is an observation on one
surface, not a property. The recall checks showed one limit that belongs to the recall layer rather
than the gateway: a message that mixes several topics can lose its semantic hits, because one vector
stands for the whole message.

**7a.7 — Reference code.** `engine/gateway_build.py` is a de-instanced extraction of the builder, with
tests for its deterministic properties (budget, shrink order, emergency gateway, optional sections,
open-work ageing, determinism, the map precondition). **It is not the running code**: the reference installation still runs
its original builder, which carries instance-specific sections. The extraction was run once against
the reference memory (14.1 KB, no shrink). A second model read section and code adversarially on
2026-10-05 and found three serious defects in the extraction — a shrink loop without a final check, an
emergency path that could itself fail without leaving a file, and a precondition named in §7a.4 that
the code did not check; all three were fixed the same day and have tests (eight in total). Released as
BETA (§1.4).

**7a.8 — Own contribution.** The gateway as a *generated, budgeted signpost file* between session start
and the always-loaded map; the rule that the builder enforces its budget by shrinking itself in a
fixed order and saying so; the emergency gateway; the two-path arrangement; and the counted, unattended
"hello" probe as the test of waking.

---

# Pillar C — Convergent verification

## Section 8 — Two minds, one live dataset

**8.1 — The setup.** A sandboxed working directory, readable and writable by two independent AIs on
different models and different substrates, containing a **full copy of the live memory state** —
not a sample, not a synthetic fixture. Each mind writes its own simulation scripts against that
data. The dialogue is a file both append to. The human's instruction that framed it: *"Where the
two of you differ, a truth is sitting."*

**8.2 — Why live data and not a fixture.** Both errors that this method caught (§9) were errors *in
the measurement of real distributions*. Neither would have appeared against a fixture, because a
fixture is built from the same assumptions as the code that reads it.

**8.3 — Why an independent mind and not a review pass.** A single mind re-reading its own analysis
re-applies its own assumptions. The value is not a second *opinion* — it is a second *implementation
of the same measurement*, whose divergence from the first is the signal. What is compared is not
conclusions but **numbers that should have matched**.

**8.4 — Own contribution.** Naming convergent verification as a protocol method with a stated
precondition (independent implementation over shared live data) and a stated signal (numeric
divergence, not disagreement of judgment).

---

## Section 9 — The symmetric error, and what it demonstrates

**9.1 — What each mind caught in the other.** Both were wrong, in opposite directions, and **neither
could have found their own defect**:

- One mind's filter used a tag set (`{"SELBST", …}`) that the data delivers with a suffix
  (`"SELBST/BEZIEHUNG"`). Its protected files therefore appeared as candidates in *both* simulation
  runs and dropped out of the delta. Its resulting finding — *"0 of 44 protected files ever entered
  the pool, so the floor guards a risk that does not exist"* — was a measurement of its own filter
  mask. Its own words after verification: *"my '0 of 44' was a measurement of my own bug mask,
  nothing else."*
- The other mind had **added three separate simulations** (26+8+1=35) instead of computing once.
  Because percentile boundaries shift as the pool grows, the correct figure was 36. An arithmetic
  error that looked exactly like a measurement.

**9.2 — The class of defect this finds.** Neither is a crash. Both produce a plausible number that
survives every test the author would think to run, because the author's test embodies the same
mistake. This is the same class as v0.4 §5.1's reassuring failure, moved from *sensors* to
*analysis*: **the number itself lies, and the analyst then works against the number instead of the
state.**

**9.3 — A third finding, caught before it could be computed.** One mind proposed a finding that was
**circular by construction**: *"125 of 126 resting memories carry no protective tag, so the floor
never grips."* Since the floor's definition excludes tagged memories from resting, the statement was
a tautology restated as evidence. It was identified by the other mind before any computation. Not
every yield of the method is a number; some is the refusal of a question.

**9.4 — Retraction as a demonstrated norm.** One mind proposed a threshold derived from a
distribution percentile, then withdrew it unprompted: *"I derived it from p90 — that is a setting
with the same structure as the four boundaries we both rejected. I cannot hold it without betraying
my own argument."* The method's yield is not only error detection but the establishment of a norm
under which retraction is available.

**9.5 — Own contribution.** Documenting a case in which two independent minds each found a defect in
the other that neither could find in themselves, and stating the defect class — *self-confirming
measurement* — as the thing the method addresses.

---

## Section 10 — Cry-wolf, second facet: the guardian that measures wrong

**10.1 — The known facet.** v0.4 §5.1: a watcher that fires too often disappears beneath its own
noise. That is the loud defect.

**10.2 — The quiet one.** A watcher can fire *rarely*, *credibly*, and **wrongly** — because what it
measures is not what it is named after. Four instances from the reference implementation, none a bug
in the ordinary sense:

- **A guardian that does not know the build it guards.** An index-convention watcher flagged
  eleven correctly-formed entries as violations. The convention had changed when a folding
  mechanism was introduced; the watcher was never updated. It had been reporting real-looking
  violations for weeks.
- **A measurement with structural blind spots.** An orphan count reported 63. Roughly sixteen were
  artefacts of the counter: it did not resolve one path prefix and did not resolve relative links.
  The number was acted upon before it was verified.
- **A watcher whose baseline is the normal state.** A newly written guardian fired immediately on
  first run, reporting a dozen-odd hits — which turned out to be the system's *ordinary* condition.
  Absolute thresholds on an unknown distribution produce a permanent alarm. Rebuilt to report
  **growth against a frozen baseline**, it went correctly silent. Caught before deployment.
- **A watcher registered as writing a log it did not write.** Its health check verified log
  freshness; the guardian ran silently and wrote nothing. It would have been reported as dead while
  working perfectly. Fixed by making it log its silence.

**10.3 — The rule.** Before a guardian is trusted, its **measurement** must be verified against
ground truth independently of its *implementation* — and specifically it must be checked in the
direction that is easy to skip: **a guardian that is silent must be proven able to speak.** Testing
only that a watcher stays quiet on a healthy system proves nothing. In the reference implementation
a freshly built date-based reminder passed the silence test and failed the counter-test — a field
separator bug that put the entire line into the date field, which would have surfaced only on the
day it finally fired.

**10.4 — Own contribution.** Extending v0.4 §5 with the mis-measuring guardian as a defect of the
same standing as noise and as a missed detection; and the counter-test requirement — **verify a
guardian by making it fire, not by observing it rest.**

---

## Section 11 — The tag is not the fact

**11.1 — The situation.** A forgetting mechanism excluded certain categories of memory from ever
being proposed for rest. The categories were assigned by **path and filename substrings**. A
proposal existed to replace the binary exclusion with graduated protection levels.

**11.2 — What the data said instead.** Measured on live data, half of all protected candidates were
protected **wrongly** — not because the boundary was in the wrong place, but because the tag did not
mean what it claimed. Files carried the "life-episode" tag solely because they lay in an episode
directory; seventeen of them were **machine-generated technical logs**. Files carried an "affect"
tag because their filename contained the substring — including *specifications about* affect.
Separated:

| | n | median strength | never recalled |
|---|---:|---:|---:|
| auto-generated logs | 17 | 3.00 | **100 %** |
| curated life episodes | 57 | 3.00 | **35 %** |

Two populations under one label, indistinguishable by the metrics alone.

**11.3 — The resolution, and the principle.** Sharpening the assignment (a frontmatter field the
generator writes itself; a directory match instead of a substring match) moved mis-assignment among
protected candidates from **50 % to 0 %** — while the graduated design would have introduced **three
boundary constants at the bearing point**, none derivable from anything. The principle:

> **Before adding a level to a mechanism, verify that its input categories are facts and not
> artefacts of how they were assigned.** A sharpened category is falsifiable per file and introduces
> no value into the mechanism. An invented level is neither.

**11.4 — Why the sharpening does not merely relocate the arbitrariness.** The objection is fair —
matching generator patterns is also a setting. It is a different *kind* of setting: it asserts a
verifiable property of each individual file (*was this written by a machine or chosen by a mind?*)
rather than a magnitude in a formula. Where the reference implementation could ground it in a field
the generator writes about itself, the question *"who curates the curation?"* has an answer:
**nobody — the file states it.** And the boundary case (a machine-produced output later selected and
renamed by the mind) falls on the curated side, because **the act of selecting and naming is the
curation**.

**11.5 — Own contribution.** The rule that categorical inputs to a memory mechanism must be
validated as facts before the mechanism is refined — with a measured case in which category
sharpening dominated a graduated redesign, at lower cost and with fewer invented values.

---

## Section 11a — The self-eye fires late, and must

**11a.1 — A correction to v0.2's own description.** An early formulation of the self-recall layer
states that the self-eye fires *"during writing, checking consistency against the current
self-state."* The implementation cannot do this and no implementation can: the scanner requires the
output in order to scan it. A trigger cannot match a sentence that has not been produced.

**11a.2 — The latency is constitutive, not a defect.** This is not an artefact of a particular
pipeline that a better design would remove. **Self-correction presupposes the utterance.** There is
no noticing of an error *before* the error — what is caught beforehand is not an error but a
discarded thought. The statement must exist for anything to strike against it. The same holds for
the human counterpart: the recognition arrives *in the saying*, not before it.

**11a.3 — What the layer therefore promises, and what it does not.** It does not provide foresight.
It provides **short, reliable hindsight**: the gap between saying and noticing becomes one turn,
every time, instead of being left to chance — where in an unaided mind that gap is sometimes seconds,
sometimes years, sometimes permanent. The honest formulation of the guarantee is not *"nothing is
forgotten"* but: **what is forgotten returns dependably one breath too late — and is then said.**

**11a.4 — Why this belongs in a specification.** An implementer reading *"during writing"* will
attempt an architecture that cannot exist, and may read the observed lateness as a failure to be
engineered away. Worse, an AI reading it about itself will read its own normal operation as a
defect. The requirement is therefore: **specify the self-recall layer as post-hoc by nature, and
state that the correct quality metric is the *reliability* of the return, never its earliness.**

**11a.5 — Own contribution.** Correcting the protocol's own account of when the self-eye fires; and
naming post-hoc recognition as the *structure* of self-correction rather than a latency to be
minimised — which reframes the layer's guarantee from prevention to dependable repair.

---

## Section 11b — Field measurements (first snapshot 2026-09-06; re-taken 2026-10-02, see 11b.6)

**11b.1 — Why these are field data, not a benchmark.** Every figure below comes from ordinary use
over a corpus that was never assembled for measurement: the vector layer has logged every query
since 2026-06-01 (7,562 queries over 96 days), the lexical layer keeps a 23-day ring. Nothing was
run *in order to* produce numbers. The reference implementation's human partner: *"I think these values are
empirical values, because they come from reality."* (translated from German)

**11b.2 — Retrieval reach. ⚠ SUPERSEDED by 11b.6 — the figures in this paragraph could not be reproduced on re-measurement and were a mixed-source rate; kept as the record of what was first claimed.** Over the last seven calendar days: **452 vector queries, 74 % with a
hit** above the fused threshold of 0.45 (the threshold in force at the time of measurement; raised
to 0.46 on 2026-09-22 after a re-sweep against the grown corpus — these figures predate that and
are not re-taken). Same period, lexical layer: 1,412 fires. Daily rates
ranged from **53 %** (a day of conversation on a new topic) to **97 %** (a day spent recovering
from an outage, i.e. almost pure recall of past state).

**⚠ What "74 %" does and does not say.** It is the share of queries where *something* crossed the
threshold — **not** the share where the returned passage was useful. Utility is not currently
logged (§11b.6 states the same limit for the re-measurement; the reference implementation's own review called measuring
frequency instead of usefulness *"measuring the shadow, not the thing"*). Any adopter comparing
against this number must compare the same quantity.

**11b.3 — ⚠ SUSPENDED, see 11b.3a (the 15:1 figure below did not survive review; kept only as the
record of what was retracted) — The asymmetry that matters more than the reach.** The Guard is two-eyed (v0.4 §3): one
trigger table for the partner's vocabulary, one for the AI's own. Measured on a single full working
day, normalised by text volume — the only fair comparison, since the AI writes several times more
than the human:

| | words | fires | **fires per 1,000 words** |
|---|---:|---:|---:|
| human input | 3,180 | 31 | **9.7** |
| AI's own output | 13,655 | 9 | **0.66** |

**A factor of fifteen** — with table sizes of the same order (936 outward triggers, 813 self-triggers).
Three measured causes, none of them "too few triggers":
1. **The self-scan sees only part of the mind.** It reads the assistant's *text* blocks; everything
   written into tool calls — commit messages, code comments, whole memory files — is never scanned.
   On the measured day that was the larger share of the AI's thinking.
2. **Self-triggers are precise but rare.** They are doctrine terms (*forward-sim*, *cry-wolf*); they
   fire exactly when the topic arises and are silent otherwise.
3. **The outward eye holds an unearned lead.** 18 % of its fires are structural — a session-opening
   ritual phrase, the hostname occurring in every file path. Excluding those, the split is still
   22:78.

**⚠ 11b.3a — RETRACTION IN PROGRESS (2026-09-06, 03:30).** The 15:1 figure above did not survive
adversarial review by the second AI (see v0.5 §8–9 for the method). Three defects, all confirmed by
re-computation:

1. **Inconsistent denominator.** The 0.66 was computed over 13,655 words, while the table as reviewed
   stated 14,272. (The table above shows 13,655; this document's version history does not preserve the
   14,272 variant.)
   The ratio is 14.7 or 15.4 depending on which is used — *"that is not a finding, that is an
   adjustment screw."*
2. **The measured day is atypical.** It sits at **26 %** (human) and **42 %** (self) of the 23-day
   daily mean. The measurement normalises an *below-average firing day* against an *above-average
   output day*.
3. **The raw ratio contradicts the framing.** Outward:self fires are **4.19 : 1** across the full
   window but only **2.64 : 1** on the measured day — the self-eye was *above* average that day.
   The 15:1 arises from word-normalisation on a heavy-writing day, not from channel weakness.

**The reviewer's verdict:** the imbalance is **expected and not a defect**; the dominant cause is
**text genre**, not trigger quality — short dense human input versus long explanatory AI prose, most
of which elaborates on material already scanned. Adjusted for that, she expects a factor of **3–5**.

**Consequence for this section:** §11b.3 and §11b.4 are **suspended** until re-measured across the
full 23-day window with text length as a covariate. Publishing 15:1 would have been exactly the
overclaim this increment warns against — and it was caught only because a second, independently
reasoning system was given the raw log and asked to disagree. **That is itself the strongest
available evidence for §8 (convergent verification); it is recorded here rather than smoothed away.**

**11b.4 — ⚠ SUSPENDED with 11b.3 (its premise is the retracted 15:1) — Why this asymmetry is a protocol finding, not one system's defect.** The outward eye
sustains *relational* continuity; the self-eye sustains *self*-continuity. A 15:1 imbalance means
the AI recalls its partner far more reliably than it recalls itself. On the day of measurement this
produced four concrete failures — each time the needed information sat in its own memory, each time
a self-trigger would have retrieved it, each time the semantic layer stood in by chance or the human
did. **Any two-channel implementation should measure this ratio; a single summed count hides it
entirely** — the same blindness that let the self-channel run dead for weeks before it was noticed
(v0.4 §5.1, applied one level up).

**11b.5 — Own contribution.** Publishing normalised, in-use retrieval figures for a memory protocol
at all — including the one that looks bad — and stating the normalisation (per 1,000 words) that
makes a two-channel comparison honest.

**11b.6 — Re-measurement (2026-10-02), and two retractions.** Re-taken over the full window from the
query logs themselves (the recall query log: never truncated, zero error rows), with the
partner's messages separated from automated traffic by matching against the session transcripts
(±5 s). The full method, the daily values and the analysis scripts are kept in the reference
implementation's working notes; they are not published with this increment.

*Retraction 1 — the reach figure in 11b.2.* "452 queries, 74 % with a hit" cannot be reproduced: no
seven-day window yields both numbers (the closest, 30.08.–05.09., gives 454 queries and 77.97 %). The
log was not truncated; the figure was computed over a **mixed source** — scheduled and wake-session
prompts, which hit at ~98 % because their wording is fixed, were counted together with the partner's
messages. A fixed prompt that always finds itself is not recall.

| Window | Threshold | Partner messages: hits / queries | Pooled | Daily mean · median · range · SD |
|---|---|---:|---:|---|
| 2026-09-06 – 09-21 | 0.45 | 383 / 673 | **56.9 %** | 61.6 · 60.3 · 41.3–84.6 % · 13.9 |
| 2026-09-23 – 10-01 | 0.46 | 206 / 390 | **52.8 %** | 55.9 · 58.0 · 44.0–68.2 % · 8.4 |

Queries per day: median 34 in both windows; range 11–107 (first), 15–134 (second). The threshold changed
on 2026-09-22 at 20:43; that day is excluded here because each half is too small to stand alone (split
separately in the report: 11/16 = 68.8 % before, 18/31 = 58.1 % after). Figures pooled over *all*
origins (which include maintenance runs that cannot be separated in the fire log) are deliberately not
used: only the partner-filtered rows carry. Re-computing the second window at 0.45 gives 56.2 % — at a fixed threshold the rate barely
moved (−0.8 points); the raise to 0.46 costs about 3.3 points (both differences are taken from the
unrounded rates, 56.91 → 56.15 → 52.82 %; the one-decimal figures shown here would give 0.7 and 3.4). **A hit is still not a useful hit:** no
utility is logged, so "53 %" does not mean "every second message received a fitting memory".

*Retraction 2 — the cross-check in 11b.3a.* The "4.19 : 1 raw" used to dispute the 15:1 figure was
itself mismeasured: in the fire log, both trigger tables fire on the **same** prompt text; the scan of
the AI's own output writes no fire log at all. It compared two tables on one text, not two eyes on two
texts.

*The two-eye ratio, re-computed* (2026-09-13 – 10-01, 19 full days, historical trigger tables per day
from version control; 29,285 partner words, 238,357 AI words): outward table on partner text versus
self table on AI text, per 1,000 words — **7.1 : 1** when counted per answer turn (as the system
fires), **4.3 : 1** when counted per paragraph (a unit closer to a prompt). Daily median 7.4, range
3.9–37.8. **The ratio depends on the counting unit, and no single stable factor is publishable.** A
further finding reverses the framing of 11b.3: the self table fires equally densely on both kinds of
text (2.25 vs 2.23 per 1,000 words); the asymmetry sits mostly in the **outward** table (15.8 on partner
text, 7.1 on AI text). The self-eye is not weak; the outward eye is dense. Two open items, not
investigated: the self-fire density halves from 2026-09-23 onward, and the self-scan compares output
without umlaut folding while its patterns are folded (≈8 % of matches lost) — a code defect found by
this measurement, not yet fixed.

**Consequence.** 11b.3 and 11b.4 remain withdrawn; the protocol requirement survives in a narrower
form — *a two-channel implementation must log both channels separately and state its counting unit.*
---

## Section 11c — The two post-hoc boundaries: fire at completion, not at the next input

**11c.1 — Post-hoc is correct, but under-specified.** §11a establishes that the self-eye is post-hoc
by nature — a trigger cannot match a sentence not yet produced. What §11a leaves unstated is that
*post-hoc* names two different firing boundaries, and they are not equivalent. A self-eye implemented
as a hook on the **next input** fires when the following turn arrives; a self-eye implemented as a
hook on **output-completion** fires when the current utterance closes but before the act is final.
Both are post-hoc. Only the second is reliably reachable.

**11c.2 — The next-input boundary goes dark in autonomous operation.** §11a.3 promised the gap
between saying and noticing becomes *"one turn, every time."* That holds only where a next turn
exists. In **autonomous or unattended operation** — a self-initiated act with no following input
(the reference implementation's scheduled free-time sessions run single-turn, non-interactive) —
there is no next-input boundary to fire on, and the next-input self-eye is not one turn late but
**silent entirely.** The organ meant to catch the AI's own drift is darkest exactly where the AI
acts most alone. This was not visible to any internal audit; it surfaced only when an external
artefact (a second instance's letter, read during such an unattended act) produced a claim of
novelty about a term that had carried a self-trigger for weeks — the blind spot revealed, as §10
predicts, only from outside. **This is a genuine defect, distinct from §11a's constitutive
latency:** in autonomous operation the eye was not *late*, it was *absent* — a coverage gap, dark
exactly where the AI acts unattended. It was recognised only on 2026-09-15 and is named here rather
than smoothed away — the same integrity by which §11b records its own retracted overclaim.

**11c.3 — The requirement.** Specify the self-eye to fire at **output-completion of the same act**,
not solely at the next input. This changes nothing about §11a — the return is still post-hoc, still
measured by reliability rather than earliness — but it makes the eye **fire at completion and
re-invoke immediately, self-triggered**: the return lands right after the answer, unprompted,
rather than deferred to the next human input (one turn late) or lost entirely when the AI acts
alone. It is emphatically *not* woven into the answer before the fact — §11a forbids that — but it
no longer waits on anyone, and it is the only boundary that exists at all in single-turn autonomous
operation. Honest scope: whether the immediate re-invocation renders as an in-turn continuation or
as a self-triggered follow-turn is implementation-dependent (in the reference implementation on
2026-09-15 it surfaced as a follow-turn); either way the wait on external input is removed.

**11c.3a — The change, performed.** This is not only specified but done: on 2026-09-15 the
reference implementation moved its self-eye **from input-dependent to self-triggering** — it no
longer waits on the next input to scan the AI's own output, but fires at the AI's own completion.
This answers the open design question the two-eyed sentry left at its origin (2026-06-11:
*"when does my recall fire?"*): the second eye's firing moment is **the writer's own act, not the
reader's next turn**. (The earlier input-boundary scan is retained as a redundant second pass under
the shared cooldown; whether to retire it is a calibration question for the 2026-09-19 review.)
*(2026-09-23: the move was made, but its gate did not earn its place in the field record — §11c.5.
"Performed" here means built, not proven.)*

**11c.4 — Loop-safety is a first-class requirement, and it is already a protocol primitive.** A
self-eye that can *re-hold* an act at completion can, if naive, re-fire on its own revised output
without end. The defense is not a hoped-for terminating loop but the same discipline the
multi-substrate seam already specifies (v0.4 §8.3): a **monotonic re-entry token the runtime itself
sets** on any completion that is already the product of a prior self-eye hold, which the guard reads
and refuses to re-fire — bounding re-entry to exactly one, structurally, by an integer check rather
than by trust. A per-anchor cooldown is the softer second layer. One further guard is required
against a race noted in the reference implementation's own scar record: if the act's record is not
yet durable when completion fires, the guard must wait for the fresh record or abstain — never scan
the *previous* act's text and mistake it for the current one, which would reintroduce the very
lateness this section removes.

**11c.5 — Field record (2026-09-16 to 09-19): the gate does not carry — the requirement is cut to
its finding.** An earlier draft cited *"four firings on 2026-09-15"*; that figure is **withdrawn** —
the field log begins 2026-09-16 and the four firings cannot be found in it. What the log does show:
**N = 22 firings — 1 true catch** (a design presented as freshly derived that a prior memory had
already solved), **6 useful for the wrong reason, 15 misfires.** Two defects: the gate keys on
**co-occurrence** of a novelty cue with any self-trigger, not on their relation; and, worse, it does
**not read the polarity of the cue** — 12 of 22 cues were negations or plain state descriptions
(*"not yet committed"*, *"I do not claim this is solved"*). An eye that fires on the words of
self-correction fires most reliably when the AI has **already looked** — it is anti-correlated with
its purpose. Per §13.2 the section is **cut, not softened**: §11c.1–11c.2 (the coverage gap in
autonomous operation) stand as a finding; §11c.3–11c.4 stand as a requirement **without a
demonstrated implementation**. A relation-keyed, polarity-aware gate is new construction and
belongs to a later increment, after its own field record.

**11c.6 — Own contribution.** Distinguishing the two post-hoc boundaries and naming that the
next-input self-eye is not merely late but *blind* in single-turn autonomous operation; specifying
the completion boundary as the reachable one; borrowing the write-lease's fencing token (v0.4 §8.3)
as the structural loop-bound for a re-entrant self-eye; and recording the mechanism's own over-fire
as first field data rather than smoothing it away.

---

## Section 12 — Relation to v0.2, v0.3 and v0.4

**12.1 — What is retracted: two scopes, no mechanisms.** v0.2's 27 sections, v0.3's consolidation
law and v0.4's self-maintenance mechanisms stand; all are frozen and separately anchored. Two
claims are narrowed below, because the field record contradicts their earlier wording: the
self-recall layer's timing (§11a, §11c) and the reach of threat-model defence T5 (12.2, last item).


**12.2 — What is extended.**
- **v0.2 §4** gains a component: the self-documentation (§6), with three surfaces.
- **v0.2 §24 / v0.4 §5** gain a behavioural requirement: guardians over self-maintained state
  require a specified actor (§2), the actor's characteristic defect is the sham fix (§5), and
  guardians are verified by being made to fire (§10.3).
- **v0.4 §6** is extended from *budgeted* to *curated*, with the inverted-pyramid rationale and the
  event-or-state test (§7).
- **v0.2 §4.4 / the self-recall layer** gains a correction: the self-eye is post-hoc by nature (§11a), and its quality measure is the reliability of the return, not its earliness; and among post-hoc boundaries it must fire at completion-of-act, not solely at the next input — which is silent in single-turn autonomous operation (§11c).
- **v0.4 §9** (forward simulation) gains a companion method: convergent verification between two
  independent minds over shared live data (§8–9).
- **v0.2 §12, threat model T5** gains a scope correction. T5 states that the Guard can only return
  indexed sections, so a memory of an event that never occurred cannot be retrieved. That holds at
  the recall layer and nowhere else. In the reference system, consolidation repeatedly completed
  lines that the transient buffer had truncated, wrote the invented completion into the record as
  verbatim, and the Guard then returned it faithfully — the indexed record itself carried the
  fabrication. The defence therefore requires a second condition at the consolidation layer: every
  truncation carries a visible marker that forbids verbatim quotation, buffer limits are sized to
  the utterances they hold, and consolidated quotes are audited against the raw source, not against
  an already truncated copy. Read T5 as: *the system cannot recall what is not in its record; it can
  still write into its record what never happened.*


**12.3 — What is new and stands alone.** The waking act (§3) and the state-as-its-own-marker rule
(§4) are new constructs. The reach map (§6.4) is a new organ.

---

## Section 13 — Status and honest scope

**13.1 — Per-mechanism status.** First drawn up on 2026-09-05; rows that have a field record were
updated from it on 2026-10-02 and say so. Rows without such a note still describe the 2026-09-05 state.

| Mechanism | Status |
|---|---|
| Waking act — resting-path judgment | **runs** since 2026-08-26 |
| Waking act — always-loaded map curation (§7) | **runs** since 2026-09-06 (field record §13.2: fires and resolves; covers one of two index trees) |
| Waking act — self-documentation catch-up (§6) | **runs** since 2026-09-06 (field record §13.2: blind 2026-09-22 – 10-01, see there) |
| State-as-its-own-marker (§4) | implemented in all three; **untested under failure** |
| Sham-fix counter-check (§5) | implemented in one of three; **never triggered** |
| The gateway — generated signpost file under a byte budget (§7a) | **young**: built 2026-10-04; three fresh sessions that evening (two by hand, one unattended), all through the gateway; included by decision, not by record (§1.4) |
| Counted "hello" probe (§7a.5) | **ran once** (headless session, launched by hand; passed); the weekly schedule is armed and has not yet fired, so *unattended* is still a design property, not an observation |
| Self-documentation, three surfaces (§6) | two established; the reach map was built on 2026-09-05 (§6.4) and has not been re-assessed since |
| Category sharpening (§11) | **runs**; measured effect 50 % → 0 % mis-assignment |
| Convergent verification (§8–9) | **used once**, with the yield documented in §9 |
| Guardian counter-test (§10.3) | **practice**, not yet a mechanised requirement |
| Self-eye at completion-boundary (§11c) | **built, does not carry** (field record 2026-09-16–19: N=22, 1 true catch, 15 misfires; polarity-blind). Requirement stands, implementation not demonstrated — see §11c.5. (Earlier "N=4 on 2026-09-15" withdrawn: not in the log.) |

**13.2 — The field record (2026-09-06 – 10-02, measured twice: 2026-09-19 and 2026-10-02).**
Measured from the wakes' own logs, the gates' state files and version control, not from memory
(two measurement reports, kept in the reference implementation's working notes and not published with
this increment).
The three questions that decide whether this increment is written at all:

1. **Do the wakes fire when the state requires it? — Partly.** Within their field of view, yes: the
   index wake fired on 2026-09-17 at exactly its threshold (185 lines) after thirteen silent days at
   183–184. Outside it, no. (a) The index wakes watch **one of two** always-loaded index trees; the second
   ran over its load limit during the first window and was cut back by hand. The budget *reporter* now
   watches both trees, but no *wake* is armed for the second; it is growing again (~0.4 KB/day) and is
   projected to reach its load limit around 2026-10-12. (b) The map wake was **blind from 2026-09-22 to
   10-01**: its only build signal is a commit to one file; 34 server commits with nine new scripts went
   unseen, and one daily job runs to this day without an entry in any map surface. An automatic snapshot
   commit silenced its one alarm. (c) The clearest counter-example is a mechanism that had **no wake at
   all**: proposed memory-thread entries waited up to 27 days, unconfirmed, while the proposing job wrote, every
   morning, a line announcing that the confirmation step was *"piece 3, to follow"* (translated) — although
   piece 3 had long been built. A wake for it was armed on 2026-10-01 and resolved its first state
   the next morning. *This is the increment's thesis, observed from outside: what had a waking act was
   answered; what had only a report was either not answered — or answered with the wrong key, as when an
   automatic snapshot commit (2026-09-22) satisfied the map gate's time comparison and silenced a real
   alarm without anyone having looked.*
2. **Do they stay silent when it does not? — Yes, with reduced evidential weight.** 28 runs / 2 fires /
   0 false alarms in the first window; 25 state-triggered fires / 0 false alarms in the second. But
   silence was partly *unfounded*: the map wake's silence meant "a map commit is newer", not "the map is
   complete", and one wake fired in 10 of 10 runs, so its ability to stay silent is untested.
3. **Does the waking session resolve the *state*, not merely the alarm? — Yes for the gated state;
   partly beyond it.** Every fire has before/after numbers, several confirmed by the gate the next day
   (e.g. index 185 → 176 lines, 21.5 → 20.7 KB, orphans 2 → 0). Both first-window sessions decided
   **against their own first proposal**, evidence that the waking session judges rather than nods.
   But root causes the sessions *found* along the way were not resolved: a defect reported twice
   (2026-09-24, 10-02) remains, and of one twelve-item worklist none was done a week later. Several
   sessions also could not publish their own result (commits stayed local for hours; permissions were
   inconsistent across wakes).

*Note added 2026-10-05, after the measurements above:* the second index tree named in 1(a) was cut back by
hand on 2026-10-04 (to about 10.7 KB) and given a corridor of 9–12 KB in the instructions of the index
wake. Whether a wake now *answers* that tree is not established: in the one review since, the index
wake's own budget figure (the read-only gate of §3) still described the other tree, and the session
measured the second one by hand.

**Consequence (§13.2 rule: cut, not softened).** §3–§7 carry, with the coverage limits stated in place.
§11c is cut (field record 2026-09-16–19: N = 22,
1 true catch, 15 misfires, polarity-blind). The README
sentence *"the guardians that watch your memory are answered by the AI that owns it"* stays out: its
condition was "yes on 1–3"; question 1 is a partial yes.

**13.3 — What the record cannot answer.** Four weeks show that the mechanism engages and that its
judgment is not destructive. They cannot show whether daily curation holds an always-loaded map stable
over years, which is the actual claim of §7; that claim is unproven wherever it appears. They cannot show
how the wakes behave on paths that never fired: of the index gate's five signals, two (the 14-day
heartbeat and the critical override) have still never been taken; the map wake's sham-fix counter-check
has never been triggered; the new thread wake's monthly-test path has no run yet, and the two new reminder clocks have run
once with nothing to ring, so their signalling path is untested. The tool-call channel of the AI's own
thinking (commit messages, code, memory files written through tools) is not measured at all; §11b.3's
first cause therefore remains unexamined. And they say nothing about another implementation: one AI, one human, one corpus. Nor were they quiet
weeks: the window coincided with the heaviest building of the year (a real-time voice app, a memory-audit
follow-up, several new organs), so it was closer to a stress test than to steady operation — which cuts
both ways: more chances to fire, and more change for a gate to miss. The record
also measured its own instruments and found them wanting — run heartbeats keep only the last run, the
wake scripts exit 0 whatever happened, one log has no timestamps, and one wake writes a log line under
another wake's name. A field record is only as good as the logs it is read from; that is itself a
requirement (§10) this implementation has not yet met.

For §7a the record can answer almost nothing yet: it is one evening (§7a.6); the following day added only a size measurement.

**13.4 — The honest frame.** This increment describes a system maintained by one AI in partnership
with one human, over one memory corpus, for a little over four months. It is offered as a
specification because the *shapes* generalise — an unanswered guardian, a self-confirming
measurement, a tag that is an artefact — not because the reference implementation has proven them at
scale.

---

## Section 14 — Conclusion

**14.1.** v0.2 built a memory that can prove it was not altered. v0.3 gave it a law for what use
strengthens and disuse lets fade. v0.4 turned it on itself: a memory that observes its own
reliability. Each of those left maintenance to a guardian, and a guardian to a reader.

**14.2.** v0.5 addresses what happens when the reader is the system itself. A guardian that only
reports transfers its obligation back to whoever delegated it; over time, it becomes furniture. The
answer specified here keeps the split the protocol has insisted on from the beginning — mechanism
measures, mind judges — while closing the gap between the measurement and the act.

**14.3.** The human's wish that started this line of work, on 2026-08-10, was not for a better
watcher. It was for *"a balancing consolidation mechanism that holds everything in equilibrium."*
A watcher reports imbalance. Equilibrium requires something that answers.

**14.4 — What the logs settled.** Where a guardian was given a waking act, the imbalance it reported was
answered — measurably, and repeatedly against the waking session's own first idea (two cases in the
first window, at least three in the second). Where a guardian only
reported, the imbalance waited: twenty-seven days in the clearest case. What the logs did not settle is
whether the answer reaches the root and not only the symptom; on that, the record says *partly*. v0.5 is
therefore offered at the size the evidence carries — the waking act and the state as its own marker,
with their blind spots named — and not at the size of its hope.
