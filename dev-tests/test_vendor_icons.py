# Subprocess tests for dev-scripts/vendor_icons.py.
#
# The script is the one new seam (see .scratch/vendored-icons/spec.md,
# "Testing decisions"): every test runs it as a subprocess against a small
# fixture tarball shaped like the upstream `@canonical/ds-assets` npm package
# (`package/icons/*.svg` + optional `package/icons/metadata.json`), into a
# throwaway repository root. No network access is needed. These are
# development-tooling tests, kept apart from dev-scripts/; tests/ is reserved
# for tests against the extension implementation itself.

import json
import subprocess
import tarfile
import tempfile
import unittest
from datetime import date
from io import BytesIO
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "dev-scripts" / "vendor_icons.py"

SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">'
    "<path id=\"{name}\" d=\"M1 1h14v14H1z\"/></svg>\n"
)


def make_svg(name: str) -> bytes:
    return SVG.format(name=name).encode()


def make_tarball(
    version: str,
    icons: list[str],
    metadata: dict[str, dict] | None = None,
) -> bytes:
    """Build a fake ds-assets npm tarball (`package/icons/...`) in memory."""
    buf = BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        def add(name: str, data: bytes) -> None:
            info = tarfile.TarInfo(f"package/{name}")
            info.size = len(data)
            tar.addfile(info, BytesIO(data))

        add("package.json", json.dumps({"name": "@canonical/ds-assets", "version": version}).encode())
        if metadata:
            add("icons/metadata.json", json.dumps({"icons": metadata}).encode())
        for icon in icons:
            add(f"icons/{icon}.svg", make_svg(icon))
    return buf.getvalue()


class VendorIconsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.icons_dir = self.root / "resources" / "icons" / "pragma"
        self.manifest_path = self.icons_dir / "MANIFEST.json"
        self.less_path = self.root / "resources" / "ext.ubuntu.styles" / "vendor" / "pragma-icons.less"
        self.catalog_path = self.root / "seed" / "Icon_catalog.txt"

    def run_script(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["python3", str(SCRIPT), "--repo-root", str(self.root), *args],
            capture_output=True,
            text=True,
            check=False,
        )

    def sync(self, version: str, **kwargs) -> subprocess.CompletedProcess:
        self.write_package_json(version)
        return self.run_script("--tarball", self.write_tarball(version, **kwargs))

    def check(self, version: str, **kwargs) -> subprocess.CompletedProcess:
        self.write_package_json(version)
        return self.run_script("--check", "--tarball", self.write_tarball(version, **kwargs))

    def write_tarball(self, version: str, **kwargs) -> str:
        path = self.root / f"ds-assets-{version}.tgz"
        path.write_bytes(make_tarball(version, **kwargs))
        return str(path)

    def write_package_json(self, version: str) -> None:
        (self.root / "package.json").write_text(
            json.dumps({"dependencies": {"@canonical/ds-assets": version}})
        )

    def tree_state(self) -> dict[str, bytes]:
        return {
            str(p.relative_to(self.root)): p.read_bytes()
            for p in sorted(self.root.rglob("*"))
            if p.is_file() and not p.name.startswith("ds-assets-")
        }


class TestInitialSync(VendorIconsTestCase):
    """First sync into an empty tree copies, manifests, and generates."""

    def test_sync_uses_package_json_version_by_default(self) -> None:
        self.write_package_json("0.1.0")

        result = self.run_script(
            "--tarball", self.write_tarball("0.1.0", icons=["settings"])
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(self.manifest_path.read_text())["version"], "0.1.0")

    def test_initial_sync(self) -> None:
        result = self.sync("0.1.0", icons=["arrow-right", "settings"])

        self.assertEqual(result.returncode, 0, result.stderr)
        # Unmodified SVGs land in the icon source directory.
        self.assertEqual(
            (self.icons_dir / "arrow-right.svg").read_bytes(),
            make_svg("arrow-right"),
        )
        self.assertEqual(
            (self.icons_dir / "settings.svg").read_bytes(),
            make_svg("settings"),
        )
        # Manifest records source, pinned version, upstream URL, licence, date.
        manifest = json.loads(self.manifest_path.read_text())
        self.assertEqual(manifest["source"], "pragma")
        self.assertEqual(manifest["version"], "0.1.0")
        self.assertIn("npmjs.com", manifest["upstream"])
        self.assertEqual(manifest["licence"], "LGPL-3.0")
        self.assertEqual(manifest["synced"], date.today().isoformat())
        # Generated LESS: do-not-edit header, shared base rule, one rule per icon.
        less = self.less_path.read_text()
        self.assertIn("do not edit", less.lower())
        self.assertIn("background-color: currentColor", less)
        self.assertIn("var( --ubuntu-icon-size, 1em )", less)
        self.assertIn(".ubuntu-pragma-icon-settings::before", less)
        self.assertIn('url( ../icons/pragma/settings.svg )', less)
        self.assertIn(".ubuntu-pragma-icon-arrow-right::before", less)
        self.assertIn('url( ../icons/pragma/arrow-right.svg )', less)

        catalog = self.catalog_path.read_text()
        self.assertIn("AUTO-GENERATED", catalog)
        self.assertIn('<span class="ubuntu-pragma-icon-settings" aria-hidden="true"></span>', catalog)
        self.assertIn("| <code>settings</code>", catalog)
        self.assertIn("| <code>ubuntu-pragma-icon-settings</code>", catalog)
        self.assertIn(
            "&lt;span class=&quot;ubuntu-pragma-icon-settings&quot; aria-hidden=&quot;true&quot;&gt;&lt;/span&gt;",
            catalog,
        )

        # The documented public class is self-contained: an editor should not
        # need to add the unsuffixed base class as a second class.
        settings_selector = less.index(".ubuntu-pragma-icon-settings::before")
        shared_rule_end = less.index("}", less.index(".ubuntu-pragma-icon::before"))
        self.assertLess(settings_selector, shared_rule_end)
        # Report names what was added.
        self.assertIn("added:", result.stdout)

    def test_initial_sync_reports_deprecated_icons(self) -> None:
        result = self.sync(
            "0.1.0",
            icons=["settings", "old-thing"],
            metadata={"old-thing": {"deprecated": True, "replacedBy": "new-thing", "since": "0.1.0"}},
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("deprecated:", result.stdout)
        self.assertIn("old-thing", result.stdout)
        # Deprecation metadata is recorded in the manifest.
        manifest = json.loads(self.manifest_path.read_text())
        self.assertEqual(
            manifest["icons"]["old-thing"],
            {"deprecated": True, "replacedBy": "new-thing", "since": "0.1.0"},
        )


class TestResyncIdempotent(VendorIconsTestCase):
    """Re-running sync on an already-synced tree makes no changes."""

    def test_resync_is_idempotent(self) -> None:
        self.sync("0.1.0", icons=["arrow-right", "settings"])
        before = self.tree_state()

        result = self.sync("0.1.0", icons=["arrow-right", "settings"])

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.tree_state(), before)

    def test_resync_keeps_the_original_sync_date(self) -> None:
        # A re-sync on a later day must not rewrite the manifest: the tree
        # stays clean until the upstream set actually changes.
        self.sync("0.1.0", icons=["settings"])
        original = json.loads(self.manifest_path.read_text())["synced"]

        self.sync("0.1.0", icons=["settings"])

        self.assertEqual(json.loads(self.manifest_path.read_text())["synced"], original)


class TestVersionBump(VendorIconsTestCase):
    """A version bump reports added, removed, renamed, and deprecated icons."""

    def setUp(self) -> None:
        super().setUp()
        self.old_meta = {"old-name": {"deprecated": True, "replacedBy": "new-name", "since": "0.1.0"}}
        self.result = None

    def sync_from_to(self) -> subprocess.CompletedProcess:
        self.sync("0.1.0", icons=["settings", "keep-me", "old-name"], metadata=self.old_meta)
        return self.sync(
            "0.2.0",
            icons=["settings", "keep-me", "new-name", "extra"],
            metadata={"extra": {"deprecated": True, "since": "0.2.0"}},
        )

    def test_bump_updates_tree_and_manifest(self) -> None:
        result = self.sync_from_to()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.icons_dir / "old-name.svg").exists())
        self.assertEqual((self.icons_dir / "new-name.svg").read_bytes(), make_svg("new-name"))
        self.assertEqual((self.icons_dir / "keep-me.svg").read_bytes(), make_svg("keep-me"))
        manifest = json.loads(self.manifest_path.read_text())
        self.assertEqual(manifest["version"], "0.2.0")
        self.assertNotIn("old-name", manifest["icons"])
        self.assertIn("extra", manifest["icons"])
        catalog = self.catalog_path.read_text()
        self.assertNotIn("ubuntu-pragma-icon-old-name", catalog)
        self.assertIn("ubuntu-pragma-icon-new-name", catalog)
        self.assertIn("ubuntu-pragma-icon-extra", catalog)

    def test_bump_reports_every_change(self) -> None:
        result = self.sync_from_to()

        self.assertIn("renamed: old-name -> new-name", result.stdout)
        self.assertIn("added:", result.stdout)
        self.assertIn("extra", result.stdout)
        self.assertIn("deprecated:", result.stdout)
        self.assertIn("extra", result.stdout)
        # A rename is not double-reported as a removal.
        self.assertNotIn("removed:", result.stdout)


class TestUsageScan(VendorIconsTestCase):
    """Sync fails when authored content references removed icons."""

    def write_usage(self) -> None:
        less_dir = self.root / "resources" / "ext.ubuntu.styles" / "components"
        less_dir.mkdir(parents=True)
        (less_dir / "usage.less").write_text(
            ".ubuntu-pragma-icon-old-name {}\n"
        )
        seed_dir = self.root / "seed"
        seed_dir.mkdir()
        (seed_dir / "Usage.txt").write_text(
            '<span class="ubuntu-pragma-icon-removed-name"></span>\n'
        )

    def test_sync_fails_and_reports_every_missing_icon_usage(self) -> None:
        self.write_usage()
        self.sync(
            "0.1.0",
            icons=["old-name", "removed-name"],
            metadata={
                "old-name": {
                    "deprecated": True,
                    "replacedBy": "replacement",
                    "since": "0.1.0",
                }
            },
        )

        result = self.sync("0.2.0", icons=["replacement"])

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ubuntu-pragma-icon-old-name", result.stdout)
        self.assertIn("ubuntu-pragma-icon-removed-name", result.stdout)

    def test_sync_allows_deprecated_icon_usage(self) -> None:
        self.write_usage()
        self.sync("0.1.0", icons=["old-name", "removed-name"])

        result = self.sync(
            "0.2.0",
            icons=["old-name", "removed-name"],
            metadata={
                "old-name": {
                    "deprecated": True,
                    "replacedBy": "replacement",
                    "since": "0.2.0",
                }
            },
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("deprecated: old-name", result.stdout)


class TestCheck(VendorIconsTestCase):
    """--check exits zero in sync and non-zero out of sync."""

    def test_check_passes_when_in_sync(self) -> None:
        self.sync("0.1.0", icons=["arrow-right", "settings"])

        result = self.check("0.1.0", icons=["arrow-right", "settings"])

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_check_fails_when_a_vendored_svg_was_hand_edited(self) -> None:
        self.sync("0.1.0", icons=["arrow-right", "settings"])
        (self.icons_dir / "settings.svg").write_bytes(b"<svg>hand-edited</svg>")

        result = self.check("0.1.0", icons=["arrow-right", "settings"])

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("settings.svg", result.stdout + result.stderr)

    def test_check_fails_when_the_pinned_version_differs(self) -> None:
        self.sync("0.1.0", icons=["settings"])

        result = self.check("0.2.0", icons=["settings"])

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("0.2.0", result.stdout + result.stderr)

    def test_check_fails_when_the_generated_less_was_hand_edited(self) -> None:
        self.sync("0.1.0", icons=["settings"])
        self.less_path.write_text("/* hand edit */\n")

        result = self.check("0.1.0", icons=["settings"])

        self.assertNotEqual(result.returncode, 0)

    def test_check_fails_when_the_generated_catalog_was_hand_edited(self) -> None:
        self.sync("0.1.0", icons=["settings"])
        self.catalog_path.write_text("<!-- hand edit -->\n")

        result = self.check("0.1.0", icons=["settings"])

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Icon_catalog.txt", result.stdout)

    def test_check_fails_when_the_generated_catalog_is_missing(self) -> None:
        self.sync("0.1.0", icons=["settings"])
        self.catalog_path.unlink()

        result = self.check("0.1.0", icons=["settings"])

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Icon_catalog.txt", result.stdout)


if __name__ == "__main__":
    unittest.main()
