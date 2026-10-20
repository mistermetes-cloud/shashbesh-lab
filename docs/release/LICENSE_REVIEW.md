# License and source-ownership review

Status: **reviewed evidence; public release not cleared**. No repository-wide
license has been invented, selected or granted by the release tooling.

1. The pinned Core LICENSE declares GPL-3.0-only for the exact owner-controlled
   materials in its manifest, within the owner's rights. The local approval
   record covers eight fixed-hash files, including geometry CSV. It is an
   owner-attested record, not independent proof of every source contribution.
2. The manifest's CSV role still says `rights unresolved`. That is inconsistent
   with the later approval record. Reconcile the release evidence with the
   maintainer; **do not edit the protected artifact** to conceal the annotation.
   The limited grant must not be stretched to all Game/Lab materials.
3. `@noble/hashes@1.8.0` is separately MIT-licensed. Preserve its upstream notice
   when distributing an approved combined artifact. The Core scope/notice and
   corresponding-source requirements must be reviewed for the chosen release.
4. The wider Lab code, web source and documentation do not have an approved
   repository-wide LICENSE. The maintainer must confirm ownership/provenance
   and choose compatible terms before publication/contributor acceptance.
5. No Game UI/assets, private owner declarations/signatures, research datasets
   or Core archives are in the proposed source export. Do not infer Game-wide
   licensing from the Core's limited grant. GitHub API did not detect a license
   for the current public Game repository; that is not an independent rights finding.
6. Runtime audit tooling is optional and isolated: workerd package declares
   Apache-2.0, esbuild declares MIT. Do not copy their node_modules/binaries into
   the release. Lockfiles record exact versions/integrities. The web build has
   no npm runtime dependency. Python uses standard library; pytest/Firefox/
   geckodriver are local test tools, not shipped application binaries.

Before distribution, approve a per-component license/source inventory, include
applicable LICENSE/copyright/notices and any required corresponding source for
bundled Core. The proposed public static build does not contain Core/CSV.
A clean export helps privacy but does not itself grant missing rights.

References: the artifact's actual LICENSE/notices are the primary evidence;
[GitHub licensing guidance](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository).
This document records release gates, not a new license grant.

RU: Core-grant ограничен восемью точными файлами; CSV включён в запись утверждения,
но старый manifest содержит противоречивую пометку. Общая лицензия Lab не выбрана.
Нужно подтвердить provenance и условия публикации, не изменяя защищённый Core.

## L4-RELEASE-02 follow-up

GPL-3.0-only is now the explicit **proposal** for owner-confirmed Lab source and
documentation. Exact-file provenance review found 56 project-origin sources
awaiting rights attestation and 5 generated metadata files in the original 61.
See PROVENANCE_REVIEW.md and FILE_PROVENANCE_61.json. Draft LICENSE.md, COPYING
and third-party notices/texts are prepared; no owner or license grant is invented.
The clean owner-review package excludes 74 old validation build files and has
its own exact allowlist/manifest. Publication remains on hold.
