# Keep `--pragma-color-*-root` naming and per-theme-class reassignment when wiring in vendored Pragma tokens

Vendoring `@canonical/design-tokens` (#38) surfaced two mismatches with this
extension's existing Pragma tokens: upstream's CSS custom properties drop the
`pragma-`/`-root` naming (`--color-border` vs. `--pragma-color-border-root`),
and upstream resolves light/dark per-token via the native CSS `light-dark()`
function gated on `color-scheme`, whereas this extension reassigns a full set
of Pragma (and Codex) tokens per theme class
(`html.skin-theme-clientpref-{day,night,os}`; see `CONTEXT.md`).

We decided to keep `--pragma-color-*-root` as this extension's own stable
name (translating vendored values underneath it, rather than renaming
consumers to upstream's names), and to keep resolving light vs. dark by
reassigning tokens per theme class rather than adopting `light-dark()`
directly. Reasons:

- `--pragma-color-*-root` is namespaced independently from both Codex's own
  token names and upstream Pragma's `--color-*` names; adopting the latter
  risks colliding with or being confused for Codex tokens, which already use
  a bare `--color-*`-style vocabulary.
- The Ubuntu skin fork (a separately-maintained repo) is documented in
  `common.less` as depending on these tokens directly as a stable contract;
  renaming them is out of scope for this map (a hand-off finding, not a
  local decision) per `docs/adr` for map #37's own scoping.
- Per-theme-class reassignment (rather than delegating to `color-scheme`
  resolution) is an assumption already relied on elsewhere in this
  extension's theming (e.g. `Header.less` reads `--pragma-color-*` directly
  per theme class), so switching mechanisms here would need to happen
  everywhere at once, not just for the vendored tokens.

Consequence: any future wiring-in of the vendored tokens needs a translation
mixin that assigns `--pragma-color-*-root` from the vendored `--color-*`
values once per theme class (day/night/os), rather than emitting the
vendored tokens' single `light-dark()`-resolved block directly.
