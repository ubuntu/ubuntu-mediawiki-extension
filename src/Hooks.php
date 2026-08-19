<?php

declare(strict_types=1);

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
class Hooks implements BeforePageDisplayHook, SkinAddFooterLinksHook
{

    public function __construct(
        private readonly Config $config,
        private readonly LinkRenderer $linkRenderer,
    ) {}

    /**
     * Conditionally attach feature modules to every page view.
     *
     * ext.ubuntu.styles is the extension's shared base styling and is loaded
     * on every skin (as a style-only module, so it is in place before first
     * paint); the minerva-specific addition still comes via
     * ResourceModuleSkinStyles.
     *
     * @param OutputPage $out
     * @param Skin $skin
     */
    public function onBeforePageDisplay($out, $skin): void
    {
        $out->addModuleStyles(['ext.ubuntu.styles']);
        $out->addModules(['ext.ubuntu.codeBlock']);

        if ($this->config->get('UbuntuCookieConsentEnabled')) {
            $out->addModules(['ext.ubuntu.cookieConsent']);
        }
    }

    /**
     * Add Ubuntu footer links to the 'places' footer section.
     *
     * Targets come from the `UbuntuFooterLinks` config (a name => target map
     * where target is a wiki page title or an external URL); labels come
     * from the `ubuntu-footer-<name>-desc` messages, which can be overridden
     * on-wiki via the MediaWiki: namespace. Set a target to null to drop a
     * default link entirely.
     *
     * The cookie-settings link is always added: it reopens the consent banner
     * via its .js-revoke-cookie-manager class when the cookie consent module
     * is loaded, and is a harmless '#' link otherwise.
     *
     * @param Skin $skin
     * @param string $key Footer section key ('places', 'info', ...)
     * @param array &$footerlinks Link items for that section
     */
    public function onSkinAddFooterLinks(Skin $skin, string $key, array &$footerlinks): void
    {
        if ($key !== 'places') {
            return;
        }

        $links = $this->config->get('UbuntuFooterLinks');
        foreach ($links as $name => $target) {
            $descMsg = $skin->msg("ubuntu-footer-$name-desc");
            if ($target === null || !$descMsg->exists()) {
                continue;
            }
            $link = $this->buildFooterLink($target, $descMsg->text());
            if ($link !== null) {
                $footerlinks["ubuntu-$name"] = $link;
            }
        }

        $footerlinks['cookie-settings'] = Html::rawElement('a', [
            'href' => '#',
            'class' => 'js-revoke-cookie-manager',
        ], $skin->msg('ubuntu-manage-trackers-button-label')->escaped());
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
    private function buildFooterLink(string $target, string $label): ?string
    {
        if (str_starts_with($target, 'https://') || str_starts_with($target, 'http://')) {
            return Html::rawElement('a', [
                'href' => $target,
                'rel' => 'noreferrer noopener',
            ], htmlspecialchars($label));
        }

        $title = Title::newFromText($target);
        if ($title === null) {
            return null;
        }
        return $this->linkRenderer->makeLink($title, $label);
    }
}
