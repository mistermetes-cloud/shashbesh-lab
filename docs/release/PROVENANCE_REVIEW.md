# L4-RELEASE-02 — source provenance and GPL clearance

**Audit complete; rights approval pending. No publication clearance is granted.**

## Exact baseline review

All **61** allowlisted files in the original reviewed export were read and hashed.
All match their recorded SHA256. The per-file record is FILE_PROVENANCE_61.json.
It includes path, byte count, hash, creation evidence, license/provenance markers,
classification and the outstanding release condition for every file.

| Classification | Original 61 files | Meaning |
|---|---:|---|
| OWNER_AUTHORED | 0 confirmed | No Lab-wide exact-file owner declaration has been supplied. A Git author/session is not proof of rights. |
| THIRD_PARTY | 0 implementation files | External tools/Core are referenced, not copied into the source tree. New license documents have their own third-party provenance. |
| GENERATED | 5 | Audit/URL/workerd/allowlist JSON and npm lock metadata; producers/inputs are recorded. |
| UNKNOWN_ORIGIN | 56 | Project/session origin is observed, but owner/employer/client/contributor rights for the exact release bytes are not attested. This is not an allegation of copying. |

The term UNKNOWN_ORIGIN is conservative: it distinguishes unresolved ownership
from the fact that project-directed creation/history evidence exists. It is not
a blanket assertion that 56 unrelated files were found. All 56 are **withheld
from publication until the owner confirms rights or supplies an existing license**.
Do not mark them OWNER_AUTHORED merely because the owner controls the checkout.

The old directory also contains **74 generated build files** in ignored dist/
and dist-public/ from prior validation. They are not part of the 61 source
allowlist and are not included in the clean approval package. The old export is
left intact. No node_modules, .git, databases or original Core files are added.

## Proposed GPL-3.0-only compatibility

- Core's existing grant is GPL-3.0-only for eight exact files within the owner's
  rights. The earlier owner record includes the CSV; the manifest retains a
  contradictory legacy label. No new grant or protected-file edit is invented.
  Same-version GPL scope is compatible in principle, subject to actual rights
  and retaining the original source/notices when redistributing Core. Core is
  excluded from this proposed public package.
- MIT (Expat) esbuild and noble-hashes terms are compatible with GPLv3 when their
  copyright/permission notices remain. They are not relicensed as Lab-owned code.
- Apache-2.0 workerd is compatible with GPLv3 integration in that direction;
  Apache license/NOTICE/change-notice duties remain where applicable. The tool
  binary and unreviewed binary transitive closure are **not** redistributed.
- No third-party implementation/documentation/font/image license incompatible
  with GPLv3 was identified in the 61 source files. This does not substitute for
  the required owner provenance statement for project text and translations.
- Owner-authored documentation/RU/EN translations can be included in the proposed
  GPL scope only after explicit rights confirmation. No separate CC/GFDL license
  is inferred. Generated static outputs derive their terms from their actual
  inputs; generated output is not automatically public domain or Lab-owned.
- The standard GPL text in COPYING and other license documents keep their own
  verbatim-copy terms. Merely including COPYING does not activate Lab licensing.

Primary compatibility sources:
[FSF Expat entry](https://www.gnu.org/licenses/license-list.html#Expat),
[FSF Apache-2.0 entry](https://www.gnu.org/licenses/license-list.html#apache2),
[Apache compatibility statement](https://www.apache.org/licenses/GPL-compatibility.html),
[GPLv3 text](https://www.gnu.org/licenses/gpl-3.0.txt).

## Included notices and exclusions

LICENSE.md is an explicit **draft**, not a fabricated copyright grant. COPYING
is the unchanged GPLv3 text. THIRD_PARTY_NOTICES.md and THIRD_PARTY_COMPONENTS.json
record component name/version/source/license/attribution/redistribution conditions.
LICENSES/ contains verbatim MIT notices and the standard Apache text; no Core
implementation, geometry, Game UI, binary tool or private approval record is copied.

No positively identified non-redistributable implementation was found in the
source allowlist. Unapproved Core artifacts/binaries remain excluded, and unknown
rights remain a hold rather than an invented permission. If the owner cannot
confirm a held file, remove it from the proposed release or obtain appropriate
permission and review build impact before any publication.

The fresh owner-review package is governed by PUBLIC_PACKAGE_ALLOWLIST_V0_1.json,
not the contaminated old export directory. An external SHA256 manifest binds its
exact files; no signature/approval is fabricated. Owner approval records should
stay private unless the owner explicitly approves their disclosure.

## Functional/publication state

See FUNCTIONAL_RELEASE_BOUNDARY.md. No Lab online Gateway is publicly working.
The static public build remains interactive=false. Core/workerd feasibility is
established locally, but public backend security and cloud cost gates remain.
No GitHub repository creation, push, deployment or cloud resource is performed.

RU: проверены все 61 файл; пять — механические метаданные, 56 требуют подтверждения
прав на точные байты. Это не утверждение о незаконном копировании. Совместимость
GPLv3 с выявленными MIT/Apache-2.0 условиями проверена; чужие notices сохраняются.
До подтверждения владельца и активации лицензии публикация не разрешена.
