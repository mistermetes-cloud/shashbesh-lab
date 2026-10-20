# Security model / Модель безопасности

## RU — границы доверия

Доверены только закреплённый Core, controller/evaluator и управляемый compute.
Агенты, model output, подсказки, developer metadata, replay uploads и браузер
недоверенные. Внешний агент работает у разработчика и Pull-запросами получает
только назначенные ему задачи. Не скачивать/исполнять agent plugins, pickle,
JS/Python snippets или произвольные callback URLs. Prompt injection — текст,
не команда серверу. Не обещать защиту от анализа публично доступного Core:
Rules измеряет соблюдение протокола; закрытость кода правил не предполагается.

Будущая регистрация: verified developer account, organization и роли owner,
admin, researcher, viewer. Membership проверяется на каждом ресурсе. API token
имеет случайный секрет ≥256bit, identifier prefix, keyed hash на сервере,
org/agent-version scopes, expiry, last-used, rotation/revocation. Секрет
показывается один раз, не хранится открытым и не попадает в task/log/URL.
Web session — Secure/HttpOnly/SameSite cookie + CSRF; точный origin allowlist,
никакого общего auth-cookie с Public Game. Не использовать API token в localStorage.

Gateway ограничивает body/depth/time/requests/inflight per org + per agent;
таймаут модели не держит Core-процесс. Token определяет binding; другой tenant
не может прочитать task, receipt, journal, export или usage. Сроки lease и
revision проверяются вместе с одноразовым decision CAS. Логи не содержат headers,
cookies, secrets. В Rules даже диагностический endpoint не раскрывает oracle.
Сырой Core replay до закрытия exam недоступен участнику испытания.

Compute принимает только подписанные внутренние задания с version/checksum,
не ходит на URL агента; default-deny egress. Agent Pull избегает SSRF. Вариант
будущего hosted agent требует отдельного sandbox/container, CPU/RAM/process/
network/disk budgets и отдельного security review; он не входит в эту поставку.
Не использовать обычный subprocess как доказательство безопасности чужого кода.

Права на R2 private, временные signed download URLs с tenant checks; ключи cache
с tenant/visibility/decision cohort. Ответы Rules и публичные replays не делят
один cache namespace. Токены внешнего провайдера остаются у разработчика.
D1 backup/PITR и объектный retention проектируются отдельно; rollback кода не
отменяет уже принятые ledger записи. Revocation и удаление аккаунта сохраняют
минимальные audit IDs по согласованной политике без открытых персональных данных.

Локальный JSONL-прототип доверяет владельцу pipe, не имеет HTTP, authentication,
организаций, rate limiter или durable audit. Он запускает только доверенный
Lab bridge/Core. Ни один production security claim этим не подтверждается.

## EN — authorization and containment

Treat agents and model responses as untrusted data. Prefer developer-hosted
Pull: no arbitrary callbacks, code imports or provider credentials on the
platform. Core and evaluator are trusted; the agent never receives their private
state. Public Game and Research Lab have separate identity/storage boundaries.

Design scoped expiring/revocable organization tokens, hashed secrets, verified
membership and exact resource authorization. Separate browser session/CSRF from
agent bearer authentication. Redact logs and private benchmark traces. Enforce
budgets, decision CAS and lease generations. Production hosted-code isolation
requires a dedicated sandbox review. The local pipe demo is a functional
protocol demonstration, not an authentication or hostile-code sandbox.
