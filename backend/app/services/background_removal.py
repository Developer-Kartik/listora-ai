
from pathlib import Path
from io import BytesIO

from PIL import Image
from rembg import new_session, remove


# Reuse the model session instead of loading it for every request.
_session = None


def get_session():
    global _session

    if _session is None:
        _session = new_session("u2netp")

    return _session


def remove_background(input_path: Path, output_path: Path) -> dict:
    """
    Remove the background from an uploaded product image
    and save the result as a transparent PNG.
    """

    if not input_path.exists():
        raise FileNotFoundError("Uploaded image not found.")

    input_bytes = input_path.read_bytes()

    if not input_bytes:
        raise ValueError("Input image is empty.")

    output_bytes = remove(
        input_bytes,
        session=get_session()
    )

    # Validate the generated image before saving.
    with Image.open(BytesIO(output_bytes)) as image:
        image.load()

        if image.mode != "RGBA":
            image = image.convert("RGBA")

        width, height = image.size
        output_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path, format="PNG", optimize=True)

    return {
        "filename": output_path.name,
        "width": width,
        "height": height,
        "format": "PNG",
        "background": "transparent",
        "status": "completed"
    }
