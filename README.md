# Ubuntu Wiki MediaWiki Extension

This is a MediaWiki extension for the Ubuntu Wiki, holding special integrations as well as shared resources.

## Local development with Docker

The repo ships a Makefile and docker-compose.yml that spin up a throwaway MediaWiki 1.46 + MariaDB instance with this extension live-mounted at `extensions/UbuntuWiki` — edits to `src/` and `resources/` apply on page reload, no rebuilds.

Prerequisites: Docker (with the compose plugin) and git. Vector is the default skin; MobileFrontend is also installed (shallow-cloned into the gitignored `.ext/` by `make setup`) and serves MinervaNeue to mobile devices — use a mobile user-agent or append `?useformat=mobile` to test the minerva skin styles. (The Ubuntu skin is deliberately not installed: its current release declares `UbuntuCookieConsentEnabled` itself, which conflicts with this extension.)

```sh
make setup   # first run: start containers, install MediaWiki, seed test pages
```

Then open <http://localhost:8080> (user `admin`, password `UbuntuWiki2026!`).

| Target        | What it does                                                     |
| ------------- | ---------------------------------------------------------------- |
| `make setup`  | First-time setup: containers, DB install, seeded pages           |
| `make up`     | Start containers (redeploys LocalSettings.php)                   |
| `make down`   | Stop containers                                                  |
| `make clean`  | Stop containers and DELETE the database volume (full reset)      |
| `make deploy` | Copy LocalSettings.php into the container and run update.php     |
| `make seed`   | (Re)import the test pages from seed/ (overwrites existing pages) |
| `make update` | Run MediaWiki's update.php in the container                      |
| `make lint`   | Run phpcs, parallel-lint and minus-x locally                     |
| `make shell`  | Open a shell in the mediawiki container                          |

Note: don't run this and the skin repo's environment at the same time — both bind port 8080.

### Seeded test pages

`make setup` imports the wikitext files in [seed/](seed/) (file name = page title):

- **Main Page** — overview and links
- **Code block examples** — `.ubuntu-code-block` markup in regular wikitext: template-driven blocks, raw HTML blocks, custom copy labels, tabindex/focus-order cases, and a SyntaxHighlight comparison
- **Template:Code block** — the template used by the examples page
- **CAPTCHA testing** — instructions for the CAPTCHA scenario

### Testing code blocks outside wikitext (CAPTCHA)

The example LocalSettings enables ConfirmEdit + QuestyCaptcha **for testing only**, with `skipcaptcha` revoked from every group so each edit shows a CAPTCHA. The question embeds an `.ubuntu-code-block.ubuntu-code-block--captcha` block as raw HTML — the same markup the on-wiki templates produce — so you can verify the copy button where no parser output is involved:

1. Edit any page and hit save — the CAPTCHA appears with a code block (the answer is `42`).
2. Check the copy button appears, copies the command, and gets the "Copy terminal command for CAPTCHA" aria-label.
3. Also try VisualEditor: its CAPTCHA widget is injected dynamically after the failed save, exercising the MutationObserver path in codeBlock.js.
