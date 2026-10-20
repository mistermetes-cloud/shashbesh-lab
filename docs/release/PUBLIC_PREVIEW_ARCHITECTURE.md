# Smallest honest public preview

Release mode: **static RU/EN public preview; interactive backend disabled**.
Local Rules Lab remains functional. No public account, payments, untrusted agent
execution or API is created by this preparation stage.

Build separation:

- `npm run build` → `dist/`: local UI, researcher test-session login and Core demo.
- `npm run build:public` → `dist-public/`: explicit public-preview notice,
  Rules Lab disabled screen, documentation and developer examples.
- `wrangler.jsonc` points only at `dist-public/`. Pages build command must be
  `npm run build:public`. Both source/builds belong to the Lab project only.
- Runtime `build-config.json` defaults fail-closed if missing/unreadable.
  It is a presentation gate, not production authorization. The static hosting
  plan defines **no API handler/binding**, so editing browser JS cannot create
  a public backend. Never deploy `server.py` behind the public hostname.

The real workerd result establishes Core feasibility, not backend readiness.
A future bounded interactive demo needs a small Worker adapter plus trial owner:
fixed Core-created fixtures, bounded manual dice, <=10 attempts, expiring anonymous
capabilities, atomic first-attempt receipt, durable retry identity, response
allowlists and per-IP/trial/global resource limits. No agent source execution.
Use unchanged Core Engine methods; retain original event/hash semantics.

Security acceptance before enabling: malformed/deep/oversized JSON, cross-trial
access, duplicate/racing submits, expiry/restart, oracle leakage, rate/cost caps,
CPU timeout and memory stress, exact Node/workerd behavior parity, bilingual
rules review. Keep long Replay out of synchronous edge requests.

Current public-preview Firefox check traverses 18 RU/EN routes, sees disabled
Rules UI in both languages, no researcher/token/action controls and **zero API
POSTs**, served as static files without starting a Core backend.

RU: первый публичный вариант — честный статический предпросмотр. Рабочие Exam/
Learning пока только локальные. Core в workerd работает, но публичный adapter,
лимиты и лицензирование — отдельные незакрытые gates.
