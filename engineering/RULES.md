# Rules that apply to every edit

- Every commit message and PR title is in conventional form; the
  `commit-msg` hook enforces it, `make help-cc` prints the types.
- After generating or modifying Python code, run `make format`, then
  `make lint`; fix all errors before committing. `make test` before
  every push. The git hooks installed by `make require` run `make
lint` at commit and `make test` at push and refuse on failure; read
  the exit of a command all the same, a hook can be skipped.
- Only append to the root `CLAUDE.md` when explicitly requested by the
  user; a new rule is a map row there or a paragraph in the document
  the map names.
