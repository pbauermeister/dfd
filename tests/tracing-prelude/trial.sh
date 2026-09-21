# Trial of the tracing prelude, run by tests/test_tracing_prelude.py
# from the repository root: every helper context, ending with a guard
# that exits 3. Expected output (stdout and stderr merged) in
# expected.txt: no `+ echo`/`+ banner`/`+ step`/`+ set` line, the
# other commands traced as usual.
. ./tools/init-tracing.sh
banner "Banner"
step "a step"
true
true || echo "X should NOT print"
false || echo "Y should print"
true && echo "Z should print"
V=$(echo "inside command substitution")
banner2 "banner2: V=$V"
echo
echo "to stderr" >&2
echo "piped" | cat
true
if echo "in a condition"; then true; fi
ls no-such-file 2>/dev/null || { echo "in a brace group"; exit_code=1; }
f() { step "in a user function"; true; }
f
if [ ! -f .no-such-token ]; then
    echo "ERROR: guard message, then exit 3"
    exit 3
fi
