// PROTOTYPE — throwaway. Answers: "can @canonical/react-ds-global components
// be pre-rendered to static HTML at build time, with placeholder tokens a
// MediaWiki Lua module/template can later substitute via plain string
// replacement, with zero Node process at request time?"
//
// Not production code. See ticket #40 / docs/adr for the recorded decision.

import { renderToStaticMarkup } from "react-dom/server";
import React from "react";
import { Button, Icon, Card } from "@canonical/react-ds-global";

// Placeholder tokens: chosen to be wikitext-safe (no chars MediaWiki's
// parser would treat specially) and easy to string-replace in a Lua module.
const LABEL = "\u0001LABEL\u0001";
const HREF = "\u0001HREF\u0001";

function renderFragment(name, element) {
	const html = renderToStaticMarkup(element);
	console.log(`\n--- ${name} ---`);
	console.log(html);
	return html;
}

// One button per icon Main Page needs, with a label placeholder. The href
// itself isn't part of Button's own output (Button doesn't render an <a>),
// so the wiki-side template wraps the rendered <button>/<span> markup in its
// own <a href="HREF">...</a> — meaning Button's static output can be reused
// verbatim across every link, and only the wrapping anchor changes per use.
const desktopButton = renderFragment(
	"Button icon=desktop",
	React.createElement(Button, { icon: "desktop" }, LABEL),
);

const machinesButton = renderFragment(
	"Button icon=machines",
	React.createElement(Button, { icon: "machines" }, LABEL),
);

const plainIcon = renderFragment(
	"Icon icon=containers",
	React.createElement(Icon, { icon: "containers", rootPath: "/w/extensions/UbuntuWiki/resources/icons" }),
);

const card = renderFragment(
	"Card (bare)",
	React.createElement(Card, {}, React.createElement("p", {}, LABEL)),
);

console.log("\n--- Cost notes ---");
console.log("react + react-dom (server) + react-ds-global installed size:");
