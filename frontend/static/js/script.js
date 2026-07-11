const uploadInput = document.getElementById("medicine_image");
const uploadBox = document.querySelector(".upload-box");
const previewContainer = document.getElementById("preview-container");
const previewImage = document.getElementById("preview-image");
const analyzeBtn = document.getElementById("analyzeBtn");

// ---------- Preview ----------
uploadInput.addEventListener("change", function () {

    const file = this.files[0];

    if (!file) return;

    const reader = new FileReader();

    reader.onload = function (e) {

        previewImage.src = e.target.result;

        previewContainer.style.display = "block";

        analyzeBtn.disabled = false;

    };

    reader.readAsDataURL(file);

});

// ---------- Drag Events ----------
["dragenter", "dragover"].forEach(eventName => {

    uploadBox.addEventListener(eventName, e => {

        e.preventDefault();
        e.stopPropagation();

        uploadBox.style.background = "#eef6ff";
        uploadBox.style.borderColor = "#2563eb";

    });

});

["dragleave", "drop"].forEach(eventName => {

    uploadBox.addEventListener(eventName, e => {

        e.preventDefault();
        e.stopPropagation();

        uploadBox.style.background = "#f8fbff";
        uploadBox.style.borderColor = "#3b82f6";

    });

});

// ---------- Drop ----------
uploadBox.addEventListener("drop", function (e) {

    const files = e.dataTransfer.files;

    if (!files.length) return;

    uploadInput.files = files;

    uploadInput.dispatchEvent(new Event("change"));

});

// ==============================
// Loading Screen
// ==============================

const form = document.querySelector("form");

if(form){

    form.addEventListener("submit",function(){

        document.getElementById("loadingOverlay").style.display="flex";

    });

}