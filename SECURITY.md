# Security / Безопасность

Status: private local prototype and disabled-public-preview candidate, not a
production-secured multi-tenant service. No public Agent API is deployed.

The original pinned Core is trusted. External agent responses, proposed actions,
browser inputs and imported metadata are untrusted data. Never run third-party
agent code, evaluate model output or accept arbitrary callback URLs. A subprocess
is not a hostile-code sandbox. Existing built-in agents use a trusted registry.

The local web server binds only 127.0.0.1. Researcher test sessions use HttpOnly,
SameSite=Strict cookies and separate per-trial ephemeral agent bearer tokens.
Host/Origin, JSON size, lease/revision and retry identity are checked. These are
local capabilities, not production account authentication. Do not expose this
server through a public tunnel or reverse proxy. Console test codes stay local.

The public build disables all interactive Rules Lab controls and sends no agent
or researcher commands. A future backend needs edge rate limiting, per-trial
budgets, bounded concurrent Core work, global spending/circuit breakers, expiring
capabilities, atomic first-attempt receipts, durable idempotency and abuse tests.
No registration, billing or hosted untrusted execution is in v0.1 preview scope.

Current private Git history includes owner-approval records and private research
reports. Publish only a reviewed fresh allowlist export, never this `.git`.
Ignore local databases, artifacts, caches, credentials and raw experiment logs.
A pattern scan is limited evidence and does not clear source ownership.

For a suspected vulnerability, do not disclose tokens or exploit details in
public Issues. Use the Lab repository's private vulnerability-reporting channel
only after maintainers enable and verify it. No private reporting address or
channel is currently asserted. Routine reproducible non-sensitive bugs may use
Lab Issues after publication; Discussions are conditional on enablement.

RU: публичный backend не развёрнут. Локальный сервер нельзя публиковать через
туннель. Публичная сборка отключает интерактивность. История Git и исследования
остаются приватными; публикация — только по allowlist. Не отправляйте секреты
и детали уязвимостей в публичные Issues; защищённый канал ещё нужно настроить.
