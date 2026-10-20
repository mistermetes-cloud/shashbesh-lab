# Publication plan — NOT EXECUTED

All steps below require the maintainer's later explicit publication authorization.
No GitHub repository/cloud resource is created, no push/tag or deployment is
performed in L4-RELEASE-01. Only the web checkpoint was committed locally.

## A. GitHub repository

1. Close the license/provenance gates in LICENSE_REVIEW; approve the reviewed
   allowlist and source snapshot. Re-run source/history scans. Keep private owner
   records, research data and this repository's `.git` entirely private.
2. Run the allowlist exporter into a fresh local directory under /tmp. Review
   its exact SHA256 manifest and build/test there. It contains no Core archive,
   CSV, SQLite, raw results, credentials, dependencies, generated bundles or Git
   history. A missing separately approved Core makes Core-dependent tests gated;
   do not fetch an unverified replacement or invent sample rules.
3. After authorization, create `mistermetes-cloud/shashbesh-lab` separately,
   initially private if a final review is needed. Do not repurpose the Game repo.
4. In the reviewed export only, initialize a new Git history, add the approved
   source files and actual approved LICENSE/notices, and create the initial
   release-preparation commit. Do not push any branch/ref from this private Lab.
5. Configure the new remote only in that separate repo; review its full diff and
   scan once more. Push only after approval. Verify the unauthenticated public
   URL before marking the Lab repository published.

No repository-wide license file is generated here because the owner has not
selected terms for the wider Lab. Do not create a misleading automatic license.

## B. Cloudflare website

1. Verify the independent Lab project name, owner/account and final source repo.
   Do not change Public Game's Pages project, domains, secrets or build settings.
2. Approve a static-only preview first. Build root `apps/shashbesh-lab-web`,
   command `npm run build:public`, output `dist-public`.
3. Review `build-config.json`: mode `public-preview`, interactive false. Check
   both languages show disabled Rules Lab, no login/test token/action controls,
   no API requests and no server/Worker bindings. Do not publish `dist/`.
4. After separate deployment authorization, deploy only that reviewed static
   output; no Python backend, Core bundle, public Agent endpoint or paid service.
5. Verify actual HTTPS URLs, 18 routes, language/theme/fallback, 404, CSP/headers,
   disabled interactions, browser console and mobile layout. Only then update
   URL_STATUS and README to confirmed published. Keep rollback to prior static
   artifact/version; do not delete local experiments to roll back a site.
6. Interactive Rules Lab is a later deployment gate: secure the thin Core Worker
   adapter, consistent trial storage, rate/cost budgets and production CPU/heap
   behavior first. A workerd unit test does not authorize that backend.

## C. English/Russian documentation

Review README.md/README.ru.md parity, preview wording and links. Pin rules-language
translation/version independently from UI locale. Include the actual approved
license and notices, limitations and runtime evidence. Keep raw ownership records
and private experiment logs outside the public docs and downloadable assets.

## D. Links between Game and Lab

Game and its GitHub URL are currently verified public. Lab URLs remain planned.
After Lab verification, add a Lab→Game link in the Lab project. Any Game→Lab link
is a separate Game change/review/deployment, never silently bundled here.
No shared cookies, credentials, databases or deployment pipeline.

## E. Release v0.1.0

Once publication/license checks pass, review release notes against actually
published capabilities. Tag/publish v0.1.0 only in the new reviewed source repo
and only with authorization. State clearly whether Rules Lab is local-only.
Attach reviewed source/checksums/notices, not private Core binaries, databases,
node_modules or raw model data. Never label a candidate as already released.

## F. Community channels

Enable Lab Issues for ordinary bugs/research proposals when ready. Enable
Discussions separately for methodology and external-model integration. Verify
both URLs before advertising them. Enable and verify a private vulnerability
reporting route before claiming one exists; do not invent an email/contact.
Set contribution/license guidance, issue templates and moderation policy without
requesting tokens or private datasets. No messages or channel changes are sent
by this preparation stage.

RU: план не выполнен. Сначала лицензия и чистый allowlist-экспорт, затем отдельное
разрешение на GitHub/Pages. Публичная сборка отключает интерактивность. Ссылки и
Issues/Discussions объявляются доступными только после внешней проверки.

## L4-RELEASE-02 clearance supersedes the earlier 61-file preparation

The original 61-file export has been reviewed but owner rights remain unconfirmed.
For the license-approval snapshot use `PUBLIC_PACKAGE_ALLOWLIST_V0_1.json` and
`tools/release/prepare_approval_package.py --output <NEW-/tmp-directory>`. This
source-only private review package adds draft GPL/attribution/provenance files
and excludes old validation builds. The old exporter still represents the
historical 61-file preparation and must not be mistaken for the final licensed
release. Owner confirmation and license activation must precede publication.
