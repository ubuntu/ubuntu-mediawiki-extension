# Resources

ResourceLoader modules shipped by the UbuntuWiki extension. Each module lives
in a directory named after it. Entry files contain doc comments describing
their purpose in detail; this file is the map.

## Modules

| Module                          | Purpose                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | Loaded when                                                                                                          |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------- |
| `ext.ubuntu.styles`             | Common layer applied to every skin: Vanilla palette tokens (CSS custom properties), Ubuntu Sans webfonts, variables/mixins, and skin-agnostic component styles (code blocks, on-wiki template styles, content classes, print heading rules, link hover colors, blanked-footer-link hiding). The ubuntu skin fork depends on these tokens and fonts directly.                                                                                                             | Every page view (added in `Hooks::onBeforePageDisplay`); minerva additionally gets it via `ResourceModuleSkinStyles` |
| `zzz.ext.ubuntu.styles.minerva` | Minerva-specific adaptations of the shared styles.                                                                                                                                                                                                                                                                                                                                                                                                                       | Every page view; only serves minerva (module `skins` option)                                                         |
| `zzz.ext.ubuntu.styles.vector`  | Ubuntu branding for Vector-2022-class skins: dark header, logo and search-box theming (`components/Header.less`), page surroundings and content spacing (`components/Layout.less`), page-action tab and titlebar styles (`components/Body.less`), Tools menu colors and dropdown-button padding (`components/PageTools.less`), and icon button sizing and hover background (`components/Icons.less`). Selectors only match Vector markup, so other skins are unaffected. | Every page view; only serves ubuntu / vector / vector-2022 (module `skins` option)                                   |
| `ext.ubuntu.codeBlock`          | Copy-button enhancement for `.ubuntu-code-block` markup (clipboard copy, accessible status announcements). Styles live in `ext.ubuntu.styles/components/CodeBlock.less`.                                                                                                                                                                                                                                                                                                 | Every page view (added in `Hooks::onBeforePageDisplay`)                                                              |
| `ext.ubuntu.cookieConsent`      | Canonical cookie-policy consent banner integration (vendored library + MediaWiki glue).                                                                                                                                                                                                                                                                                                                                                                                  | `$wgUbuntuCookieConsentEnabled = true` (added in `Hooks::onBeforePageDisplay`)                                       |

Per-skin layers are delivered via the module's own `skinStyles` (appended
after the shared base within the module's stylesheet), never via top-level
`ResourceModuleSkinStyles` — that attribute is reserved for skins (or the
site) overriding a _module's_ styles, and module-defined skinStyles take
precedence over it. Each layer's module declares a `skins` option listing
the skins it serves; ResourceLoader reads that list itself, so the hook
attaches every layer unconditionally and the skin list lives only in
extension.json. Layer modules are named `zzz.ext.*` so they sort after
every `skins.*` module in the combined stylesheet — their rules win
specificity ties against the skin's own styles by source order alone.

## Conventions

- **Entry files are import-only.** `common.less` / `minerva.less` /
  `vector.less` only `@import`; actual declarations live in
  `components/*.less` (per-component), `components/templates/*.less`
  (on-wiki template styles), and `vendor/*.less` (generated design tokens).
  Add a file, add an import — extension.json does not need to change.
- **Variables and mixins are shared** via `ext.ubuntu.styles/variables.less`
  and `mixins.less`, which other modules import relatively
  (e.g. `@import '../ext.ubuntu.styles/variables.less';`).
- **Template styles are shared content styles.** The on-wiki templates emit
  the same markup no matter which skin is active, so their styling belongs in
  `ext.ubuntu.styles`, not in any individual skin.
- **CSS custom properties are the cross-repo bridge.** The Ubuntu skin fork
  (ubuntu-mediawiki-skin) owns its own styling but depends on tokens like
  `var(--vf-color-brand)` defined in `ext.ubuntu.styles/vendor/`.
  LESS-time imports across repos are not possible, so treat the token names
  as a stable public contract.
- **Fonts live in `resources/fonts/`** and are declared in
  `ext.ubuntu.styles/components/Fonts.less` with per-script `unicode-range`
  subsets, so browsers only download what a page uses. The base
  (`Ubuntu Sans`) and mono (`Ubuntu Sans Mono`) stacks are applied in
  `ext.ubuntu.styles/components/Typography.less`, so both skins get them
  from this module.
- **Vendored code goes in a `vendor/` subdirectory** of its module and is
  never hand-edited — see `ext.ubuntu.cookieConsent/vendor/README.md` and the
  `vendor-cookie-policy` GitHub workflow.

## Ownership boundary

- **This extension**: cross-skin integrations (cookie banner, footer links),
  shared design tokens, on-wiki template styles, Minerva adaptations, and the
  Ubuntu _theme/branding_ layer for Vector-2022-class skins
  (`zzz.ext.ubuntu.styles.vector`) — colors, token re-application, logo and
  search-box theming on the skin's own classes.
- **ubuntu-mediawiki-skin**: the skin's HTML structure and layout mechanics
  (grid, heights, component arrangement). Its `ubuntu/ubuntu-header.less`
  branding layer is superseded by this extension's vector layer and should be
  dropped once the skin requires the updated extension. No skin-chrome markup
  or layout changes may live in the extension — it must stay possible to
  understand the skin's HTML from the skin repo alone.
