#!/usr/bin/env node
// Copies the CSS shipped by @canonical/design-tokens, @canonical/styles,
// @canonical/styles-typography, and normalize.css into
// resources/ext.ubuntu.styles/vendor/pragma/, then rewrites bare
// package-specifier @import url("@canonical/...") statements to relative
// paths so the vendored tree resolves standalone.
//
// See resources/ext.ubuntu.styles/vendor/pragma/README.md for what's
// vendored and why.

import { cpSync, mkdirSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const vendorRoot = join(
	repoRoot,
	"resources/ext.ubuntu.styles/vendor/pragma",
);

function copyCssFiles(srcDir, destDir, exclude = []) {
	mkdirSync(destDir, { recursive: true });
	for (const entry of readdirSync(srcDir, { withFileTypes: true })) {
		if (!entry.isFile() || !entry.name.endsWith(".css")) continue;
		if (exclude.includes(entry.name)) continue;
		cpSync(join(srcDir, entry.name), join(destDir, entry.name));
	}
}

// design-tokens: all dist/*.css (tokens.json is not needed for CSS-only consumption)
copyCssFiles(
	join(repoRoot, "node_modules/@canonical/design-tokens/dist"),
	join(vendorRoot, "design-tokens"),
);

// styles: all src/*.css except fonts.css (requires @canonical/ds-assets, out of scope)
copyCssFiles(
	join(repoRoot, "node_modules/@canonical/styles/src"),
	join(vendorRoot, "styles"),
	["fonts.css"],
);

// styles-typography: all src/*.css (src/scripts is a build-time TS helper, not needed at runtime)
copyCssFiles(
	join(repoRoot, "node_modules/@canonical/styles-typography/src"),
	join(vendorRoot, "styles-typography"),
);

// normalize.css: single file
cpSync(
	join(repoRoot, "node_modules/normalize.css/normalize.css"),
	join(vendorRoot, "normalize.css"),
);

// Rewrite bare package-specifier @import url("@canonical/...") statements
// to relative paths, so the vendored tree resolves standalone.
const rewrites = [
	{
		file: join(vendorRoot, "styles/index.css"),
		replacements: [
			['@import url("normalize.css");', '@import url("../normalize.css");'],
			[
				'@import url("@canonical/styles-typography");',
				'@import url("../styles-typography/index.css");',
			],
			[
				/@import url\("@canonical\/design-tokens\/dist\/([\w.-]+\.css)"\);/g,
				'@import url("../design-tokens/$1");',
			],
		],
	},
	{
		file: join(vendorRoot, "styles-typography/baseline-cap.css"),
		replacements: [
			[
				'@import url("@canonical/design-tokens/dist/modifiers.typography.css");',
				'@import url("../design-tokens/modifiers.typography.css");',
			],
		],
	},
	{
		file: join(vendorRoot, "styles-typography/baseline-metrics.css"),
		replacements: [
			[
				'@import url("@canonical/design-tokens/dist/modifiers.typography.css");',
				'@import url("../design-tokens/modifiers.typography.css");',
			],
		],
	},
	{
		file: join(vendorRoot, "styles-typography/baseline-trim.css"),
		replacements: [
			[
				'@import url("@canonical/design-tokens/dist/modifiers.typography.css");',
				'@import url("../design-tokens/modifiers.typography.css");',
			],
		],
	},
];

for (const { file, replacements } of rewrites) {
	let css = readFileSync(file, "utf8");
	for (const [pattern, replacement] of replacements) {
		css = css.replaceAll(pattern, replacement);
	}
	writeFileSync(file, css);
}

console.log("Vendored Pragma tokens/styles into", vendorRoot);
