// ======================================================
// ELEMENTS
// ======================================================
console.log("scan.js loaded");

const loadingOverlay = document.getElementById("loadingOverlay");

const loadingText = document.getElementById("loadingText");

const cameraBtn = document.getElementById("cameraBtn");

const removeImage = document.getElementById("removeImage");

const imageInput = document.getElementById("imageInput");

const browseBtn = document.getElementById("browseBtn");

const uploadArea = document.querySelector(".upload-area");

const previewImage = document.getElementById("previewImage");

const placeholder = document.getElementById("placeholder");

const fileName = document.getElementById("fileName");

const fileSize = document.getElementById("fileSize");

const resolution = document.getElementById("resolution");

const analyzeBtn = document.getElementById("analyzeBtn");

const scanForm = document.getElementById("scanForm");

// ======================================================
// OPEN FILE PICKER
// ======================================================

browseBtn.addEventListener("click", function () {
  imageInput.click();
});

cameraBtn.addEventListener("click", function () {
  imageInput.setAttribute("capture", "environment");

  imageInput.click();
});

// ======================================================
// IMAGE SELECTED
// ======================================================

imageInput.addEventListener("change", function () {
  if (this.files.length === 0) return;

  loadImage(this.files[0]);
});

// ======================================================
// LOAD IMAGE
// ======================================================

function loadImage(file) {
  // Only images

  if (!file.type.startsWith("image/")) {
    alert("Please select an image.");

    return;
  }

  // Preview

  const reader = new FileReader();

  reader.onload = function (e) {
    previewImage.src = e.target.result;

    previewImage.style.display = "block";

    removeImage.style.display = "flex";

    removeImage.addEventListener("click", function () {
      imageInput.value = "";

      previewImage.src = "";

      previewImage.style.display = "none";

      placeholder.style.display = "block";

      removeImage.style.display = "none";

      fileName.textContent = "-";

      fileSize.textContent = "-";

      resolution.textContent = "-";

      analyzeBtn.disabled = true;
    });

    placeholder.style.display = "none";
  };

  reader.readAsDataURL(file);

  // Filename

  fileName.textContent = file.name;

  // File Size

  fileSize.textContent = (file.size / (1024 * 1024)).toFixed(2) + " MB";

  // Resolution

  const img = new Image();

  img.onload = function () {
    resolution.textContent = img.width + " × " + img.height;
  };

  img.src = URL.createObjectURL(file);

  // Enable Analyze

  analyzeBtn.disabled = false;
}

// ======================================================
// DRAG EVENTS
// ======================================================

uploadArea.addEventListener("dragover", function (e) {
  e.preventDefault();

  uploadArea.classList.add("drag-active");
});

uploadArea.addEventListener("dragleave", function () {
  uploadArea.classList.remove("drag-active");
});

uploadArea.addEventListener("drop", function (e) {
  e.preventDefault();

  uploadArea.classList.remove("drag-active");

  const file = e.dataTransfer.files[0];

  if (!file) return;

  imageInput.files = e.dataTransfer.files;

  loadImage(file);
});

// ======================================================
// ANALYZE BUTTON
// ======================================================

analyzeBtn.addEventListener("click", function () {
  console.log("STEP 1");

  if (imageInput.files.length === 0) {
    console.log("NO IMAGE");
    return;
  }

  console.log("STEP 2");

  loadingOverlay.style.display = "flex";

  console.log("STEP 3");

  setTimeout(function () {
    console.log("STEP 4");
    scanForm.submit();
  }, 3000);
});
