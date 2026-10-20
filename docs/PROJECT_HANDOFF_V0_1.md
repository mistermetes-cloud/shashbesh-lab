# ShashBesh AI Lab — project handoff v0.1

```text
LAB_RELEASE: v0.1.0 candidate
LAB_DEVELOPMENT: READY_TO_PAUSE
GAME_DEVELOPMENT: NEXT_PRIORITY
LAB_PUBLICATION: NOT_CONFIRMED
```

## Implemented

The private local Lab retains Core-backed 2–4-player Live Arena, deterministic
checkpoints, built-in AI agents, Replay timeline/roll groups and bounded isolated
Replay processing. L4 adds the bilingual research architecture and separate
`apps/shashbesh-lab-web/` frontend: nine RU/EN routes, local Rules Lab, Exam,
Learning, Researcher/Agent serialization boundaries and Agent Pull V1 client.

The last architecture checkpoint was `e18307d05d590fdd5cc17c03a90074c85b6cf7bd`.
The authorized 17-file web checkpoint is
`34cdc7497116825e3a9807461e2db1f6439520f4` with message
`L4-WEB-01: bilingual research web foundation`.
Subsequent release preparation remains **uncommitted**: public-build gate,
runtime verification tools/evidence and publication documentation. No other
local commit is authorized/performed for this stage.

Actual local workerd (2026-10-19, package 1.20261019.1) executes unchanged pinned
Core with no Node compatibility flags. Two/three/four-player hashes match Node;
Exam/Learning and a bounded 25-repeat stress test pass. Whole-process peak RSS
~61–65 MiB and CPU ~0.12–0.57 s including startup are measurements, not cloud SLAs.
See release/CLOUDFLARE_RUNTIME.md and its exact raw-result summary.

## Run locally

Node >=20, Python >=3.10. In `apps/shashbesh-lab-web`:

```sh
npm run build
python3 server.py --port 8787
```

Open `http://127.0.0.1:8787/`, enter the ephemeral researcher code printed in
that local console. Select players/position/dice and Exam/Learning. The pinned
Core artifact must already be available and pass archive/extracted-file hashes;
it is excluded from public export. Do not expose the server or copy test codes.
Use existing local Lab Viewer/checkpoint instructions separately; do not
recreate or migrate protected research databases.

Static public candidate, no deployment: `npm run build:public` produces
`dist-public/` with interaction disabled. Do not confuse it with local `dist/`.

## What is published

Checked unauthenticated on 2026-10-20: Game website HTTP 200; Game GitHub public
API HTTP 200. Lab GitHub returned 404 and the Lab website could not be reached.
Therefore the Lab remains **unpublished/unverified**. A 404 does not prove that
an inaccessible private repo cannot exist. Read release/URL_STATUS.json.
No push, deployment, cloud resources, messages, payments or public API occurred.

## What remains private

All SQLite databases/sidecars, raw historical experiments, Core archive/package,
owner-approval/provenance records, console credentials, dependency installs,
logs/screenshots, generated builds and the existing `.git` history. The history
contains private research/ownership documents and an unreviewed contact identity;
never make this private repository public wholesale. Tools/evidence under /tmp
are not release attachments. Publish only a reviewed fresh allowlist export.

## Planned / known limitations

The workerd test is not a deployed host adapter. Public interaction stays off
until rate limiting, global budgets, trial authorization/isolation, atomic
Exam/receipt storage, expiry/retry/security tests and cloud CPU/heap checks pass.
No registration, real billing, public untrusted execution or valid rankings.
Local attempts vanish at restart/expiry; UI reload does not restore a trial.
Bilingual rules text remains preview material requiring editorial review.
Cold Replay remains up to 53.57 s, Firefox gaps up to 1.48 s in earlier L2-V4
measurements. Heavy Replay must remain isolated. Core rules must not change to
satisfy runtime limits. Lab-wide license is unresolved; Core's limited approved
scope and legacy manifest annotation require careful release reconciliation.

## Resume development

1. Inspect Git status and this handoff; preserve release changes and protected
   hashes. Do not reset/clean, commit everything or restart the application work.
2. Read release/CLOUDFLARE_RUNTIME.md, LICENSE_REVIEW.md, SECURITY_AUDIT.md,
   PUBLIC_PREVIEW_ARCHITECTURE.md and PUBLICATION_PLAN.md.
3. Confirm licensing/provenance and the allowlist. Re-run only relevant checks
   when changes justify them. The historical full Lab run was 93 passed; the
   web checkpoint had 4 frontend + 9 backend tests. Release checks add public
   mode/runtime/export validation; see release validation evidence.
4. Review the prepared export privately. Publication and any additional commit
   need new authorization. If enabling a backend, implement only the thin host
   adapter and protections around original Core, not a second game engine.
5. Keep Lab ready to pause; resume Game work as the next priority independently.

## External agents

Models run on developer-owned compute. Use the local Pull V1 example and
`docs/AGENT_INTEGRATION.md`. Tokens are ephemeral test capabilities, never
provider keys in browser JS. Rules agents do not receive legalActions, ready
IDs, private journals or future RNG. Strategy tasks may provide legal actions.
Future support uses Lab Issues/Discussions only when published/enabled.

## Game/Lab separation

Game: https://shashbesh.pages.dev and
https://github.com/mistermetes-cloud/ShashBesh — verified public.
Lab: https://shashbesh-lab.pages.dev and
https://github.com/mistermetes-cloud/shashbesh-lab — planned/unpublished.
Separate repositories/build roots/deployments, credentials, cookies and data.
No Game code, site settings or services changed during this stage.

RU: Lab — кандидат v0.1.0, готов к паузе; игра — следующий приоритет. Не считать
Lab опубликованным. Все исследования, базы, Core artifact и история Git остаются
приватными. Продолжать с текущими изменениями и handoff, а не создавать всё заново.
