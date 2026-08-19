#!/usr/bin/env bash
# Is this checkout the same code that is deployed?
#
#     ./check-sync.sh          report; exit 1 if the checkout is behind
#     ./check-sync.sh --sync   fast-forward to the remote first, then report
#
# Run this BEFORE reporting on repository contents -- before a diagnosis, a file
# check, a catalogue count, an image check, a build verification or a deployment
# check.
#
# Why it exists. This container has twice come back with a checkout at an older
# commit while origin was correct. Everything then reads as broken in a way that
# looks real: source folders "missing", products "never committed", counts wrong.
# On 19 Aug a diagnosis went out saying the customer's original photographs had
# never been committed and were lost. They were not lost. All 67 files were in
# the commit; the checkout was a day behind and was being read as though it were
# the truth. Nothing is more expensive than a confident report built on a stale
# tree, so the tree gets checked first and the verified hash is quoted in what
# follows.
#
# Deliberately not wired into build-hosted.js. That build runs offline by design
# -- every input it needs is committed -- and making it fetch from the network on
# every run would trade one failure mode for a worse one. This is a separate
# step, run by whoever is about to make a claim about what the repository holds.
set -u

cd "$(dirname "$0")" || exit 2
SYNC=0
[ "${1:-}" = "--sync" ] && SYNC=1

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "FAIL  not a git checkout"; exit 2
fi

if ! git fetch origin --quiet 2>/dev/null; then
  echo "WARN  could not reach origin -- the comparison below may be stale itself"
fi

BRANCH=$(git branch --show-current)
LOCAL=$(git rev-parse HEAD)
# --verify matters here. Plain `git rev-parse origin/` echoes its own argument
# back and exits 0, so on a detached HEAD -- where BRANCH is empty -- UPSTREAM
# became the literal string "origin/", which then poisoned the commit range and
# the counts came out as "?". --verify fails properly instead.
UPSTREAM=""
[ -n "$BRANCH" ] && UPSTREAM=$(git rev-parse --verify --quiet "origin/$BRANCH^{commit}" || echo "")
MAIN=$(git rev-parse --verify --quiet "origin/main^{commit}" || echo "")
DIRTY=$(git status --porcelain | wc -l | tr -d ' ')

printf 'branch        %s\n' "${BRANCH:-(detached)}"
printf 'local HEAD    %s\n' "$LOCAL"
if [ -n "$BRANCH" ]; then
  printf 'origin/%s  %s\n' "$BRANCH" "${UPSTREAM:-(no upstream branch)}"
else
  printf 'upstream      (detached HEAD -- comparing against origin/main)\n'
fi
printf 'origin/main   %s\n' "${MAIN:-(unknown)}"
printf 'working tree  %s\n' "$([ "$DIRTY" = "0" ] && echo clean || echo "$DIRTY change(s)")"

TARGET="${UPSTREAM:-$MAIN}"
if [ -z "$TARGET" ]; then
  echo "WARN  no remote to compare against; treat any file check as unverified"
  exit 1
fi

if [ "$LOCAL" = "$TARGET" ]; then
  echo "OK    checkout matches the remote"
  echo "      quote this hash in any report about repository contents: ${LOCAL:0:7}"
  exit 0
fi

# Behind, ahead, or diverged -- say which, because the fix differs.
BEHIND=$(git rev-list --count "$LOCAL..$TARGET" 2>/dev/null || echo "?")
AHEAD=$(git rev-list --count "$TARGET..$LOCAL" 2>/dev/null || echo "?")
echo "STALE checkout differs from the remote: $BEHIND behind, $AHEAD ahead"

if [ "$SYNC" = "1" ] && [ "$AHEAD" = "0" ]; then
  echo "      fast-forwarding..."
  if git merge --ff-only "$TARGET" >/dev/null 2>&1; then
    echo "OK    now at $(git rev-parse --short HEAD)"
    exit 0
  fi
  echo "FAIL  fast-forward refused -- untracked files may be in the way."
  echo "      move them aside and rerun; do not report on files until this is clean."
  exit 1
fi

echo "      DO NOT report files as present or missing from this tree."
echo "      run ./check-sync.sh --sync first, or reconcile by hand if ahead."
exit 1
