# 139 — Study the token budgeting and model choice

Date: 2026-09-26
Status: ONGOING
Issue: #139 · PR: #142 · Branch: `doc/139-token-budgeting`
Task nature: analysis
Track: fast
Agent: Claude Fable 5.1

## 1. Mandate

### 1.1 Context

TODO item 36 (raised at the review of #130, removed by the filing
commit of the batch). Third of the batch 30, 28, 36 of 2026-09-26,
off `main`, reviewed last. Framed as a study only: whether measures
follow is decided upon the report.

### 1.2 Goal

`discussions/token-budgeting.md` answers the item from measured
consumption: what the past tasks cost by shape, what a model or an
effort per phase would save at that shape, what the quota is and how
it is read, and the options for recording an estimate and reading the
actual back. No change to PROCESS.md or the templates.

### 1.3 Design decisions

| #   | Decision                                                                                                                | Basis                                            | Alternatives considered                              |
| --- | ----------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ | ---------------------------------------------------- |
| 1   | The local transcripts mined for usage, deduplicated by message id, totals only in the report                            | batch assessment (taste, the user's yes)         | Reason by analogy from devlog sizes                  |
| 2   | Priced at Fable 5.1 list rates with the one-hour cache write, the subscription's TTL; the five-minute figure given once | pricing page and the costs page, read on the day | Tokens only, no dollars                              |
| 3   | Sessions mapped to tasks by date; shapes stated as ranges, the variance attributed to the count of calls                | the data (rule)                                  | Per-task attribution, impossible in a shared session |
| 4   | The model question answered with the switch cost at the measured context, not with a quality claim                      | measure, don't estimate (rule)                   | A recommendation of a model per phase                |
| 5   | Model facts from the `claude-api` skill and the current pricing and Claude Code pages, dated                            | batch assessment (rule)                          | Recollection                                         |

### 1.4 Acceptance criteria

1. Consumption totals and per-session table from the transcripts, the
   script reproducible.
2. Shapes with an order of magnitude each.
3. The model and effort levers priced at the measured shape; the
   quota described from the plan's own words.
4. Options with their cost; sources dated; `make lint` passes.

Approved: 2026-09-26 (the go for the batch)

## 2. Findings

Measured on 2026-09-26 (the discussion holds the tables):

- 29 sessions with a model call, 2,167 calls (2,071 distinct message
  ids across files, a 5% double count from resumed sessions kept in
  the per-session table), 13 active days, $422 at list price.
- Cache writes 48%, cache reads 26%, output 25%; thinking 32% of the
  output; 204k tokens of context per call on average, 395k in the
  three-day session.
- A model switch mid-session rebuilds the cache: $4.1 back to Fable at
  204k; a fast task's saving on Opus 5.5 or Sonnet 5 is $3 to $4.
- The Max plan's allowance is not published in tokens; `/usage` shows
  the bars and a 24-hour or 7-day breakdown from the same transcripts.
- The mining script (kept in the scratchpad, quoted here so that it
  can be re-run or become `tools/usage-report.py`):

```python
"""Sum the token usage of the Claude Code transcripts of one project.

One row per session: date range, turns, tool calls, tokens by kind,
per model. Usage is deduplicated by message id (a streamed message is
written once per content block with the same usage).
"""
import glob, json, os, sys, collections
D = os.path.expanduser('~/.claude/projects/-home-pascal-dev-pb-dfd')
rows = []
tot = collections.Counter(); bymodel = collections.defaultdict(collections.Counter)
for f in sorted(glob.glob(D + '/*.jsonl')):
    usage = {}; first = last = None; user_turns = tools = 0
    for line in open(f):
        try: e = json.loads(line)
        except json.JSONDecodeError: continue
        ts = e.get('timestamp')
        if ts: first = first or ts; last = ts
        if e.get('type') == 'user':
            c = e.get('message', {}).get('content')
            if isinstance(c, str) or (isinstance(c, list) and c and c[0].get('type') == 'text'):
                user_turns += 1
        if e.get('type') == 'assistant':
            m = e['message']; u = m.get('usage')
            if u: usage[m['id']] = (m.get('model'), u)
            for b in m.get('content', []):
                if isinstance(b, dict) and b.get('type') == 'tool_use': tools += 1
    c = collections.Counter()
    for model, u in usage.values():
        k = collections.Counter(inp=u.get('input_tokens', 0), cc=u.get('cache_creation_input_tokens', 0),
                                cr=u.get('cache_read_input_tokens', 0), out=u.get('output_tokens', 0), calls=1)
        c.update(k); bymodel[model].update(k)
    tot.update(c)
    if c['calls'] == 0: continue
    rows.append((first[:16], last[:16], user_turns, tools, c['calls'], c['inp'], c['cc'], c['cr'], c['out'], os.path.basename(f)[:8]))
print('first            last             turns tools calls   input  cache_w   cache_r    output  session')
for r in rows: print('%s %s %5d %5d %5d %7d %8d %9d %8d  %s' % r)
print('\nTOTAL calls=%d input=%d cache_w=%d cache_r=%d output=%d' % (tot['calls'], tot['inp'], tot['cc'], tot['cr'], tot['out']))
for m, c in bymodel.items(): print('  %-22s calls=%5d input=%8d cache_w=%9d cache_r=%10d output=%8d' % (m, c['calls'], c['inp'], c['cc'], c['cr'], c['out']))
```

Pricing: per session, `(input × 10 + cache_w × 20 + cache_r × 0.25 +
  output × 50) / 1e6`.

Account: `d196fa5` the discussion; this devlog.

## 3. Delivery

### 3.1 Verdict

**Recommendation:** accept

- Criteria 1 to 4 met. The agent's reading, for the review: the item
  asked for an estimate and a model per phase; the numbers say the
  context is the cost, so the cheapest measures are the session
  discipline (C) and the output hygiene (E), and the model per phase
  only as a subagent (D). B is worth it if the read-back is wanted
  as a record.

### 3.2 Discussion

| #   | Point                                                                                                           | Decision |
| --- | --------------------------------------------------------------------------------------------------------------- | -------- |
| 1   | The three-day session of the last two batches cost $144, half of it the context; a `/clear` per batch next time | review   |

## 4. Closure

### 4.1 Retrospective

| #   | Point                                                                                                                 | Agent    | User |
| --- | --------------------------------------------------------------------------------------------------------------------- | -------- | ---- |
| 1   | Process and template fit: analysis nature in fast form, Findings in place of Execution, the script in the devlog      | well     |      |
| 2   | The transcripts answered the item better than any estimate could; the first script run took a minute                  | well     |      |
| 3   | The item's premise (model per phase, token estimate) survived only in part; the measure it needed was the switch cost | surprise |      |

Process: 1 round before the go (the batch assessment); 0 loops.

Closed: pending

### 4.2 Rule trace

| Source                                                      | Rule                                | Verb (applied / created) |
| ----------------------------------------------------------- | ----------------------------------- | ------------------------ |
| `engineering/PROCESS.md` Established tool vs bespoke script | Measure, don't estimate             | applied                  |
| `engineering/PROCESS.md` discussions/ files                 | Executive summary and outcomes last | applied                  |
