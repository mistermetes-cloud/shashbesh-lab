# ShashBesh AI Lab Web — L4-WEB-01

Independent website foundation. Baseline: `e18307d05d590fdd5cc17c03a90074c85b6cf7bd`.
This directory has its own build and future Pages project. It does not modify
or share a deployment with `shashbesh.pages.dev`.

## Run locally / Локальный запуск

From this directory, using the existing Node >=20 and Python >=3.10:

```sh
npm run build
python3 server.py --port 8787
```

Open `http://127.0.0.1:8787/`. The console prints an **ephemeral researcher test
code**. Enter it in Rules Lab. Never publish the console output or reuse this
code for a real account. The server only binds 127.0.0.1 and stops with Ctrl-C.
No package installation is needed. No existing database is opened or modified.

Откройте локальный адрес, введите временный код из консоли в лаборатории правил.
Выберите 2–4 игроков, позицию, кубики, Exam/Learning и язык правил, затем загрузите
демонстрацию. Это задача выбора одного действия, а не новая реализация полной
Arena. Все позиции и переходы создаёт оригинальный Core.

## Delivered / Реализовано

- Nine pages in English and Russian, path-based routing, saved language choice,
  navigator-language detection, English fallback, light/dark themes.
- Home and working local Rules Lab; Arena, Strategy, multi-match Learning,
  Benchmarks, Rankings and registration are explicitly Preview/Planned.
- Original 64-cell geometry, 5 pieces per player, four Core sides/colors, dice.
  Reserve pieces are visually placed in their Core home sector with a dashed
  outline; their authoritative status remains reserve. No move rules in JS.
- Researcher-only legal actions, Core reasons, attempt table and actual-result
  plot. No invented leaderboard scores or hosted AI results.
- Exam seals its first game attempt. Invalid proposals leave Core state intact.
  Learning allows up to 10 attempts at a decision, with minimal or category
  feedback. Summary distinguishes first/last success and failed attempts.
- Core-backed independent proposal validation, accepted action application,
  original extra-roll/finishRoll behavior and explicit no-decision roll status.
- Rules language is frozen in the task; changing UI language preserves it.
  The bilingual rules reference is **preview material**, not a reviewed complete
  benchmark rule corpus. Reviewed translations/fixtures remain a research gate.

## Agent boundary / Граница агента

Reuses `lab.platform_agent.AgentTrial` and `shashbesh-agent/1`. No replacement
protocol or modifications to existing Lab modules. The local HTTP adapter binds:

- POST `/agent/v1/tasks/pull`: the V1 pull envelope.
- POST `/agent/v1/tasks/{task_id}/submit`: the V1 submit envelope.

Researcher login sets an HttpOnly, SameSite=Strict cookie, scoped to
`/api/research`. Each trial has a different ephemeral **test** bearer token.
The agent token cannot access Researcher APIs; a researcher cookie alone cannot
call Agent APIs. No CORS, arbitrary callbacks, provider keys or remote models.
Host/Origin, JSON size, protocol, lease, revision and idempotency are checked.
Agent receives the dedicated serialized task/receipt only: no legalActions,
action_id, internal Core context/eventLog, seed, RNG counter or future dice.
Researcher/Agent tabs are an authorized researcher's preview, **not** a browser
sandbox. The security boundary is the API projection and separate credentials.

A Rules task adds public `rules` metadata (language, preview version, text hash)
to the existing V1 envelope. Learning with category feedback adds the optional
`category: illegal_action` response field; Exam never exposes Core reasons or
alternative actions. Both are additive local adapter metadata, not new action
semantics. All Core decisions remain with the pinned artifact.

`core_bridge.cjs` is a host adapter, not an engine: loads unchanged pinned Core,
parses its CSV and calls Engine.create/initialRoll/roll/legalActions/applyAction/
finishRoll. Python's existing artifact verification runs before the worker.
The researcher error text is Core's own diagnostic; category is deliberately
coarse. Core validation and trial acceptance are both checked by tests.

## External client / Внешний клиент

Open the external-agent details in Researcher view to get the test capability.
Save a complete proposal to `proposal.json`, then run:

```sh
python3 agent_client.py --base http://127.0.0.1:8787 --action proposal.json
```

The client prompts for the test token using getpass (not a CLI flag or URL),
pulls the task and submits the proposal. It never obtains legal actions.
Use only on a fresh open trial. No paid model or real registration is connected.

## Resource and data limits / Ограничения

One on-demand Node Core process, 192 MiB V8 old-space budget, 15-second RPC
budget, at most 32 in-memory trials, 20-minute trial retention, 16 researcher
sessions, 64 KiB JSON input. Decisions have a 300-second lease. Attempts/receipts
are held in memory; restart loses them. UI reload does not recover a trial yet.
This is a local demonstration, not persistent multi-tenant production auth.
No hosted third-party code, payment integration, SQLite migration or background
service. The original Lab Viewer/checkpoints/replay are unchanged.

## Build and Cloudflare plan / Сборка и Cloudflare

`npm run build` emits ignored local `dist/`: static JS/CSS/locales, 18 route HTML
files, docs, downloadable client, 404 and security headers. No Core package,
Python backend or credentials are bundled. `wrangler.jsonc` describes the future
**independent** Pages build output; no deployment has been performed.

Pages can serve this frontend. Rules Lab on a static-only host displays the
local bridge requirement instead of simulating validation. Do not deploy this
loopback Python server or put private tokens in a static binding. Existing
Python/process IPC cannot run unchanged inside Workers. The L4-RELEASE-01 follow-up now verifies original Core in actual local workerd
for bounded 2–4-player scenarios with matching native Node hashes. This does not
establish production cloud CPU/RAM quotas or a secured public API; see
`docs/release/CLOUDFLARE_RUNTIME.md`.

Next adapter gate: bundle unchanged CommonJS Core and CSV in a separate trusted
runtime adapter, compare state/event/replay hashes in local workerd, measure
2–4-player CPU and heap. If limits fail, use bounded trusted Node compute behind
a Workers gateway/DO match owner, as designed in `docs/platform/`. Do not put
long Replay work in edge request handlers. Known local Replay cost remains up
to 53.57 s and Firefox frame gap 1.48 s from L2-V4; these are not this site's SLAs.

Official references, checked 2026-10-20:
[Pages routing](https://developers.cloudflare.com/pages/configuration/serving-pages/),
[Node compatibility](https://developers.cloudflare.com/workers/runtime-apis/nodejs/),
[Workers limits](https://developers.cloudflare.com/workers/platform/limits/).

## Validation / Проверки

From repository root:

```sh
node apps/shashbesh-lab-web/build.mjs
node --test apps/shashbesh-lab-web/tests/web.test.mjs
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q apps/shashbesh-lab-web/tests/test_backend.py tests/test_platform_agent.py
PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 python3 apps/shashbesh-lab-web/tests/browser_web.py
node --check apps/shashbesh-lab-web/src/app.js
node --check apps/shashbesh-lab-web/core_bridge.cjs
git diff --check
```

The browser harness uses a temporary Firefox profile and local geckodriver only.
It measures actual content viewport widths and never changes a user's profile,
VPN or Linux services. Logs/screenshots stay in `/tmp`.

## Public preview safety gate — L4-RELEASE-01

`npm run build:public` creates separate ignored `dist-public/`. It displays an
explicit RU/EN local-only notice and disables Rules Lab login, tokens, loading
and action controls. No API is deployed or simulated. The Pages configuration
now points only to `dist-public`; its build command must be `npm run build:public`.
Default local `dist/` and the loopback server remain separate.

The package is still a candidate. Review root licensing/security/publication
documents before any GitHub or Cloudflare publication. Real workerd evidence
is available; secure public trial management and licensing remain gates.
