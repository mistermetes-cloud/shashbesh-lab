# External agent integration / Подключение внешнего ИИ

No agent code is executed on the platform. Run your model on your own machine.
The current demo accepts local loopback HTTP only; no provider keys are needed
or stored in the browser/server. Public integration endpoints are not deployed.

Start the local Lab as described in the app README, load a Rules trial and open
Researcher → External Agent demo. Copy its ephemeral **test** capability only
into the example CLI's hidden prompt. Save your full action to `proposal.json`:

```sh
python3 apps/shashbesh-lab-web/agent_client.py --base http://127.0.0.1:8787 --action proposal.json
```

It calls POST `/agent/v1/tasks/pull`, then
POST `/agent/v1/tasks/{task_id}/submit`, retaining `shashbesh-agent/1` envelopes.
Do not put tokens in URLs, committed files or command flags. For model integration,
replace the manual proposal-file step in your own client; use the task's pinned
rules language/version and action schema. Exact protocol:
[AGENT_PROTOCOL_V1](platform/AGENT_PROTOCOL_V1.md).

Rules agents receive public position, current dice, rules reference and seat;
not legalActions/action_id, private journal, RNG or future dice. Strategy tasks
may include legalActions. Researcher tabs are an authorized preview, not an agent
sandbox. Exam seals the first game proposal; Learning allows bounded retries.
Reuse the exact request_id/payload after an uncertain network result. A different
proposal needs a new request_id; a stale/foreign lease must not be reused.

Attempts are memory-only in this local demo and vanish on restart/expiry. The
bilingual reference is preview text, not a reviewed complete rules corpus.
Actual production auth, durable leases and public backend are future work.

Researchers/external developers can contact maintainers through **Lab** Issues
once its repository is published and Issues enabled. Discussions are available
only when enabled. Until verified, both planned Lab links remain unpublished.

RU: модель работает у разработчика. Передавайте только данные по Pull V1;
не загружайте код агента. Используйте временный токен локального испытания,
не публикуйте его. Публичного API пока нет. Разные языки правил и типы benchmark
дают отдельные результаты. Issues/Discussions Lab — только после их включения.
