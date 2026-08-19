# Vendored @canonical/cookie-policy files

**Do not hand-edit files in this directory.**

`cookie-policy.js` and `cookie-policy.css` are copied from
`node_modules/@canonical/cookie-policy/build/` and rewritten by the
[vendor-cookie-policy](../../../.github/workflows/vendor-cookie-policy.yml)
GitHub Actions workflow:

- JS: `var cpNs =` is rewritten to `window.cpNs =` so the IIFE can be
  `require()`'d by ResourceLoader without indirect eval (CSP-safe), and the
  `sourceMappingURL` comment is stripped since the `.map` isn't vendored.
- CSS: `:root` selectors are scoped to `.cookie-policy` and the
  `.is-dark`/`.is-light`/`.is-paper` theme classes are scoped to
  `.cookie-policy.is-*` so they don't leak outside the banner.

To update the vendored files, bump `@canonical/cookie-policy` in
package.json and let the workflow open a PR, or run the same commands
locally after `npm ci`.
