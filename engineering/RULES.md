# Rules that apply to every edit

- Every commit message and PR title is in conventional form; the
  `commit-msg` hook enforces it, `make help-cc` prints the types.
- After generating or modifying Python code, run `make format`, then
  `make lint`; fix all errors before committing. `make test` before
  every push.
- Only append to the root `CLAUDE.md` when explicitly requested by the
  user; a new rule is a map row there or a paragraph in the document
  the map names.
