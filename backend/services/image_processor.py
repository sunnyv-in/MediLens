import cv2

def process_image(image_path):

    img = cv2.imread(image_path)

    print("Original Shape:", img.shape)

    resized = cv2.resize(img, (500, 500))

    print("Resized Shape:", resized.shape)

    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

    print("Gray Shape:", gray.shape)

    edges = cv2.Canny(gray, 100, 200)

    print("Edge Shape:", edges.shape)

    return edges