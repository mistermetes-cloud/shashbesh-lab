# Cloudflare architecture and compatibility / Совместимость

Architecture baseline: L4-ARCH-01; sources checked 2026-10-19.
Update L4-RELEASE-01 (2026-10-20): actual local workerd now passes bounded Core
fixtures for 2–4 players with Node hash parity. See
[real-runtime evidence](../release/CLOUDFLARE_RUNTIME.md). No cloud deployment,
public API or paid service was created. Production budgets remain unverified.

## RU — результат проверки закреплённого Core

Core: `0.1.0-g0.65e1ec3`, archive SHA256
`acf4e1ef6af55b81607b1a9df9e8b684b6ac6bf0d95b39a389bc5e57d3c001fe`.
Package is CommonJS, Node >=20, bundled `@noble/hashes` 1.8.0; primary export
provides `require`, no ESM import export. Geometry is external CSV passed into
`Core.parseGeometry`; engine uses structuredClone, typed arrays, synchronous
hashing and optional WebCrypto. These are not Python bindings.

`tests/core_edge_probe.cjs` loads the **unchanged** package JS graph in a Node VM
without process/Buffer/filesystem/Node builtin access inside Core modules.
The trusted test host loads source/CSV and supplies standard structuredClone,
TextEncoder/TextDecoder/WebCrypto. Resolver explicitly chooses bundled noble
`crypto.js` (WebCrypto) instead of Node conditional crypto entry. Eleven modules
load. For 2/3/4 players, create → initialRoll → 6+6 → Core actions → finishRoll →
replay produce identical native/preflight state hashes. This verifies a limited
portable dependency path; it is **not** a security sandbox or workerd test.

Existing Python adapter requires subprocess/select/filesystem; the Node Lab
worker requires fs/path/readline and private process IPC. They cannot run
unchanged in Workers. Cloudflare documents `child_process` and `readline` as
non-functional stubs: import success does not imply executable subprocesses.
See [official Node compatibility](https://developers.cloudflare.com/workers/runtime-apis/nodejs/).

At the ARCH-01 baseline no `wrangler` or `workerd` executable was installed.
The release follow-up installed pinned audit tools under /tmp only and tested
the bundled unchanged Core in actual workerd. No cloud login was attempted. Bundling the original
CommonJS graph with browser crypto resolution and text-importing the CSV in a
new adapter is plausible without modifying Core, but remains a gate. Bundled
file hashes and source artifact identity must both be recorded.

## RU — выбранное размещение

Pages хранит Research static RU/EN assets. Public Game остаётся отдельным Pages
проектом. Workers — auth/gateway и короткие orchestration-запросы. Durable Object
на матч сериализует leases/revisions; alarms назначают expiry, не держат процесс
в ожидании модели. D1 — tenant metadata, versions, attempts, usage index; R2 —
private immutable Core journals и компактные replay responses. Queue переносит
job IDs, а не многомегабайтные журналы. При redelivery нужен idempotent consumer:
[Queues гарантирует at-least-once delivery](https://developers.cloudflare.com/queues/reference/delivery-guarantees/).

В первом рабочем облачном варианте Core/Replay выполняет ограниченный внешний
**доверенный** compute на обычном Node, повторно используя Lab adapter и
ReplayService. Он получает assignment по исходящему каналу; локальный ноутбук
не превращается в публичный сервер. Новая служба, её хостинг и лимиты требуют
отдельного согласования. Базовый локальный режим продолжает работать автономно.

[Workers limits](https://developers.cloudflare.com/workers/platform/limits/):
128 MB memory per isolate; Free CPU 10 ms, Paid configured CPU ceiling up to
300 s. Wall time ожидания модели и CPU time — разные метрики. Наличие большего
лимита не доказывает пригодность Core search; значения и тариф перепроверять
перед реализацией. Сам Replay process tree локально достигал ~148 MiB RSS,
это не прямое измерение JS isolate heap, но исключает обещание fit-in-128MB.

[Durable Objects limits](https://developers.cloudflare.com/durable-objects/platform/limits/)
также требуют учёта CPU/storage и overload. Не переносить Python SQLite backup
в D1 как будто это тот же API; будущие схемы/миграции версионируются и работают
только в новой базе. Повторные доставки, DO restart и частично записанный R2
объект проходят reconciliation/outbox; незавершённый artifact не публикуется.

## Replay performance budget / Производительность

Keep async jobs, one active Replay per resource budget, bounded queue/cache,
source/Core/format checksums, cancellation and retry. Existing L2-V4 measurements:
cold UI up to **53.57 s**, Firefox frame gap up to **1.48 s**, Live p95
**78/60/65 ms** (98/172/323 actions). These are local observations, not cloud SLAs.
Do not put full replay/search synchronously inside gateway or match owner.
Optional future segmented verified projections/streaming require separate
profiling and checksum-preserving tests. Never disable original Core replay
verification to satisfy an edge CPU limit.

## EN — deployment gates

The current process adapter is incompatible with Workers unchanged. A restricted
JS dependency preflight passes for 2–4 players, including deterministic replay,
and the release follow-up now passes actual local workerd fixtures. Cloudflare
production performance and the public host adapter are still unverified.
No runtime was deployed. Keep trusted bounded Node compute as the
initial execution option; edge services coordinate identity, leases and jobs.

Before considering in-isolate execution: bundle unchanged Core + CSV, pin
compatibility date/resolution, run workerd locally, compare hash/event/action
fixtures (capture, corner, bonus, no-action, all winners), measure startup/CPU/
heap with long 4-player matches, and exercise restart/replay integrity. Reject
the deployment path if budgets fail; keep Core compute outside the edge.
Keep Public Game and Research Lab deployment pipelines/resources independent.
