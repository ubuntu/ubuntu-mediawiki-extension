<?php
/**
 * PHPUnit bootstrap for the UbuntuWiki extension.
 *
 * Self-contained on purpose: the unit tests cover core-free classes, so this
 * only registers the extension's PSR-4 namespace and — when available —
 * MediaWiki core's AutoLoader (the tests run inside the mediawiki container,
 * where core lives at /var/www/html; see run-unit-tests.sh). Core's own test
 * bootstrap is deliberately NOT used: its extension-discovery step loads full
 * MW settings, which instantiates test mocks that need dev-only classes the
 * production docker image does not ship.
 */

// Extension classes (extension.json's AutoloadNamespaces, replicated here
// because MW's extension registry is not involved in unit tests).
spl_autoload_register( static function ( string $class ): void {
	$prefix = 'MediaWiki\\Extension\\UbuntuWiki\\';
	if ( str_starts_with( $class, $prefix ) ) {
		$path = __DIR__ . '/../../src/' . substr( $class, strlen( $prefix ) ) . '.php';
		if ( file_exists( $path ) ) {
			require_once $path;
		}
	}
} );

$mwInstallPath = getenv( 'MW_INSTALL_PATH' ) ?: '/var/www/html';
if ( file_exists( "$mwInstallPath/includes/AutoLoader.php" ) ) {
	// Core class autoloading (pulls in core's vendor autoload too), for any
	// future test that touches core value classes.
	require_once "$mwInstallPath/includes/AutoLoader.php";
}
