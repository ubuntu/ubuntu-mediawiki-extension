#!/usr/bin/env python3
"""Vendor Pragma icons from the pinned `@canonical/ds-assets` npm tarball.

Syncs unmodified upstream SVGs into `resources/icons/<source>/`, regenerates
the LESS exposing them as CSS-mask classes (`.ubuntu-<source>-icon-<name>`),
rewrites `MANIFEST.json`, and prints a diff report of added / removed /
renamed / deprecated icons. `--check` exits non-zero when the committed tree
is out of sync with the pinned version.

See docs/adr/0001-vendored-icon-delivery-via-generated-mask-classes.md and
docs/research/pragma-icons-distribution.md for the design decisions. Python 3
stdlib only, per the repo's tooling conventions.
"""

import argparse
import hashlib
import html
import json
import re
import shutil
import sys
import tarfile
import tempfile
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any

SOURCE = "pragma"
PACKAGE_NAME = "@canonical/ds-assets"
NPM_TARBALL_TEMPLATE = (
    "https://registry.npmjs.org/@canonical/ds-assets/-/ds-assets-{version}.tgz"
)
UPSTREAM_URL = "https://www.npmjs.com/package/@canonical/ds-assets"
LICENCE = "LGPL-3.0"

# Repo-relative paths, resolved against --repo-root (overridable for tests).
REPO_ROOT = Path(__file__).resolve().parent.parent
ICONS_DIR_TEMPLATE = "resources/icons/{source}"
MANIFEST_NAME = "MANIFEST.json"
LESS_TEMPLATE = "resources/ext.ubuntu.styles/vendor/{source}-icons.less"
CATALOG_TEMPLATE = "seed/Icon_catalog.txt"
ICON_USAGE_PATTERN = re.compile(
    rf"\bubuntu-{SOURCE}-icon-([A-Za-z0-9]+(?:-[A-Za-z0-9]+)*)\b"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tarball", help="Path to a local tarball (skip download)")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify the tree is in sync with the pinned version; exit non-zero otherwise",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="Repository root (defaults to the script's parent directory)",
    )
    args = parser.parse_args()

    repo = args.repo_root
    version = load_package_version(repo / "package.json")
    source_dir = repo / ICONS_DIR_TEMPLATE.format(source=SOURCE)
    less_path = repo / LESS_TEMPLATE.format(source=SOURCE)
    catalog_path = repo / CATALOG_TEMPLATE
    manifest_path = source_dir / MANIFEST_NAME

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        tarball = (
            Path(args.tarball) if args.tarball else download(version, tmp_path)
        )
        with tarfile.open(tarball) as tar:
            tar.extractall(tmp_path, filter="data")
        package_icons = tmp_path / "package" / "icons"

        upstream = load_upstream(package_icons, version)
        validate_icon_usages(repo, less_path, catalog_path, set(upstream))
        old = load_manifest(manifest_path)

        if args.check:
            return check(
                repo,
                source_dir,
                less_path,
                catalog_path,
                manifest_path,
                upstream,
                version,
                old,
            )

        report = sync(
            repo,
            source_dir,
            less_path,
            catalog_path,
            manifest_path,
            upstream,
            version,
            old,
            package_icons,
        )
        print(format_report(report))
        return 0


def download(version: str, dest: Path) -> Path:
    url = NPM_TARBALL_TEMPLATE.format(version=version)
    path = dest / f"ds-assets-{version}.tgz"
    print(f"Downloading {url}")
    with urllib.request.urlopen(url, timeout=60) as response, path.open("wb") as fh:
        shutil.copyfileobj(response, fh)
    return path


def load_package_version(package_json_path: Path) -> str:
    try:
        package = json.loads(package_json_path.read_text())
        version = package["dependencies"][PACKAGE_NAME]
    except (FileNotFoundError, KeyError, TypeError, json.JSONDecodeError) as error:
        raise SystemExit(
            f"ERROR: {package_json_path} does not declare {PACKAGE_NAME}"
        ) from error
    if not isinstance(version, str) or not version:
        raise SystemExit(
            f"ERROR: {package_json_path} has an invalid version for {PACKAGE_NAME}"
        )
    return version


def load_upstream(package_icons: Path, version: str) -> dict[str, Any]:
    """Return the upstream icon set: {name: {sha256, deprecated, replacedBy, since}}."""
    icons: dict[str, Any] = {}
    for svg in sorted(package_icons.glob("*.svg")):
        name = svg.stem
        meta: dict[str, Any] = {"sha256": hashlib.sha256(svg.read_bytes()).hexdigest()}
        icons[name] = meta

    metadata_path = package_icons / "metadata.json"
    if metadata_path.exists():
        data = json.loads(metadata_path.read_text())
        for name, info in data.get("icons", {}).items():
            if name not in icons:
                continue
            if info.get("deprecated"):
                icons[name]["deprecated"] = True
                if info.get("replacedBy"):
                    icons[name]["replacedBy"] = info["replacedBy"]
                if info.get("since"):
                    icons[name]["since"] = info["since"]
    if not icons:
        raise SystemExit(
            f"ERROR: no SVG icons found in {package_icons} (version {version})"
        )
    return icons


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    if not manifest_path.exists():
        return {"version": None, "icons": {}}
    return json.loads(manifest_path.read_text())


def validate_icon_usages(
    repo: Path,
    generated_less_path: Path,
    generated_catalog_path: Path,
    available_names: set[str],
) -> None:
    missing: dict[str, set[str]] = {}
    resources_dir = repo / "resources"
    seed_dir = repo / "seed"
    paths = sorted(resources_dir.rglob("*.less")) + sorted(seed_dir.rglob("*.txt"))
    for path in paths:
        if path in {generated_less_path, generated_catalog_path}:
            continue
        relative_path = str(path.relative_to(repo))
        for name in ICON_USAGE_PATTERN.findall(path.read_text()):
            if name not in available_names:
                missing.setdefault(name, set()).add(relative_path)

    if not missing:
        return

    print("ERROR: icon usages reference icons absent from the synced set:")
    for name in sorted(missing):
        locations = ", ".join(sorted(missing[name]))
        print(f"  - ubuntu-{SOURCE}-icon-{name} ({locations})")
    raise SystemExit(1)


def diff_report(old_icons: dict[str, Any], new_icons: dict[str, Any]) -> dict[str, Any]:
    """Classify upstream changes between the old and new icon sets."""
    added = sorted(set(new_icons) - set(old_icons))
    removed = sorted(set(old_icons) - set(new_icons))
    # Renames are detected two ways: an explicit upstream deprecation pointing
    # at a newly added icon (`replacedBy`), or identical SVG content appearing
    # under a new name.
    renamed: list[tuple[str, str]] = []
    added_set = set(added)
    for name in removed:
        replaced_by = old_icons[name].get("replacedBy")
        if replaced_by in added_set:
            renamed.append((name, replaced_by))
            added_set.discard(replaced_by)
            continue
        digest = old_icons[name].get("sha256")
        match = next(
            (new for new in added_set if new_icons[new].get("sha256") == digest), None
        )
        if match:
            renamed.append((name, match))
            added_set.discard(match)
    renamed_old = {old for old, _ in renamed}
    return {
        "added": sorted(added_set),
        "removed": [n for n in removed if n not in renamed_old],
        "renamed": sorted(renamed),
        "deprecated": sorted(
            n
            for n, info in new_icons.items()
            if info.get("deprecated") and not old_icons.get(n, {}).get("deprecated")
        ),
    }


def sync(
    repo: Path,
    source_dir: Path,
    less_path: Path,
    catalog_path: Path,
    manifest_path: Path,
    upstream: dict[str, Any],
    version: str,
    old: dict[str, Any],
    package_icons: Path,
) -> dict[str, Any]:
    report = diff_report(old.get("icons", {}), upstream)

    source_dir.mkdir(parents=True, exist_ok=True)
    for svg in sorted(package_icons.glob("*.svg")):
        shutil.copyfile(svg, source_dir / svg.name)
    for stale in source_dir.glob("*.svg"):
        if stale.stem not in upstream:
            stale.unlink()

    manifest = {
        "source": SOURCE,
        "version": version,
        "upstream": UPSTREAM_URL,
        "licence": LICENCE,
        "synced": date.today().isoformat(),
        "icons": {
            name: {k: v for k, v in info.items() if k != "sha256"}
            for name, info in sorted(upstream.items())
        },
    }
    manifest_text = json.dumps(manifest, indent=2) + "\n"
    # Idempotency: don't touch the file (or bump the sync date) when the
    # previous manifest already describes this exact set, so a no-op re-sync
    # leaves a clean git tree even across days.
    if manifest_path.exists():
        previous = json.loads(manifest_path.read_text())
        previous.pop("synced", None)
        if previous == {k: v for k, v in manifest.items() if k != "synced"}:
            manifest_text = manifest_path.read_text()
    manifest_path.write_text(manifest_text)

    less_path.parent.mkdir(parents=True, exist_ok=True)
    less_path.write_text(generate_less(SOURCE, sorted(upstream)))
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    catalog_path.write_text(generate_catalog(SOURCE, sorted(upstream)))
    return report


def check(
    repo: Path,
    source_dir: Path,
    less_path: Path,
    catalog_path: Path,
    manifest_path: Path,
    upstream: dict[str, Any],
    version: str,
    old: dict[str, Any],
) -> int:
    problems: list[str] = []

    if not manifest_path.exists():
        problems.append("MANIFEST.json is missing")
    else:
        manifest = json.loads(manifest_path.read_text())
        if manifest.get("version") != version:
            problems.append(
                f"pinned version is {manifest.get('version')}, upstream pinned version is {version}"
            )
        expected_meta = {
            name: {k: v for k, v in info.items() if k != "sha256"}
            for name, info in sorted(upstream.items())
        }
        if manifest.get("icons") != expected_meta:
            problems.append("MANIFEST.json icon entries do not match the upstream set")

    for name, info in sorted(upstream.items()):
        svg = source_dir / f"{name}.svg"
        if not svg.exists():
            problems.append(f"{name}.svg is missing from {source_dir}")
        elif hashlib.sha256(svg.read_bytes()).hexdigest() != info["sha256"]:
            problems.append(f"{name}.svg differs from upstream (hand-edited?)")
    for svg in source_dir.glob("*.svg"):
        if svg.stem not in upstream:
            problems.append(f"{svg.name} is not in upstream version {version}")

    expected_less = generate_less(SOURCE, sorted(upstream))
    if less_path.exists() and less_path.read_text() != expected_less:
        problems.append(
            f"{less_path} does not match the generated output (hand-edited?)"
        )

    expected_catalog = generate_catalog(SOURCE, sorted(upstream))
    if not catalog_path.exists():
        problems.append(f"{catalog_path} is missing")
    elif catalog_path.read_text() != expected_catalog:
        problems.append(
            f"{catalog_path} does not match the generated output (hand-edited?)"
        )

    if problems:
        print("ERROR: the vendored icon tree is out of sync:")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print(f"Vendored icons are in sync with {SOURCE} {version}.")
    return 0


def generate_less(source: str, names: list[str]) -> str:
    prefix = f"ubuntu-{source}-icon"
    base_selectors = [f".{prefix}::before"] + [
        f".{prefix}-{name}::before" for name in names
    ]
    lines = [
        "/**",
        f" * Vendored {source} icons as CSS-mask classes.",
        " *",
        " * AUTO-GENERATED — do not edit this file manually.",
        " * Regenerate with `make vendor-icons` (dev-scripts/vendor_icons.py).",
        " *",
        f" * Upstream: {UPSTREAM_URL}",
        " *",
        " * Usage: add the class to any element, e.g.",
        f' *   <span class="{prefix}-settings"></span>',
        " * The ::before pseudo-element below renders the icon as a CSS mask so it",
        " * inherits the surrounding text colour and scales with the font size.",
        " * Override the size per element with --ubuntu-icon-size.",
        " *",
        " * The url() paths are relative to the ext.ubuntu.styles entry point",
        " * (common.less): MediaWiki compiles LESS @imports inline and rebases all",
        " * url()s in a single pass from that entry point's directory (see ADR 0001",
        " * and components/ubuntu/Fonts.less for the same mechanism).",
        " */",
        "",
        ",\n".join(base_selectors) + " {",
        "\tcontent: '';",
        "\tdisplay: inline-block;",
        "\tbackground-color: currentColor;",
        "\twidth: var( --ubuntu-icon-size, 1em );",
        "\theight: var( --ubuntu-icon-size, 1em );",
        "\t-webkit-mask-repeat: no-repeat;",
        "\tmask-repeat: no-repeat;",
        "\t-webkit-mask-position: center;",
        "\tmask-position: center;",
        "\t-webkit-mask-size: contain;",
        "\tmask-size: contain;",
        "}",
        "",
    ]
    for name in names:
        lines.append(f".{prefix}-{name}::before {{")
        lines.append(f"\t-webkit-mask-image: url( ../icons/{source}/{name}.svg );")
        lines.append(f"\tmask-image: url( ../icons/{source}/{name}.svg );")
        lines.append("}")
        lines.append("")
    return "\n".join(lines)


def generate_catalog(source: str, names: list[str]) -> str:
    """Generate the wiki-text page editors use to browse and copy icons."""
    lines = [
        "<!-- AUTO-GENERATED: do not edit this file manually. -->",
        "<!-- Regenerate with `make vendor-icons`. -->",
        "__NOTOC__",
        "[[Category:Content presentation]]",
        "",
        f"= {source.capitalize()} icon catalog =",
        "",
        "Browse the available icons and copy the markup shown in the last column.",
        "",
        '{| class="wikitable sortable"',
        "! Preview",
        "! Name",
        "! Class",
        "! Copyable markup",
    ]
    for name in names:
        icon_class = f"ubuntu-{source}-icon-{name}"
        markup = f'<span class="{icon_class}" aria-hidden="true"></span>'
        lines.extend(
            [
                "|-",
                f"| {markup}",
                f"| <code>{html.escape(name)}</code>",
                f"| <code>{html.escape(icon_class)}</code>",
                f"| <code>{html.escape(markup)}</code>",
            ]
        )
    lines.extend(["|}", ""])
    return "\n".join(lines)


def format_report(report: dict[str, Any]) -> str:
    lines = []
    if report["renamed"]:
        lines.append(
            "renamed: " + ", ".join(f"{old} -> {new}" for old, new in report["renamed"])
        )
    if report["added"]:
        lines.append("added: " + ", ".join(report["added"]))
    if report["removed"]:
        lines.append("removed: " + ", ".join(report["removed"]))
    if report["deprecated"]:
        lines.append("deprecated: " + ", ".join(report["deprecated"]))
    if not lines:
        lines.append("No icon changes.")
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
