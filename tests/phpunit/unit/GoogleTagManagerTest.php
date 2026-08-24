<?php

declare( strict_types=1 );

namespace MediaWiki\Extension\UbuntuWiki\Test;

use MediaWiki\Extension\UbuntuWiki\GoogleTagManager;
use PHPUnit\Framework\TestCase;

/**
 * @covers \MediaWiki\Extension\UbuntuWiki\GoogleTagManager
 */
class GoogleTagManagerTest extends TestCase {

	public function testBlankContainerIdDisablesSnippets(): void {
		foreach ( [ '', '   ', "\t\n" ] as $blank ) {
			$this->assertNull( GoogleTagManager::buildHeadSnippet( $blank ) );
			$this->assertNull( GoogleTagManager::buildNoscriptSnippet( $blank ) );
		}
	}

	public function testHeadSnippetContainsContainerId(): void {
		$snippet = GoogleTagManager::buildHeadSnippet( 'GTM-ABC123' );
		$this->assertNotNull( $snippet );
		$this->assertStringContainsString( "'dataLayer',\"GTM-ABC123\"", $snippet );
		$this->assertStringContainsString( 'googletagmanager.com/gtm.js', $snippet );
	}

	public function testNoscriptSnippetContainsContainerId(): void {
		$snippet = GoogleTagManager::buildNoscriptSnippet( 'GTM-ABC123' );
		$this->assertNotNull( $snippet );
		$this->assertStringContainsString(
			'https://www.googletagmanager.com/ns.html?id=GTM-ABC123',
			$snippet
		);
	}

	public function testContainerIdIsTrimmed(): void {
		$this->assertStringContainsString(
			'"GTM-ABC123"',
			GoogleTagManager::buildHeadSnippet( '  GTM-ABC123  ' )
		);
	}

	public function testContainerIdIsEscaped(): void {
		// A hostile ID must not break out of the JS string literal or the
		// noscript iframe URL.
		$hostile = 'GTM-X\');alert(1);//';
		$this->assertStringNotContainsString(
			$hostile,
			GoogleTagManager::buildHeadSnippet( $hostile )
		);
		$this->assertStringContainsString(
			'&quot;',
			GoogleTagManager::buildNoscriptSnippet( 'GTM-X"><script>' )
		);
	}
}
