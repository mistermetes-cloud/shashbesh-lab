# Implementation roadmap / План реализации

## RU — завершённый архитектурный этап

L4-ARCH-01 создаёт девять документов, локальный Agent Pull JSONL-прототип,
независимый пример клиента, тесты protocol/disclosure/attempt semantics и
Core dependency preflight. Существующие Lab-компоненты не переписываются.
Ничего не развёртывается, платные сервисы не подключаются, commit не создаётся.

| Gate | Следующая работа | Критерий приёмки |
|---|---|---|
| ARCH-02 | Review protocol + bilingual rules corpus | согласованы observation/action schemas, язык, invalid/timeout policy |
| RUNTIME-01 | Local workerd adapter spike | unchanged Core hashes совпадают; CPU/RAM измерены; Node fallback сохранён |
| DATA-01 | New platform schema + journal storage | versioned migrations, outbox, crash restore, никакой записи в research DB |
| AUTH-01 | Developer/org registration + scoped tokens | tenant isolation, rotation/revoke, audit redaction tests |
| GATEWAY-01 | Authenticated local HTTP Pull | lease generations/CAS, duplicate/stale/race/expiry, size/depth/rate limits |
| ENGINE-01 | Integrate decisions with existing controller | 2–4 independent agents; all Core transitions; full attempt audit |
| BENCH-01 | Reviewed hidden fixture bank | Exam first attempt; Learning success@k; leakage tests; separate cohorts |
| UI-01 | RU/EN research frontend | translation parity, mobile/zoom, stable board, accessible controls |
| USAGE-01 | Metering + free quotas/ledger | atomic reservations, retry dedup, refunds and reconciliation |
| PERF-01 | Replay follow-up | no Live blocking, payload/memory budgets, Firefox profiling |
| RELEASE-01 | Deployment decision | explicit authorization, rollback/restore, verified runtime/resource plan |

Платные credits и hosted third-party code — дальнейшие самостоятельные решения,
не обязательная часть первого запуска. Внешние модели через Pull не требуют
серверного хранения provider keys. До AUTH/GATEWAY/DATA gates прототип нельзя
открывать для публичных пользователей.

Локальное воспроизведение:

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q
PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 python3 examples/platform_pull_agent.py
node tests/core_edge_probe.cjs
node --check lab/viewer_assets/viewer.js
node --check lab/shashbesh_worker.cjs
node --check tests/core_edge_probe.cjs
git diff --check
```

Test outputs and integrity manifests stay under `/tmp`; existing SQLite sources
are unchanged. Full-suite result is recorded in the completion report. Existing
78 tests must remain; new tests cover 2/3/4-seat external choices, replay hash
validity, first-error secrecy, Learning retry/budget, protocol versions, leases,
revision/type checks, idempotency conflict, strict JSON, nested disclosure and
an independently launched client. Runtime preflight is explicitly non-workerd.

## EN — phased delivery

This phase delivers architecture and a local demonstration, not a public
platform. Gate subsequent work on reviewed bilingual rules, durable data,
tenant authentication, leases/CAS and Core-backed decision integration before
opening any network service. Reuse the controller and Replay pipeline. Cloud
execution requires a separate verified runtime/performance decision; a Node
compute fallback remains available without changing rules.

Keep independent Public Game and Research Lab release boundaries. Billing
payments, hosted untrusted agent code and deployment require separate scope.
Stop after this architecture stage; do not silently begin production work.
