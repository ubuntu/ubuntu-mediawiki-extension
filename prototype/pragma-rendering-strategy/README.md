# Prototype: Pragma component rendering strategy for MediaWiki

**Throwaway — not production code.** Answers ticket #40 ("how do we render
real Pragma React components inside a PHP-rendered MediaWiki page?").
Requires `npm install react@19 react-dom@19 @canonical/react-ds-global@0.35.0
@canonical/design-tokens@0.8.2 @canonical/ds-assets@0.35.0 esbuild@0.28` in
this directory to run; not wired into the repo's own `package.json`.

## What was tried

1. **`render.mjs` + `build.mjs`** — build-time static rendering via plain
   `react-dom/server.renderToStaticMarkup()` (deliberately *not*
   `@canonical/react-ssr`, which is a full-app SSR framework expecting a
   persistent Express/Bun server and a Vite pipeline — a mismatch for
   embedding a fragment into a page MediaWiki already owns).
2. **`client-mount.mjs` + `build-client.mjs`** — client-side islands:
   bundle React + the needed components for the browser, mount into
   `.ubuntu-pragma-mount` container divs (standing in for what a PHP hook
   would emit), reading props from `data-*` attributes.

## Findings (see ticket #40 for the full discussion)

- `@canonical/react-ds-global` has no `exports` subpath map, and every
  component file side-effect-imports its own `.css` — plain Node/browser
  `import` can't load `.css`, so **a bundler (esbuild sufficed; no Vite
  needed) is mandatory for either direction**, not just client-islands.
- `Button` hardcodes `Icon`'s default `rootPath` (`/icons`) internally, with
  no prop to override it — decided **not** to serve icons from the site
  root (can't guarantee nothing else claims `/icons`), so `Button`'s built-in
  icon slot can't be used as-is with a safe path. Client-side mounting
  sidesteps this cleanly: the bundle knows the real ResourceLoader-served
  path at runtime and can pass `rootPath` to `Icon` directly.
- `Button` always renders a real `<button>`, never `<a>`, regardless of
  `variant`. This is orthogonal to the rendering strategy (both static and
  client-rendered `Button` output the same tag) — decided not to use
  `Button` for navigation links either way; use `Icon` + a hand-styled `<a>`
  for links, reserve `Button` for genuine actions.
- Bundled size: 202KB minified / ~62KB gzip, ~87% of which is React +
  ReactDOM itself; the components used add ~1KB. The cost of client-islands
  is "shipping React," not which components are chosen.
- Each component ships its own `styles.css` (e.g. `Button/styles.css`,
  referencing `--color-*`/`--dimension-*` custom properties) — a vendoring
  surface separate from what #38 vendored (tokens/reset only). A real build
  needs to collect these too.

## Verdict

**Client-side islands**, per the discussion on #40. Not verified against a
real running MediaWiki instance yet — that's #42's job.
