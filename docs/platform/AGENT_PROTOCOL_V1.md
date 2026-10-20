# Agent Protocol v1 / Протокол агента v1

Status: candidate specification. Wire marker `shashbesh-agent/1`; independent
from existing `lab-node-protocol/1`, Lab protocol 1.1 and Live controller API.

## RU — транспорт и идентификация

Предпочтителен Agent Pull: модель запускается разработчиком и сама запрашивает
задачу. Будущие HTTPS endpoints: POST `/agent/v1/tasks/pull` и
POST `/agent/v1/tasks/{task_id}/submit`. Это проект контракта, сейчас публичного
сервера нет. Bearer token привязан к org + неизменяемой agent_version; pull и
submit имеют отдельные scopes. Agent_id определяется токеном, не телом запроса.
Отсутствие работы: 204; ошибки: 400 schema/version, 401 authentication,
403 scope/tenant, 409 stale/receipt conflict, 410 lease expired, 413 size,
429 quota + Retry-After, 503 compute unavailable. Схемно корректное, но игровое
неверное действие возвращает 200 с accepted=false и фиксируется как попытка.

Локальный прототип использует JSONL stdin/stdout и operations pull/submit;
доступ — владение pipe, без токенов и HTTP. Это тот же decision payload,
но не реализация production authentication, durable leasing или billing.

```json
{"protocol":"shashbesh-agent/1","operation":"pull"}
```

Task содержит protocol, task_id, lease_id, revision (integer), agent_id,
benchmark (strategy/rules), mode (exam/learning), core_version, core_sha256,
action_schema, observation, geometry, lease_seconds. Public observation:
active_seat 0–3, phase, pieces (Core owners 1–4), players (Core IDs), dice,
remaining_actions, forced_piece_id, extra_roll. Геометрия — оригинальные Core
cells/homes/starts/corners. Seed и worker_state_id никогда не выдаются.
Strategy дополнительно получает **legalActions**; Rules поле отсутствует,
а не равно пустому списку. Нет альтернатив в ошибках, hints и debug-полях.

```json
{"protocol":"shashbesh-agent/1","operation":"submit","task_id":"<task>",
 "lease_id":"<lease>","revision":0,"request_id":"client-unique-1",
 "action":{"pieceId":"<Core piece>","kind":"move","value":1,
 "from":"<Core cell>","to":"<Core cell>","path":["<Core cell>"],"captureIds":[]}}
```

Пример иллюстрирует структуру, а не гарантированно допустимый ход.
Action schema `core-action/0.1.0-g0.65e1ec3` повторяет неизменённый Core Action:
pieceId:string; kind:deploy|move|corner_jump; value:number; from:string|null;
to:string; path:string[]; captureIds:string[]; optional jump:{from,to,path}.
Пути и captureIds в Rules вычисляет агент. Сервер не исправляет его предложение.
Допустимость полного объекта устанавливает только Core. Версия action schema
входит в benchmark cohort, любое изменение смысла требует новой major version.

Submit response: protocol/task_id/request_id, accepted:boolean,
feedback:accepted|invalid_action, trial_closed:boolean, revision:integer.
Learning повторяет submit с новым request_id на том же decision/revision после
неверной попытки. Правильное действие увеличивает revision и закрывает trial.
Exam закрывается после первой игровой попытки. Envelope/lease ошибки не являются
игровыми попытками; отдельно измеряются protocol failures и timeouts.

Один активный lease на decision, повторный pull возвращает тот же task.
После истечения production lease перевыпускается только с новой generation;
старый submit отвергается. Lease не продлевается автоматически повторным pull.
Идемпотентность: (org, agent_version, task_id, request_id) + канонический payload
hash; одинаковый retry возвращает исходный receipt, другой payload — conflict.
Receipt проверяется до срока lease, но только после авторизации того же tenant.
Параллельные submit требуют compare-and-swap decision revision у владельца.

Лимит прототипа: 64KiB UTF-8 message, ≤10 попыток (обычно 3), lease ≤300s
(обычно 60s), одна задача, один агент; receipt/audit только в памяти. JSON object,
без duplicate keys, NaN/Infinity, неизвестных envelope полей и bool revision.
Production добавит лимит глубины, rate limit, durable receipts и bounded responses.

## EN — interoperable external agents

Agents pull observations and submit complete Core actions; the platform does
not call arbitrary developer URLs. Bind identity to authenticated tenant and
immutable agent version. Strategy includes legalActions; Rules omits it and all
answer-bearing traces. Tokens, seeds and future RNG remain private.

Validate version, byte/schema limits, lease and revision before evaluating a
proposal. Only original Core defines legality. Never auto-correct actions.
Exam seals the first game attempt; Learning permits bounded retries with generic
feedback. Preserve exact proposals privately. Replays contain accepted actions;
attempt audits also retain invalid actions and protocol failures separately.

Retry the exact same request_id/payload after transport failure; conflicting
reuse is an error. Lease expiry and concurrency use durable generations/CAS in
the future service. The JSONL prototype demonstrates a single external process
interaction and does not provide production multi-tenant security.

## Local reproduction / Локальный запуск

```sh
PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 python3 examples/platform_pull_agent.py
PYTHONPATH=. python3 -m lab.platform_agent --benchmark rules --mode learning --players 4
```

First command launches a trusted bridge as a separate process and selects one
Strategy action without external network services. Second accepts JSONL on
stdin; an external client may implement its own rule reasoning. It has no
listener, modifies no SQLite, and exits on EOF. No model provider is connected.
