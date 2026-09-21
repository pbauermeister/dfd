# Set-based design: agents at the design level

Date: 2026-09-20
Status: DONE (consumed by #92, devlog 092)
Origin: continuation of [vibe-coding-distance.md](vibe-coding-distance.md),
after #90, on `main`.

**Prompt:** Given that governance made the implementation level
delegable, can preparation and delegation move up to the design
level, and by which methods? The thread below records the questions
and answers in order; the conclusions are summarized in TODO item 14.

**Terminology.** The thread coined its own words as it went; they were
replaced afterwards by the recognized ones, which the text now uses
throughout: _options_ (the alternatives; ADR "considered options",
QOC "Options") for what was called flavours; _mock-up_ (readable, not
working) for the preview, next to _spike_ (working slice, measured);
_design question_ (QOC "Questions") for the axis an option set spans;
_decision drivers_ or _criteria_ for the reason given at selection;
_design review_ for the selection round; _rework_ for the rewind;
_triggers_ for the signs that call for a mock-up; _design rationale_
for the captured why; and _set-based design_ (Toyota, Ward and Sobek)
for the method as a whole.

## Can delegation move up to the design level?

**Prompt:** Because the design gets much attention, I need less code
review: good design plus good governance (the rules we defined) drive
the agent to code that is mostly satisfactory to me, granted that the
recent tasks were slight improvements and refactorings. Now that the
implementation level is efficient enough to delegate most of it, could
preparation and delegation be defined one level higher, at the design
level? I doubt it, since the design interactions felt necessary. Are
there methods that would reduce the need: predefined ways of
approaching design (not "design patterns"), or the human no longer
caring about details and leaving them to the agent under governance
rules?

## Answer (Claude)

**What the design interactions of #90 actually were.** Thirteen
exchanges before "go", sorted by what they decided:

| Kind                        | Count | Examples                                                                     |
| --------------------------- | ----- | ---------------------------------------------------------------------------- |
| Process and presentation    | 7     | issue draft, plan format, heading level, squash, unattended?                 |
| Values not yet written down | 3     | scripts run from the root; keep the renumberer distinct; downward calls only |
| Scope and spin-offs         | 2     | the renumberer brief; TODO items 14 and 15                                   |
| Genuinely new judgment      | 1     | `runbooks/` is the wrong name                                                |

More than half were not design at all: they were the agent asking
where the boundaries of its mandate lie, and the human formatting the
plan to the shape a later reader needs. Templates retire those (TODO
item 14 is exactly that), as the implementation-level rules retired
the code-level questions. The three "values" rows are the interesting
ones: each produced a sentence in `doc/CONVENTIONS.md`, and each
sentence retires every future question of its kind. The design
conversations are the process by which the governance gets written.
That is why they felt necessary: the first occurrence of a value cannot
be skipped; only the second can. The count per task should decline if
the capture is mandatory, and it is (the Outcome section, the
conventions edits). The residual, one genuinely new judgment per task,
is the part no method removes.

**Yes, such methods exist, and they are old.** Design docs in the
Google form (context, goals and non-goals, the design, alternatives
considered, with the last section mandatory); Architecture Decision
Records (one decision, its context, the options, the consequences;
your devlog Design sections are ADRs in disguise); Ousterhout's red
flags as a checklist (shallow module, information leakage, conjoined
methods, generic-specific mixture, vague names); domain-driven design's
ubiquitous language, which your `doc/SYNTAX.md` glossary already is;
and the two you invented for this repository, "measure, don't
estimate" and the inventory-driven plan (inventory, rule, table,
sweep). Their common effect is to make a design reviewable in one
read rather than built in a dialogue: the reviewer answers "which
option" instead of "what next". #90 showed it works: the design was
presented as decisions with a recommendation, and you corrected two of
five in one round.

**Three concrete moves that would reduce the rounds further.**

1. **Label every design decision as rule-derived or taste.** The agent
   states, per decision, the rule it follows ("verb-first: rule
   Naming") or that no rule covers it. You read only the taste rows.
   That is the honest form of "not caring about details": you stop
   caring about the details a rule already decides, and keep caring
   about the ones that would otherwise be decided by the training
   distribution's median, which is how a repository stops being yours.
2. **Mine your own questions into a design self-review.** The
   questions you asked in #88 and #90 ("does the name describe the
   files or the ambition?", "which direction does this call go?",
   "what existing file violates the new rule?", "is the sequence in
   the Makefile or in the script?") become the checklist the agent
   runs before presenting a design, like the type-safety self-review
   before a PR. Half of the judgment row would have been caught:
   `build.sh` as one `make` call answers the direction question
   without you.
3. **One design round by construction.** The agent presents the whole
   design as a decision table plus alternatives considered, and asks
   one question: approve, or name the rows to change. Rejecting a
   design costs one round and a text file; it is cheaper than the
   incremental dialogue, and the doubt you express ("the interactions
   felt necessary") is answered by the fact that they still happen,
   batched.

**What does not move up.** The one genuinely new judgment per task is
where your expertise is exercised and where the repository acquires
its character. You hand-wrote #69 to stay fit at coding; design is now
the place where you stay fit at engineering, and delegating it would
remove the last such place. So the honest ceiling: delegation can
absorb the process rounds and the rule-derived rows, and can reduce a
design to one approval; it cannot absorb the taste, and you would not
want it to. The measure to watch is the count of design rounds per
task, split by the table above; if the first row does not go to zero
after TODO item 14, the templates are wrong; if the second row does
not decline, the capture is failing; the last row is yours.

## Follow-up: a formal frame instead of discovery

**Prompt:** My interpretation: the preparatory phase was largely task
goal discovery, and a more formal process (goals, non-goals,
invariants, taste, definition of done, spikes, and so on) would have
done it more efficiently. Not necessarily with less effort, but with
the same effort spent on a better coverage of the common engineering
aspects, checked against a general checklist rather than by
improvisation, intuition and discovery.

## Answer (Claude)

**Agreed, with one correction on what was discovered.** The goals of
#90 were clear from TODO item 11 on day one. What the preparatory
phase discovered were three other things: invariants (calls go down
only; every script runs from the root), taste (keep the renumberer;
"I am satisfied with how the Makefile looks"), and one definition of
done that CI supplied after the fact (every changed recipe is
exercised by a trial or a CI job). None of these is a goal. A checklist
that asks for goals would not have found them; a checklist that asks
for invariants, taste and definition of done would have, and in the
first round.

**The strongest evidence is the order in which things came out.** The
invariant "a recipe never calls make nor another recipe" was the last
thing found, after the merge, from one odd file. Stated first, as an
answer to the question "what are the invariants?", it decides the
`build` target, the publish chain and the folder name in one go: the
afternoon on `runbooks/` was the cost of discovering an invariant
bottom-up instead of asking for it top-down. That is exactly your
point: same effort, better coverage, because the checklist asks the
questions in the order in which they constrain each other.

**Where I would temper it.**

- A fixed checklist has to be sized to the task, or it becomes theater:
  a "non-goals" section for a six-file folder split is a line that
  says "none", and a template that demands it on every task teaches
  the reader to skip sections. Hence your own condition on TODO item
  14: mandatory and optional sections, in variants per kind of task.
  The frame reduces improvisation only if filling it is cheaper than
  the discovery it replaces.
- Spikes are the formal name of what happened by accident. The
  renumberer survey and the DEBUG-trap prelude were spikes, and both
  paid; the name change was a spike we did not run ("write the
  Makefile with `build` as a target and see what remains in the
  folder"). A checklist item "which decision deserves a spike?" turns
  that from luck into routine, and your "measure, don't estimate" rule
  is already its statement.
- The checklist should be two lists merged: the classical one (goals,
  non-goals, invariants, definition of done, alternatives considered,
  spikes) and the one mined from your own questions (name describes
  the files, call direction, which existing file violates the new
  rule, sequence in the Makefile or in the script). The classical list
  gives coverage of what every engineer checks; the mined one gives
  coverage of what you check, which is what makes the repository
  yours. "Taste" as an explicit section is unusual and, for a
  one-maintainer repository, right: it is where preferences that are
  not rules get written before they are discovered by contradiction.

**Practical consequence.** This is the content of TODO item 14, not a
new item: the Design template gets goals, non-goals, invariants, taste,
definition of done, spikes, a decision table with each row marked
rule-derived or taste, then the action plan; the Outcome keeps its
rule-capture role. The measure of success stays the one above: rounds
per task, by kind.

## Follow-up: would the formal devlog structure of another project address this?

**Prompt:** Another project of mine (closed source, not named here) has
a more formal devlog structure. Would it address the topic?

## Answer (Claude)

I read the structure across its 126 devlog files and one recent one in
full. The skeleton is Mandate (context, task nature, problem statement,
goal with an out-of-scope list, design decisions, test plan, acceptance
criteria, watchlist reminder, coverage check), Execution plan (steps,
planned file inventory, scope boundary), Closure (deviations, file
inventory, verification commands, gate check ticking the acceptance
criteria, manual validation, demo scenario, retrospective, forward-
looking check), then a governance trace (each clause applied, in
tension, created or skipped) and a resource consumption block. The
Mandate is approved by the user before step 1: a mandate approval gate.

**Mostly yes.** Against the frame of the previous exchange:

| Frame item              | There                                                        | Verdict                       |
| ----------------------- | ------------------------------------------------------------ | ----------------------------- |
| Goals                   | Goal                                                         | covered                       |
| Non-goals               | out-of-scope list in Goal, plus Scope boundary               | covered twice                 |
| Definition of done      | Acceptance criteria, ticked one by one in the Gate check     | covered, before and after     |
| Task variant            | Task nature (execution, analysis, ...)                       | covered, the variant selector |
| Rule-derived vs taste   | Governance trace (applied / tension / created / skipped)     | covered, but at closure       |
| Rule capture            | "created" rows of the trace                                  | covered                       |
| Mined maintainer checks | Watchlist reminder (over-engineering, proportionality)       | covered                       |
| One design round        | Mandate approval gate                                        | covered                       |
| Taste                   | the user column of the Retrospective (well / don't care ...) | recorded after, not before    |
| Invariants              | none                                                         | missing                       |
| Spikes                  | none as a slot; measured trials appear inside Test plan      | missing                       |

The two missing slots are the two that #90 needed most. Invariants
("calls go down only") is what an afternoon was spent discovering
bottom-up; a spike slot ("write the Makefile with `build` as a target
and see what remains") is how it would have been found in an hour. And
the labeling of decisions as rule-derived or taste happens there in
the governance trace, at closure, where it documents; it would cut
rounds if it happened in the Mandate, where it decides what the
reviewer must read.

**The cost warning, honestly.** The devlog I read in full is 578
lines for a mechanical port of a shell script, with eleven closure
subsections and a twenty-row governance trace keyed by clause
identifiers. Two of its thirteen retrospective rows are about friction
with the process itself. That project may need that weight; this one
does not, and the frame's own proportionality check would say so. The
devlogs here run about 200 lines and the whole preparatory phase of
#90 fits in one.

**What to import into TODO item 14.** The skeleton, not the weight:
Mandate (context, task nature, goal, non-goals, invariants, taste,
decisions each marked rule or taste, acceptance criteria), Plan (steps,
inventory, scope boundary), Closure (deviations, gate check ticking the
criteria, retrospective with the two columns, forward-looking check),
and a short rule trace with two verbs only, applied and created, in
place of clause identifiers. Plus the mandate approval gate as the one
design round. Sized per task nature: the analysis variant drops the
gate check and the inventory; the mechanical-refactor variant drops
the test plan when the definition of done is "no diff".

## Follow-up: bureaucracy, and the question that remains

**Prompt:** Record these conclusions for TODO item 14. But I must
temper: the more guardrails and automated process we define, the more
bureaucracy they generate. In the end this does not alleviate the
design effort; it makes it more efficient and predictable by perhaps
10%. So my initial question remains: how to get more benefit from
agents at the design level, without giving up to vibe coding? The
answer may be "at current agentic capabilities, not significantly".

## Answer (Claude)

**On the 10%: agreed, for that route.** Checklists and templates buy
coverage and predictability, not effort; and every section the human
must fill is bureaucracy. The one defense is to keep the form on the
agent's side: the agent fills the checklist, the human reads a
decision table. Bureaucracy the agent carries is nearly free;
bureaucracy the human carries is the whole cost.

**The route that is larger than 10% is a different one: judge
artifacts, not descriptions.** Look at where the design effort of #90
went. Almost every round was you imagining a state of the repository
from prose ("runbooks", "a build target", "recipes") and reacting to
the imagined state. The decisive moment was not a discussion: it was
the sight of `build.sh` as one `make` call. A concrete artifact
settled in a minute what prose had circled for an afternoon. The
agent can produce that artifact before the decision, for every
alternative, in a scratch clone: the Makefile as it would read, the
folder listing, one sample recipe, the `make help` output. Judging a
concrete thing is faster and more reliable than judging an imagined
one, and it surfaces unstated values earlier: a value you hold
becomes visible when an artifact violates it, and a prototype
violates it for free where an implementation violates it in CI. This
is "measure, don't estimate" applied to design itself: show, don't
describe. My estimate for #90: thirteen rounds become about five, the
five being the ones where a value or a taste was stated. That is not
10%.

**Two enablers, both about rounds rather than judgment.**

- **Exploration off the critical path.** The surveys, spikes and
  alternatives are agent work; in #90 they were done in dialogue,
  sequentially, each waiting for a turn. They can run unattended, in
  a batch, and return once, as a decision table with the prototypes
  attached. The human's turns are then spent only on deciding.
- **A design critic before the design reaches you.** A second pass,
  or a second agent, reviews the design against the checklist and
  against your mined questions ("does the name describe the files?",
  "which direction does this call go?") before you see it. This is
  the code-level self-review moved up one level. It catches the
  derivable part of what you now catch yourself; it cannot catch the
  taste.

**What does not move, at current capabilities.** The agent cannot
know in advance which of its alternatives you will like; it can only
make alternatives cheap. Your role shifts from author of one design to
selector among several concrete ones. That is not vibe coding, since
you still judge the artifact and own the rule that comes out of it,
but it is a change in the nature of the work: design by selection
rather than design by construction. Whether that is a gain depends on
what you want from the activity. If the point is the repository, it is
a gain. If part of the point is staying fit at design, as #69 was for
coding, then selection exercises judgment but not construction, and
you would want to keep authoring some detriggers by hand for the same
reason you hand-wrote #69.

**So the honest answer to "not significantly" is: not significantly on
the judgment, significantly on the rounds.** The judgment is the part
you would not give up; the rounds are the part that tires you. The
lever is to make each round a decision over artifacts, with the
exploration done before you arrive. A sentence for `CLAUDE.md`, when
TODO item 14 lands: a design is presented as a decision table with each
alternative materialized in a scratch clone, never as prose alone.

## Follow-up: design by selecting among materialized options

**Prompt:** Do you mean this: at design time, the agent generates a
concrete sample of the outcome, in several options produced by
parallel agents, in throwaway portions of the project, so that the
human selects one and a major direction is chosen earlier than now?

## Answer (Claude)

Yes, that is it, with five precisions that make the difference between
a useful practice and a costly one.

1. **The sample is the smallest slice that makes the difference
   visible**, not a partial implementation. For #90 it is the Makefile
   as it would read, the folder listing, one recipe, and the `make
help` output: fifty lines per option, readable in two minutes.
2. **Options are chosen to differ on one suspected value**, not for
   variety. The agent's job before spawning them is to name the design question
   it cannot decide alone ("does the sequence live in the Makefile or
   in the script?") and to build one option per answer. In #90 the
   three options would have been: everything stays in `tools/` with
   the naming rule only; `runbooks/` owning the sequences; the
   Makefile owning the sequences with `recipes/` as bodies. You would
   have picked the third in the first round, on sight of `build.sh`
   being one `make` call in the second.
3. **Parallel agents earn their cost by independence**, not by speed:
   an option built without seeing the others is not anchored on them,
   so the set spans the design question instead of clustering around the first
   idea. Worktrees make the throwaway free; two or three options are
   readable, more is a chore.
4. **The selection is not the deliverable; the reason is.** You pick
   one and say why, and the why is the rule that goes to the
   conventions ("calls go down only"). "None of them, because X" is a
   valid answer and yields the rule just the same. Without the why,
   selection is taste consumed once; with it, taste becomes
   governance and the next task does not ask.
5. **The chosen option is thrown away too.** The plan is then written
   for that direction and runs mechanically, as steps 1 to 4 of #90
   did. Salvaging the spike's half-built files into the real branch
   would break the one-commit-per-step discipline and reintroduce
   code review where design review had sufficed.

What it changes in the timeline: the major direction is chosen at the
first round, on artifacts, instead of surfacing at the end from an odd
file. What it does not change: you still make every judgment that is
taste, and one option still has to be built by hand now and then, for
the reason #69 was.

## Decision: adopt set-based design, gated at specification time

**Prompt:** Adopt this process, with due measure: for some tasks it
adds effort and no value. It pays when it can avoid a design rework
mid-task or at the end. Whether to engage it is decided during the
task specification discussion.

**Recorded (Claude).** The practice is named _set-based design_. The
gate is a question asked once, in Phase 3, and answered in the
devlog's Design section:

- **Engage** when a major direction is open and a wrong one would
  cost a rework (a rename, a restructure, a reversed dependency)
  after implementation has started. Then: name the design question, two or three
  options, one worktree each, the smallest visible slice, one
  design review with the reason recorded as a rule.
- **Skip** when the design is single-valued (a doc-only task, a
  mechanical refactor driven by an inventory, a fix with one obvious
  shape) and write "Options: none, because ..." so the skip is a
  decision and not an omission.

The templates of TODO item 14 carry the slot; `CLAUDE.md` Phase 3
carries the gate.

Draft of the `CLAUDE.md` Phase 3 paragraph, to be added by TODO item
14 together with the templates:

> - Decide whether to run _set-based design_: when a major direction is
>   open and a wrong one would cost a rework after implementation
>   starts, the agent names the design question, builds two or three options in
>   throwaway worktrees (the smallest slice that makes the difference
>   visible: the Makefile as it would read, a folder listing, one
>   sample file), and the user selects one in a single round, stating
>   why; the why is recorded as a rule. Otherwise the devlog says
>   "Options: none, because ...". The chosen option is discarded
>   too; the plan is then written for that direction.

## Follow-up: detecting the need for options at requirements time

**Prompt:** Can the need for set-based design be detected at
requirements time? What are the triggers? Would we have detected it while
designing devlog 090? The information was perhaps there (the table
listed every rename) but I did not realize the practical implications.
So before generating option mock-ups, a prior step would be to
generate the mock-up of the main supposed design, so that the human
can fully grasp the implications.

## Answer (Claude)

**Yes to the prior step, and it changes the gate.** A mock-up of the
supposed design is cheap: for a structural task it is a folder
listing, the Makefile as it would read, one sample file. Options are
the escalation, decided by looking at the mock-up rather than by
guessing at specification time. That resolves the "due measure"
concern better than a judgment call in Phase 3: the mock-up is the
default for any task that moves or renames things, and the options
are engaged only when the mock-up raises a question. The devlog then
records "Mock-up: yes / no, because ..." and "Options: none, because
the mock-up raised no design question" or the design question it raised.

**Would #90 have been caught? Yes, by the mock-up, and it was half
visible in the table.** The inventory row `tools/build.sh | runbook |
runbooks/build.sh` sat next to the definition "named steps, one
command each" while `build.sh` was one command calling make. Nobody
tested each row against the definition. A mock-up would have shown
what the prose hid: a folder where one file has 4 lines and another
51, one of them a `make` call. Size disparity inside a category and a
call going upward are visible in a listing and invisible in a table
of renames. The information was there; the representation was wrong
for grasping it.

**The triggers, at requirements time.** Each is checkable by the agent
before it presents a design, and each names the design question an option set
would span:

1. **A new name for a container** (folder, module, target family). A
   name is a claim about what the files are; the claim is testable
   only against the files. Design question: what the members have in common.
2. **A new rule that classifies existing items**, i.e. an inventory
   table with a level or category column. Test every row against the
   definition; an awkward row is the trigger. Design question: the definition.
3. **A thing that could live in two places** (a sequence in the
   Makefile or in a script; a constant in `config.py` or in the
   module). Design question: the two places.
4. **A decision inherited as intent from a prior task** ("intent: the
   orchestrators move to `runbooks/`", written in #88 without
   artifacts). Inherited prose is unverified. Design question: the inherited
   claim.
5. **Ambition vocabulary in the requirement** ("orchestrator",
   "runbook", "scenario", "framework") where artifact vocabulary
   would do ("script that runs three commands"). Design question: ambition
   versus what will actually be written.
6. **One conceptual decision buried in mechanical churn.** Thirteen
   Makefile lines and six sourcing lines hid one direction question.
   Design question: whatever the single non-mechanical row decides.

#90 showed triggers 1, 2, 4 and 6 at requirements time. The triggers are
cheap to check because they are about the shape of the requirement,
not about the domain; they belong in the Phase 3 checklist of the
templates, next to invariants and taste, as the trigger for the
mock-up.

**The sequence, then:** requirement; trigger check; if any trigger, the
mock-up of the supposed design in a throwaway worktree; the human
reads the mock-up; if it raises a design question, options on that design question; one
design review; the rule captured; the plan written; the run. In
#90 the mock-up would have come after the first devlog commit and
before the plan, and the afternoon on the name would have been the
ten minutes of reading a listing.

## Follow-up: is a mock-up almost as costly as the implementation?

**Prompt:** Looking at the rename table of #90, the name `runbooks/`
rang a bell and I should have reacted. Is the cost of the mock-up
almost as high as the real implementation?

## Answer (Claude)

No, by about an order of magnitude, because a mock-up needs to be
readable, not working. The expensive parts of an implementation are
the ones a mock-up skips:

| Implementation of #90 (steps 1–5 and the fix) | Mock-up of the same design      |
| --------------------------------------------- | ------------------------------- |
| every path edit correct (30 sites)            | the moves and the Makefile only |
| conventions and release page rewritten        | nothing                         |
| lint, tests, doc regeneration, wheel smoke    | nothing                         |
| grep sweeps, fake-PATH trials                 | nothing                         |
| six commits, PR body, CI, one CI-found bug    | nothing, worktree discarded     |
| about an hour of agent work                   | about five minutes              |

For a structural task the mock-up is a `git mv` and one entry-point
file, and it may even be broken: what the human reads is the listing
and the Makefile, not a passing test suite. The bell you heard on the
word "runbooks" is exactly what a mock-up turns into a sight: `ls
runbooks/` with a 4-line file next to a 51-line one.

The ratio worsens as the design moves from structure into behavior.
For a new feature the smallest visible slice is the interface: the
CLI help, the function signatures, a sample DFD with its intended
output as a hand-written golden; stubs, not code. For an algorithm it
is the test cases or pseudo-code. For a decision that only shows in
the working behavior (a performance choice, an error message under
real conditions) the mock-up is the risky slice implemented and thrown
away, which is what a spike has always been; still cheaper than the
implementation, since it carries no verification, documentation or
commits, but no longer by ten to one.

What the mock-up never costs is the thing that was actually expensive
in #90: the rework. Step 5 and the afternoon that led to it were more
than the whole implementation of steps 1 to 4. The mock-up's price is
to be compared with that, not with the implementation.

## Follow-up: how often would a mock-up be quite wrong?

**Prompt:** What are the chances that a mock-up gets quite wrong, when
the implementation is non-trivial?

## Answer (Claude)

**It depends on what decides the direction: a value or a constraint.**
A mock-up shows what the artifact will look like; it is right whenever
the direction is decided by how the artifact reads (a name, a folder,
a call direction, an interface), and it is at risk whenever the
direction is decided by something the world reveals only at
implementation (a library's behavior, a layout engine's output,
performance, real data). Mock-ups are the tool for the first kind, and
they eliminate the rework caused by unstated values. They do nothing
for rework caused by unknown constraints; those need a spike, which
is the risky slice implemented and measured. A mock-up mistaken for a
spike is the case that goes quite wrong.

**Rough odds by task kind in this repository**, from its own history:

| Task kind                                         | Mock-up fidelity                 | Evidence                                                                  |
| ------------------------------------------------- | -------------------------------- | ------------------------------------------------------------------------- |
| Structural: moves, renames, target shapes (#90)   | near-exact                       | the listing is the outcome                                                |
| Conventions applied to code (#73)                 | good on shape, weak on inventory | the "16 positional call sites" of the audit did not exist                 |
| Registry or declaration design (#71)              | good                             | three decisions revised in PR review, none a direction change             |
| Escaping and parsing rules (#67)                  | moderate                         | design revised during implementation, devlog ironed afterwards            |
| Anything whose look depends on Graphviz           | low                              | a stub cannot show what `dot` will lay out; only a rendered sample can    |
| Anything resting on a third-party tool's behavior | low, and deceptively so          | the renumberer trial: zero diff on the real doc, wrong on the first fence |

The last row is the important one. The candidate tool's "mock-up" was
perfect on the happy path and wrong in the first adversarial case; the
mutation file, not the mock-up, exposed it. So the probability that a
mock-up is quite wrong is roughly the probability that the decisive
factor is external, which for this small, stable, well-tested code
base is low for refactorings and doc tasks, moderate for parser
features, and high for rendering features.

**Three mitigations, all cheap.**

1. **The mock-up states its assumptions.** Each "assumes X behaves like
   Y" line is either verified by a measured spike or marked as a risk
   the plan carries. Unstated assumptions are where "quite wrong"
   lives.
2. **One adversarial case per mock-up**, the mutation-file principle
   applied to design: a happy-path sample plus the one input most
   likely to break the shape (a fence, a skipped level, an empty
   label).
3. **A wrong mock-up still fails early if the plan's first step is the
   risky slice.** Ordering the steps so that the constraint-bearing
   part comes first turns a late rework into an early plan revision,
   before the mechanical steps have been run.

So: for the tasks where mock-ups are proposed, structural ones, the
chance is small and the history shows it. For behavioral tasks the
mock-up is not the instrument; the spike is, and the trigger list should
say so: "the decision depends on a tool, a layout or data" triggers a
spike, not a mock-up.

## Closing note

**Prompt:** So even if a mock-up and its variants are partly
speculative, they still make the design decision more data-driven
than without.

**Agreed (Claude),** with the word made precise: a mock-up makes the
decision _artifact-driven_, a spike makes it _data-driven_, and both
replace the same thing, a decision taken on prose and imagination. A
partly wrong artifact still beats no artifact, because its wrongness
is visible and arguable, where the wrongness of an imagined design
surfaces as a rework. The gain is not certainty; it is that the
uncertainty gets a shape one can point at, at the time when pointing
is cheap.

## Postscript: does the method have a name?

**Prompt:** Does this method have a name?

**Answer (Claude).** Not as a whole; each part does, and the lineage
is worth citing in the template so a future reader can look it up.

- **Options** are _set-based design_ (Toyota's set-based concurrent
  engineering, Ward and Sobek, 1990s): develop several alternatives in
  parallel and narrow by elimination as information arrives, instead
  of committing to one and iterating. The empirical support is
  _parallel prototyping_ (Dow et al., ACM TOCHI 2010): designers who
  produce several prototypes before feedback reach better results and
  more divergence than those who iterate on one, which is the
  "independence, not anchoring" point.
- **The mock-up** is the _throwaway prototype_ (Brooks, "plan to throw
  one away", 1975), the _spike_ of Extreme Programming when it
  measures a constraint, the _tracer bullet_ of The Pragmatic
  Programmer when it is a thin end-to-end slice, and the _walking
  skeleton_ (Cockburn) when it is the structure without the behavior.
  A mock-up that is readable but not working is a paper prototype.
- **The decision table** with alternatives, criteria and the reason
  recorded is _design rationale_ capture; the closest formal notation
  is QOC, Questions, Options and Criteria (MacLean et al., 1991), and
  the closest current practice is the Architecture Decision Record.
- **The gate** ("engage when a wrong direction would cost a rework")
  is the ordinary risk-based tailoring of any process.

For this project the method goes by its recognized name, set-based
design, as recorded in TODO item 14.
What has no established name is the combination's purpose here: using
the agent's cheap generation to turn a human's unstated values into
recorded rules, one selection at a time. That part is new because the
cost structure is new.
