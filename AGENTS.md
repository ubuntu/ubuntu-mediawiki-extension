# AGENTS.md

This is the `UbuntuWiki` MediaWiki extension: shared branding, styling, and integrations (code-block copy buttons, cookie consent, Google Tag Manager, footer link customization) for the Ubuntu Wiki, layered across MediaWiki skins (Vector, Vector 2022, Minerva).

Before working in this repo, read `CONTEXT.md` for the project's domain vocabulary, and `docs/adr/` for any recorded architectural decisions relevant to the area you're touching. See `README.md` for local Docker dev setup.

## Agent skills

### Issue tracker

Issues live as GitHub issues in `ubuntu/ubuntu-mediawiki-extension`, managed via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Default vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: root `CONTEXT.md` + `docs/adr/`. See `docs/agents/domain.md`.
