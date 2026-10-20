# ShashBesh AI Lab

**v0.1.0 candidate · local research software · public Lab release not published.**

[Русская версия](README.ru.md)

An independent bilingual platform foundation for studying how AI agents follow
rules, select strategies and respond to feedback in ShashBesh. The original
pinned ShashBesh Core remains the sole game-rule authority. Public Game and
Research Lab have separate code/build/deployment boundaries.

| Resource | Status checked 2026-10-20 |
|---|---|
| [Public Game](https://shashbesh.pages.dev) | Reachable, HTTP 200 |
| [Game repository](https://github.com/mistermetes-cloud/ShashBesh) | Public, GitHub API HTTP 200 |
| [Planned Lab website](https://shashbesh-lab.pages.dev) | Unpublished/unverified; URL could not be reached |
| [Planned Lab repository](https://github.com/mistermetes-cloud/shashbesh-lab) | Unpublished; unauthenticated GitHub API returned 404 |

Availability does not establish ownership or license scope. No Lab push,
deployment, repository creation or cloud resource provisioning was performed.

## What works

- Nine RU/EN website sections, local language preference, independent rules
  language, light/dark themes, responsive original-Core board.
- **Local** Rules Lab for 2–4 players: Core-generated demonstration positions,
  user-selected dice, full action proposals and authoritative validation.
- Exam seals the first game attempt; Learning keeps retries and feedback.
- Separate Researcher and Agent API projections, Agent Pull V1 and CLI example.
- Actual local workerd Core tests pass with native Node hash equivalence.
  This is runtime evidence, not a deployed or production-secured backend.

Arena/Strategy tournaments, hosted registration, public interactive API, durable
attempt storage, rankings and billing remain Planned/Preview. The public static
build **disables** Rules Lab interaction and clearly identifies the local-only
demo. No third-party agent code is hosted or executed.

## Run

Requires Node >=20 and Python >=3.10; frontend build has no npm dependencies.

```sh
cd apps/shashbesh-lab-web
npm run build
python3 server.py --port 8787
```

Open `http://127.0.0.1:8787/`; enter the ephemeral researcher test code printed
by the local server. Do not publish that code or console logs. The optional
local backend requires the approved Core artifact/version/hash described in
[the app guide](apps/shashbesh-lab-web/README.md). That private artifact is not
included in the proposed public source export; approved redistribution remains
a release gate. Static builds require no Core artifact.

Prepare the **disabled** public preview, without deploying:

```sh
cd apps/shashbesh-lab-web
npm run build:public
```

Output: ignored `dist-public/`, independent of local `dist/`. Cloudflare Pages
must use `npm run build:public`, output `dist-public`; never publish the local
Python server or the private research repository/history.

## Participate

Researchers: propose controlled experiments, bilingual rule reviews and fixture
coverage. External AI developers: use [Agent Pull V1 integration](docs/AGENT_INTEGRATION.md).
When the **Lab** repository is published and Issues are enabled, contact the
maintainers there; use Discussions only after that channel is enabled. These
channels are not currently claimed available. Do not post tokens, private model
prompts, research databases or vulnerability details in public issues.

See [contributing](CONTRIBUTING.md), [security](SECURITY.md), [roadmap](ROADMAP.md),
[release notes](docs/release/RELEASE_NOTES_V0_1_0.md),
[publication plan](docs/release/PUBLICATION_PLAN.md) and
[project handoff](docs/PROJECT_HANDOFF_V0_1.md).

## License status

The proposed Lab-wide license is **GPL-3.0-only, pending explicit rights-holder
confirmation**; this document does not activate a grant.
Core has a limited GPL-3.0-only owner grant; its noble-hashes dependency has MIT
notices. This does not automatically license all Lab code, documentation or
Game assets. [License review](docs/release/LICENSE_REVIEW.md) is a publication
gate. Do not publish this private Git history or Core archives as a shortcut.
