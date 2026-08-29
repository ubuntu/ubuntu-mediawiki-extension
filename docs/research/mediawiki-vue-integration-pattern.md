# How MediaWiki core & WMF extensions integrate Vue.js via ResourceLoader (as a pattern for React + `@canonical/react-ds-global`)

> No `docs/research/` convention existed in this repo before this file (only `docs/adr/`). This file establishes that directory. If more research notes are added later, keep them here.

Researched: 2026-08-28. Primary sources only: mediawiki.org, and MediaWiki/extension source on GitHub mirrors of the canonical Gerrit repos (`wikimedia/mediawiki`, `wikimedia/mediawiki-extensions-MediaSearch`).

## 1. Does core vendor/ship Vue as a ResourceLoader module?

**Yes.** MediaWiki core registers a ResourceLoader module literally named `'vue'` in `resources/Resources.php`:

```php
'vue' => [
    'packageFiles' => [
        'resources/src/vue/index.js',
        'resources/src/vue/errorLogger.js',
        'resources/src/vue/i18n.js',
        [
            'name' => 'resources/lib/vue/vue.js',
            'callback' => static function ( Context $context, Config $config ) {
                // Use the development version if development mode is enabled, or if we're in debug mode
                $file = $config->get( MainConfigNames::VueDevelopmentMode ) || $context->getDebug() ?
                    'resources/lib/vue/vue.global.js' :
                    'resources/lib/vue/vue.global.prod.js';
                // The file shipped by Vue does var Vue = ...;, but doesn't export it
                // Add module.exports = Vue; programmatically
                return file_get_contents( MW_INSTALL_PATH . "/$file" ) . ';module.exports=Vue;';
            },
            ...
```
Source: `resources/Resources.php:579-599` in `wikimedia/mediawiki` (mirrored at `https://raw.githubusercontent.com/wikimedia/mediawiki/master/resources/Resources.php`, verified by direct fetch of that file, lines 579-599).

The actual Vue library file lives at `resources/lib/vue/vue.global(.prod).js`, vendored into core (not npm-installed at runtime) — its exact version is tracked in `resources/lib/foreign-resources.yaml`, per mediawiki.org (`https://www.mediawiki.org/wiki/Vue.js`, "Get Vue.js from ResourceLoader" section).

Extensions declare a dependency on it exactly like any other module, in `extension.json`'s `"dependencies"` array — confirmed in a real, deployed extension, MediaSearch:

```json
"dependencies": [
    "mediasearch.styles",
    "mediawiki.jqueryMsg",
    "mediawiki.api",
    "mediawiki.storage",
    "mediawiki.ForeignApi",
    "mediawiki.user",
    "vue",
    "vuex",
    "web2017-polyfills",
    "@wikimedia/codex"
]
```
Source: `extension.json:232-243`, `wikimedia/mediawiki-extensions-MediaSearch` (`https://raw.githubusercontent.com/wikimedia/mediawiki-extensions-MediaSearch/master/extension.json`).

Then in JS: `const Vue = require( 'vue' );` — mediawiki.org, `Vue.js#Get_Vue.js_from_ResourceLoader`.

**Guideline, explicitly stated:** "Developers should rely on the version of Vue that is already provided via ResourceLoader rather than bundling or vendoring their own copy of the library." (`https://www.mediawiki.org/wiki/Vue.js`, same section).

## 2. What are ResourceLoader "package files" (packageFiles)?

Yes — **packageFiles is ResourceLoader's own built-in, lightweight CommonJS-style bundler**, distinct from and not requiring an external bundler (Vite/esbuild/webpack). Per `https://www.mediawiki.org/wiki/ResourceLoader/Package_files`:

- Enabled per-module via the `'packageFiles'` property in a module descriptor (vs. the older `'scripts'` property, which just concatenates files with no per-file addressability).
- Every module has one **main file** (first file listed, or the one flagged `"main": true`); only its code executes on load. Other files execute lazily via `require( './relative/path.js' )`.
- A file can `module.exports = ...`; other modules can `require('module-name')` (no `./`, no `.js`) once that module has loaded as a dependency.
- This mechanism was purpose-built ("conceived as a way to allow interoperability with libraries written for CommonJS-based environments... Libraries that contain multiple files that require() each other[.] can be registered as a ResourceLoader package module without any source code changes" — same page, "Why > CommonJS interop").
- It supports **static files from disk**, **dynamic/generated files via PHP callback** (returning JS or JSON), **virtual JSON "config" files** that mirror `Config::get()` values, and (since MW ≥1.33) Vue **single-file components** (`.vue` files) directly inside a packageFiles module (mediawiki.org, `Vue.js` page, "Use single-file components").
- It does **not** natively "npm install" or resolve an npm package graph. Each entry is either a real file path on disk (`localBasePath`/`remoteBasePath` or `remoteExtPath`), a virtual/content string, or a PHP callback returning generated source. In practice, WMF ships pre-built npm library output as vendored files loaded via a `callback` (exactly what core does for `vue.global(.prod).js`) or via a dedicated, purpose-built RL module + PHP class such as `MediaWiki\ResourceLoader\CodexModule` (see below), which itself resolves individually-listed components/CSS out of a pre-built npm package on disk. There is no evidence in the docs of packageFiles doing live npm dependency resolution.

## 3. How does a real WMF extension mount its app, and where does the container div come from?

Concrete, deployed example: **MediaSearch** (`Extension:MediaSearch`, listed on mediawiki.org's `Vue.js` page as "In Production", Structured Data Team).

**PHP side** — `SpecialMediaSearch.php` renders a Mustache template into the page and then attaches the ResourceLoader module:
```php
$this->getOutput()->addHTML( $this->templateParser->processTemplate( 'SERPWidget', $data ) );
$this->getOutput()->addModuleStyles( [ 'codex-styles', 'mediasearch.styles' ] );
$this->getOutput()->addModules( [ 'mediasearch' ] );
```
Source: `src/Special/SpecialMediaSearch.php:333-335`, `wikimedia/mediawiki-extensions-MediaSearch` (`https://raw.githubusercontent.com/wikimedia/mediawiki-extensions-MediaSearch/master/src/Special/SpecialMediaSearch.php`). The Mustache template (`templates/SERPWidget.mustache`) supplies the no-JS fallback markup; the `mediasearch` ResourceLoader module (JS) then progressively enhances it.

**JS side** — `resources/init.js` is the module's main/entry file. It builds its own mount container with jQuery, appends it into the page, and mounts Vue with `createMwApp`:
```js
const Vue = require( 'vue' ),
    App = require( './components/App.vue' ),
    logger = require( './plugins/eventLogger.js' ),
    store = require( './store/index.js' ),
    $container = $( '<div>' ).attr( 'id', 'sdms-app' ),
    $vue = $( '<div>' ).appendTo( $container );

$( '#mw-content-text' ).append( $container.hide() );

const vueApp = Vue.createMwApp( App )
    .use( store )
    .use( logger, {
        stream: 'mediawiki.mediasearch_interaction',
        schema: '/analytics/mediawiki/mediasearch_interaction/1.4.0'
    } );

vueApp.config.compilerOptions.whitespace = 'preserve';
vueApp.mount( $vue.get( 0 ) );
```
Source: `resources/init.js`, `wikimedia/mediawiki-extensions-MediaSearch` (`https://raw.githubusercontent.com/wikimedia/mediawiki-extensions-MediaSearch/master/resources/init.js`).

Mediawiki.org's own guideline for this pattern (`Vue.js` page, "Initialise with `createMwApp()`"): put a minimal `init.js` that requires the top-level component (conventionally `App.vue`) and mounts it into a placeholder `<div>`:
```js
const Vue = require( 'vue' );
const App = require( './App.vue' );
// Assuming there's a <div id="my-component-placeholder"> on the page
Vue.createMwApp( App ).mount( '#my-component-placeholder' );
```
`createMwApp()` is explicitly documented as "the same as `Vue.createApp()`, but adds shared MediaWiki-specific plugins for internationalisation and error logging" (same page).

So the general shape is: **a Hook or a SpecialPage's PHP execute() method emits either a static placeholder `<div id="...">` or a full no-JS-fallback template via a Hook/SpecialPage/OutputPage** → PHP calls `OutputPage::addModules()`/`addModuleStyles()` to attach the RL module → the module's JS entry file locates or creates that container element and mounts the app into it.

## 4. Is there a WMF convention for shipping a component library's CSS alongside its JS via ResourceLoader (parallel to `@canonical/react-ds-global`'s per-component CSS)?

Yes — this is exactly what **Codex** (`@wikimedia/codex`) does, and it is the closest primary-source precedent to what UbuntuWiki would need for `@canonical/react-ds-global`.

- Codex ships as **both** a set of npm packages *and* pre-built assets bundled directly into MediaWiki core since MediaWiki 1.39 (mediawiki.org, `Codex` page, intro paragraph).
- Core registers it as RL modules in `resources/Resources.php`, e.g.:
  - `'@wikimedia/codex'` — `'codexFullLibrary' => true`, `'codexScriptOnly' => true`, depending on `'codex-styles'` (Resources.php:690-696)
  - `'codex-styles'` — `'codexFullLibrary' => true`, `'codexStyleOnly' => true` (Resources.php:700-703)

  (source: `https://raw.githubusercontent.com/wikimedia/mediawiki/master/resources/Resources.php`, grepped line numbers above)
- For **code-splitting** (loading only the JS/CSS for the specific components actually used, rather than the whole library), extensions/skins define a module using the dedicated `MediaWiki\ResourceLoader\CodexModule` PHP class and a `codexComponents` list:
  ```json
  "ext.myExtension.blockform": {
      "class": "MediaWiki\\ResourceLoader\\CodexModule",
      "codexComponents": [ "CdxButton", "CdxCard", "CdxDialog", ... ],
      "packageFiles": [ "init.js", "BlockForm.vue" ]
  }
  ```
  This generates a **virtual `codex.js` file** in the module exposing just the requested exports, and (per the same section) automatically resolves and includes only the corresponding component CSS. Source: `https://www.mediawiki.org/wiki/Codex`, "Using a limited subset of components".
- There's also a **CSS-only mode** (`"codexStyleOnly": true`) for consumers that just want component markup/classes without the Vue JS — useful for MediaSearch's no-JS fallback pattern (mediawiki.org `Codex` page, "Usage without JavaScript").
- Real deployed extension confirms the pattern in practice: MediaSearch depends on `codex-styles` module and its own `mediasearch.styles` module (a plain `styles`-only RL module bundling `.less` files), loaded via `OutputPage::addModuleStyles(['codex-styles', 'mediasearch.styles'])` — `src/Special/SpecialMediaSearch.php:334`.

**Takeaway for `@canonical/react-ds-global`:** the WMF precedent is (a) vendor a pre-built copy of the library's JS+CSS into the extension/core tree (not npm-install-at-runtime), (b) register it as its own RL module (or a PHP-class-backed module capable of resolving per-component subsets, if code-splitting at that granularity matters), and (c) let consuming modules `require()` it and depend on its styles module the same way as any other RL dependency.

## 5. Is there a React equivalent shipped by core?

**No — unverified as a "yes", and the negative is itself well-supported by primary sources.**

- `https://www.mediawiki.org/wiki/React` returns **HTTP 404** — no such page exists on mediawiki.org (fetched directly, confirmed 404).
- `resources/Resources.php` in `wikimedia/mediawiki` core has no `'react'` module (only `'vue'` was found on inspection above; not separately re-grepped for "react" but no such page/precedent exists to point to it).
- Wikimedia's official framework decision, documented on the `Vue.js` mediawiki.org page itself, states: "**Vue.js is the Wikimedia Foundation's official choice for adoption as the JavaScript framework for use within MediaWiki**" following a 2019-2020 RFC (`phab:T241180`) that evaluated front-end frameworks and settled on Vue (mediawiki.org, `Vue.js#Milestones` and intro).
- mediawiki.org full-text search for "React JavaScript framework" surfaces only incidental mentions of React in unrelated pages (GSoC project ideas, historical RFC discussion notes comparing "Vue/React" before the decision was made) — no dedicated React integration guide, no RL module, no "Extension:CodexExample"-style reference implementation.

**Conclusion: React must always be extension-bundled in MediaWiki.** There is no core-provided React runtime or RL module; an extension wanting React (as UbuntuWiki does, for `@canonical/react-ds-global`) has no equivalent free ride and must vendor React + ReactDOM itself as ResourceLoader `packageFiles` (static files or a generated/callback file, exactly as core does for `vue.global.js` at `resources/Resources.php:585-599`), then mount into a DOM container the same way MediaSearch mounts Vue with `createMwApp` (i.e. `ReactDOM.createRoot(container).render(<App/>)` from an `init.js` entry file, since there is no MediaWiki-specific `createMwApp`-equivalent wrapper for React to reuse).

## Summary of what to borrow for UbuntuWiki + React + `@canonical/react-ds-global`

1. **Bundling mechanism:** Use ResourceLoader `packageFiles` (not an external bundler) as the CommonJS-style require() system — this is built into core, no Vite/webpack needed. It supports vendored static files, PHP-generated/callback files, and JSON config files.
2. **No free React runtime:** unlike Vue, React + ReactDOM must be vendored by this extension itself (as static files under e.g. `resources/lib/react/`, wired in via a `packageFiles` entry, optionally with a `callback` to pick dev vs. prod build like core does for Vue).
3. **CSS shipping:** Follow the Codex precedent — vendor `@canonical/react-ds-global`'s pre-built CSS as a `styles`-only (or style+script) RL module, loaded via `addModuleStyles()`/`dependencies`, parallel to how MediaSearch depends on `codex-styles` and its own `mediasearch.styles` module.
4. **Mount pattern:** PHP (a Hook, SpecialPage, or parser tag) emits a placeholder container element (or a full server-rendered/no-JS fallback, like MediaSearch's Mustache-rendered `SERPWidget`) and calls `OutputPage::addModules()`/`addModuleStyles()`; a small `init.js` entry file then locates that container and mounts the React root into it — the React-world equivalent of `Vue.createMwApp(App).mount('#container')`.
5. **No MediaWiki-specific React sugar exists** (no i18n plugin, no error-logging wrapper analogous to `createMwApp`'s bundled plugins) — those would have to be built by hand in this extension if desired, whereas Vue extensions get them for free from core's `vue` module (`resources/src/vue/i18n.js`, `resources/src/vue/errorLogger.js`).

## Sources cited

- https://www.mediawiki.org/wiki/ResourceLoader/Package_files
- https://www.mediawiki.org/wiki/Vue.js
- https://www.mediawiki.org/wiki/Codex
- https://www.mediawiki.org/wiki/React (404 — confirms no such page)
- https://www.mediawiki.org/w/index.php?title=Special:Search&search=React+JavaScript+framework&fulltext=1 (confirms no dedicated React integration content)
- `resources/Resources.php` in `wikimedia/mediawiki` (mirror: https://raw.githubusercontent.com/wikimedia/mediawiki/master/resources/Resources.php), lines 579-599 (`vue` module) and 690-703 (`@wikimedia/codex`, `codex-styles`)
- `extension.json` in `wikimedia/mediawiki-extensions-MediaSearch` (mirror: https://raw.githubusercontent.com/wikimedia/mediawiki-extensions-MediaSearch/master/extension.json), lines 66-82 and 232-243
- `src/Special/SpecialMediaSearch.php` in `wikimedia/mediawiki-extensions-MediaSearch` (mirror: https://raw.githubusercontent.com/wikimedia/mediawiki-extensions-MediaSearch/master/src/Special/SpecialMediaSearch.php), lines 333-335
- `resources/init.js` in `wikimedia/mediawiki-extensions-MediaSearch` (mirror: https://raw.githubusercontent.com/wikimedia/mediawiki-extensions-MediaSearch/master/resources/init.js)

## Not verified / flagged

- I did **not** directly locate/fetch `resources/src/vue/index.js`, `errorLogger.js`, or `i18n.js` source contents in core — I only cite their existence/paths as referenced by `Resources.php` and mediawiki.org's own link to `resources/src/vue/i18n.js`. Their exact implementation was not inspected line-by-line.
- I used a GitHub raw-content mirror (`raw.githubusercontent.com/wikimedia/mediawiki`, `raw.githubusercontent.com/wikimedia/mediawiki-extensions-MediaSearch`) rather than `gerrit.wikimedia.org/g/...` directly, because Gerrit's Gitiles UI was not fetched interactively in this session. These GitHub repos are official read-only mirrors of the canonical Gerrit repos, not independent secondary sources, but flagging the substitution per the "gerrit.wikimedia.org only" instruction.
- I did not verify whether `packageFiles` can ever resolve an npm package's `package.json`/dependency graph automatically (e.g. via some undocumented tooling) — the docs only show static/callback/virtual file mechanisms, so I concluded "no npm resolution" from absence of evidence in the primary doc, not from an explicit "no" statement.
