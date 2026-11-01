document.addEventListener("DOMContentLoaded", () => {

    const imageInput = document.getElementById("imageInput");
    const scanForm = document.getElementById("scanForm");

    const browseBtn = document.getElementById("browseBtn");
    const cameraBtn = document.getElementById("cameraBtn");

    const uploadArea = document.getElementById("uploadArea");

    const previewImage = document.getElementById("previewImage");
    const placeholder = document.getElementById("placeholder");
    const removeImage = document.getElementById("removeImage");

    const fileName = document.getElementById("fileName");
    const fileSize = document.getElementById("fileSize");
    const resolution = document.getElementById("resolution");
    const previewStatus = document.getElementById("previewStatus");

    const analyzeBtn = document.getElementById("analyzeBtn");

    const loadingOverlay = document.getElementById("loadingOverlay");

    let previewURL = null;
    let isSubmitting = false;

    const MAX_FILE_SIZE = 15 * 1024 * 1024;

    // =====================================
    // FILE PICKER
    // =====================================

    browseBtn.addEventListener("click", () => {

        imageInput.removeAttribute("capture");
        imageInput.click();

    });

    // =====================================
    // CAMERA
    // =====================================

    cameraBtn.addEventListener("click", () => {

        imageInput.setAttribute("capture", "environment");
        imageInput.click();

    });

    // =====================================
    // IMAGE SELECTION
    // =====================================

    imageInput.addEventListener("change", () => {

        const file = imageInput.files[0];

        if (file) {
            loadImage(file);
        }

    });

    // =====================================
    // LOAD IMAGE
    // =====================================

    function loadImage(file) {

        if (!file.type.startsWith("image/")) {

            alert("Please select a valid image.");

            resetImage();

            return;
        }

        if (file.size > MAX_FILE_SIZE) {

            alert("Image size must be less than 15 MB.");

            resetImage();

            return;
        }

        if (previewURL) {
            URL.revokeObjectURL(previewURL);
        }

        previewURL = URL.createObjectURL(file);

        previewImage.onload = () => {

            previewImage.style.display = "block";

            placeholder.style.display = "none";

            removeImage.style.display = "flex";

            resolution.textContent =
                `${previewImage.naturalWidth} × ${previewImage.naturalHeight}`;

        };

        previewImage.onerror = () => {

            alert("Unable to preview this image.");

            resetImage();

        };

        previewImage.src = previewURL;

        fileName.textContent = file.name;

        fileSize.textContent =
            (file.size / (1024 * 1024)).toFixed(2) + " MB";

        previewStatus.textContent = "Image ready";

        analyzeBtn.disabled = false;

    }

    // =====================================
    // RESET IMAGE
    // =====================================

    function resetImage() {

        imageInput.value = "";

        previewImage.removeAttribute("src");
        previewImage.style.display = "none";

        placeholder.style.display = "block";

        removeImage.style.display = "none";

        fileName.textContent = "Not selected";
        fileSize.textContent = "-";
        resolution.textContent = "-";

        previewStatus.textContent = "No image";

        analyzeBtn.disabled = true;

        if (previewURL) {
            URL.revokeObjectURL(previewURL);
            previewURL = null;
        }

    }

    // =====================================
    // REMOVE IMAGE
    // =====================================

    removeImage.addEventListener("click", resetImage);

    // =====================================
    // DRAG AND DROP
    // =====================================

    ["dragenter", "dragover"].forEach(eventName => {

        uploadArea.addEventListener(eventName, event => {

            event.preventDefault();
            event.stopPropagation();

            uploadArea.classList.add("drag-active");

        });

    });

    ["dragleave", "drop"].forEach(eventName => {

        uploadArea.addEventListener(eventName, event => {

            event.preventDefault();
            event.stopPropagation();

            uploadArea.classList.remove("drag-active");

        });

    });

    uploadArea.addEventListener("drop", event => {

        const file = event.dataTransfer.files[0];

        if (!file) return;

        try {

            const transfer = new DataTransfer();

            transfer.items.add(file);

            imageInput.files = transfer.files;

            loadImage(file);

        } catch (error) {

            console.error("File drop error:", error);

            alert("Could not select this image. Please use Browse Files.");

        }

    });

    // =====================================
    // FORM SUBMISSION
    // =====================================

    scanForm.addEventListener("submit", event => {

        if (isSubmitting) {

            event.preventDefault();

            return;

        }

        if (!imageInput.files.length) {

            event.preventDefault();

            alert("Please select a medicine image first.");

            return;

        }

        isSubmitting = true;

        analyzeBtn.disabled = true;

        analyzeBtn.innerHTML =
            '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing...';

        loadingOverlay.style.display = "flex";

        loadingOverlay.setAttribute("aria-hidden", "false");

    });

    // =====================================
    // CLEANUP
    // =====================================

    window.addEventListener("pagehide", () => {

        if (previewURL) {
            URL.revokeObjectURL(previewURL);
        }

    });

});