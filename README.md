# Ubuntu Wiki MediaWiki Extension

This is a MediaWiki extension for the Ubuntu Wiki, holding special integrations as well as shared resources.

## Local development with Docker

The repo ships a Makefile and docker-compose.yml that spin up a throwaway MediaWiki 1.46 + MariaDB instance with this extension live-mounted at `extensions/UbuntuWiki` — edits to `src/` and `resources/` apply on page reload, no rebuilds.

Prerequisites: Docker (with the compose plugin) and git. `make setup` and `make up` install the Ubuntu desktop skin, UbuntuMinervaNeue, and MobileFrontend from `composer.local.json`. Ubuntu is the default desktop skin; MobileFrontend uses the `ubuntu-minerva` skin for mobile requests. Use a mobile user-agent or append `?useskin=ubuntu-minerva` to test Ubuntu Minerva styling.

```sh
make setup   # first run: start containers, install MediaWiki, seed test pages
```

Then open <http://localhost:8088> (user `admin`, password `UbuntuWiki2026!`).

Common targets:

- `make setup`: First-time setup: start containers, install MediaWiki, and seed pages.
- `make up`: Start containers, install Composer dependencies, and copy settings if the wiki is installed.
- `make down`: Stop containers.
- `make clean`: Stop containers and delete the database volume (full reset).
- `make settings`: Copy LocalSettings.php into the container and run the database update.
- `make db-update`: Run MediaWiki's database update script.
- `make seed`: Reimport or overwrite the test pages from seed/.
- `make composer`: Install dependencies from composer.local.json.
- `make composer-update`: Update Composer dependencies and regenerate the lock file.
- `composer test`: Run PHPCS, parallel PHP lint, and minus-x checks.
- `make shell`: Open a shell in the MediaWiki container.

The environment binds port 8088 by default (the skin repo's environment uses 8080, so both can run side by side). To use a different port, set `UBUNTU_EXT_PORT` before running make: `UBUNTU_EXT_PORT=9090 make setup`.

### Seeded test pages

`make setup` imports the wikitext files in [seed/](seed/) (file name = page title):

- **Main Page** — overview and links
- **Code block examples** — `.ubuntu-code-block` markup in regular wikitext: template-driven blocks, raw HTML blocks, custom copy labels, tabindex/focus-order cases, and a SyntaxHighlight comparison
- **Tables** — tables rendered from wikitext
- **Syntax highlighting** — examples in several highlighted languages
- **TOC test** — long article with many sections
- **Template:Code block** — the template used by the examples page
- **Template examples** — shared admonition styles across all variants
- **Template:Admonition** — the generic admonition template, plus typed admonition wrappers for note, warning, tip, doccan, info, and danger
- **CAPTCHA testing** — instructions for the CAPTCHA scenario

### Testing code blocks outside wikitext (CAPTCHA)

The example LocalSettings enables ConfirmEdit + QuestyCaptcha **for testing only**, with `skipcaptcha` revoked from every group so each edit shows a CAPTCHA. The question embeds an `.ubuntu-code-block.ubuntu-code-block--captcha` block as raw HTML — the same markup the on-wiki templates produce — so you can verify the copy button where no parser output is involved:

1. Edit any page and hit save — the CAPTCHA appears with a code block (the answer is `42`).
2. Check the copy button appears, copies the command, and gets the "Copy terminal command for CAPTCHA" aria-label.
3. Also try VisualEditor: its CAPTCHA widget is injected dynamically after the failed save, exercising the MutationObserver path in codeBlock.js.
