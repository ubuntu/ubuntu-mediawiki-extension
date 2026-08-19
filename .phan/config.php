<?php

// Static analysis config for Phan.
// Run against a MediaWiki core checkout by setting MW_INSTALL_PATH:
//   MW_INSTALL_PATH=/path/to/mediawiki composer phan
$cfg = require __DIR__ . '/../vendor/mediawiki/mediawiki-phan-config/src/config.php';

return $cfg;
