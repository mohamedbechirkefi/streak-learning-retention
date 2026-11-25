<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->
# Dependency licences (M6, 2026-11-25)

Sources: Python licences read from the installed `.venv` package metadata (`License-Expression`, else the licence classifiers) after `uv sync --frozen --all-groups --all-extras`; npm licences read from `demo/node_modules/*/package.json` after `npm ci --prefer-offline`, with the package list taken from `demo/package-lock.json`. Tool licences read from the shared tool environment's package metadata. Nothing here is legal advice; the owner reviews the licence statements (`author_review.md`).

Accepted without a flag: MIT, BSD, ISC, Apache-2.0, PSF, MPL-2.0, 0BSD, Zlib, CC0-1.0 and similarly permissive licences.

## Python (runtime and development, from `uv.lock`)

| Package | Version | Licence | Role | Flag |
|---|---|---|---|---|
| numpy | 2.5.4 | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 | runtime | none |
| pytest | 9.2.0 | MIT | development | none |
| hypothesis | 6.170.15 | MPL-2.0 | development | none (file-level copyleft; used unmodified, not distributed) |
| iniconfig | 2.3.1 | MIT | development | none |
| packaging | 26.3 | Apache-2.0 OR BSD-2-Clause | development | none |
| pluggy | 1.7.0 | MIT | development | none |
| Pygments | 2.21.0 | BSD-2-Clause | development | none |
| sortedcontainers | 2.4.0 | Apache-2.0 (classifier "Apache Software License") | development | none |
| streak | 0.2.0 | LicenseRef-STREAK-NC-Research-1.0 | this project | not applicable (own licence, not OSI approved) |
| uv_build | >= 0.9.5, < 0.10 (build backend, `pyproject.toml`) | Apache-2.0 OR MIT (upstream statement, not read from installed metadata: the backend is not installed in `.venv`) | build | unverified locally |

## npm (demo, from `demo/package-lock.json`)

84 entries in the lock file; 53 installed on this machine (macOS arm64). The other 31 are optional platform-specific binaries for other systems (`@rolldown/binding-*`, `lightningcss-*` for other platforms, `@emnapi/*`, `@napi-rs/wasm-runtime`, `@tybys/wasm-util`, `tslib`); they were not installed, so their licences were not read here.

Runtime (shipped in the built page): react 19.3.1 (MIT), react-dom 19.3.1 (MIT), scheduler 0.28.0 (MIT). No flag.

Development and build (not shipped):

| Licence | Count | Packages |
|---|---|---|
| MIT | 42 | @jridgewell/sourcemap-codec, @oxc-project/types, @rolldown/binding-darwin-arm64, @rolldown/pluginutils, @standard-schema/spec, @types/chai, @types/deep-eql, @types/estree, @types/react, @types/react-dom, @vitejs/plugin-react, @vitest/expect, @vitest/mocker, @vitest/pretty-format, @vitest/runner, @vitest/snapshot, @vitest/spy, @vitest/utils, assertion-error, chai, convert-source-map, csstype, es-module-lexer, estree-walker, fdir, fsevents, magic-string, nanoid, obug, pathe, picomatch, postcss, rolldown, stackback, std-env, tinybench, tinyexec, tinyglobby, tinyrainbow, vite, vitest, why-is-node-running |
| Apache-2.0 | 3 | detect-libc, expect-type, typescript |
| MPL-2.0 | 2 | lightningcss, lightningcss-darwin-arm64 |
| ISC | 2 | picocolors, siginfo |
| BSD-3-Clause | 1 | source-map-js |

No flag.

## Tools used to build artefacts (not dependencies of the code)

| Tool | Version | Licence | Use | Flag |
|---|---|---|---|---|
| typst (Python package) | 0.15.0 | Apache-2.0 | PDF compilation | none |
| pypdf | 6.20.0 | BSD-3-Clause | PDF metadata checks | none |
| pillow | 11.3.0 | MIT-CMU | image checks | none |
| pandoc | 3.6.3 | GPL-2.0-or-later (upstream statement) | Markdown to Typst and LaTeX | **flag: copyleft tool.** It is run as an external program and is neither linked nor distributed with the project, so its licence does not attach to the outputs; listed so that the owner can confirm. |
| Node | v22.23.3 | MIT (upstream statement) | demo build | none |

## Result

No runtime dependency carries a non-permissive licence. One flag for the owner's information: pandoc (GPL-2.0-or-later) as an external build tool. The project's own licence is custom and not OSI approved (README, Licence).
