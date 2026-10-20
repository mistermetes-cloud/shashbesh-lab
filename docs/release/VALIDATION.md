# Release validation record

Only the existing 17-file web foundation was committed as
`34cdc7497116825e3a9807461e2db1f6439520f4`. Release changes remain uncommitted.

- Web checkpoint: 4 JavaScript frontend tests and 9 Python backend tests passed;
  Core/database hashes matched, no high-confidence credential patterns found.
- Prior architecture full Lab run: 93 passed in 647.50 s. It is historical
  evidence, not a claim of a fresh full-suite run during release preparation.
- Real workerd: 2/3/4-player fixtures and 25-repeat four-player stress passed;
  exact native Node state hashes match. See WORKERD_RESULTS.json.
- Public static build and Firefox: 18 RU/EN routes, disabled Rules Lab in both
  languages, no interactive controls and zero API POSTs. No backend was started.
- Frontend changes add explicit local/public build configuration; local UI and
  backend checks are repeated separately to preserve working demonstrations.
- Fresh allowlisted export is built and tested without private history/Core.
- Source/history credential/artifact scan, original 283 protected hashes,
  JavaScript syntax and git diff whitespace checks are repeated at completion.

Raw logs, runtime bundles, dependency installs, temporary source exports and
browser artifacts stay under /tmp and are not public release attachments.
The maintainer must review licensing and publication gates before any release.

Final release checks: **27 Python tests passed** (release export/safety, web
backend and Agent protocol); **6 frontend JavaScript tests passed**. Local
Firefox interactive scenarios passed on actual 320/360/390/768/1280 viewports,
with no script errors; public static Firefox passed all 18 bilingual routes
with zero API POSTs. Both builds pass. Optional pinned runtime-tool npm advisory
audit reported **0 vulnerabilities** on 2026-10-20. This is not a new full Lab
pytest run. Real workerd tests remain the separate five-case runtime evidence.
