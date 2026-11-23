
from pathlib import Path

import cv2
import numpy as np


def analyze_image(image_path: Path) -> dict:
    image = cv2.imread(str(image_path))

    if image is None:
        raise ValueError("Unable to read image.")

    height, width = image.shape[:2]

    if width == 0 or height == 0:
        raise ValueError("Invalid image dimensions.")

    file_size = image_path.stat().st_size

    aspect_ratio = round(width / height, 2)

    if 0.95 <= aspect_ratio <= 1.05:
        orientation = "square"
    elif aspect_ratio > 1.05:
        orientation = "landscape"
    else:
        orientation = "portrait"

    total_pixels = width * height

    if total_pixels >= 8_000_000:
        resolution = "high"
    elif total_pixels >= 2_000_000:
        resolution = "medium"
    else:
        resolution = "low"

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    brightness = round(float(np.mean(gray)), 2)

    sharpness = round(
        float(cv2.Laplacian(gray, cv2.CV_64F).var()), 2
    )

    contrast = round(float(np.std(gray)), 2)

    if brightness < 60:
        brightness_status = "dark"
    elif brightness > 200:
        brightness_status = "bright"
    else:
        brightness_status = "balanced"

    if sharpness < 50:
        sharpness_status = "possibly_blurry"
    else:
        sharpness_status = "reasonably_sharp"

    return {
        "filename": image_path.name,
        "file_size_bytes": file_size,
        "dimensions": {
            "width": width,
            "height": height
        },
        "aspect_ratio": aspect_ratio,
        "orientation": orientation,
        "resolution": resolution,
        "brightness": {
            "score": brightness,
            "status": brightness_status
        },
        "sharpness": {
            "score": sharpness,
            "status": sharpness_status
        },
        "contrast_score": contrast
    }
