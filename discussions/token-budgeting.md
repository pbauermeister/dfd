# Token budgeting and model choice, per task and per batch

Date: 2026-09-26
Status: PENDING
Origin: #139 (devlog `devlog/139-token-budgeting.md`), branch
`doc/139-token-budgeting`.

**Prompt:** Should a task's action plan carry a model per phase and a
token estimate, and a batch's assessment an early check against the
quota; at what granularity, recorded where, and how is the actual
consumption read back for the next estimate?

## 1. What the past tasks cost

The Claude Code transcripts of this project (29 sessions with at
least one model call, 2026-09-03 to 2026-09-26, 13 active days) carry
the usage of every call: input, cache write, cache read and output
tokens, with the model. A script in the devlog sums them per session,
deduplicated by message id, and prices them at the list rates of
Claude Fable 5.1 read on 2026-09-26 ($10 input, $20 one-hour cache
write, $0.25 cache read, $50 output per million tokens; a subscription
session runs the one-hour cache). On a subscription the dollars are
notional, but they are the only common unit the plan and the API
share, and Claude Code's own `/usage` figure is computed the same way.

| Kind                          | Tokens | Share of $422 |
| ----------------------------- | -----: | ------------: |
| Cache writes (new context)    |  10.2M |           48% |
| Cache reads (context re-read) | 441.8M |           26% |
| Output, of which thinking 32% |   2.1M |           25% |
| Uncached input                |  0.06M |            0% |

Two thirds of the cost is the context: what a call adds to it (tool
results, at $20 per million) and what every later call re-reads (at
$0.25 per million, 204k tokens per call on average). Output is a
quarter. So the drivers are, in order, the volume of tool output, the
number of calls, the size of the context at each call, and only then
the model and the effort. Under a five-minute cache the writes would
cost $127 instead of $203 and the total $345: the TTL is worth
knowing when reading `/usage`.

The sessions map onto the devlogs by their dates, which gives the
order of magnitude per shape. Calls, context per call and list price
from the script; the tasks from the devlog dates:

| Session dates              | Tasks                                                                        | Calls | Context/call | $ list |
| -------------------------- | ---------------------------------------------------------------------------- | ----: | -----------: | -----: |
| 09-03 to 09-04 (4)         | #69, #71, #73, full track of the older template                              |   185 |     78k–109k |     26 |
| 09-16 to 09-17 (6)         | #75, #77, #79, #80, #84, #85                                                 |   407 |     69k–137k |     49 |
| 09-17 18:53 to 09-19       | #88 conventional commits, first live release                                 |   220 |         230k |     49 |
| 09-19 to 09-21             | #90 script levels, #92 devlog templates                                      |   209 |         236k |     52 |
| 09-21 evening              | #94 tracing prelude (refactor)                                               |    73 |         118k |     11 |
| 09-21 to 09-23             | #96 fast, #98 full (454 lines)                                               |    76 |         135k |     22 |
| 09-23 morning (7 tiny)     | the load trials of #98, 2 to 7 calls each                                    |    30 |          47k |      5 |
| 09-23 to 09-24 morning (2) | #100 fast, #102 fast                                                         |    99 |          80k |     11 |
| 09-24 10:20 to 20:01       | #104 full (505 lines) and the build batch #107 to #117 (six fast)            |   197 |         213k |     31 |
| 09-24 20:01 to 09-26 12:51 | filter batch #119 to #125 (four), #127 full, third batch #129 to #136 (four) |   473 |         395k |    144 |
| 09-26 12:51 to 14:21       | the closing of the third batch                                               |    91 |         138k |     12 |

Read off the table, at list price and Fable 5.1:

- A **fast-track task** costs $3 to $6 and 20 to 50 calls, reviews
  included, whether alone (#100, #102) or in a batch (the build batch:
  six tasks and one full task for $31).
- A **full-track task** costs $20 to $50 and 100 to 220 calls: #88,
  #90 with #92, #98, #104 with its three rounds and three loops.
- A **batch session kept open for three days** costs $144: its
  context per call is 395k, twice the one-day sessions, and 133 user
  turns re-read it. The same work in one session per batch would have
  cost about half on the reads and nothing less on the rest.
- A **release** or a trial is a few calls, under $1.

The variance inside a shape is the number of calls, which follows the
rounds and loops, not the size of the change: #94 (400 lines of
devlog, a refactor) took 73 calls, #88 took 220 with the first
release on the way.

## 2. The model and the effort, priced at the measured shape

The average call re-reads 204k tokens, adds 4.7k and writes 1k. At
the list rates of 2026-09-26:

| Model            |  Reads | Writes | Output | Per call | Fast task (30 calls) |
| ---------------- | -----: | -----: | -----: | -------: | -------------------: |
| Claude Fable 5.1 | $0.051 | $0.094 | $0.049 |    $0.19 |                 $5.8 |
| Claude Opus 5.5  | $0.041 | $0.038 | $0.020 |    $0.10 |                 $3.0 |
| Claude Sonnet 5  | $0.041 | $0.019 | $0.010 |    $0.07 |                 $2.1 |

The cache read is priced within 20% across the three, so a long
context costs about the same whatever the model; the saving of a
cheaper model is on the writes and the output, two to three times per
call. Two facts decide where that saving is real:

- **A model switch rebuilds the cache.** The cache is scoped to the
  model, so `/model` in a session with 204k of context writes it again
  on the next call: $0.8 to Sonnet, $4.1 back to Fable at the one-hour
  rate. A fast task's whole saving is $3 to $4. Hence the model per
  phase pays only when the phase runs in its own fresh context: a
  subagent (`model: sonnet` in its definition or the Agent tool's
  `model` parameter, `CLAUDE_CODE_SUBAGENT_MODEL` for all) or a new
  session started at the phase boundary, never a switch mid-session.
  The `opusplan` alias is the harness's own version of the idea.
- **Effort is an output lever.** Thinking is 32% of the output, output
  a quarter of the cost, so the levels (`/effort`, default `high` on
  Fable, `medium` on Opus 5.5) move at most a few percent of a task
  unless they also cut the number of calls, which lower effort does
  (fewer, more consolidated tool calls). On the API an effort change
  invalidates the messages cache like a model change; whether Claude
  Code uses the per-message effort of Fable 5.1 that avoids it is not
  documented, and the cache line of `/usage` after a switch would
  tell.

Quality is not measured here. The mechanical steps of this project
(a rename sweep, a fixture regeneration, a devlog in fast form) are
the candidates for a cheaper model, and a subagent is the mechanism
that makes them cheap without the rebuild.

## 3. The quota

A Max plan has "a session-based usage limit [that] will reset every
five hours" and "a weekly usage limit that applies across all models";
the tiers are 5x and 20x "the Pro plan's per-session usage allowance".
The allowance is not published in tokens, and the model-specific
limits ("You've hit your Opus limit") are separate from the shared
window. So there is no number to estimate against, only two bars.
`/usage` shows them, with a breakdown of the last 24 hours or 7 days
computed from the local transcripts: attribution to subagents, skills
and MCP servers, and flags on long context and cache misses when one
exceeds 10% of the usage.

An early check for a batch is then a reading, not an estimate: the
bars before the go, against the shape's order of magnitude. The
missing piece is the exchange rate between a shape's dollars and a
bar's percent, which the plan does not publish and one reading before
and after a batch calibrates well enough for the next.

## 4. Options

| Option                                  | What it adds                                                                                                                                                                          | Cost                                                                                                              |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| A. Nothing recorded                     | The bars read before a go; the shape table above as the order of magnitude                                                                                                            | none; the table ages                                                                                              |
| B. A budget line per task and per batch | The Mandate (or the fast devlog header) gets `Budget: <shape>, ~N calls, ~$X`; the closure gets `Consumed:` from the script; a batch's assessment gets one line for the sum           | a template line, `tools/usage-report.py` (the devlog's script, about 40 lines), one session per task or per batch |
| C. Session discipline                   | `/clear` at the go of a task or a batch, so that the context restarts and the consumption is one session; the session id in the devlog header for the read-back                       | a habit; the closure step names it                                                                                |
| D. Cheap phases in fresh contexts       | The mechanical steps delegated to a subagent at `sonnet`, or run in a session of their own; never `/model` mid-session                                                                | a line in PROCESS.md "Implementation workflow"; the quality of the cheap steps to watch                           |
| E. Tool-output hygiene                  | `head`, `tail`, `grep -c` and `--quiet` on every command whose output is not read; one chained command per step; the largest lever (writes, 48%) and already the habit of the batches | a line in `engineering/CONVENTIONS.md` or the prose sheet                                                         |

A and C cost nothing and C alone would have halved the largest
session. B gives the read-back the item asks for, and its estimate is
by shape until three or four tasks of a shape have a `Consumed:` line.
D is the model-per-phase of the item, in the only form where it pays.
E is the lever the numbers point at, whatever else is decided.

## Executive summary

Measured over 29 sessions and 2,167 calls: $422 at list price, of
which two thirds is context (writes 48%, reads 26%) and a quarter
output. A fast task costs $3 to $6, a full task $20 to $50, a
three-day batch session $144, and the count of calls, not the size of
the change, sets the variance. A cheaper model saves two to three
times per call but a mid-session switch rebuilds a 200k cache for
about the saving of a fast task, so the model per phase pays only in
a subagent or a fresh session. The quota is two bars, not a token
count; the check is a reading before the go. The cheapest measures
are a `/clear` per task or batch and terse tool output.

## Outcomes and measures

To decide at the review of #139, none taken here:

- Which of A to E, and for B where the line lives (Mandate, fast
  header, assessment).
- Whether the script becomes `tools/usage-report.py`.
- The mechanical steps to try on a `sonnet` subagent, and how their
  quality is judged.
