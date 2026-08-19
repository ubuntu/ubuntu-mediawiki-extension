# Vendored design tokens

**Do not hand-edit files in this directory.**

`ubuntu-palette.less` is generated from Vanilla Framework's
[`_settings_colors.scss`](https://github.com/canonical/vanilla-framework/blob/main/scss/_settings_colors.scss)
and exposes each theme's colour set as callable LESS mixins
(`.vf-theme-light-colors()`, `.vf-theme-dark-colors()`,
`.vf-theme-paper-colors()`) plus constant Ubuntu branding
(`.vf-static-colors()`). The mixins produce no output until invoked.

See the file header for the upstream ref and generation date.
