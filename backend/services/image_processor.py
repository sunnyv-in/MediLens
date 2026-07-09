import cv2
import os
import numpy as np


def crop_medicine_region(img):
    """
    Attempts to remove large empty/white backgrounds around a medicine package.

    Important:
    If a reliable crop cannot be found, the original image is returned.
    This prevents aggressive cropping from destroying useful information.
    """

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detect pixels that are sufficiently different from a white background
    mask = cv2.threshold(
        gray,
        245,
        255,
        cv2.THRESH_BINARY_INV
    )[1]

    # Remove tiny isolated noise
    kernel = np.ones((5, 5), np.uint8)

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        kernel,
        iterations=2
    )

    # Find all external regions
    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        return img

    # Ignore extremely small contours
    image_area = img.shape[0] * img.shape[1]

    valid_contours = []

    for contour in contours:
        contour_area = cv2.contourArea(contour)

        if contour_area > image_area * 0.001:
            valid_contours.append(contour)

    if not valid_contours:
        return img

    # Combine all meaningful contours
    all_points = np.vstack(valid_contours)

    x, y, w, h = cv2.boundingRect(all_points)

    # Prevent suspiciously tiny crops
    crop_area = w * h

    if crop_area < image_area * 0.03:
        return img

    # Add padding so text near package edges is not lost
    padding_x = max(10, int(w * 0.05))
    padding_y = max(10, int(h * 0.05))

    x1 = max(0, x - padding_x)
    y1 = max(0, y - padding_y)

    x2 = min(img.shape[1], x + w + padding_x)
    y2 = min(img.shape[0], y + h + padding_y)

    cropped = img[y1:y2, x1:x2]

    if cropped.size == 0:
        return img

    return cropped


def resize_for_ocr(img):
    """
    Resize image while maintaining aspect ratio.

    Small medicine packages are upscaled.
    Large images are limited to avoid excessive OCR processing.
    """

    h, w = img.shape[:2]

    max_side = max(h, w)

    # Small image -> upscale aggressively
    if max_side < 1000:
        target_size = 1600

    # Medium image -> moderate upscale
    elif max_side < 1600:
        target_size = 1800

    # Already sufficiently large
    else:
        target_size = min(max_side, 2200)

    scale = target_size / max_side

    new_width = max(1, int(w * scale))
    new_height = max(1, int(h * scale))

    # INTER_CUBIC is generally better for enlarging text
    if scale > 1:
        interpolation = cv2.INTER_CUBIC
    else:
        interpolation = cv2.INTER_AREA

    resized = cv2.resize(
        img,
        (new_width, new_height),
        interpolation=interpolation
    )

    return resized


def process_image(image_path):

    print(f"\nProcessing image: {image_path}")

    img = cv2.imread(image_path)

    if img is None:
        raise Exception("Image could not be loaded.")

    processed_folder = os.path.join(
        os.path.dirname(__file__),
        "..",
        "processed"
    )

    os.makedirs(processed_folder, exist_ok=True)

    # --------------------------------------------------
    # 1. Smart crop
    # --------------------------------------------------

    cropped = crop_medicine_region(img)

    print(
        f"Original size: {img.shape[1]}x{img.shape[0]}"
    )

    print(
        f"After crop: {cropped.shape[1]}x{cropped.shape[0]}"
    )

    # --------------------------------------------------
    # 2. Resize / upscale for OCR
    # --------------------------------------------------

    resized = resize_for_ocr(cropped)

    print(
        f"OCR size: {resized.shape[1]}x{resized.shape[0]}"
    )

    # --------------------------------------------------
    # 3. Grayscale
    # --------------------------------------------------

    gray = cv2.cvtColor(
        resized,
        cv2.COLOR_BGR2GRAY
    )

    # --------------------------------------------------
    # 4. Contrast enhancement using CLAHE
    # --------------------------------------------------

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    contrast_enhanced = clahe.apply(gray)

    # --------------------------------------------------
    # 5. Otsu threshold
    # Better than fixed threshold=150 for different images
    # --------------------------------------------------

    _, threshold = cv2.threshold(
        contrast_enhanced,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # --------------------------------------------------
    # 6. Adaptive threshold
    # --------------------------------------------------

    adaptive = cv2.adaptiveThreshold(
        contrast_enhanced,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11
    )

    # --------------------------------------------------
    # 7. Sharpen
    # --------------------------------------------------

    sharpen_kernel = np.array([
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
    ])

    sharpen = cv2.filter2D(
        contrast_enhanced,
        -1,
        sharpen_kernel
    )

    # --------------------------------------------------
    # 8. Rotations for vertical/sideways medicine text
    # --------------------------------------------------

    rotated_90 = cv2.rotate(
        resized,
        cv2.ROTATE_90_CLOCKWISE
    )

    rotated_270 = cv2.rotate(
        resized,
        cv2.ROTATE_90_COUNTERCLOCKWISE
    )

    # --------------------------------------------------
    # 9. Save processed variants
    # --------------------------------------------------

    paths = {
        "original": os.path.join(
            processed_folder,
            "original.jpg"
        ),

        "gray": os.path.join(
            processed_folder,
            "gray.jpg"
        ),

        "threshold": os.path.join(
            processed_folder,
            "threshold.jpg"
        ),

        "adaptive": os.path.join(
            processed_folder,
            "adaptive.jpg"
        ),

        "sharpen": os.path.join(
            processed_folder,
            "sharpen.jpg"
        ),

        "rotated_90": os.path.join(
            processed_folder,
            "rotated_90.jpg"
        ),

        "rotated_270": os.path.join(
            processed_folder,
            "rotated_270.jpg"
        ),
    }

    cv2.imwrite(
        paths["original"],
        resized
    )

    cv2.imwrite(
        paths["gray"],
        gray
    )

    cv2.imwrite(
        paths["threshold"],
        threshold
    )

    cv2.imwrite(
        paths["adaptive"],
        adaptive
    )

    cv2.imwrite(
        paths["sharpen"],
        sharpen
    )

    cv2.imwrite(
        paths["rotated_90"],
        rotated_90
    )

    cv2.imwrite(
        paths["rotated_270"],
        rotated_270
    )

    print("Images Saved Successfully")

    return paths