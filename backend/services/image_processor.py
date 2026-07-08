import cv2
import os

def process_image(image_path):

    img = cv2.imread(image_path)

    processed_folder = os.path.join(
        os.path.dirname(__file__),
        "..",
        "processed"
    )

    os.makedirs(processed_folder, exist_ok=True)

    # -------------------
    # Resize
    # -------------------

    resized = cv2.resize(img, (1000, 1000))

    # -------------------
    # Gray
    # -------------------

    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

    # -------------------
    # Binary Threshold
    # -------------------

    _, threshold = cv2.threshold(
        gray,
        150,
        255,
        cv2.THRESH_BINARY
    )

    # -------------------
    # Adaptive Threshold
    # -------------------

    adaptive = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2
    )

    # -------------------
    # Sharpen
    # -------------------

    kernel = [
        [0,-1,0],
        [-1,5,-1],
        [0,-1,0]
    ]

    import numpy as np

    sharpen = cv2.filter2D(
        gray,
        -1,
        np.array(kernel)
    )

    # -------------------
    # Save every version
    # -------------------

    cv2.imwrite(
        os.path.join(processed_folder,"original.jpg"),
        resized
    )

    cv2.imwrite(
        os.path.join(processed_folder,"gray.jpg"),
        gray
    )

    cv2.imwrite(
        os.path.join(processed_folder,"threshold.jpg"),
        threshold
    )

    cv2.imwrite(
        os.path.join(processed_folder,"adaptive.jpg"),
        adaptive
    )

    cv2.imwrite(
        os.path.join(processed_folder,"sharpen.jpg"),
        sharpen
    )

    print("Images Saved Successfully")

    return {
    "original": os.path.join(processed_folder, "original.jpg"),
    "gray": os.path.join(processed_folder, "gray.jpg"),
    "threshold": os.path.join(processed_folder, "threshold.jpg"),
    "adaptive": os.path.join(processed_folder, "adaptive.jpg"),
    "sharpen": os.path.join(processed_folder, "sharpen.jpg")
}