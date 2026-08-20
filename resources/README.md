# Resources

ResourceLoader modules shipped by the UbuntuWiki extension. Each module lives
in a directory named after it. Entry files contain doc comments describing
their purpose in detail; this file is the map.

## Modules

| Module                      | Purpose                                                                                                                                                                                                                                                                    | Loaded when                                                                                                          |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `ext.ubuntu.styles`         | Common layer applied to every skin: Vanilla palette tokens (CSS custom properties), Ubuntu Sans webfonts, variables/mixins, and skin-agnostic component styles (code blocks and on-wiki template styles). The ubuntu skin fork depends on these tokens and fonts directly. | Every page view (added in `Hooks::onBeforePageDisplay`); minerva additionally gets it via `ResourceModuleSkinStyles` |
| `ext.ubuntu.styles.minerva` | Minerva-specific adaptations of the shared styles.                                                                                                                                                                                                                         | Minerva skin active                                                                                                  |
| `ext.ubuntu.codeBlock`      | Copy-button enhancement for `.ubuntu-code-block` markup (clipboard copy, accessible status announcements). Styles live in `ext.ubuntu.styles/components/CodeBlock.less`.                                                                                                   | Every page view (added in `Hooks::onBeforePageDisplay`)                                                              |
| `ext.ubuntu.cookieConsent`  | Canonical cookie-policy consent banner integration (vendored library + MediaWiki glue).                                                                                                                                                                                    | `$wgUbuntuCookieConsentEnabled = true` (added in `Hooks::onBeforePageDisplay`)                                       |

## Conventions

- **Entry files are import-only.** `common.less` / `minerva.less` only
  `@import`; actual declarations live in `components/*.less` (per-component),
  `components/templates/*.less` (on-wiki template styles), and `vendor/*.less`
  (generated design tokens). Add a file, add an import — extension.json does
  not need to change.
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
  shared design tokens, on-wiki template styles, Minerva adaptations.
- **ubuntu-mediawiki-skin**: all styling of the `ubuntu` skin itself.
