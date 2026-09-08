# Vendored icon delivery via generated mask classes

Icons for the Ubuntu Wiki are vendored from external design systems (currently
Canonical Pragma, via the `@canonical/ds-assets` npm tarball, pinned by exact
version) into `resources/icons/<source>/` as unmodified SVG files, and exposed
to wiki text and extension components through one public CSS class contract:
`.ubuntu-<source>-icon-<name>` (e.g. `.ubuntu-pragma-icon-settings`). The
generated LESS applies each icon to an element's `::before` as a CSS mask with
`background-color: currentColor` and `width/height: var(--ubuntu-icon-size, 1em)`,
so icons inherit text colour (recoloring, dark mode) and scale with surrounding
text; explicit per-element override is done via the custom property. Icon names
pass through from upstream unchanged rather than through a local alias layer —
instead, the vendoring script scans our own LESS and seed content for
`ubuntu-<source>-icon-<name>` usages and fails loudly when a name is removed or
renamed upstream. The generated LESS and a per-source `MANIFEST.json` are
committed (deployment needs no build step); a Python 3 stdlib script
(`dev-scripts/vendor_icons.py`, run via `make vendor-icons`) performs sync and
`--check`, and a scheduled GitHub workflow auto-opens a PR when a new upstream
version exists. Vendored Pragma icons are LGPL-3.0; accepted.

## Considered options

- **Inline data URIs in the generated LESS**: rejected — duplicates the on-disk
  SVGs and hand-rolls what ResourceLoader's CSS `url()` handling already does
  (small files get inlined automatically).
- **Local alias/mapping layer over upstream names**: rejected as speculative
  drift-prone indirection; the usage scan gives the safety without the layer.
- **A dedicated conditional icon ResourceLoader module**: rejected — arbitrary
  wiki-text usage makes conditional loading unreliable, and the payload is
  modest and compresses well; classes ship in the `ext.ubuntu.styles` base.
- **Node for the vendoring script**: rejected — the task is HTTP + tarball +
  string substitution; Python 3 stdlib does it with zero dependencies and
  matches existing tooling.

## Consequences

- The class-name contract is public: renaming it later breaks wiki pages.
  Future icon sources must adopt the same `.ubuntu-<source>-icon-<name>` shape.
- The empty-per-source layout (`resources/icons/<source>/` + `MANIFEST.json`)
  is the extension point for future sources; no registry schema exists until a
  second source actually arrives.
- ResourceLoader path resolution of the relative `url()` references must be
  verified in implementation; if embedding behaviour differs from expectation,
  switching the generated rules to data URIs is a contained, reversible change.
