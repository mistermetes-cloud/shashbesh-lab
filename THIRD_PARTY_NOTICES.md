# Third-party attribution and scope

This is an inventory/notice file, not a new license grant or a claim that all
referenced software is bundled. The public candidate contains **no third-party
implementation source, binary dependencies, Core artifact or geometry CSV**.
License documents are included verbatim for reference and notice preservation.
Exact component inventory: `docs/release/THIRD_PARTY_COMPONENTS.json`.

| Component | Role | License | Notice / source |
|---|---|---|---|
| ShashBesh Core 0.1.0-g0.65e1ec3 | External local prerequisite; excluded | Existing limited GPL-3.0-only grant, eight fixed files | Original artifact LICENSE/manifest/owner approval remain authoritative; do not relicense |
| @noble/hashes 1.8.0 | Core's external bundled dependency; excluded here | MIT | Copyright (c) 2022 Paul Miller; verbatim `LICENSES/MIT-noble-hashes.txt`; https://github.com/paulmillr/noble-hashes/tree/1.8.0 |
| esbuild 0.28.2 | Optional downloaded audit/build tool; excluded | MIT | Copyright (c) 2020 Evan Wallace; verbatim `LICENSES/MIT-esbuild.txt`; https://github.com/evanw/esbuild |
| workerd 1.20261019.1 | Optional downloaded test runtime; excluded | Apache-2.0 | https://github.com/cloudflare/workerd; `LICENSES/Apache-2.0.txt` is the standard license text, not a fabricated upstream NOTICE |
| GNU GPL version 3 text | Included license document only | Its own verbatim-copy permission | Copyright (C) 2007 Free Software Foundation, Inc.; COPYING; https://www.gnu.org/licenses/gpl-3.0.txt |

MIT copies require their original copyright and permission notice. Apache
redistribution requires its license, applicable notices and change notices;
preserve an upstream NOTICE if one accompanies the redistributed work. No NOTICE
was found in the installed npm workerd package; this is not a claim that every
upstream/binary transitive component has been cleared for redistribution. Do not
ship the runtime binary from this source-only inventory without its own audit.

The lockfile lists optional workerd/esbuild platform packages, whose upstream
terms stay separate; it does not contain their implementation code. Python/Node,
pytest, Firefox and geckodriver are external system/test prerequisites, not
redistributed here. No font files, images or Game UI assets are included. Naming
a local font fallback does not bundle that font.

If a future build includes Core or any third-party code, include the required
corresponding source/notices and review the actual bundle closure. Compatibility
with GPLv3 does not transfer upstream copyrights to the Lab owner.

RU: сторонний исполняемый код не входит в кандидат. Прилагаются точные тексты
лицензий; авторство и условия сторонних материалов сохраняются. Нельзя считать
этот список разрешением на публикацию Core или бинарных инструментов.
