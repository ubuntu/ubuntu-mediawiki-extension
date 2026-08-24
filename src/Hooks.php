<?php

declare( strict_types=1 );

namespace MediaWiki\Extension\UbuntuWiki;

use MediaWiki\Config\Config;
use MediaWiki\Hook\BeforePageDisplayHook;
use MediaWiki\Hook\SkinAddFooterLinksHook;
use MediaWiki\Html\Html;
use MediaWiki\Linker\LinkRenderer;
use MediaWiki\Output\OutputPage;
use MediaWiki\Skin\Skin;
use MediaWiki\Title\Title;

/**
 * Main hook handler for the UbuntuWiki extension.
 *
 * Wires config-gated features (cookie consent banner, footer links) into
 * page rendering. Keep hook bodies thin; put feature logic in dedicated
 * classes as they grow.
 */
class Hooks implements BeforePageDisplayHook, SkinAddFooterLinksHook {

	public function __construct(
		private readonly Config $config,
		private readonly LinkRenderer $linkRenderer,
	) {
	}

	/**
	 * Attach feature modules to every page view.
	 *
	 * ext.ubuntu.styles is the extension's shared base styling, loaded on
	 * every skin (style-only, so it is in place before first paint).
	 * zzz.ext.ubuntu.styles.vector and zzz.ext.ubuntu.styles.minerva are the
	 * per-skin branding layers: both are attached unconditionally, and their
	 * `skins` module option (extension.json) tells ResourceLoader which skin
	 * each serves — the skin list lives only there. The `zzz.` prefix sorts
	 * them after every skins.* module in the combined stylesheet, so their
	 * rules win specificity ties by source order.
	 *
	 * @param OutputPage $out
	 * @param Skin $skin
	 */
	public function onBeforePageDisplay( $out, $skin ): void {
		$out->addModuleStyles( [
			'ext.ubuntu.styles',
			'zzz.ext.ubuntu.styles.vector',
			'zzz.ext.ubuntu.styles.minerva',
		] );
		$out->addModules( [ 'ext.ubuntu.codeBlock' ] );

		if ( $this->config->get( 'UbuntuCookieConsentEnabled' ) ) {
			$out->addModules( [ 'ext.ubuntu.cookieConsent' ] );
		}
	}

	/**
	 * Add Ubuntu footer links to the 'places' footer section.
	 *
	 * Targets come from the `UbuntuFooterLinks` config (name => wiki title or
	 * URL); labels from the `ubuntu-footer-<name>-desc` messages. A null
	 * target drops the link — for the core default keys ('privacy', 'about',
	 * 'disclaimers') that means blanking the default item with a truthy
	 * marker element (an empty string would fall back to the default text).
	 *
	 * Core merges hook items over the default list by key, and a replaced key
	 * keeps the default item's position. So 'privacy' never reuses the core
	 * key: the default slot is blanked and the link added as 'ubuntu-privacy',
	 * making the order fully ours.
	 *
	 * The cookie-settings link is always added: it reopens the consent banner
	 * via its .js-revoke-cookie-manager class, and is a harmless '#' link
	 * when the consent module is not loaded.
	 *
	 * Render order follows insertion order: the blanked core defaults keep
	 * their leading positions but are hidden by the .ubuntu-footer-blank
	 * rule, so the visible links come out in config order (Legal, Data
	 * privacy, Code of Conduct) followed by Tracker settings. MobileFrontend
	 * appends its Mobile view toggle after this hook runs.
	 *
	 * @param Skin $skin
	 * @param string $key Footer section key ('places', 'info', ...)
	 * @param array &$footerlinks Link items for that section
	 */
	public function onSkinAddFooterLinks( Skin $skin, string $key, array &$footerlinks ): void {
		if ( $key !== 'places' ) {
			return;
		}

		$links = $this->config->get( 'UbuntuFooterLinks' );

		foreach ( $links as $name => $target ) {
			if ( $name === 'privacy' ) {
				// Blank the default slot (see docblock); the link is re-added
				// below under an extension-owned key in config order.
				$footerlinks['privacy'] = $this->blankFooterLink();
			} elseif ( $target === null && in_array( $name, [ 'about', 'disclaimers' ], true ) ) {
				// Blank a core default link by key; unknown names aren't added.
				$footerlinks[$name] = $this->blankFooterLink();
			}
			if ( $target === null ) {
				continue;
			}
			$descMsg = $skin->msg( "ubuntu-footer-$name-desc" );
			if ( !$descMsg->exists() ) {
				continue;
			}
			$link = $this->buildFooterLink( $target, $descMsg->text() );
			if ( $link !== null ) {
				$footerlinks["ubuntu-$name"] = $link;
			}
		}

		$footerlinks['cookie-settings'] = Html::rawElement( 'a', [
			'href' => '#',
			'class' => 'js-revoke-cookie-manager',
		], $skin->msg( 'ubuntu-manage-trackers-button-label' )->escaped() );
	}

	/**
	 * HTML marker for a blanked-out footer link. The element is truthy but
	 * empty, and the .ubuntu-footer-blank rule in ext.ubuntu.styles hides
	 * the whole list item so no gap is left behind.
	 *
	 * @return string HTML
	 */
	private function blankFooterLink(): string {
		return Html::element( 'span', [ 'class' => 'ubuntu-footer-blank' ] );
	}

	/**
	 * Build a footer link for a configured target.
	 *
	 * If the target is an http(s) URL an external link is rendered, if it
	 * parses as a wiki title an internal link is rendered, otherwise no
	 * link is produced.
	 *
	 * @param string $target Wiki page title or http(s) URL
	 * @param string $label Link text (already escaped/plain)
	 * @return string|null HTML for the link, or null if the target is invalid
	 */
	private function buildFooterLink( string $target, string $label ): ?string {
		if ( str_starts_with( $target, 'https://' ) || str_starts_with( $target, 'http://' ) ) {
			return Html::rawElement( 'a', [
				'href' => $target,
				'rel' => 'noreferrer noopener',
			], htmlspecialchars( $label ) );
		}

		$title = Title::newFromText( $target );
		if ( $title === null ) {
			return null;
		}
		return $this->linkRenderer->makeLink( $title, $label );
	}
}
