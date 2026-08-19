<?php
# See https://www.mediawiki.org/wiki/Manual:Configuration_settings

if (!defined('MEDIAWIKI')) {
    exit;
}

# Site
$wgSitename = "Ubuntu Wiki";
$wgServer = "http://localhost:8080";
$wgScriptPath = "";
$wgResourceBasePath = $wgScriptPath;
$wgLanguageCode = "en";
$wgLocaltimezone = "UTC";

# Database (matches docker-compose.yml defaults)
$wgDBtype = "mysql";
$wgDBserver = "db";
$wgDBname = "mediawiki";
$wgDBuser = "mediawiki";
$wgDBpassword = "mediawiki";

# Keys — replace with unique values for any non-local deployment
$wgSecretKey = "change-me";
$wgUpgradeKey = "change-me";

# Uploads
$wgEnableUploads = false;
$wgUseInstantCommons = true;

# The extension under test. This repository is live-mounted at
# extensions/UbuntuWiki, so edits to src/ and resources/ apply on reload.
wfLoadExtension('UbuntuWiki');

# Skin
# Vector (default) and MinervaNeue ship with the MediaWiki tarball. Minerva
# stays enabled to test the minerva skin styles — append ?useskin=minerva
# to any URL.
#
# Note: the Ubuntu skin is intentionally not used here for now — its current
# release still declares UbuntuCookieConsentEnabled itself, which fatals when
# loaded together with this extension.
wfLoadSkin('Vector');
wfLoadSkin('MinervaNeue');
$wgDefaultSkin = 'vector-2022';

# Logo — uses the Ubuntu logo bundled in this extension.
# Replace with your own image path to use a custom logo.
$wgLogos = [
    '1x'   => "$wgResourceBasePath/extensions/UbuntuWiki/resources/images/Tag-CoF-Orange-Digital.svg",
    'icon' => "$wgResourceBasePath/extensions/UbuntuWiki/resources/images/Tag-CoF-Orange-Digital.svg",
];

unset($wgFooterIcons['poweredby']);

# Cookie consent & Google Tag Manager
# Enable the Canonical cookie policy consent banner. The extension also adds
# a "Manage your tracker settings" footer link that reopens the banner.
$wgUbuntuCookieConsentEnabled = true;

# Google Tag Manager container ID (leave empty/null to disable GTM).
# The GTM snippet is injected via the BeforePageDisplay hook below.
$wgGTMContainerID = '';

# Google Tag Manager injection.
# The cookie-policy vendor IIFE is loaded by the skin's ResourceLoader module
# (skins.ubuntu.cookieConsent). Its addGoogleConsentMode() sets
# gtag('consent','default',...) with all categories denied. The GTM snippet
# must load AFTER the vendor so that consent defaults are set before GTM
# initialises. When the user accepts cookies, the vendor library calls
# gtag('consent','update',...) automatically.
$wgHooks['BeforePageDisplay'][] = function (MediaWiki\Output\OutputPage $out, MediaWiki\Skin\Skin $skin) use (&$wgGTMContainerID) {
    if ($wgGTMContainerID) {
        $id = htmlspecialchars($wgGTMContainerID, ENT_QUOTES);

        // Google Tag Manager — official <head> snippet
        // https://developers.google.com/tag-manager/quickstart
        $out->addHeadItem(
            'gtm-head',
            <<<HTML
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','{$id}');</script>
<!-- End Google Tag Manager -->
HTML
        );

        // Google Tag Manager — official <noscript> body snippet
        $out->addHTML(
            <<<HTML
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={$id}"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->
HTML
        );
    }
};

# Extensions bundled with the MediaWiki tarball, enabled for testing.
wfLoadExtension('WikiEditor');
wfLoadExtension('VisualEditor');
wfLoadExtension('SyntaxHighlight_GeSHi');

$wgDefaultUserOptions['visualeditor-newwikitext'] = 1;
$wgHiddenPrefs[] = 'visualeditor-newwikitext';

# ---------------------------------------------------------------------------
# Local testing only — do NOT copy to production.
#
# ConfirmEdit with QuestyCaptcha, configured so that EVERY edit (by anyone)
# shows a CAPTCHA whose question embeds .ubuntu-code-block markup as raw
# HTML — the same markup the on-wiki templates produce, and the reason the
# ext.ubuntu.codeBlock copy button must work outside of regular wikitext
# rendering (QuestyCaptcha inserts the question into the edit form unparsed,
# and VisualEditor injects its CAPTCHA widget dynamically after a failed
# save, exercising the MutationObserver path in codeBlock.js).
#
# Try it: edit any page and save. The answer is 42. See the seeded
# "CAPTCHA testing" page for details.
# ---------------------------------------------------------------------------
# QuestyCaptcha is a sub-module of ConfirmEdit with its own extension.json,
# hence the "ConfirmEdit/QuestyCaptcha" path form.
wfLoadExtension('ConfirmEdit');
wfLoadExtension('ConfirmEdit/QuestyCaptcha');
$wgCaptchaClass = 'QuestyCaptcha';
$wgCaptchaTriggers['edit'] = true;

# Nobody skips the CAPTCHA in this test setup.
$wgGroupPermissions['*']['skipcaptcha'] = false;
$wgGroupPermissions['user']['skipcaptcha'] = false;
$wgGroupPermissions['autoconfirmed']['skipcaptcha'] = false;
$wgGroupPermissions['bot']['skipcaptcha'] = false;
$wgGroupPermissions['sysop']['skipcaptcha'] = false;

# The CAPTCHA answer field uses tabindex=1, which also exercises the copy
# button's positive-tabindex inheritance (see codeBlock.js).
$wgCaptchaQuestions[] = [
    'question' => 'To prove that you are human, run this command in a terminal and enter its output: ' .
        '<div class="ubuntu-code-block ubuntu-code-block--captcha"><pre>echo $(( 6 * 7 ))</pre></div>',
    'answer' => '42',
];

# Debug (disable in production)
$wgShowExceptionDetails = true;
