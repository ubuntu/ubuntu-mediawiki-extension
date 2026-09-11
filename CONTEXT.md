# Ubuntu Wiki Extension

Shared branding, styling, and integrations for the Ubuntu Wiki, layered on top of MediaWiki core and its skins.

## Language

### Ubuntu Wiki concepts

**Seeded wiki page**:
A wiki page imported from a file under `seed/` for local development and demonstration.
_Avoid_: Fixture, sample page

**Seed category**:
A native MediaWiki category that classifies one or more seeded wiki pages for reader-facing discovery. Seed categories can be nested where useful, and a seeded wiki page can belong to multiple seed categories.
_Avoid_: Seed folder, seed group

**Seed category hierarchy**:
The tree-like navigation presented by linked seed categories, rooted at `Seed content`. Because categories and pages can have multiple parents, its underlying structure is a graph rather than a strict tree.
_Avoid_: Seed tree, seed folder hierarchy

**Module documentation page**:
A wikitext `Module:` subpage ending in `/doc` that describes a seeded Lua module and can belong to seed categories without modifying executable module source.
_Avoid_: Module source documentation, Lua category marker

**Seed catalogue**:
The compact directory on the Main Page that links to every seed category and highlights selected seeded wiki pages. It is not a complete page-by-page listing.
_Avoid_: Seed index, seed inventory

**Demonstration category link**:
A category link used only to illustrate a homepage layout, without implying that seeded wiki pages belong to that category.
_Avoid_: Seed category, taxonomy category

**Editorial card collection**:
A source-ordered group of content cards that uses compact, column-oriented visual flow for standard cards while placing featured cards in their own full-width sections. Its visual layout must not change the linear reading order exposed to keyboard and screen-reader users.
_Avoid_: Masonry grid, reordered card grid

**Featured card**:
A card in an editorial card collection that is intentionally presented in a full-width section because its content benefits from more horizontal space than a standard card. This is a presentation role, not a different semantic content type.
_Avoid_: Double-width card, hero card

**Card composition classes**:
The `ubuntu-card-*` CSS classes that provide reusable card collection, flow, featured-card, and card-internal layout roles. They may be used on any wiki page; homepage templates and Lua modules are convenience authoring interfaces, not the sole consumers.
_Avoid_: Main-page CSS, homepage-only components

**Card link directory**:
A reusable card-internal arrangement pairing a contextual label and description with a group of navigational links. It adapts between side-by-side and stacked presentation according to the rendered card width.
_Avoid_: Documentation-card split, homepage link panel

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

**Vendored icon**:
An SVG icon file copied unmodified from an external design system into this repository (under `resources/icons/`), never hand-edited, and refreshed only by the vendoring script. Its wiki-visible interface is the generated icon class, not the file.
_Avoid_: Bundled icon, asset copy

**Icon source**:
An external design system from which icons are vendored (currently Canonical Pragma). Identified by a short lowercase token (e.g. `pragma`) used consistently as the vendor directory name and the class-name segment. One directory + one manifest per source.
_Avoid_: Icon vendor, icon provider

**Icon class contract**:
The public CSS class naming scheme `.ubuntu-<source>-icon-<name>` (e.g. `.ubuntu-pragma-icon-settings`) used in wiki text and extension components alike. Icon names pass through from the upstream source unchanged; the classes are the stable contract, the underlying files are not.
_Avoid_: Icon alias, icon mapping

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
