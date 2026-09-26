# Prose style

The style sheet for the prose of this project: `doc/`, the top-level
`README.md`, `engineering/`, the devlogs, the discussions, PR bodies
and commit bodies. Code comments follow `engineering/COMMENTING.md`.
The reader is a developer or an agent; the aim is text that reads as
written by the author, plainly, and not as generated.

The sheet takes "The Elements of Style" (Strunk & White) as read: the
book's rules of usage and composition apply, and this sheet does not
repeat them. It records what the project adds: the departures kept on
purpose, the rules of the book that need pressing, the forms preferred,
and the tells that mark generated text. When a rule and clarity
disagree, clarity wins; the rule serves the reader, never the reverse.

## Departures from the book, kept on purpose

- No em-dash in prose, not even for an abrupt break. Use a comma, a
  semicolon, a colon or a full stop; for a paired break, parentheses.
  The dash stays permitted in headings and labels as a separator.
- "So", "Hence" and "Now" open a sentence as logical pivots.
- "i.e.", "e.g." and "aka" belong in running text; they gloss a term
  on first use, and the term is then used freely.
- Parentheses are a frequent device, for a qualification or an aside.
  Keep them short; a footnote is not an aside.
- American spelling (color, neighbor), as the code and the DSL use it.

## From the book, the rules to press

- Use the active voice. "The checker reports the error", not "the
  error is reported by the checker".
- Keep related words together: the subject next to its verb, the
  modifier next to what it modifies.
- Put the emphatic words at the end of the sentence.
- Keep one tense in a passage. The present is the default for what the
  tool does and what a document says; the past for what happened in a
  task.
- Omit needless words. "The flow is dropped", not "the flow ends up
  being dropped"; "because", not "due to the fact that".
- Use definite, specific, concrete language: the file, the flag, the
  number, not "the relevant configuration".

## Forms preferred

- The point first: in a section, in a paragraph, in a bullet.
- One idea per paragraph, short paragraphs. A reader who skims the
  first sentence of each still gets the gist.
- Short sentences by default, varied on purpose; one longer sentence
  may carry an explanation. Uniform medium-length sentences are the
  texture of generated text.
- Full clauses, linked by a comma, a semicolon, a colon or "but". Two
  related thoughts make one sentence, not two fragments.
- A list for the enumerable and the sequential, prose for a narrative
  or an argument; items parallel in form. Neither bullet soup (full
  thoughts that should flow) nor a wall of text (a list in disguise).
- A one-line "why" before a procedure or a block, no more.
- Plain vocabulary, the specific over the generic. Enthusiasm, when
  any, is understated ("handy", "neat"), never inflated.
- The imperative in how-to text ("Run `make test`"), the indicative
  elsewhere.
- A hedge only when the uncertainty is real, then a precise one ("on
  a cold cache"), not a defensive one ("generally", "arguably").

## Tells to avoid

The forms below mark a text as generated. Each has a plain form.

| Tell                                                                                      | Write instead                                               |
| ----------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| Em-dash in prose                                                                          | comma, semicolon, colon, full stop, parentheses             |
| The elliptic apposition: "..., an error."; "It is X: a Y."                                | a full clause: "..., which is an error."; "X is a Y."       |
| The staccato correction: "Not per day. Per week."                                         | linked: "not per day, per week"; "not per day but per week" |
| The pivot that counters the previous sentence for drama                                   | say the true thing once                                     |
| The elevation pivot: "not just a tool, a partner"                                         | a concrete, linked contrast, or nothing                     |
| The tricolon by reflex: "clear, concise and compelling"                                   | as many items as the content has                            |
| "Furthermore", "Moreover", "Additionally", "In summary", "It's worth noting", "Note that" | "So", "Hence", "Also", or just the next point               |
| Scaffold openers: "Here's the thing", "At its core", "Let's dive in"                      | the point                                                   |
| "In order to", "in terms of", "as mentioned above", "the fact that"                       | "to", the thing itself, a link, "that"                      |
| Inflated vocabulary: "leverage", "delve", "unlock", "robust", "seamless", "game-changer"  | "use", "look into", plain adjectives or none                |
| A jargon term re-explained at every use, or all terms defined up front                    | one gloss on first use, then the term                       |
| The recap close: "In summary, ..."                                                        | stop when the content stops                                 |
| A heading or a label where the passage is a narrative                                     | paragraph logic                                             |

The staccato rule is not a ban on short sentences, which carry
independent thoughts. The tell is one thought cut into fragments for
effect, most often a correction.

## Before delivering

- Read the text once for the tells table, once aloud for rhythm.
- Check that each paragraph opens with its point and holds one idea.
- Check the tense of each passage and the voice of each sentence.
- Check every gloss: first use only, and the term used freely after.

Source: the author's blog-post style rules, of which this sheet is the
subset that fits technical documentation; their anecdotes, humor,
first-person storytelling and British spelling stay with the blog.
