<?php

declare( strict_types=1 );

namespace MediaWiki\Extension\UbuntuWiki;

/**
 * Builds the Google Tag Manager snippets.
 *
 * Core-free on purpose: no MediaWiki type dependencies, so the snippet
 * logic is unit-testable without bootstrapping MediaWiki. Hooks is the thin
 * adapter that feeds the configured container ID in and hands the snippets
 * to OutputPage.
 *
 * The feature is dormant unless a container ID is configured: a blank ID
 * (empty or whitespace-only) yields no snippets at all.
 */
final class GoogleTagManager {

	/**
	 * Official GTM <head> snippet.
	 *
	 * https://developers.google.com/tag-manager/quickstart
	 *
	 * The container ID is embedded as a JSON string literal so any value is
	 * safe inside the inline <script>.
	 *
	 * @param string $containerId Configured container ID (e.g. GTM-XXXXXX)
	 * @return string|null HTML for OutputPage::addHeadItem(), or null when
	 *   the container ID is blank
	 */
	public static function buildHeadSnippet( string $containerId ): ?string {
		$id = self::normalizeContainerId( $containerId );
		if ( $id === null ) {
			return null;
		}
		$jsId = json_encode( $id );
		return <<<HTML
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer',$jsId);</script>
<!-- End Google Tag Manager -->
HTML;
	}

	/**
	 * Official GTM <noscript> body snippet, for browsers without JavaScript.
	 *
	 * @param string $containerId Configured container ID (e.g. GTM-XXXXXX)
	 * @return string|null HTML for OutputPage::addHTML(), or null when the
	 *   container ID is blank
	 */
	public static function buildNoscriptSnippet( string $containerId ): ?string {
		$id = self::normalizeContainerId( $containerId );
		if ( $id === null ) {
			return null;
		}
		$htmlId = htmlspecialchars( $id, ENT_QUOTES );
		return <<<HTML
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=$htmlId"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->
HTML;
	}

	/**
	 * Trim the configured container ID; a blank value disables the feature.
	 *
	 * @param string $containerId Raw configured value
	 * @return string|null Trimmed ID, or null when blank
	 */
	private static function normalizeContainerId( string $containerId ): ?string {
		$id = trim( $containerId );
		return $id === '' ? null : $id;
	}
}
