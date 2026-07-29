#!/usr/bin/env bash
#
# Every gate this branch is meant to hold, in one command.
#
#     scripts/check_gates.sh [--offline] [--skip-parity] [--skip-recall]
#                            [--skip-live] [--seed N]
#
# Five things have to stay true for the search work to be safe to deploy, and
# each is checked by a different harness for a different reason:
#
#   1. unit      — everything under tests/: the /xref shaping logic and the
#                  shed/coalescing regressions (offline; the latter drives the
#                  real handlers through a loopback aiohttp server)
#   2. client    — the client's request shaping (offline, monkeypatched)
#   3. parity    — /search still orders results exactly like the website's JS.
#                  Needs node and a geppetto-vfb checkout, because it runs the
#                  real comparator, not a description of it.
#   4. recall    — the exact-label boost still fixes what it was added to fix
#                  and still moves nothing else. Hits the live Solr index.
#   5. live      — the client's live tests against a server started *from this
#                  checkout*. /search and /xref do not exist on the public
#                  deploy yet, so pointing the live tests at v3-cached would
#                  only ever prove that. Started here, they are a real gate:
#                  the /xref round trip that tests/test_xref.py deliberately
#                  does not attempt offline runs end to end before merge.
#
# Gate 1 is the whole directory rather than a list of files, so a test added
# later is covered by having been written rather than by also remembering to
# name it here.
#
# A missing prerequisite is a FAILURE, not a pass: "could not check" and
# "checked, fine" must not look the same from the exit code. Opt out explicitly
# with the flags above and the script says so in the summary rather than quietly
# counting it as green — and still exits non-zero for anything that ran and
# failed. `--offline` is the shorthand for "gates 1 and 2 only"; use it on a
# plane, not before a merge.
#
# Exit codes: 0 all green; 1 a gate failed; 2 the environment is not set up
# (dependencies missing) — a distinct code because that is not a verdict on the
# code.
set -uo pipefail

cd "$(dirname "$0")/.."
REPO="$PWD"
GVFB="${GEPPETTO_VFB:-/tmp/gvfb}"
SKIP_PARITY=0
SKIP_RECALL=0
SKIP_LIVE=0
SEED=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --offline)     SKIP_PARITY=1; SKIP_RECALL=1; SKIP_LIVE=1 ;;
        --skip-parity) SKIP_PARITY=1 ;;
        --skip-recall) SKIP_RECALL=1 ;;
        --skip-live)   SKIP_LIVE=1 ;;
        --seed)        # `${2:-}` on a trailing --seed yields "", and an empty
                       # SEED is indistinguishable from "no --seed given" three
                       # lines further down — so the flag would be silently
                       # dropped and the gate would run the default sample while
                       # the operator believed it had widened the net. Refuse.
                       if [[ $# -lt 2 || -z "$2" ]]; then
                           printf -- '--seed requires a value\n' >&2; exit 2
                       fi
                       SEED="$2"; shift ;;
        -h|--help)     sed -n '2,40p' "$0"; exit 0 ;;
        *)             printf 'unknown option: %s (try --help)\n' "$1" >&2; exit 2 ;;
    esac
    shift
done

# Importing vfbquery otherwise patches in the SOLR result cache, which is a
# network dependency the offline gates do not want.
export VFBQUERY_CACHE_ENABLED="${VFBQUERY_CACHE_ENABLED:-false}"

results=()
rc=0

run () {                       # run <name> <command...>
    local name="$1"; shift
    printf '\n=== %s %s\n' "$name" "$(printf '=%.0s' {1..40})"
    if "$@"; then
        results+=("PASS  $name")
    else
        results+=("FAIL  $name")
        rc=1
    fi
}

# 0 — preflight ---------------------------------------------------------------
# PYTHONPATH below makes the *source tree* importable; it does nothing about the
# runtime dependencies that `vfbquery/__init__` pulls in (pysolr, marshmallow,
# psycopg...). Without this check the gate dies at collection with a bare
# ModuleNotFoundError, which reads as a broken test suite rather than an
# incomplete install — the exact confusion that `pip install -e . --no-deps`
# caused in CI.
if ! env PYTHONPATH="$REPO/src" python3 -c "import vfbquery.ha_api" >/dev/null 2>&1; then
    printf 'vfbquery is not importable — its runtime dependencies are missing.\n' >&2
    printf 'Install them first:\n\n    pip install -e %s\n\n' "$REPO" >&2
    printf 'Details:\n' >&2
    env PYTHONPATH="$REPO/src" python3 -c "import vfbquery.ha_api" 2>&1 | tail -3 >&2
    exit 2
fi

# 1 + 2 — offline tests -------------------------------------------------------
# PYTHONPATH is set explicitly for both so the gate tests *this* checkout rather
# than whatever version happens to be installed on the box running it.
run "unit    (xref + shed/coalescing + resilience)" \
    env PYTHONPATH="$REPO/src" \
    python3 -m pytest "$REPO/tests" -q

run "client  (request shaping)" \
    env PYTHONPATH="$REPO/clients/vfbquery-client/src" \
    python3 -m pytest "$REPO/clients/vfbquery-client/tests" -q

# 3 — parity against the real website JS --------------------------------------
if [[ $SKIP_PARITY == 1 ]]; then
    results+=("SKIP  parity  (skipped by flag; ordering is UNVERIFIED)")
elif ! command -v node >/dev/null 2>&1; then
    results+=("FAIL  parity  (node not installed — cannot run the website comparator)")
    rc=1
elif [[ ! -d "$GVFB" ]]; then
    results+=("FAIL  parity  (no geppetto-vfb checkout at $GVFB — clone it or set GEPPETTO_VFB:
              git clone --depth 1 https://github.com/VirtualFlyBrain/geppetto-vfb $GVFB)")
    rc=1
else
    # --fuzz is on deliberately. The 22 hand-picked cases are the ones I already
    # know discriminate; the comparator is non-transitive, so the cases that
    # would catch a *new* divergence are by definition ones I have not thought
    # of. Without this the gate re-checks what was already checked.
    #
    # The seed is fixed by default so a failure is reproducible from the summary
    # line alone; pass --seed to draw a different 56 and widen the net.
    parity_cmd=(python3 "$REPO/docs/search-parity/check_parity.py" --fuzz 56)
    [[ -n "$SEED" ]] && parity_cmd+=(--seed "$SEED")
    run "parity  (vs website JS)" env GEPPETTO_VFB="$GVFB" "${parity_cmd[@]}"
fi

# 4 — recall against the live index -------------------------------------------
if [[ $SKIP_RECALL == 1 ]]; then
    results+=("SKIP  recall  (skipped by flag; the exact-label boost is UNVERIFIED)")
else
    run "recall  (exact-label boost)" \
        python3 "$REPO/docs/search-parity/check_recall.py" --gate
fi

# 5 — the client against a server built from this checkout --------------------
if [[ $SKIP_LIVE == 1 ]]; then
    results+=("SKIP  live    (skipped by flag; /search and /xref are UNVERIFIED end to end)")
else
    PORT="${VFBQUERY_GATE_PORT:-8971}"
    LOG="$(mktemp -t vfbquery-gate-XXXXXX.log)"

    # Every probe gets `--max-time`. Without it, a *wedged* server — one holding
    # the port and accepting connections but never answering — blocks each curl
    # indefinitely, and the retry loop below turns that into a hang measured in
    # minutes with no output. That happens for real: kill this script with
    # Ctrl-C or a timeout and the EXIT trap does not run for every signal, so
    # the previous run's server can still own the port on the next one. Two
    # seconds is far longer than a local /health, which is a dict literal.
    probe() { curl -fsS --max-time 2 "http://127.0.0.1:$PORT/health" >/dev/null 2>&1; }

    # Refuse to start on an occupied port rather than starting, failing to bind,
    # and then reporting the *other* process's health as this checkout's. That
    # misreads either way round: a stale server passes the gate for code that is
    # no longer there, or a wedged one fails it for code that is fine.
    if probe || curl -fsS --max-time 2 "http://127.0.0.1:$PORT/" >/dev/null 2>&1; then
        results+=("FAIL  live    (port $PORT is already serving; stop it, or set VFBQUERY_GATE_PORT)")
        rc=1
    else
        # 127.0.0.1 rather than 0.0.0.0: this server is up for the length of a
        # test run and has no business being reachable from off the box. It also
        # lands inside the default TRUSTED_NETWORKS, so the security middleware
        # does not 404 the new paths at us.
        env PYTHONPATH="$REPO/src" VFBQUERY_WORKERS=2 \
            python3 -m vfbquery.ha_api --host 127.0.0.1 --port "$PORT" \
            >"$LOG" 2>&1 &
        SERVER_PID=$!
        # INT and TERM as well as EXIT: an interrupted run that leaves the
        # server behind is what makes the *next* run fail on the port check, and
        # "it worked when I reran it" is a bad way to find that out.
        trap 'kill "$SERVER_PID" 2>/dev/null; wait "$SERVER_PID" 2>/dev/null' EXIT INT TERM

        for _ in $(seq 1 60); do
            probe && break
            kill -0 "$SERVER_PID" 2>/dev/null || break
            sleep 1
        done

        if ! probe; then
            results+=("FAIL  live    (server from this checkout never became healthy; log: $LOG)")
            tail -20 "$LOG" >&2
            rc=1
        else
            # -k selects the live set by name: the offline tests already ran as
            # gate 2, and running them twice would pad the count without adding
            # a check.
            run "live    (client vs local server)" \
                env PYTHONPATH="$REPO/clients/vfbquery-client/src" \
                    VFB_LIVE_TESTS=1 VFB_API_BASE="http://127.0.0.1:$PORT" \
                python3 -m pytest "$REPO/clients/vfbquery-client/tests" -q \
                    -k "live" -p no:cacheprovider
        fi

        kill "$SERVER_PID" 2>/dev/null
        wait "$SERVER_PID" 2>/dev/null
        trap - EXIT INT TERM
    fi
fi

# -----------------------------------------------------------------------------
printf '\n%s\nSummary\n%s\n' "$(printf '=%.0s' {1..48})" "$(printf '=%.0s' {1..48})"
printf '  %s\n' "${results[@]}"
if [[ $rc == 0 ]]; then
    printf '\nAll gates green.\n'
else
    printf '\nOne or more gates failed — see above.\n'
fi
exit $rc
