# How far is this way of working from "vibe coding"?

Date: 2026-09-20
Status: DONE
Origin: side discussion after #90 (and #88 before it), on `main`.

**Prompt:** In #88 and #90 the work went through many small
human-agent exchanges, even where no code was written: that matches
how I care about concepts, architecture and details, at the
granularity I am comfortable with and aim at. Honestly, and with no
negative opinion of it: how far is that from what is generally meant
by "vibe coding"? It is only that I do not think it is my way.

## Answer (Claude)

**Far, on the design question that defines the term.** Vibe coding, as Karpathy
coined it in early 2025, is a stance toward the code: describe what you
want, accept the diffs without reading them, paste the errors back,
judge by whether it runs, and "forget that the code even exists". The
defining move is ceding ownership of the artifact. Simon Willison's
sharpening is the usual test: if a model wrote every line but you
reviewed, tested and understood it all, that is not vibe coding, that
is using a model as a typing assistant.

By that test the two tasks are the opposite. In #90 you renamed a
folder the day it was created because the rule, once written down, did
not describe the files; you rejected a fix proposal by asking for the
precedence argument and got it measured; your PR review found a `sudo`
fallback from another project's era; you asked for a survey with
numbers before keeping a 160-line script. None of that is possible for
someone who has forgotten the code exists. The ownership stayed with
you at every layer: the concepts, the names, the folder, the Makefile
shape, the comment at the top of each recipe.

**Close, on the design question people usually mean informally.** You did not
type the implementation. The research, the trials, the renames, the
verification, the commits and the CI loop were delegated, and for #90
you granted the whole plan unattended once it was tabled. Natural
language was the interface; the agent ran the experiments. Seen from
outside, "Pascal talks and the repo changes" looks like vibe coding.
The difference is invisible in the transcript's shape and total in its
content.

**What the interactions were about is the tell.** Vibe coding's loop
runs at the behavior level: it does not work, fix it. A classical
review runs at the code level: this line, this type. Your loop ran
almost entirely at the concept level: what is a runbook, what is a
recipe, which direction may calls go, what does a target name promise.
You rarely touched the code by hand (#69, deliberately, to stay fit),
and you rarely discussed lines; you discussed the rules that generate
the lines, then let the generation run. A fair name would be
concept-level engineering with delegated implementation. The nearest
common term is "AI-assisted engineering"; "agentic engineering" is
also used for it.

**The honest costs of your way, since you asked for honesty.**

- It is expensive in attention. #90 took about a dozen exchanges
  before "go", for a change with no user-visible effect. The
  fatigue you reported earlier came from this, and the terse-output
  rule and the tabled plans are the mitigations you built. The
  granularity is a choice with a price, and you are paying it
  knowingly.
- It can over-invest in things that will not be read again. The
  `runbooks/` to `recipes/` afternoon produced a better rule; it also
  cost an afternoon on the name of a folder with six files. On a
  repository you maintain for years that is a good trade; on a
  throwaway it would not be.
- Process grows by accretion. `CLAUDE.md` at 265 lines and the devlog
  non-uniformity are the symptoms you filed yourself as TODO items 14
  and 15. Vibe coding has no such debt because it keeps no process.

**Where each wins.** Vibe coding wins on prototypes, explorations and
anything you will throw away or never maintain: speed is the whole
point and ownership is a cost. Your way wins on exactly this
repository: a tool you install on your own machine, with conventions
you want to still understand in five years, where a wrong name or a
wrong dependency direction compounds. The two are not points on one
scale of rigor; they are answers to different questions about who owns
the artifact afterwards. You have answered that you do.

**One measurable proxy from #90.** Human turns before implementation:
about thirteen. Human turns during implementation: zero (unattended).
Defects reaching the branch: one, caught by CI, in the one recipe no
local trial covers. Review comments: one, on legacy code the rename
had merely moved. That distribution, nearly all interaction before the
code and almost none after, is the signature of design ownership, and
the inverse of the vibe-coding loop.

The discussion continued on how to get more from agents at the design
level; that part serves TODO item 14 and lives in
[set-based-design.md](set-based-design.md).
