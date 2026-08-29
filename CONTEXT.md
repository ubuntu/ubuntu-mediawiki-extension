# Ubuntu Wiki Extension

Shared branding, styling, and integrations for the Ubuntu Wiki, layered on top of MediaWiki core and its skins.

## Language

### Ubuntu Wiki concepts

**Code block**:
A `.ubuntu-code-block` element in rendered wiki content (produced by the `Code block` template or raw HTML), enhanced client-side with a copy-to-clipboard button.
_Avoid_: Snippet, terminal block

**Admonition**:
A styled callout template (Note, Warning, Tip, Info, Danger, DocCan) used to highlight a passage of wiki content.
_Avoid_: Callout, alert box

**DocCan**:
An admonition variant that points readers to official documentation hosted outside the wiki, rather than highlighting in-page content.
_Avoid_: External note

**Consent Mode**:
Google Consent Mode v2 integration: default `ad_storage`/`analytics_storage` signals sent as "denied" until the user opts in via the cookie consent banner.
_Avoid_: Tracking consent, GTM consent

**Footer link blanking**:
The pattern of suppressing one of MediaWiki core's default footer links while keeping its position in the footer, rather than removing it outright, so Ubuntu-configured replacement links land in the same slot.
_Avoid_: Hiding a footer link, removing a footer link

**Skin branding layer**:
A per-skin ResourceLoader module (e.g. `ext.ubuntu.styles.vector`, `ext.ubuntu.styles.minerva`) that layers Ubuntu-specific styling on top of the shared `ext.ubuntu.styles` base for one particular skin. The `vector` layer is a mandatory compatibility target (Ubuntu skin lineage); the `minerva` layer is currently a nice-to-have, expected to become mandatory once an Ubuntu Minerva fork exists.
_Avoid_: Skin override, skin theme

**Ubuntu skin**:
A separate extension/skin, maintained in another repository, forked from Vector 2022, registered in MediaWiki as `Ubuntu`. It is this extension's primary compatibility target — Vector and Vector 2022 compatibility matter mainly as a side effect of that fork lineage, not as goals in their own right. A parallel Ubuntu Minerva fork is expected in the future, at which point Minerva compatibility becomes mandatory too.
_Avoid_: Ubuntu Skin (capital S), UbuntuSkin repo

### MediaWiki concepts

**Hook**:
An extension point MediaWiki core calls into at a fixed point in its request lifecycle (e.g. `BeforePageDisplayHook`, `SkinAddFooterLinksHook`). This extension implements hooks in `src/Hooks.php`, kept thin, with feature logic delegated to dedicated classes.
_Avoid_: Event, callback

**ResourceLoader module**:
A named bundle of JS and/or LESS/CSS registered in `extension.json`, loaded on demand by MediaWiki's ResourceLoader. The unit this extension uses to ship client-side code and styles.
_Avoid_: Asset bundle, RL module (spell out on first use)

**Skin**:
A MediaWiki theme controlling page layout and chrome (e.g. Vector, Vector 2022, Minerva, the separate Ubuntu skin). This extension layers branding onto skins; it is not a skin itself. See **Ubuntu skin** for which skins actually matter here and why.
_Avoid_: Theme

**Extension**:
A MediaWiki plugin, registered via `extension.json`, that adds functionality to core without modifying it. This repo is one such extension (`UbuntuWiki`).
_Avoid_: Plugin (in MediaWiki context, "extension" is the canonical term)

**Theme class**:
One of the three `html.skin-theme-clientpref-{day,night,os}` classes MediaWiki's Vector clientpref feature toggles on the document root. Each theme class fully (re)assigns this extension's Codex and Pragma token custom properties for that theme; `os` additionally wraps its assignment in `@media (prefers-color-scheme: dark)` rather than resolving via the CSS `color-scheme` property.
_Avoid_: Clientpref (spell out on first use), color scheme (reserve for the CSS `color-scheme` property, a different mechanism this extension deliberately doesn't rely on)

### Design token concepts

**Codex token**:
A CSS custom property belonging to MediaWiki's Codex design system (e.g. `--background-color-base`), consumed by this extension's `codex-tokens.less`, which maps Codex's expected variable names onto this extension's own color values.
_Avoid_: Design token (too generic — see also **Pragma token**)

**Pragma token**:
A `--pragma-color-*-root` CSS custom property defined in `pragma-tokens.less`. This extension's own stable name for a Canonical Pragma color value, deliberately kept independent of both Codex tokens and upstream Pragma's own `--color-*` npm-package variable names — so a rename on either side doesn't collide with or silently reinterpret the other's namespace.
_Avoid_: Design token, vendor token (the raw, untranslated upstream output in `vendor/pragma/`, distinct from the translated Pragma token consumed by `codex-tokens.less`)

**Pragma component**:
A stable React component imported from `@canonical/react-ds-global` (e.g. `Button`, `Icon`, `Card`, `Tile`) and rendered into a MediaWiki page. Excludes anything under that package's `_work_in_progress/` folder, which this extension treats as unstable and out of scope regardless of how closely it matches a needed shape.
_Avoid_: Design-system component, DS component

**Homepage card**:
A hand-rolled section on the Main Page (a top rule, an uppercase eyebrow label, and content), styled by this extension's own CSS rather than a Pragma component — there is no stable Pragma equivalent for this exact anatomy. Distinct from a **Pragma component** like `Card`/`Tile`, which may end up as the surface underneath a homepage card but doesn't by itself produce the rule/label layout.
_Avoid_: Card (ambiguous with Pragma's `Card` component — say "homepage card" when talking about the Main Page's own section shape)
