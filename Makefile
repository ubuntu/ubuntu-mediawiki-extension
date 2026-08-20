.PHONY: setup deploy up down clean update seed lint shell

# Password for the initial admin account created by `make setup`
ADMIN_PASSWORD := UbuntuWiki2026!

# Host port for the test wiki; override with UBUNTU_WIKI_PORT=<port> to run
# alongside other MediaWiki environments (see docker-compose.yml).
PORT := $(or $(UBUNTU_WIKI_PORT),8088)
export UBUNTU_WIKI_PORT

setup: LocalSettings.php .ext/MobileFrontend .ext/CodeMirror
	docker compose up -d
	@echo "Waiting for database..."
	@until docker compose exec -T mediawiki bash -c "php -r \"new mysqli('db', 'mediawiki', 'mediawiki', 'mediawiki');\"" > /dev/null 2>&1; do printf '.'; sleep 2; done
	@echo " ready."
	docker compose exec mediawiki php maintenance/run.php install \
		--dbtype mysql --dbserver db --dbname mediawiki \
		--dbuser mediawiki --dbpass mediawiki \
		--pass '$(ADMIN_PASSWORD)' \
		"Ubuntu wiki" admin
	docker compose cp LocalSettings.php mediawiki:/var/www/html/LocalSettings.php
	docker compose exec mediawiki php maintenance/run.php update --quick
	$(MAKE) --no-print-directory seed
	@echo ""
	@echo "Setup complete!"
	@echo "  URL:      http://localhost:$(PORT)"
	@echo "  Username: admin"
	@echo "  Password: $(ADMIN_PASSWORD)"

deploy: LocalSettings.php
	docker compose cp LocalSettings.php mediawiki:/var/www/html/LocalSettings.php
	docker compose exec mediawiki php maintenance/run.php update --quick

up: LocalSettings.php .ext/MobileFrontend .ext/CodeMirror
	docker compose up -d
	docker compose cp LocalSettings.php mediawiki:/var/www/html/LocalSettings.php

down:
	docker compose down

clean:
	docker compose down -v

update:
	docker compose exec mediawiki php maintenance/run.php update --quick

# Import the test pages from seed/ into the wiki. Page titles come from the
# file names (e.g. "Template:Code_block.txt" becomes "Template:Code block").
# Idempotent: --overwrite replaces pages that already exist.
seed:
	docker compose exec -T mediawiki mkdir -p /tmp/seed
	docker compose cp seed/. mediawiki:/tmp/seed/
	docker compose exec -T mediawiki bash -c '\
		php maintenance/run.php importTextFiles \
			--user Admin --summary "Seed test content" --overwrite \
			/tmp/seed/*.txt'
	# Pages imported early in the glob (e.g. Main_Page) link to pages created
	# later (e.g. Template examples); the backlink refresh jobs are queued but
	# not run during CLI import, so run them now or those links stay red.
	docker compose exec -T mediawiki php maintenance/run.php runJobs

lint:
	composer test

shell:
	docker compose exec mediawiki bash

LocalSettings.php:
	cp LocalSettings.example.php LocalSettings.php
	@echo "Created LocalSettings.php from LocalSettings.example.php — edit it before running setup."

# Some extensions we want to test with are not bundled with the MediaWiki tarball.
# They are shallow-cloned into .ext/ (gitignored) and mounted into the
# container — see docker-compose.yml. Keep this target at the bottom: the
# FIRST target in a Makefile is the default run by a bare `make`, which must
# stay `setup`.
.ext/MobileFrontend:
	git clone --depth 1 --branch REL1_46 \
		https://github.com/wikimedia/mediawiki-extensions-MobileFrontend.git $@

.ext/CodeMirror:
	git clone --depth 1 --branch REL1_46 \
		https://github.com/wikimedia/mediawiki-extensions-CodeMirror.git $@
