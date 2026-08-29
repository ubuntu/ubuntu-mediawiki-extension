import * as esbuild from "esbuild";

const result = await esbuild.build({
	entryPoints: ["client-mount.mjs"],
	outfile: "client-mount.bundle.js",
	bundle: true,
	platform: "browser",
	format: "iife",
	minify: true,
	metafile: true,
	loader: { ".css": "empty" }, // real build would extract CSS separately for a <link>, not drop it — see write-up
});

const text = await esbuild.analyzeMetafile(result.metafile);
console.log(text);
