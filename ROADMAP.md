# Roadmap / План

v0.1.0 candidate: local bilingual web foundation, Core-backed Rules Lab,
Exam/Learning, Agent Pull V1, real workerd compatibility evidence and a
fail-closed public static preview. None of the Lab is published yet.

1. Resolve Lab-wide license and source ownership; reconcile limited Core grant,
   legacy manifest annotation and redistribution/source-notice requirements.
2. Review the fresh source allowlist and independent history; approve publication.
3. Publish the disabled RU/EN static preview only with explicit authorization.
4. Implement a thin Workers/DO trial adapter around the unchanged Core bundle.
   Add rate limiting, atomic Exam receipts, quotas, replay-safe retries, expiry,
   durable attempts, security tests and real account CPU/heap-budget validation.
5. Review bilingual rules/fixtures, then enable bounded public Exam/Learning.
6. Add scoped developer identity/organizations and persistent Agent Pull leases.
7. Add controlled Strategy benchmarks and separate statistically valid rankings.
8. Profile long Replay/UI further; keep heavy Replay isolated from live requests.

Real billing and hosted third-party code require separate scope/security review.
The project is ready to pause after this handoff; Game development is the next
priority. Resume from `docs/PROJECT_HANDOFF_V0_1.md`, not by recreating the app.

RU: сначала лицензия и allowlist, затем разрешённая публикация отключённого
статического предпросмотра. Публичный Core backend — отдельный этап с лимитами,
защитой и проверенной методологией. Сейчас Lab готов к паузе; приоритет — игра.
