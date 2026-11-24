from pathlib import Path

from PIL import Image


CANVAS_SIZE = (3000, 3000)
PRODUCT_AREA_RATIO = 0.88


def create_hero_image(input_path: Path, output_path: Path) -> dict:
    """
    Create a square white-background hero image
    while preserving the original product proportions.
    """

    if not input_path.is_file():
        raise FileNotFoundError("Transparent product image not found.")

    with Image.open(input_path) as source:
        source.load()
        product = source.convert("RGBA")

    if product.width == 0 or product.height == 0:
        raise ValueError("Invalid product image dimensions.")

    max_width = int(CANVAS_SIZE[0] * PRODUCT_AREA_RATIO)
    max_height = int(CANVAS_SIZE[1] * PRODUCT_AREA_RATIO)

    product.thumbnail(
        (max_width, max_height),
        Image.Resampling.LANCZOS
    )

    canvas = Image.new("RGBA", CANVAS_SIZE, (255, 255, 255, 255))

    x = (CANVAS_SIZE[0] - product.width) // 2
    y = (CANVAS_SIZE[1] - product.height) // 2

    canvas.alpha_composite(product, (x, y))

    output_path.parent.mkdir(parents=True, exist_ok=True)

    canvas.convert("RGB").save(
        output_path,
        format="JPEG",
        quality=95,
        optimize=True,
        subsampling=0
    )

    return {
        "filename": output_path.name,
        "width": CANVAS_SIZE[0],
        "height": CANVAS_SIZE[1],
        "format": "JPEG",
        "background": "white",
        "quality": 95,
        "status": "completed"
    }
