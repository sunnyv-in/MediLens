import cv2
import os
import numpy as np

DEBUG = False

# Keep True because OCR currently reads saved images.
SAVE_DEBUG_IMAGES = True

# Reusable kernels
KERNEL = np.ones((5, 5), np.uint8)

SHARPEN_KERNEL = np.array([
    [0, -1, 0],
    [-1, 5, -1],
    [0, -1, 0]
])


def assess_image_quality(image_path):
    """
    Checks if an uploaded image is usable or 'super bad'
    (corrupted, tiny, pitch black, blank/overexposed, or extreme blur).

    Returns:
        (is_usable: bool, error_message: str)
    """
    img = cv2.imread(image_path)

    if img is None or img.size == 0:
        return (
            False,
            "The uploaded image could not be opened. Please upload a valid JPG, PNG, or WEBP image."
        )

    h, w = img.shape[:2]
    if h < 80 or w < 80:
        return (
            False,
            "This image is too small to read medicine details. Please upload a clearer, closer photo."
        )

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mean_brightness = float(np.mean(gray))
    std_contrast = float(np.std(gray))

    # 1. Pitch dark check
    if mean_brightness < 18:
        return (
            False,
            "This image is too dark. Please turn on your flash or take the photo in better lighting."
        )

    # 2. Completely washed out / blank white image check
    if mean_brightness > 248 and std_contrast < 8:
        return (
            False,
            "This image is overexposed or blank. Avoid direct glare on the medicine strip and try again."
        )

    # 3. Solid color / zero contrast check
    if std_contrast < 7:
        return (
            False,
            "No readable medicine packaging was detected. Please upload a clear photo of the medicine."
        )

    # 4. Extreme motion blur / out-of-focus check (normalized to 600px)
    scale = 600.0 / max(h, w)
    norm_gray = cv2.resize(
        gray,
        (max(1, int(w * scale)), max(1, int(h * scale))),
        interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_CUBIC
    )
    blur_score = float(cv2.Laplacian(norm_gray, cv2.CV_64F).var())

    if blur_score < 8.0:
        return (
            False,
            "This image is too blurry to safely read the medicine text. Please hold the camera steady and upload a clearer image."
        )

    return True, ""


def crop_medicine_region(img):
    """
    Attempts to remove large empty/white backgrounds around a medicine package.

    Important:
    If the background is not uniform white (e.g., wooden table, hand, cloth),
    the original image is returned immediately so text near edges is never clipped.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Only run white-background cropping if the image corners are actually white
    corners = [gray[0, 0], gray[0, -1], gray[-1, 0], gray[-1, -1]]
    if np.mean(corners) < 225:
        return img

    # Detect pixels that are sufficiently different from a white background
    mask = cv2.threshold(
        gray,
        240,
        255,
        cv2.THRESH_BINARY_INV
    )[1]

    # Remove tiny isolated noise
    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        KERNEL,
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

    image_area = img.shape[0] * img.shape[1]
    valid_contours = []

    for contour in contours:
        contour_area = cv2.contourArea(contour)
        if contour_area > image_area * 0.01:
            valid_contours.append(contour)

    if not valid_contours:
        return img

    all_points = np.vstack(valid_contours)
    x, y, w, h = cv2.boundingRect(all_points)

    crop_area = w * h
    if crop_area < image_area * 0.06 or crop_area > image_area * 0.92:
        return img

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
    Small medicine packages are upscaled; huge images are capped at 1350px for speed.
    """
    h, w = img.shape[:2]
    max_side = max(h, w)

    if max_side < 600:
        target_size = 1200
    elif max_side < 1200:
        target_size = 1350
    else:
        target_size = 1350

    if abs(max_side - target_size) < 80:
        return img

    scale = target_size / max_side
    new_width = max(1, int(w * scale))
    new_height = max(1, int(h * scale))

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
    if DEBUG:
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

    # 1. Smart crop
    cropped = crop_medicine_region(img)

    # 2. Resize / upscale for OCR
    resized = resize_for_ocr(cropped)

    # 3. Grayscale + edge-preserving bilateral denoise (helps noisy/bad images)
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    denoised = cv2.bilateralFilter(gray, 5, 50, 50)

    # 4. Contrast enhancement using CLAHE
    clahe = cv2.createCLAHE(
        clipLimit=2.2,
        tileGridSize=(8, 8)
    )
    contrast_enhanced = clahe.apply(denoised)

    # 5. Otsu threshold
    _, threshold = cv2.threshold(
        contrast_enhanced,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # 6. Adaptive threshold
    adaptive = cv2.adaptiveThreshold(
        contrast_enhanced,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11
    )

    # 7. Sharpen
    sharpen = cv2.filter2D(
        contrast_enhanced,
        -1,
        SHARPEN_KERNEL
    )

    # 8. Rotations for vertical/sideways medicine text
    rotated_90 = cv2.rotate(
        resized,
        cv2.ROTATE_90_CLOCKWISE
    )

    rotated_270 = cv2.rotate(
        resized,
        cv2.ROTATE_90_COUNTERCLOCKWISE
    )

    # 9. Save processed variants (preserves exact keys for all existing code)
    paths = {
        "original": os.path.join(processed_folder, "original.jpg"),
        "gray": os.path.join(processed_folder, "gray.jpg"),
        "threshold": os.path.join(processed_folder, "threshold.jpg"),
        "adaptive": os.path.join(processed_folder, "adaptive.jpg"),
        "sharpen": os.path.join(processed_folder, "sharpen.jpg"),
        "rotated_90": os.path.join(processed_folder, "rotated_90.jpg"),
        "rotated_270": os.path.join(processed_folder, "rotated_270.jpg"),
    }

    if SAVE_DEBUG_IMAGES:
        cv2.imwrite(paths["original"], resized)
        cv2.imwrite(paths["gray"], gray)
        cv2.imwrite(paths["threshold"], threshold)
        cv2.imwrite(paths["adaptive"], adaptive)
        cv2.imwrite(paths["sharpen"], sharpen)
        cv2.imwrite(paths["rotated_90"], rotated_90)
        cv2.imwrite(paths["rotated_270"], rotated_270)

    return paths