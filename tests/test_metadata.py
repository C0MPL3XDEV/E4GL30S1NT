"""Tests for metadata extraction provider."""
import pytest
from pathlib import Path

from eagleosint.providers.metadata import (
    MetadataProvider,
    _dms_to_decimal,
    _extract_image_metadata,
    _extract_pdf_metadata,
)
from eagleosint.models import MetadataResult


class TestDmsToDecimal:
    def test_north_east(self):
        dms = (41.0, 53.0, 24.0)
        result = _dms_to_decimal(dms, "N")
        assert abs(result - 41.890000) < 0.001

    def test_south_negative(self):
        dms = (33.0, 51.0, 54.0)
        result = _dms_to_decimal(dms, "S")
        assert result < 0

    def test_west_negative(self):
        dms = (118.0, 14.0, 34.0)
        result = _dms_to_decimal(dms, "W")
        assert result < 0

    def test_tuple_rationals(self):
        dms = ((41, 1), (53, 1), (24, 1))
        result = _dms_to_decimal(dms, "N")
        assert abs(result - 41.890000) < 0.001

    def test_zero_denominator(self):
        dms = ((0, 0), (0, 1), (0, 1))
        result = _dms_to_decimal(dms, "N")
        assert result == 0.0


class TestExtractImageMetadata:
    def test_basic_image(self, tmp_path):
        from PIL import Image
        img_path = tmp_path / "test.png"
        img = Image.new("RGB", (100, 50))
        img.save(str(img_path))

        result = _extract_image_metadata(str(img_path))
        assert result["file_type"] == "image"
        assert result["image_width"] == 100
        assert result["image_height"] == 50

    def test_no_exif(self, tmp_path):
        from PIL import Image
        img_path = tmp_path / "plain.png"
        Image.new("RGB", (10, 10)).save(str(img_path))

        result = _extract_image_metadata(str(img_path))
        assert result["file_type"] == "image"
        assert result.get("device_make") is None
        assert result.get("gps_latitude") is None

    def test_with_exif(self, tmp_path):
        from PIL import Image

        try:
            import piexif
        except ImportError:
            pytest.skip("piexif not installed")

        img_path = tmp_path / "exif.jpg"
        img = Image.new("RGB", (200, 150))

        exif_dict = {
            "0th": {
                piexif.ImageIFD.Make: b"TestMake",
                piexif.ImageIFD.Model: b"TestModel",
                piexif.ImageIFD.Software: b"TestSoft",
            },
        }
        exif_bytes = piexif.dump(exif_dict)
        img.save(str(img_path), exif=exif_bytes)

        result = _extract_image_metadata(str(img_path))
        assert result["device_make"] == "TestMake"
        assert result["device_model"] == "TestModel"
        assert result["software"] == "TestSoft"


class TestExtractPdfMetadata:
    def test_basic_pdf(self, tmp_path):
        try:
            from reportlab.pdfgen import canvas as pdf_canvas
        except ImportError:
            pytest.skip("reportlab not installed")

        pdf_path = tmp_path / "test.pdf"
        c = pdf_canvas.Canvas(str(pdf_path))
        c.setAuthor("Test Author")
        c.setTitle("Test Title")
        c.setCreator("Test Creator")
        c.drawString(100, 750, "Hello World")
        c.save()

        result = _extract_pdf_metadata(str(pdf_path))
        assert result["file_type"] == "pdf"
        assert result["author"] == "Test Author"
        assert result["title"] == "Test Title"
        assert result["software"] == "Test Creator"
        assert result["page_count"] == 1

    def test_minimal_pdf(self, tmp_path):
        pdf_path = tmp_path / "minimal.pdf"
        pdf_path.write_bytes(
            b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
            b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
            b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\n"
            b"xref\n0 4\n"
            b"0000000000 65535 f \n"
            b"0000000009 00000 n \n"
            b"0000000058 00000 n \n"
            b"0000000115 00000 n \n"
            b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n190\n%%EOF"
        )
        result = _extract_pdf_metadata(str(pdf_path))
        assert result["file_type"] == "pdf"
        assert result["page_count"] == 1


class TestMetadataProvider:
    def test_file_not_found(self):
        provider = MetadataProvider()
        results = provider.execute("/nonexistent/file.jpg")
        assert results == []

    def test_unsupported_extension(self, tmp_path):
        txt = tmp_path / "test.txt"
        txt.write_text("hello")
        provider = MetadataProvider()
        results = provider.execute(str(txt))
        assert results == []

    def test_image_returns_metadata_result(self, tmp_path):
        from PIL import Image
        img_path = tmp_path / "test.png"
        Image.new("RGB", (80, 60)).save(str(img_path))

        provider = MetadataProvider()
        results = provider.execute(str(img_path))
        assert len(results) == 1
        assert isinstance(results[0], MetadataResult)
        assert results[0].file_type == "image"
        assert results[0].image_width == 80
        assert results[0].file_size > 0

    def test_pdf_returns_metadata_result(self, tmp_path):
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(
            b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
            b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
            b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\n"
            b"xref\n0 4\n"
            b"0000000000 65535 f \n"
            b"0000000009 00000 n \n"
            b"0000000058 00000 n \n"
            b"0000000115 00000 n \n"
            b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n190\n%%EOF"
        )
        provider = MetadataProvider()
        results = provider.execute(str(pdf_path))
        assert len(results) == 1
        assert isinstance(results[0], MetadataResult)
        assert results[0].file_type == "pdf"
        assert results[0].page_count == 1

    def test_quoted_path_stripped(self, tmp_path):
        from PIL import Image
        img_path = tmp_path / "quoted.png"
        Image.new("RGB", (10, 10)).save(str(img_path))

        provider = MetadataProvider()
        results = provider.execute(f'"{img_path}"')
        assert len(results) == 1