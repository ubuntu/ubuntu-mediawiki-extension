// PROTOTYPE — throwaway build step. Bundles render.mjs with esbuild so
// @canonical/react-ds-global's side-effect .css imports don't break plain
// Node ESM (they have no `exports` subpath map, and every component file
// imports its own CSS — this is unavoidable without a bundler).
import * as esbuild from "esbuild";

await esbuild.build({
	entryPoints: ["render.mjs"],
	outfile: "render.bundle.mjs",
	bundle: true,
	platform: "node",
	format: "esm",
	external: ["react", "react-dom", "react-dom/server"],
	loader: { ".css": "empty" }, // we only need the rendered HTML, not the CSS text, for this spike
	logLevel: "info",
});
