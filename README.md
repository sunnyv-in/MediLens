![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask)
![EasyOCR](https://img.shields.io/badge/OCR-EasyOCR-green)
![Gemini AI](https://img.shields.io/badge/AI-Gemini-blueviolet)
![License](https://img.shields.io/badge/License-MIT-yellow)

# 💊 MediLens

<p align="center">

<!-- Replace this with your logo -->

<img src="assets/logo.png" width="180">

</p>

<h3 align="center">
AI-Powered Medicine Scanner using EasyOCR, OpenCV & Gemini AI
</h3>

<p align="center">

Scan • Identify • Explain • Verify

</p>

---

# 📖 About

MediLens is an AI-powered medicine analysis web application that helps users scan medicine packaging using an image and automatically extract useful medicine information.

Using **EasyOCR**, **OpenCV**, and **Google Gemini AI**, MediLens can identify medicines, explain them in simple language, analyze counterfeit risks, organize medicine records, and help users manage their medications.

This project was built as a hackathon solution to make medicine information more accessible, understandable, and safer for everyone.

---

# 🌟 Features

## 🔍 AI Medicine Scanner

- Upload medicine image
- Automatic OCR extraction
- Intelligent preprocessing
- High accuracy medicine recognition

---

## 💊 Medicine Information

Extracts:

- Brand Name
- Generic Name
- Manufacturer
- Composition
- Strength
- Batch Number
- Manufacturing Date
- Expiry Date
- Dosage
- Storage Instructions
- Warnings
- Pack Size

---

## 🤖 Gemini AI Medicine Explanation

Generates easy-to-understand explanations including:

- What the medicine is
- Uses
- How to take it
- Side Effects
- Precautions
- Storage
- Important Notes

---

## 🛡 Counterfeit Risk Analysis

Automatically checks

- Manufacturer detected
- Batch number validity
- Manufacturing date
- Expiry date
- Packaging consistency
- Overall counterfeit risk score
- Confidence level

---

## 📚 Medicine Shelf

Save medicines for future reference.

---

## 📜 Medicine History

Track previously scanned medicines.

---

## ⏰ Medication Reminders

Create reminders so users never miss a dose.

---

# 🖼 Screenshots

## 🏠 Home Page

![Home](docs/images/home.png)

---

## 📷 Medicine Scanner

![Scanner](docs/images/scanner.png)

---

## 📊 Analysis Result

![Result](docs/images/result.png)

---

## 🤖 AI Explanation

![AI Explanation](docs/images/ai-explanation.png)

---

## 🛡 Counterfeit Analysis

![Counterfeit](docs/images/counterfeit.png)

---

## 📚 Medicine Shelf

![Shelf](docs/images/shelf.png)

---

## ℹ About Page

![About](docs/images/about.png)

---

# 🛠 Built With

### Backend

- Python
- Flask
- SQLAlchemy

### AI

- Google Gemini AI
- EasyOCR

### Image Processing

- OpenCV
- Pillow

### Database

- SQLite

### Frontend

- HTML5
- CSS3
- JavaScript

---

# 📂 Project Structure

```text
MediLens
│
├── assets/
│
├── backend/
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── uploads/
│   ├── processed/
│   ├── app.py
│   └── config.py
│
├── database/
│
├── docs/
│   └── images/
│
├── frontend/
│   ├── static/
│   └── templates/
│
├── .env.example
├── .gitignore
├── LICENSE
├── Procfile
├── README.md
├── requirements.txt
└── run.py
```

---

# ⚙ Installation

## Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/MediLens.git
```

---

## Move into Project

```bash
cd MediLens
```

---

## Create Virtual Environment

### Windows

```bash
python -m venv venv
```

### Linux / macOS

```bash
python3 -m venv venv
```

---

## Activate Virtual Environment

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Create Environment File

Create a file named

```
.env
```

Copy the following:

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY

SECRET_KEY=YOUR_SECRET_KEY

DATABASE_URL=sqlite:///database/medilens.db
```

---

## Run Application

```bash
python run.py
```

---

Visit

```
http://127.0.0.1:5000
```

---

# 🧠 How It Works

1. User uploads medicine image.

2. OpenCV preprocesses the image.

3. EasyOCR extracts text.

4. OCR results are cleaned and ranked.

5. Gemini AI extracts structured medicine information.

6. Gemini AI generates medicine explanation.

7. Counterfeit Analyzer validates packaging information.

8. Medicine is saved into local database.

9. Results are displayed to the user.

---

# 🚀 Future Improvements

- Barcode Scanner
- QR Code Verification
- Mobile Application
- User Authentication
- Cloud Database
- Multi-language Support
- Voice Assistant
- Doctor Portal
- Medicine Recommendation
- Drug Interaction AI
- Prescription Scanner

---

# 👨‍💻 Team

## Sunny Verma

- OCR Pipeline
- OpenCV Processing
- Gemini AI Integration
- Backend Development

---

## Nikhil

- Medicine Shelf
- Medicine Database
- History Module

---

## Ankush

- Dashboard
- Safety Features
- UI Components

---

# 📜 License

This project is licensed under the MIT License.

See the LICENSE file for details.

---

# ❤️ Acknowledgements

- Google Gemini AI
- EasyOCR
- OpenCV
- Flask
- SQLAlchemy
- Python Community

---

# ⭐ Support

If you like this project, please consider giving it a ⭐ on GitHub.

It helps others discover the project and motivates us to keep improving MediLens.
