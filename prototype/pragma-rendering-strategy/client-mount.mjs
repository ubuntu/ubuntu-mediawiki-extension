// PROTOTYPE — throwaway. Answers: "can @canonical/react-ds-global be bundled
// for the browser, mounted into a container div a PHP hook emits, with a
// real (non-default) icon rootPath passed at runtime?"
import React from "react";
import { createRoot } from "react-dom/client";
import { Button, Icon } from "@canonical/react-ds-global";

// What a MediaWiki hook would emit: a container div with data-* attributes
// carrying the (small, fixed) set of props this specific mount needs.
// e.g. <div class="ubuntu-pragma-mount" data-component="button" data-icon="desktop" data-label="Desktop"></div>
function mountAll(rootPath) {
	const mounts = document.querySelectorAll(".ubuntu-pragma-mount");
	for (const el of mounts) {
		const root = createRoot(el);
		const { component, icon, label } = el.dataset;
		if (component === "button") {
			// Deliberately NOT used for navigation links (see ticket #40 findings) —
			// this mount point is only for genuine actions.
			root.render(React.createElement(Button, { icon }, label));
		} else if (component === "icon") {
			root.render(React.createElement(Icon, { icon, rootPath }));
		}
	}
}

mountAll(window.ubuntuPragmaIconRootPath || "/w/extensions/UbuntuWiki/resources/icons");
