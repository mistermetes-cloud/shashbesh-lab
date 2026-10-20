# Real Cloudflare Workers-runtime verification — 2026-10-20

**Result: PASS for the bounded original-Core fixtures in actual local workerd.**
This supersedes the earlier VM-only preflight. It does not certify a public API,
all possible game states, long Replay or Cloudflare account quotas.

Pinned test tooling: `workerd@1.20261019.1` (`workerd 2026-10-19`),
`esbuild@0.28.2`, Node 20.20.2, Linux x86_64/glibc 2.35.
Compatibility date `2026-10-19`, **no compatibility flags**, no sockets and
explicit deny-all outbound networking. No cloud account/resources were used.

Original Core: `0.1.0-g0.65e1ec3`, archive SHA256
`acf4e1ef6af55b81607b1a9df9e8b684b6ac6bf0d95b39a389bc5e57d3c001fe`.
Its archive/extracted-file verification runs before testing. Core source, rules,
CSV, licenses and research databases are unchanged.

esbuild bundles the existing CommonJS modules to ESM, includes the unchanged
CSV as text and resolves noble-hashes to its browser/WebCrypto entry. No rule
function is reimplemented. Thirteen build inputs, bundle size **93,266 bytes**.
Bundle SHA256 and exact state hashes are in [WORKERD_RESULTS.json](WORKERD_RESULTS.json).
The local bundle is private test output under /tmp, not a website asset/export.

## Tests and measured resources

For each of 2/3/4 players: Core loads, geometry parses, Engine initializes,
state creates, legalActions evaluates, Core.applyAction accepts/rejects, invalid
Exam proposal leaves state hash unchanged, Exam seals first attempt, Learning
records failure then success, replay hash matches, 6+6 / 6+5 / empty-roll bonus
follow Core. Agent projection excludes the oracle, private state and RNG.
The same bundle in native Node produces identical initial/accepted/final hashes.
A four-player stress case repeats the fixed unit fixture 25 times; no tournament.

| Process case | User CPU s | System CPU s | Wall s | Peak RSS KiB |
|---|---:|---:|---:|---:|
| Empty workerd baseline | 0.02 | 0.01 | 0.04 | 44,800 |
| 2 players | 0.11 | 0.02 | 0.17 | 61,952 |
| 3 players | 0.10 | 0.02 | 0.18 | 62,080 |
| 4 players | 0.10 | 0.03 | 0.19 | 62,080 |
| 4 players, 25 repeats | 0.53 | 0.04 | 0.60 | 66,560 |

GNU time measures the **whole workerd process including startup**. Peak RSS is
not isolate heap; these numbers cannot prove a specific Cloudflare memory or
CPU allowance. They are one local series, not a percentile SLA. No production
routing, durable trial state, hostile payload load or deployed account limits
were exercised. Core search on complex positions/long Replay needs separate
budget tests. Current [Workers limits](https://developers.cloudflare.com/workers/platform/limits/)
are plan-dependent; do not infer Free-plan compliance from this result.

## Reproduce without listening on any port

Create an empty local tool directory under /tmp. Copy `runtime.package.json` to
its `package.json` and `runtime.package-lock.json` to its `package-lock.json`,
then run `npm ci --prefix <tool-dir> --cache <temporary-cache> --no-audit --no-fund`.
This installs only the pinned test tools outside the project/global environment.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tools/release/test_workerd.py --tool-root <tool-dir>
```

Requires the separately approved pinned Core artifact. The harness emits raw
logs, bundle/config and resource JSON to a fresh `/tmp/shashbesh-workerd-audit-*`.
`workerd test` is the actual runtime invocation, not a static build or Node VM.

## Minimal public integration

The Python/subprocess local backend still cannot be copied unchanged into
Workers. The feasible path is a **thin host adapter around this tested Core
bundle**: fixed bounded demonstration fixtures, manual demo dice, short trials,
Core-only validation, versioned Agent Pull projection and consistent trial owner
(e.g. Durable Object) for atomic Exam/idempotency/expiry. Add rate/concurrency/
request limits, global budgets and adversarial tests before enabling it.
No arbitrary code execution, registration, billing or long Replay is needed.
Until those gates pass, `build:public` keeps interaction disabled.

RU: настоящий workerd подтвердил ограниченные Core-сценарии для 2–4 игроков и
совпадение хешей Node. Это не проверка готового публичного сервиса или облачных
квот. Нужен тонкий безопасный host adapter; правила Core не меняются.
