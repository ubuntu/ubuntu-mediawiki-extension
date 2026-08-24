<?php
/**
 * Reduce the staged MediaWiki core composer.json's require-dev to phpunit
 * only. The staged copy (see `make test-unit`) is a throwaway install used
 * solely to run the extension's unit tests, so core's other dev tools
 * (phan, codesniffer, ...) are dropped to keep the install small.
 *
 * Usage: php strip-core-dev-deps.php /path/to/staged/composer.json
 */

$file = $argv[1] ?? '';
$json = json_decode( file_get_contents( $file ) );
if ( $json === null || !isset( $json->{'require-dev'}->{'phpunit/phpunit'} ) ) {
	fwrite( STDERR, "Unexpected composer.json shape at $file\n" );
	exit( 1 );
}
$json->{'require-dev'} = [ 'phpunit/phpunit' => $json->{'require-dev'}->{'phpunit/phpunit'} ];
// autoload-dev.files references dev packages we just dropped (hamcrest
// shims); the extension's unit tests do not need them.
unset( $json->{'autoload-dev'}->files );
file_put_contents( $file, json_encode( $json, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES ) . "\n" );
