from io import BytesIO
from pathlib import Path
from uuid import uuid4
from app.services.image_analysis import analyze_image
from app.services.background_removal import remove_background
from app.services.hero_image import create_hero_image
import re

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from PIL import Image, UnidentifiedImageError

router = APIRouter()

PROJECT_ROOT = Path(__file__).resolve().parents[3]
UPLOAD_DIR = PROJECT_ROOT / "storage" / "uploads"
PROCESSED_DIR = PROJECT_ROOT / "storage" / "processed"

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

FORMAT_EXTENSIONS = {
    "JPEG": {".jpg", ".jpeg"},
    "PNG": {".png"},
    "WEBP": {".webp"},
}


@router.post("/uploads")
async def upload_product_image(file: UploadFile = File(...)):

    original_name = Path(file.filename or "image").name
    extension = Path(original_name).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG, PNG and WebP images are allowed."
        )

    contents = await file.read(MAX_FILE_SIZE + 1)

    if not contents:
        raise HTTPException(status_code=400, detail="Empty file.")

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Image size must not exceed 10 MB."
        )

    try:
        with Image.open(BytesIO(contents)) as image:
            image_format = image.format
            image.verify()

        if extension not in FORMAT_EXTENSIONS.get(image_format, set()):
            raise HTTPException(
                status_code=400,
                detail="File extension does not match the image format."
            )

        with Image.open(BytesIO(contents)) as image:
            width, height = image.size

    except HTTPException:
        raise
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        raise HTTPException(
            status_code=400,
            detail="Invalid or unsupported image file."
        )

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    upload_id = uuid4().hex
    saved_filename = f"{upload_id}{extension}"
    file_path = UPLOAD_DIR / saved_filename

    file_path.write_bytes(contents)

    return {
        "message": "Product image uploaded successfully",
        "upload_id": upload_id,
        "filename": saved_filename,
        "original_filename": original_name,
        "size_bytes": len(contents),
        "width": width,
        "height": height,
        "status": "uploaded"
    }

@router.get("/uploads/{upload_id}")
async def preview_product_image(upload_id: str):

    if not re.fullmatch(r"[0-9a-f]{32}", upload_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid upload ID."
        )

    matching_files = list(UPLOAD_DIR.glob(f"{upload_id}.*"))

    if not matching_files:
        raise HTTPException(
            status_code=404,
            detail="Uploaded image not found."
        )

    file_path = matching_files[0]

    return FileResponse(
        path=file_path,
        filename=file_path.name,
        content_disposition_type="inline"
    )


@router.get("/uploads/{upload_id}/analysis")
async def get_product_image_analysis(upload_id: str):

    if not re.fullmatch(r"[0-9a-f]{32}", upload_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid upload ID."
        )

    matching_files = list(UPLOAD_DIR.glob(f"{upload_id}.*"))

    if not matching_files:
        raise HTTPException(
            status_code=404,
            detail="Uploaded image not found."
        )

    file_path = matching_files[0]

    try:
        analysis = analyze_image(file_path)
    except (ValueError, OSError):
        raise HTTPException(
            status_code=400,
            detail="Unable to analyze this image."
        )

    return {
        "message": "Image analysis completed successfully",
        "upload_id": upload_id,
        "analysis": analysis
    }

@router.post("/uploads/{upload_id}/remove-background")
async def remove_product_background(upload_id: str):

    if not re.fullmatch(r"[0-9a-f]{32}", upload_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid upload ID."
        )

    matching_files = list(UPLOAD_DIR.glob(f"{upload_id}.*"))

    if not matching_files:
        raise HTTPException(
            status_code=404,
            detail="Uploaded image not found."
        )

    input_path = matching_files[0]

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    output_path = PROCESSED_DIR / f"{upload_id}_no_bg.png"

    try:
        result = remove_background(input_path, output_path)

    except (ValueError, OSError) as error:
        raise HTTPException(
            status_code=400,
            detail=f"Background removal failed: {error}"
        )

    return {
        "message": "Background removed successfully",
        "upload_id": upload_id,
        "processed_image": result,
        "preview_url": f"/api/v1/processed/{upload_id}"
    }


@router.get("/processed/{upload_id}")
async def preview_processed_image(upload_id: str):

    if not re.fullmatch(r"[0-9a-f]{32}", upload_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid upload ID."
        )

    output_path = PROCESSED_DIR / f"{upload_id}_no_bg.png"

    if not output_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Processed image not found."
        )

    return FileResponse(
        path=output_path,
        media_type="image/png",
        content_disposition_type="inline"
    )


@router.post("/uploads/{upload_id}/hero-image")
async def generate_hero_image(upload_id: str):

    if not re.fullmatch(r"[0-9a-f]{32}", upload_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid upload ID."
        )

    input_path = PROCESSED_DIR / f"{upload_id}_no_bg.png"

    if not input_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Transparent product image not found. Remove background first."
        )

    output_path = PROCESSED_DIR / f"{upload_id}_hero.jpg"

    try:
        result = create_hero_image(input_path, output_path)

    except (ValueError, OSError) as error:
        raise HTTPException(
            status_code=400,
            detail=f"Hero image generation failed: {error}"
        )

    return {
        "message": "White background hero image generated successfully",
        "upload_id": upload_id,
        "hero_image": result,
        "preview_url": f"/api/v1/hero/{upload_id}"
    }


@router.get("/hero/{upload_id}")
async def preview_hero_image(upload_id: str):

    if not re.fullmatch(r"[0-9a-f]{32}", upload_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid upload ID."
        )

    output_path = PROCESSED_DIR / f"{upload_id}_hero.jpg"

    if not output_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Hero image not found."
        )

    return FileResponse(
        path=output_path,
        media_type="image/jpeg",
        content_disposition_type="inline"
    )
