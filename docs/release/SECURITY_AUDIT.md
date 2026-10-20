# Release security audit — v0.1.0 candidate

Status: **private preparation complete; publication approval withheld**.
No GitHub/Cloudflare publication or public API is performed by this audit.

## Scope and findings

Read-only source/history scan covers current tracked/untracked source and all
reachable Git blobs, using private-key, AWS/GitHub-token and credential-URL
patterns. The initial completed scan found no high-confidence credential values
and no tracked SQLite/archive/key/log files across **8 commits / 122 distinct
historical blobs**. The final repeat is recorded in AUDIT_RESULTS.json.
Pattern scanning is not proof of absence; selected release files need human
ownership/privacy review before publication.

**Do not publish this Git history.** Fifteen historical document paths contain
private research or owner-approval/engineering evidence; one commit contact
identity has not been approved as a public technical address. Values and private
content are deliberately not reproduced here. This is why the source exporter
starts a fresh tree and does not copy `.git`, rather than relying on .gitignore.

Protected Core/archive/extracted files and existing research/Live databases are
verified against the preserved 283-file SHA256 baseline. Runtime fixtures do not
modify them. Local dependencies/binaries, logs, browser profiles, raw responses,
Core bundles, private experiment data and generated dist stay outside source
publication. No arbitrary external model code or callbacks are introduced.

## Dependencies

The web application has no npm dependencies. Its build uses Node standard
library; the local server/client use Python standard library plus existing Lab
adapters. pytest, Firefox and geckodriver are test tools already present.
The optional runtime audit installs only pinned workerd/esbuild under /tmp with
lock integrities. Its advisory result is recorded separately in the validation
summary. Do not treat an advisory scan as source-ownership approval or copy
node_modules/binaries into Git/public assets.

## API and public/private separation

Local Researcher cookie and per-trial Agent bearer capability are distinct.
Host/Origin/JSON size, task/lease/revision and idempotency checks are tested.
Agent responses use dedicated projections, exclude the Core oracle/private
journals/future RNG, and do not expose researcher diagnostics. Core independently
validates proposals; invalid Exam state remains unchanged. Learning keeps audit.
These are local tests, not production authentication or comprehensive abuse tests.

The public build has no interactive login/token/proposal controls and makes
zero API POSTs in Firefox across its 18 routes. Static-only publishing has no
backend binding, so client-side flag tampering cannot create a service.
Never expose the local Python server. Public backend gates: edge rate limits,
per-IP/trial/tenant/global quotas, bounded compute/concurrency, strict depth/
size/schema checks, consistent atomic Exam/idempotency/expiry, secret rotation,
CSP/CORS/CSRF review, attack tests and cloud CPU/heap/spending verification.

## Publication decision

Use only RELEASE_ALLOWLIST.json through the fresh /tmp source exporter. The
prepared export excludes all Core packages/CSV, databases and private documents.
It builds a disabled public preview independently. Missing Lab-wide license and
unresolved release approval prevent calling the repo publication-ready. Actual
interactive backend hardening remains another gate. No registration, payments,
provider credentials or public untrusted execution are in the preview scope.

RU: секреты по заданным шаблонам не обнаружены, но приватную Git-историю
публиковать нельзя. Только свежий проверенный allowlist-экспорт. Публичная
интерактивность отключена; лицензирование и разрешение на публикацию не закрыты.
