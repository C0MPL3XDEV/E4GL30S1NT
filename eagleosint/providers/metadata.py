"""Metadata extraction provider for images and PDF documents"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from eagleosint.display import BLUE, WHITE, SPACE_PREFIX, LINES_SEPARATOR
from eagleosint.models import MetadataResult, ProviderResult
from eagleosint.plugin import BaseProvider, ProviderCategory

logger = logging.getLogger(__name__)

_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tif", ".heic", ".tiff", ".webp"}
_PDF_EXTENSIONS = {".pdf"}
_SUPPORTED_EXTENSIONS = _IMAGE_EXTENSIONS | _PDF_EXTENSIONS

def _dms_to_decimal(dms: tuple, ref: str) -> float:
    """Convert GPS DMS (degrees, minutes, seconds) to decimal degrees.

    EXIF stores GPS as ((deg_num, deg_den), (min_num, min_den), (sec_num, sec_den)).
    Pillow >= 8.0 already converts IFDRational to float, so each element
    is either a float or a tuple/IFDRational. We handle both cases.
    """
    def _to_float(val: Any) -> float:
        if isinstance(val, (int, float)):
            return float(val)
        if isinstance(val, tuple) and len(val) == 2:
            return val[0] / val[1] if val[1] else 0.0
        return float(val)

    degrees = _to_float(dms[0])
    minutes = _to_float(dms[1])
    seconds = _to_float(dms[2])
    decimal = degrees + minutes / 60.0 + seconds / 3600.0
    if ref in ("S", "W"):
        decimal = -decimal
    return round(decimal, 6)

def _extract_image_metadata(file_path: str) -> dict[str, Any]:
    """Extract EXIF metadata from and image using Pillow.

    How EXIF works internally:
    - Images store metadata in tagged fields (IFD entries)
    - Each tag is a numeric ID (e.g. 271 = Make, 272 = Model)
    - Pillow's ExifTags.TAGS maps these IDs to human-readable names
    - GPS data lives in a sub-IFD with its own tag namespace (GPSTAGS)
    """
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS

    result: dict[str, Any] = {"file_type": "image"}

    with Image.open(file_path) as img:
        result["image_width"] = img.width
        result["image_height"] = img.height

        exif_data = img.getexif()
        if not exif_data:
            return result

        decoded: dict[str, Any] = {}
        for tag_id, value in exif_data.items():
            tag_name = TAGS.get(tag_id, str(tag_id))
            decoded[tag_name] = value

        result["device_make"] = decoded.get("Make")
        result["device_model"] = decoded.get("Model")
        result["software"] = decoded.get("Software")
        result["created"] = decoded.get("DateTimeOriginal") or decoded.get("DateTime")

        gps_info = exif_data.get_ifd(0x8825)
        if gps_info:
            gps_decoded: dict[str, Any] = {}
            for tag_id, value in gps_info.items():
                tag_name = GPSTAGS.get(tag_id, str(tag_id))
                gps_decoded[tag_name] = value

            lat = gps_decoded.get("GPSLatitude")
            lat_ref = gps_decoded.get("GPSLatitudeRef")
            lon = gps_decoded.get("GPSLongitude")
            lon_ref = gps_decoded.get("GPSLongitudeRef")

            if lat and lat_ref and lon and lon_ref:
                result["gps_latitude"] = _dms_to_decimal(lat, lat_ref)
                result["gps_longitude"] = _dms_to_decimal(lon, lon_ref)

        extra = {}

        for key in ("ExposureTime", "FNumber", "ISOSpeedRatings", "FocalLength", "Flash", "ColorSpace"):
            if key in decoded:
                val = decoded[key]
                if hasattr(val, "numerator"):
                    val = float(val)
                extra[key] = val

        if extra:
            result["extra"] = extra

    return result

def _extract_pdf_metadata(file_path: str) -> dict[str, Any]:
    """Extract metadata from a PDF document.

    PDF files store metadata in a /Info dictionary at the document level.
    Fields include /Author, /Creator, /Producer, /Title, /CreationDate, etc.
    pdfplumber exposes this via pdf.metadata as a plain dict.

    :param file_path: Path to the PDF file.
    :return: A dictionary containing extracted metadata.
    """
    import pdfplumber

    result: dict[str, Any] = {"file_type": "pdf"}

    with pdfplumber.open(file_path) as pdf:
        result["page_count"] = len(pdf.pages)

        meta = pdf.metadata or {}
        result["author"] = meta.get("Author")
        result["title"] = meta.get("Title")
        result["software"] = meta.get("Creator")
        result["producer"] = meta.get("Producer")
        result["created"] = meta.get("CreationDate")
        result["modified"] = meta.get("ModDate")

        extra = {}
        skip = {"Author", "Title", "Creator", "Producer", "CreationDate", "ModDate"}
        for k, v in meta.items():
            if k not in skip and v:
                extra[k] = v

        if extra:
            result["extra"] = extra

    return result

class MetadataProvider(BaseProvider):
    name = "metadata"
    version = "1.0.0"
    description = "Extract metadata from images and documents"
    category = ProviderCategory.DOCUMENT

    def execute(self, query: str, **kwargs: Any) -> list[MetadataResult]:
        file_path = query.strip().strip("'\"")
        path = Path(file_path)

        if not path.exists():
            logger.error("File not found: %s", file_path)
            return []

        ext = path.suffix.lower()
        if ext not in _SUPPORTED_EXTENSIONS:
            logger.error("Unsupported file type: %s", ext)
            return []

        file_size = path.stat().st_size

        if ext in _IMAGE_EXTENSIONS:
            meta = _extract_image_metadata(file_path)
        else:
            meta = _extract_pdf_metadata(file_path)

        return [MetadataResult(
            query=file_path,
            file_path=str(path.resolve()),
            file_size=file_size,
            **meta
        )]

# ------------------------------------------------------------------
# Interactive CLI wrapper
# ------------------------------------------------------------------

def metadata_extract() -> MetadataResult | None:
    file_path = input(
        f"{SPACE_PREFIX}{WHITE}{BLUE}>{WHITE} enter file path:{BLUE} "
    ).strip()
    if not file_path:
        return None

    provider = MetadataProvider()
    results: list[MetadataResult] = provider.run(file_path)  # type: ignore[assignment]

    if not results:
        print(f"{SPACE_PREFIX}{WHITE}no metadata found or unsupported file.")
        return None

    result = results[0]
    print(f"\n{WHITE}{LINES_SEPARATOR}")
    print(f"{SPACE_PREFIX}{BLUE}file      :{WHITE} {result.file_path}")
    print(f"{SPACE_PREFIX}{BLUE}type      :{WHITE} {result.file_type}")
    print(f"{SPACE_PREFIX}{BLUE}size      :{WHITE} {result.file_size} bytes")

    if result.device_make:
        print(f"{SPACE_PREFIX}{BLUE}device    :{WHITE} {result.device_make} {result.device_model or ''}")
    if result.author:
        print(f"{SPACE_PREFIX}{BLUE}author    :{WHITE} {result.author}")
    if result.software:
        print(f"{SPACE_PREFIX}{BLUE}software  :{WHITE} {result.software}")
    if result.created:
        print(f"{SPACE_PREFIX}{BLUE}created   :{WHITE} {result.created}")
    if result.modified:
        print(f"{SPACE_PREFIX}{BLUE}modified  :{WHITE} {result.modified}")
    if result.title:
        print(f"{SPACE_PREFIX}{BLUE}title     :{WHITE} {result.title}")
    if result.producer:
        print(f"{SPACE_PREFIX}{BLUE}producer  :{WHITE} {result.producer}")
    if result.image_width:
        print(f"{SPACE_PREFIX}{BLUE}dimensions:{WHITE} {result.image_width}x{result.image_height}")
    if result.gps_latitude is not None:
        print(f"{SPACE_PREFIX}{BLUE}GPS       :{WHITE} {result.gps_latitude}, {result.gps_longitude}")
    if result.page_count:
        print(f"{SPACE_PREFIX}{BLUE}pages     :{WHITE} {result.page_count}")
    if result.extra:
        print(f"{SPACE_PREFIX}{BLUE}extra     :{WHITE}")
        for k, v in result.extra.items():
            print(f"{SPACE_PREFIX}  {k}: {v}")

    print(f"{WHITE}{LINES_SEPARATOR}")
    return result