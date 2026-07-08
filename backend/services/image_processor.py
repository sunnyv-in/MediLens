import cv2
import os
import numpy as np


def process_image(image_path):
    img = cv2.imread(image_path)

    print(image_path)
    print(img)

    if img is None:
        raise Exception("Image could not be loaded.")

    processed_folder = os.path.join(
        os.path.dirname(__file__), "..", "processed"
    )
    os.makedirs(processed_folder, exist_ok=True)

    # -------------------
    # Resize (aspect ratio maintain karte hue, max side 1000px)
    # -------------------
    h, w = img.shape[:2]
    scale = 1000 / max(h, w)
    resized = cv2.resize(img, (int(w * scale), int(h * scale)))

    # -------------------
    # Gray
    # -------------------
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

    # -------------------
    # Contrast enhance (CLAHE) - blurry/low-light photos ke liye helpful
    # -------------------
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    contrast_enhanced = clahe.apply(gray)

    # -------------------
    # Binary Threshold
    # -------------------
    _, threshold = cv2.threshold(
        contrast_enhanced, 150, 255, cv2.THRESH_BINARY
    )

    # -------------------
    # Adaptive Threshold
    # -------------------
    adaptive = cv2.adaptiveThreshold(
        contrast_enhanced, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )

    # -------------------
    # Sharpen
    # -------------------
    kernel = np.array([
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
    ])
    sharpen = cv2.filter2D(contrast_enhanced, -1, kernel)

    # -------------------
    # Save every version
    # -------------------
    paths = {
        "original": os.path.join(processed_folder, "original.jpg"),
        "gray": os.path.join(processed_folder, "gray.jpg"),
        "threshold": os.path.join(processed_folder, "threshold.jpg"),
        "adaptive": os.path.join(processed_folder, "adaptive.jpg"),
        "sharpen": os.path.join(processed_folder, "sharpen.jpg"),
    }

    cv2.imwrite(paths["original"], resized)
    cv2.imwrite(paths["gray"], gray)
    cv2.imwrite(paths["threshold"], threshold)
    cv2.imwrite(paths["adaptive"], adaptive)
    cv2.imwrite(paths["sharpen"], sharpen)

    print("Images Saved Successfully")

    return paths