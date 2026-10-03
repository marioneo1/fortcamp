import tempfile
import unittest
import json
from pathlib import Path

from PIL import Image, PngImagePlugin

from tools import portrait_import_core as importer
from tools.portrait_grid import detect_grid_bounds


class PortraitImportTests(unittest.TestCase):
    def test_square_previews_keep_uncropped_rectangular_source(self):
        with tempfile.TemporaryDirectory() as directory:
            image=Image.new('RGB',(80,160),(110,150,90))
            importer._render_cells(image,['001.webp'],Path(directory),1,1,0)
            with Image.open(Path(directory)/'original-001.webp') as source:
                self.assertEqual(source.size,(80,160))
            for kind,expected in [('full',(768,768)),('thumb',(192,192))]:
                with Image.open(Path(directory)/f'{kind}-001.webp') as preview:
                    self.assertEqual(preview.size,expected)
                    self.assertGreater(preview.getpixel((0,0))[1],100)

    def test_detects_uneven_dark_grid_separators(self):
        image = Image.new("RGB", (403, 397), "white")
        pixels = image.load()
        for x in (96, 205, 301):
            for y in range(image.height):
                pixels[x, y] = (0, 0, 0)
        for y in (91, 201, 306):
            for x in range(image.width):
                pixels[x, y] = (0, 0, 0)

        x_bounds, y_bounds, evidence = detect_grid_bounds(image, 4, 4)

        self.assertEqual(x_bounds, [0, 97, 206, 302, 403])
        self.assertEqual(y_bounds, [0, 92, 202, 307, 397])
        self.assertTrue(all(item["accepted"] for axis in evidence.values() for item in axis))

    def test_grid_detection_falls_back_without_separator_evidence(self):
        image = Image.new("RGB", (402, 398), "gray")

        x_bounds, y_bounds, evidence = detect_grid_bounds(image, 4, 4)

        self.assertEqual(x_bounds, [0, 100, 201, 302, 402])
        self.assertEqual(y_bounds, [0, 100, 199, 298, 398])
        self.assertFalse(any(item["accepted"] for axis in evidence.values() for item in axis))

    def test_detects_uneven_five_by_four_pool_grid(self):
        image = Image.new("RGB", (503, 397), "white")
        pixels = image.load()
        vertical = (94, 199, 307, 405)
        horizontal = (91, 201, 306)
        for x in vertical:
            for y in range(image.height):
                pixels[x, y] = (0, 0, 0)
        for y in horizontal:
            for x in range(image.width):
                pixels[x, y] = (0, 0, 0)

        x_bounds, y_bounds, evidence = detect_grid_bounds(image, 5, 4)

        self.assertEqual(x_bounds, [0, 95, 200, 308, 406, 503])
        self.assertEqual(y_bounds, [0, 92, 202, 307, 397])
        self.assertEqual(sum(item["accepted"] for item in evidence["x"]), 4)
        self.assertEqual(sum(item["accepted"] for item in evidence["y"]), 3)

    def test_pixel_dedupe_and_revision_append_preserve_ids(self):
        original_root = importer.POOL_ROOT
        original_manifest = importer.MANIFEST_PATH
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            importer.POOL_ROOT = root / "pools"
            importer.MANIFEST_PATH = importer.POOL_ROOT / "import_manifest.json"
            first = root / "slimefolk_female.png"
            same_pixels = root / "resaved.png"
            changed = root / "changed.png"

            image = Image.new("RGB", (500, 400), (20, 120, 150))
            image.save(first)
            metadata = PngImagePlugin.PngInfo()
            metadata.add_text("note", "different file metadata")
            image.save(same_pixels, pnginfo=metadata, compress_level=9)

            initial = importer.import_sheet(first, "slimefolk_female")
            duplicate = importer.import_sheet(same_pixels, "slimefolk_female")
            image.putpixel((0, 0), (21, 120, 150))
            image.save(changed)
            revision = importer.import_sheet(changed, "slimefolk_female")

            self.assertEqual(initial["written"][0], "slimefolk_female_001.webp")
            self.assertEqual(duplicate["status"], "duplicate")
            self.assertEqual(revision["written"][0], "slimefolk_female_021.webp")
            self.assertEqual(importer.pool_count("slimefolk_female"), 40)
        importer.POOL_ROOT = original_root
        importer.MANIFEST_PATH = original_manifest

    def test_row_major_companion_metadata_follows_stable_split_names(self):
        original_root = importer.POOL_ROOT
        original_manifest = importer.MANIFEST_PATH
        original_metadata = importer.METADATA_PATH
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            importer.POOL_ROOT = root / "pools"
            importer.MANIFEST_PATH = importer.POOL_ROOT / "import_manifest.json"
            importer.METADATA_PATH = importer.POOL_ROOT / "portrait_metadata.json"
            sheet = root / "banshee_female_magic.png"
            Image.new("RGB", (200, 100), "gray").save(sheet)
            sheet.with_suffix(".metadata.json").write_text(json.dumps({"portraits": [
                {"hair_color": "silver", "eye_color": "blue", "summary": "A pale spectral woman with silver hair."},
                {"hair_color": "black", "distinctive_features": "a translucent veil"},
            ]}), encoding="utf-8")

            result = importer.import_sheet(sheet, "banshee_female_magic", columns=2, rows=1)
            registry = importer.read_metadata_registry()["portraits"]

            self.assertEqual(result["metadata_written"], 2)
            self.assertEqual(registry["banshee_female_magic/banshee_female_magic_001.webp"]["hair_color"], "silver")
            self.assertEqual(registry["banshee_female_magic/banshee_female_magic_002.webp"]["distinctive_features"], "a translucent veil")
        importer.POOL_ROOT = original_root
        importer.MANIFEST_PATH = original_manifest
        importer.METADATA_PATH = original_metadata

    def test_refresh_rebuilds_same_twenty_ids_and_creates_backup(self):
        original_root = importer.POOL_ROOT
        original_manifest = importer.MANIFEST_PATH
        original_metadata = importer.METADATA_PATH
        original_backup = importer.BACKUP_ROOT
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            importer.POOL_ROOT = root / "pools"
            importer.MANIFEST_PATH = importer.POOL_ROOT / "import_manifest.json"
            importer.METADATA_PATH = importer.POOL_ROOT / "portrait_metadata.json"
            importer.BACKUP_ROOT = root / "backups"
            sheet = root / "half_orc_female_melee.png"
            image = Image.new("RGB", (500, 400), (60, 90, 70))
            image.save(sheet)
            initial = importer.import_sheet(sheet, "half_orc_female_melee")
            initial_names = initial["written"]
            old_hash = (importer.POOL_ROOT / "half_orc_female_melee" / "full" / initial_names[0]).read_bytes()

            image.paste((140, 70, 50), (0, 0, 100, 100))
            image.save(sheet)
            refreshed = importer.refresh_sheet(sheet, "half_orc_female_melee")

            manifest = importer.read_manifest()
            new_hash = (importer.POOL_ROOT / "half_orc_female_melee" / "full" / initial_names[0]).read_bytes()
            self.assertEqual(refreshed["files"], initial_names)
            self.assertEqual(importer.pool_count("half_orc_female_melee"), 20)
            self.assertEqual(len(manifest["imports"]), 1)
            self.assertNotEqual(old_hash, new_hash)
            self.assertTrue((Path(refreshed["backup"]) / "repair.json").is_file())
        importer.POOL_ROOT = original_root
        importer.MANIFEST_PATH = original_manifest
        importer.METADATA_PATH = original_metadata
        importer.BACKUP_ROOT = original_backup


if __name__ == "__main__":
    unittest.main()
