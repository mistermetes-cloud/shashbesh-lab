# Functional release boundary — L4-RELEASE-02

| Classification | Actual state |
|---|---|
| PUBLICLY_WORKING | The separate Game website/repository were verified public on 2026-10-20. **No Lab website, online Gateway or public interactive API is verified published.** |
| LOCAL_ONLY | RU/EN Lab UI, Rules Lab, original-Core validation, Exam/Learning, local Agent Pull V1/client, workerd compatibility checks and disabled-static-preview build. These are tested locally, not online services. |
| DOCUMENTED_ONLY | Public Gateway/Agent registration design, cloud deployment/integration instructions, usage/credits architecture and publication procedures. Documentation/examples are not live endpoint availability. |
| PLANNED | Secure public Core adapter, rate/cost limits, durable atomic trial receipts, registration, online benchmarks/rankings and community channels after enablement. Payments and untrusted-code hosting are outside the current preview. |

The public build uses `mode=public-preview`, `interactive=false` and explicit
RU/EN disabled messaging. It exposes no login/token/proposal controls and makes
zero API POSTs in the verified Firefox scenario. Its static host has no backend
handler/binding. Browser flag manipulation cannot create an online Gateway.

Core's actual local workerd tests pass, but public interaction must remain off
until backend security, resource/concurrency/cost checks and publication approval
pass. A license approval alone does not approve a deployment or turn on a service.

RU: публично подтверждена отдельная игра; Lab не опубликован. Рабочие Core,
Exam/Learning и Agent Pull — локальные. Онлайн Gateway только спроектирован.
Публичный Rules Lab остаётся отключённым до проверок безопасности и стоимости.
