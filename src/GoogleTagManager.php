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
	 * The container ID is embedded as a JSON string literal with all
	 * HTML-significant characters hex-escaped (and invalid UTF-8
	 * substituted), so any value is safe inside the inline <script> and
	 * cannot break out of it via a `</script>` sequence.
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
		$jsId = json_encode(
			$id,
			JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT |
				JSON_INVALID_UTF8_SUBSTITUTE
		);
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
	 * Google Consent Mode v2 defaults, for embedding ahead of the GTM
	 * <head> snippet when the cookie consent banner is enabled.
	 *
	 * The ResourceLoader consent module (ext.ubuntu.cookieConsent) sets the
	 * same defaults via its vendor library, but module execution is not
	 * guaranteed to happen before the async gtm.js request starts. Emitting
	 * the defaults inline in <head> before the GTM snippet guarantees
	 * consent is "denied" before any tag can fire. The values mirror the
	 * Canonical cookie-policy vendor defaults; the vendor skips re-setting
	 * them when window.gtag already exists, and still pushes consent
	 * "update" commands when the user makes a choice.
	 *
	 * @return string HTML for OutputPage::addHeadItem()
	 */
	public static function buildConsentDefaultsSnippet(): string {
		return <<<'HTML'
<!-- Google Consent Mode defaults -->
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)};
gtag('consent','default',{ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied',
analytics_storage:'denied',functionality_storage:'denied',personalization_storage:'denied',
security_storage:'denied'});</script>
<!-- End Google Consent Mode defaults -->
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
