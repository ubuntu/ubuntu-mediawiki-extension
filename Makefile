.DEFAULT_GOAL := help

.PHONY: help setup up down restart clean distclean settings db-update \
	composer composer-update seed logs shell run jobs

# Password for the initial admin account created by `make setup`
ADMIN_PASSWORD := UbuntuWiki2026!

# Host port for the test wiki; override with UBUNTU_EXT_PORT=<port> to run
# alongside other MediaWiki environments (see docker-compose.yml).
PORT := $(or $(UBUNTU_EXT_PORT),8088)
export UBUNTU_EXT_PORT

COMPOSE := docker compose
MW := $(COMPOSE) exec mediawiki
MW_T := $(COMPOSE) exec -T mediawiki

# Shell snippet (run inside the container) that makes composer and unzip
# available. Composer is installed with the officially documented phar + sha384
# signature check. Quoting: single-quoted shell string, so double quotes inside
# are written as \" (escaped for make).
define COMPOSER_SETUP
export COMPOSER_ALLOW_SUPERUSER=1; \
command -v composer >/dev/null 2>&1 || { \
	php -r "copy(\"https://getcomposer.org/installer\", \"/tmp/composer-setup.php\");" && \
	php -r "copy(\"https://composer.github.io/installer.sig\", \"/tmp/composer-setup.sig\");" && \
	php -r "if (hash_file(\"sha384\", \"/tmp/composer-setup.php\") !== trim(file_get_contents(\"/tmp/composer-setup.sig\"))) { fwrite(STDERR, \"ERROR: Invalid Composer installer signature. Aborting.\\n\"); exit(1); }" && \
	php /tmp/composer-setup.php --install-dir=/usr/local/bin --filename=composer --quiet && \
	rm -f /tmp/composer-setup.php /tmp/composer-setup.sig; \
}; \
command -v unzip >/dev/null 2>&1 || { apt-get update -qq && apt-get install -y -qq unzip; }
endef

# Help is generated from this file: `## name: description` comments document
# targets, `### Name` comments start a category. Both are printed in file
# order, so keep targets ordered by importance within their category.
## help: Show this help (default target)
help:
	@echo "Usage: make <target>"
	@awk '/^### / { printf "\n%s:\n", substr($$0, 5); next } /^## [a-zA-Z_-]+: / && !/^## help:/ { line = substr($$0, 4); i = index(line, ": "); printf "  %-18s %s\n", substr(line, 1, i - 1), substr(line, i + 2) }' $(MAKEFILE_LIST)
	@echo ""

### Lifecycle

## setup: Create and initialize the wiki from scratch (installs MediaWiki)
setup: up
	@echo "Waiting for database..."
	@until $(MW_T) bash -c "php -r \"new mysqli('db', 'mediawiki', 'mediawiki', 'mediawiki');\"" > /dev/null 2>&1; do printf '.'; sleep 2; done
	@echo " ready."
	$(MW) php maintenance/run.php install \
		--dbtype mysql --dbserver db --dbname mediawiki \
		--dbuser mediawiki --dbpass mediawiki \
		--pass '$(ADMIN_PASSWORD)' \
		"Ubuntu wiki" admin
	@# The installer writes its own LocalSettings.php; overwrite with ours
	$(COMPOSE) cp LocalSettings.php mediawiki:/var/www/html/LocalSettings.php
	$(MAKE) --no-print-directory db-update
	$(MAKE) --no-print-directory seed
	@echo ""
	@echo "Setup complete!"
	@echo "  URL:      http://localhost:$(PORT)"
	@echo "  Username: admin"
	@echo "  Password: $(ADMIN_PASSWORD)"

## up: Start the containers (runs `composer`; copies LocalSettings.php if installed)
up: LocalSettings.php
	$(COMPOSE) up -d
	$(MAKE) --no-print-directory composer
	@# Only copy settings if the wiki is already installed; the installer
	@# refuses to run when LocalSettings.php already exists. Probe the DB
	@# directly (maintenance scripts need LocalSettings.php themselves, so
	@# they cannot answer "am I installed?" before the file exists). Wait for
	@# the DB first: after a fresh `up`/`restart` MariaDB may still be
	@# initializing, and the probe would wrongly conclude "not installed".
	@until $(MW_T) bash -c "php -r \"new mysqli('db', 'mediawiki', 'mediawiki', 'mediawiki');\"" > /dev/null 2>&1; do sleep 2; done
	@if $(MW_T) bash -c "php -r \"exit((new mysqli('db', 'mediawiki', 'mediawiki', 'mediawiki'))->query('SELECT 1 FROM page LIMIT 1') ? 0 : 1);\"" > /dev/null 2>&1; then \
		$(COMPOSE) cp LocalSettings.php mediawiki:/var/www/html/LocalSettings.php; \
	else \
		echo "Wiki not installed yet; skipping LocalSettings.php copy (run 'make setup')."; \
	fi

## down: Stop and remove the containers
down:
	$(COMPOSE) down

## restart: Restart the containers (`down` then `up`)
restart: down up

## clean: Stop the containers and delete the database volume (DESTRUCTIVE)
clean:
	$(COMPOSE) down -v

## distclean: `clean` plus delete the generated LocalSettings.php (DESTRUCTIVE)
distclean: clean
	rm -f LocalSettings.php

### Content

# Import the test pages from seed/ into the wiki. Page titles come from the
# file names (e.g. "Template:Code_block.txt" becomes "Template:Code block").
# Idempotent: --overwrite replaces pages that already exist.
## seed: Import the test pages from seed/ into the wiki (idempotent)
seed:
	$(MW_T) mkdir -p /tmp/seed
	$(COMPOSE) cp seed/. mediawiki:/tmp/seed/
	$(MW_T) bash -c '\
		php maintenance/run.php importTextFiles \
			--user Admin --summary "Seed test content" --overwrite \
			/tmp/seed/*.txt'
	$(MW_T) bash -c '\
		find /tmp/seed -mindepth 2 -type f -name "*.txt" -print0 | \
		while IFS= read -r -d "" file; do \
			relative="$${file#/tmp/seed/}"; \
			prefix="$${relative%/*}/"; \
			php maintenance/run.php importTextFiles \
				--user Admin --summary "Seed test content" --overwrite \
				--prefix "$$prefix" "$$file"; \
		done'
	@# Pages imported early in the glob (e.g. Main_Page) link to pages created
	@# later (e.g. TOC test); the backlink refresh jobs are queued but not run
	@# during CLI import, so run them now or those links stay red.
	$(MAKE) --no-print-directory jobs

## jobs: Force-run the MediaWiki job queue
jobs:
	$(MW_T) php maintenance/run.php runJobs

### Configuration

## settings: Copy LocalSettings.php into the container and run DB update
settings: LocalSettings.php
	$(COMPOSE) cp LocalSettings.php mediawiki:/var/www/html/LocalSettings.php
	$(MAKE) --no-print-directory db-update

## db-update: Run the MediaWiki database update script
db-update:
	$(MW_T) php maintenance/run.php update --quick

### Composer

# Install composer dependencies defined by the mounted composer.local.json.
# This will utilize the lock file if available, and generate one if not.
## composer: Install composer dependencies defined by the mounted composer.local.json.
composer:
	$(MW_T) bash -c '$(COMPOSER_SETUP); \
		composer install --no-interaction --no-progress && \
		composer update ubuntu/mediawiki-ubuntu-skin --with-all-dependencies --no-interaction --no-progress'

## composer-update: Update all composer dependencies to their latest versions and regenerate the lockfile
composer-update:
	$(MW_T) bash -c '$(COMPOSER_SETUP); composer update --no-interaction --no-progress'


### Debugging

## logs: Follow the mediawiki container logs (Ctrl-C to stop)
logs:
	$(COMPOSE) logs -f mediawiki

## shell: Open an interactive bash shell in the mediawiki container
shell:
	$(MW) bash

## run: Run a MediaWiki maintenance script, e.g. make run SCRIPT="runJobs --maxjobs 5"
run:
	$(MW_T) php maintenance/run.php $(SCRIPT)

LocalSettings.php:
	cp LocalSettings.example.php LocalSettings.php
	@echo "Created LocalSettings.php from LocalSettings.example.php — edit it before running setup."
