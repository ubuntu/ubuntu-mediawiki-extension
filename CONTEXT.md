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
