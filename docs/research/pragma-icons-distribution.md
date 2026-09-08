# Pragma icon distribution — research findings (2026-09-08)

Facts about how Canonical's "Pragma" design system distributes icons for
downstream (non-JS) consumption. Verified against primary sources on this date.

## 1. npm package

**`@canonical/ds-assets`** exists and is the official icon (and font) distribution channel.

- URL: https://www.npmjs.com/package/@canonical/ds-assets
- Current version: **0.37.0** (published 2026-09-02; 37 published versions, weekly downloads ~3,085)
- Package description: "Icons, fonts, and shared visual assets for the Pragma design system."
- License field on npm: **LGPL-3.0** (with an exception, see §4)
- Versions are kept in lockstep with the whole Pragma monorepo via Lerna (currently the 0.37.x line; the monorepo README mentions lockstep versioning precisely to eliminate compatibility matrices). Note the 0.x line: breaking changes can appear in minor releases (`feat(...)!: commits exist in the changelog`).
- There is **no** `@canonical/pragma` icons package and no `@canonical/ds-assets-icons`; this is the only assets package. Related packages: `@canonical/design-tokens`, `@canonical/styles` (styles, not icons), `@canonical/react-components` (legacy Vanilla React lib).

## 2. Source repository

All of Pragma lives in a single monorepo: **https://github.com/canonical/pragma** (the successor to Vanilla Framework for Canonical's new design system; Vanilla Framework itself, https://github.com/canonical/vanilla-framework, is the older system and its icon set was migrated into Pragma — see §3/§4).

- Icon source of truth: `packages/ds-assets/icons/` (raw SVG files)
- Package source: `packages/ds-assets/` with `src/icons/` exporting `ICON_NAMES`, `IconName`, `ICON_CATEGORIES`, `ICON_METADATA`
- Icon spec doc: `packages/ds-assets/docs/ICONS.md` — https://github.com/canonical/pragma/blob/main/packages/ds-assets/docs/ICONS.md
- GitHub Releases: https://github.com/canonical/pragma/releases — latest **v0.37.0** (2026-09-02). Releases have **only 1 asset**: `pragma-implementations.v0.37.0.ttl` (the RDF implementation graph). **No icon zip/tarball is attached to releases.** Only the generic source tarball/zipball covers icons (`.../archive/refs/tags/v0.37.0.tar.gz`), which drags in the entire monorepo.

## 3. Icon set characteristics

- **Format:** one file per icon, plain SVG, `icons/<name>.svg`, **kebab-case** names.
- **Size/viewBox:** uniform **16×16 viewBox**.
- **Structure:** each file wraps contents in a single `<g id="<name>">`, enabling `<use href="path/to/name.svg#name">` sprite reuse.
- **Colouring:** all paths `fill="currentColor"` (branded logos excepted per spec). This is a deliberate change from Vanilla, where colouring was inconsistent — Pragma normalised everything to `currentColor`, and Vanilla's `-dark` variants were removed.
- **Count:** "over 150 SVG icons" (README). Exact count varies per release.
- **Categories (closed list):** `navigation`, `action`, `status`, `object`, `social-brand`, `product`, `theme`.
- **Metadata:** every icon has ≥3 search tags and ≥1 category; optional `aliases` (often former Vanilla names, e.g. `unstarred` → `starred-off`), descriptions for product/theme icons, and `{ replacedBy, since }` deprecation blocks. Exported as `ICON_METADATA` for icon-pickers.
- **Lineage:** the set migrated from Vanilla Framework; `docs/ICONS.md` has a "Changes from Vanilla" section (colour normalisation, removed `-dark` variants, simplified multichromatic icons).

## 4. License

- Package/repo license: **LGPL-3.0** (pragma repo `LICENSE`, npm `license` field).
- **Exception:** the bundled Ubuntu Sans fonts under `fonts/ubuntu-sans/` are licensed under the **Ubuntu Font Licence v1.0**, not LGPL. Icons themselves are LGPL-3.0. If vendoring icons only, LGPL-3.0 applies.
- LGPL applies to a MediaWiki PHP extension repo the same way it does to any LGPL-licensed asset library: keep the license text, note modifications if files are altered.

## 5. Documented non-JS consumption of raw SVGs

Yes — the package README and `docs/ICONS.md` document raw-SVG use explicitly:

- Raw SVGs ship in the npm tarball under `icons/`, intended to be referenced directly:
  ```html
  <svg width="16" height="16">
    <use href="path/to/search.svg#search" />
  </svg>
  ```
- The `<g id>` convention is documented as the mechanism that lets platform libraries "stay lightweight because they only handle loading and displaying SVGs" — i.e. the icon behaviour lives in the SVG standard, not in JS.
- Accessibility guidance (ARIA attributes / `aria-hidden`) is documented for both meaningful and decorative usage.
- There is no dedicated CDN documented for icons (no jsdelivr/unpkg instructions in the README); the README only says `bun add @canonical/ds-assets`. However, any npm package is trivially fetchable from a CDN or via `npm pack`.

## 6. Recommendation for automated vendoring

**Most stable source: the npm tarball** —
`https://registry.npmjs.org/@canonical/ds-assets/-/ds-assets-<version>.tgz`

Reasons:
1. It is the artefact the release pipeline itself publishes and verifies (the release workflow "publishes to npm" and CI verifies the publish against the registry).
2. The npm tarball contains exactly the published set (raw `icons/*.svg` + metadata), versioned and immutable once published.
3. GitHub Releases carry **no icon assets**, and GitHub source tarballs bundle the whole monorepo (much larger, no separate icon artefact).

Practical notes:
- Fetch `https://registry.npmjs.org/@canonical/ds-assets/latest` to resolve the current version, then download the `.tgz` and extract only `package/icons/*.svg` (+ the license).
- Pin an explicit version; the 0.x line allows breaking changes in minor releases, so treat icon renames/removals as possible at each bump (check `deprecated.replacedBy` in `ICON_METADATA` / the package CHANGELOG: https://github.com/canonical/pragma/blob/main/packages/ds-assets/CHANGELOG.md).
- Alternative for pin-by-commit: raw.githubusercontent per-file (`https://raw.githubusercontent.com/canonical/pragma/v0.37.0/packages/ds-assets/icons/<name>.svg`) works but needs a per-file manifest and no integrity guarantees; npm tarball is preferable.

## Ambiguities / caveats

- **Exact icon count** is not pinned in any doc ("over 150"); it changes release to release. Count from the extracted tarball at vendoring time.
- **No dedicated icon-only release artefact** exists; if Canonical later adds one to GitHub Releases, that would become preferable to npm for size.
- **LGPL-3.0 for assets** is unusual but is what's declared; if licensing is a concern for the wiki extension, confirm with legal whether SVG assets being LGPL (vs CC-BY or MIT) matters for vendored copies. The repo does not offer an alternative license for icons.
- The migration from Vanilla is ongoing in the sense that Pragma is 0.x; `@canonical/react-components` (the Vanilla-era React lib) still exists and is more widely used (4.10.2, ~16k weekly downloads) — don't confuse its icon story with Pragma's.

## Source URLs

- npm package: https://www.npmjs.com/package/@canonical/ds-assets
- Repo root: https://github.com/canonical/pragma
- ds-assets in repo: https://github.com/canonical/pragma/tree/main/packages/ds-assets
- Icon spec: https://github.com/canonical/pragma/blob/main/packages/ds-assets/docs/ICONS.md
- Icon CHANGELOG: https://github.com/canonical/pragma/blob/main/packages/ds-assets/CHANGELOG.md
- Releases: https://github.com/canonical/pragma/releases (v0.37.0 API: https://api.github.com/repos/canonical/pragma/releases/latest)
- License: https://github.com/canonical/pragma/blob/main/LICENSE (LGPL-3.0); Ubuntu Font Licence for `fonts/ubuntu-sans/`
- Vanilla Framework (legacy): https://github.com/canonical/vanilla-framework
