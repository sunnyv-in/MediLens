
# 💊 MediLens

<p align="center">

<!-- PROJECT LOGO -->
<img src="assets/logo.png" alt="MediLens Logo" width="180">

</p>

<h3 align="center">
AI-Powered Medicine Scanner & Analysis Platform
</h3>

<p align="center">
Scan • Identify • Explain • Analyze • Manage
</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.14+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask)
![EasyOCR](https://img.shields.io/badge/OCR-EasyOCR-green)
![Gemini AI](https://img.shields.io/badge/AI-Gemini-blueviolet)
![SQLite](https://img.shields.io/badge/Database-SQLite-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

</p>

---

# 🌐 Live Demo

🚧 **Live Demo:** Coming Soon

> MediLens is currently being prepared for production deployment.

---

# 📖 About MediLens

**MediLens** is an AI-powered medicine analysis web application designed to help users understand information printed on medicine packaging.

Users can upload an image of a medicine package, after which MediLens processes the image using **OpenCV and EasyOCR**, cleans and ranks the extracted text, and uses **Google Gemini AI** to identify and structure medicine information.

The application can also generate an easy-to-understand AI explanation of the medicine and perform a basic packaging-based counterfeit risk analysis.

Beyond scanning, MediLens includes medicine management and safety-related features such as:

- Medicine Shelf
- Medicine History
- Medication Reminders
- Expiry Alerts
- Drug Interaction Information
- Emergency Mode

MediLens was developed as a collaborative hackathon project using Python, Flask, EasyOCR, OpenCV, Gemini AI, SQLAlchemy, SQLite, HTML, CSS, JavaScript, and Git/GitHub.

---

# ✨ Features

## 🔍 AI Medicine Scanner

Upload an image of medicine packaging and MediLens processes it through an AI-powered analysis pipeline.

### Pipeline

```text
Medicine Image
      ↓
OpenCV Image Processing
      ↓
EasyOCR
      ↓
OCR Text Extraction
      ↓
OCR Cleaning
      ↓
OCR Ranking
      ↓
Gemini AI
      ↓
Structured Medicine Information


---

💊 Medicine Information Extraction

MediLens attempts to extract important information from medicine packaging.

Information extracted

Medicine / Brand Name

Generic Name

Manufacturer

Strength

Composition

Batch Number

Manufacturing Date

Expiry Date

Dosage

Storage

Warnings

Pack Size


The system combines OCR results with Gemini AI to handle noisy, incomplete, or imperfect OCR text.


---

🤖 Gemini AI Medicine Explanation

After medicine information is identified, Gemini AI generates an easy-to-understand explanation.

The explanation can include:

What the medicine is

Common uses

General instructions

Common side effects

Important precautions

Storage information

Important safety information


The purpose is to make medicine information easier for ordinary users to understand.


---

🛡️ Counterfeit Risk Analysis

MediLens includes a basic packaging validation and counterfeit-risk analysis feature.

The system checks available information such as:

Medicine name

Manufacturer

Strength

Batch number

Manufacturing date

Expiry date

Manufacturing and expiry-date consistency


Result includes

Risk Score

Risk Level

Confidence

Packaging Validation Checks


> ⚠️ Important: This feature provides a software-based risk assessment only. It cannot guarantee that a medicine is genuine or counterfeit. Users should verify suspicious medicines through official sources, pharmacists, manufacturers, or qualified healthcare professionals.




---

📚 Medicine Shelf

Users can save analyzed medicines and organize their medicine records.

The medicine shelf provides a convenient place to access saved medicines.


---

📜 Medicine History

MediLens keeps track of previously analyzed medicines so users can review their scan history.


---

⏰ Medication Reminders

Users can create medication reminders to help keep track of their medicines and scheduled doses.


---

⚠️ Expiry Alerts

MediLens includes expiry-related functionality to help users identify medicines that are approaching or have passed their expiry date.


---

💊 Drug Interaction Information

The application includes a drug interaction section designed to provide information about potential interactions between medicines.


---

🚨 Emergency Mode

MediLens includes an emergency-mode feature providing quick access to important safety-related information.


---

🖼️ Screenshots

🏠 Home Page

<!-- PLACE YOUR HOME PAGE SCREENSHOT HERE --><p align="center">
  <img src="docs/images/home.png" alt="MediLens Home Page" width="900">
</p>
---

📷 Medicine Scanner

<!-- PLACE YOUR SCANNER SCREENSHOT HERE --><p align="center">
  <img src="docs/images/scanner.png" alt="MediLens Medicine Scanner" width="900">
</p>
---

🔬 Medicine Analysis Result

<!-- PLACE YOUR MEDICINE ANALYSIS SCREENSHOT HERE --><p align="center">
  <img src="docs/images/result.png" alt="MediLens Medicine Analysis" width="900">
</p>
---

🤖 Gemini AI Explanation

<!-- PLACE YOUR AI EXPLANATION SCREENSHOT HERE --><p align="center">
  <img src="docs/images/ai-explanation.png" alt="Gemini AI Medicine Explanation" width="900">
</p>
---

🛡️ Counterfeit Risk Analysis

<!-- PLACE YOUR COUNTERFEIT ANALYSIS SCREENSHOT HERE --><p align="center">
  <img src="docs/images/counterfeit.png" alt="Counterfeit Risk Analysis" width="900">
</p>
---

📚 Medicine Shelf

<!-- PLACE YOUR MEDICINE SHELF SCREENSHOT HERE --><p align="center">
  <img src="docs/images/shelf.png" alt="Medicine Shelf" width="900">
</p>
---

📜 Medicine History

<!-- PLACE YOUR MEDICINE HISTORY SCREENSHOT HERE --><p align="center">
  <img src="docs/images/history.png" alt="Medicine History" width="900">
</p>
---

⏰ Medication Reminders

<!-- PLACE YOUR REMINDER SCREENSHOT HERE --><p align="center">
  <img src="docs/images/reminders.png" alt="Medication Reminders" width="900">
</p>
---

ℹ️ About MediLens

<!-- PLACE YOUR ABOUT PAGE SCREENSHOT HERE --><p align="center">
  <img src="docs/images/about.png" alt="About MediLens" width="900">
</p>
---

🧠 How MediLens Works

The main medicine-scanning workflow works as follows:

USER
                          │
                          ▼
                Upload Medicine Image
                          │
                          ▼
                 OpenCV Processing
                          │
                          ▼
                       EasyOCR
                          │
                          ▼
                  OCR Text Extraction
                          │
                          ▼
                  OCR Cleaning
                          │
                          ▼
                  OCR Line Ranking
                          │
                          ▼
                    Gemini AI
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
      Medicine Information      AI Explanation
              │
              ▼
       Counterfeit Analysis
              │
              ▼
          Final Result
              │
        ┌─────┴─────┐
        ▼           ▼
     History      Shelf
        │
        ▼
     Reminders


---

🏗️ Application Architecture

MediLens
                            │
             ┌──────────────┴──────────────┐
             │                             │
         Frontend                       Backend
             │                             │
      HTML / CSS / JS                    Flask
             │                             │
             │                    ┌────────┴────────┐
             │                    │                 │
             │                 Routes           Services
             │                    │                 │
             │                    │        ┌────────┼────────┐
             │                    │        │        │        │
             │                    │      OCR      Gemini   Risk
             │                    │
             │                    │
             │                 SQLAlchemy
             │                    │
             │                  SQLite
             │
             └──────────────┬──────────────┘
                            │
                       User Interface


---

🛠️ Technology Stack

Frontend

HTML5

CSS3

JavaScript

Jinja2 Templates

Font Awesome


Backend

Python

Flask

Flask-SQLAlchemy

SQLAlchemy


Artificial Intelligence

Google Gemini AI

Google GenAI Python SDK


OCR & Image Processing

EasyOCR

OpenCV

Pillow

NumPy

scikit-image


Database

SQLite

SQLAlchemy


Development Tools

Git

GitHub

Visual Studio Code

Python Virtual Environment



---

📂 Project Structure

MediLens/
│
├── assets/
│   └── logo.png
│
├── backend/
│   │
│   ├── models/
│   │   ├── medicine.py
│   │   ├── medicine_history.py
│   │   ├── reminder.py
│   │   └── drug_interaction.py
│   │
│   ├── routes/
│   │   ├── home_routes.py
│   │   ├── scan_routes.py
│   │   ├── about_routes.py
│   │   ├── medicine_shelf.py
│   │   ├── medicine_history.py
│   │   ├── reminder_routes.py
│   │   ├── expiry_routes.py
│   │   ├── drug_interaction.py
│   │   └── emergency_routes.py
│   │
│   ├── services/
│   │   ├── image_processor.py
│   │   ├── ocr_service.py
│   │   ├── gemini_service.py
│   │   ├── counterfeit_service.py
│   │   ├── medicine_record_service.py
│   │   └── fallback_extractor.py
│   │
│   ├── uploads/
│   ├── processed/
│   ├── app.py
│   ├── config.py
│   └── extensions.py
│
├── database/
│
├── docs/
│   └── images/
│       ├── home.png
│       ├── scanner.png
│       ├── result.png
│       ├── ai-explanation.png
│       ├── counterfeit.png
│       ├── shelf.png
│       ├── history.png
│       ├── reminders.png
│       └── about.png
│
├── frontend/
│   ├── templates/
│   └── static/
│
├── .env.example
├── .gitignore
├── LICENSE
├── Procfile
├── README.md
├── requirements.txt
└── run.py


---

⚙️ Installation

1. Clone the Repository

git clone YOUR_GITHUB_REPOSITORY_URL


---

2. Enter the Project Directory

cd MediLens


---

3. Create a Virtual Environment

Windows

python -m venv venv

Linux / macOS

python3 -m venv venv


---

4. Activate the Virtual Environment

Windows PowerShell

.\venv\Scripts\Activate.ps1

Windows Command Prompt

venv\Scripts\activate

Linux / macOS

source venv/bin/activate


---

5. Install Dependencies

pip install -r requirements.txt


---

🔑 Environment Variables

MediLens uses Google Gemini AI for AI-powered medicine analysis and explanations.

Create a .env file in the project root:

GEMINI_API_KEY=YOUR_GEMINI_API_KEY
SECRET_KEY=YOUR_SECRET_KEY

Example

MediLens/
│
├── .env
├── .env.example
├── README.md
└── run.py

> 🔒 Never upload your real .env file or Gemini API key to GitHub.




---

▶️ Running MediLens Locally

After activating your virtual environment and installing the dependencies:

python run.py

The application should start on:

http://127.0.0.1:5000

Open the address in your browser.


---

🧪 Development

For local development, MediLens uses Flask's development server.

python run.py

Application flow:

run.py
   ↓
backend.app
   ↓
Flask Application
   ↓
Registered Blueprints
   ↓
MediLens Web Application


---

🚀 Deployment

MediLens is a Python Flask application and requires a hosting platform capable of running Python applications.

Possible deployment platforms include:

Render

Railway

PythonAnywhere

Other Flask-compatible hosting services


GitHub is used to store and manage the source code, while a cloud hosting platform runs the Flask application.

The project includes a production Procfile:

web: gunicorn run:app

> Gunicorn is intended for Linux-based production environments. On Windows, use python run.py for local development.




---

🔐 Security

Do not commit sensitive information to GitHub.

Never upload:

.env
API Keys
Secret Keys
Passwords
Private Credentials

The .gitignore file should exclude sensitive and generated files.

Before making the repository public, check your Git history for accidentally committed credentials.


---

🧩 Main Components

🖼️ Image Processor

Responsible for preparing medicine images before OCR.

Technologies:

OpenCV
Pillow
NumPy


---

🔎 OCR Service

Responsible for:

Extracting text from medicine images

Cleaning OCR results

Ranking OCR lines

Handling noisy OCR output


Technology:

EasyOCR


---

🤖 Gemini Service

Responsible for:

Medicine identification

Structured medicine information extraction

Brand-name identification

AI medicine explanations

JSON-based AI responses


Technology:

Google Gemini AI
Google GenAI Python SDK


---

🛡️ Counterfeit Service

Responsible for analyzing available medicine packaging information and generating a basic counterfeit-risk assessment.


---

💾 Medicine Record Service

Responsible for preparing and organizing medicine information for storage and application workflows.


---

👨‍💻 Team

Sunny Verma

OCR, AI Pipeline & Backend

Contributions:

OpenCV image preprocessing

EasyOCR integration

OCR text extraction

OCR cleaning

OCR ranking

Gemini AI integration

Structured medicine information extraction

AI medicine explanation

Counterfeit risk analysis

Flask backend integration

Git/GitHub collaboration



---

Nikhil

Medicine Database & Frontend

Contributions:

Medicine database functionality

Medicine shelf

Medicine-related features

Frontend development

UI integration



---

Ankush Kumar

Safety Features & Dashboard

Contributions:

Safety-related functionality

Dashboard features

Application integration

Frontend/backend collaboration



---

🎯 Project Goals

MediLens was developed with the following goals:

Make medicine information easier to access

Help users understand medicine packaging

Demonstrate practical AI and OCR integration

Provide medicine-management functionality

Explore AI-assisted medicine analysis

Build a complete full-stack application

Gain practical experience with collaborative software development



---

🚧 Limitations

MediLens is an educational and hackathon project.

OCR and AI systems can sometimes produce incorrect or incomplete information because medicine packaging may contain:

Blurry text

Very small text

Reflections

Damaged packaging

Unusual fonts

Low-quality images

OCR recognition errors


AI-generated information should always be verified using the actual medicine packaging and reliable professional sources.


---

⚠️ Medical Disclaimer

MediLens is not a replacement for a doctor, pharmacist, or qualified healthcare professional.

The information generated by MediLens is intended for educational and informational purposes only.

Do not use MediLens to:

Diagnose a medical condition

Change medication

Determine a prescription dosage

Stop medication

Start medication

Replace professional medical advice


Always consult a qualified healthcare professional before starting, stopping, or changing medication.


---

🔮 Future Improvements

Potential future improvements include:

📱 Android / iOS application

🔐 User authentication

☁️ Cloud database

📦 Barcode scanning

🔳 QR-code verification

🏭 Manufacturer verification

🌐 Multi-language support

🎙️ Voice-based medicine assistant

💬 Conversational AI assistant

📄 Prescription scanning

💊 Advanced drug interaction checking

👨‍⚕️ Doctor / pharmacist portal

🔔 Advanced medication notifications

📊 User health dashboard

🔎 Larger medicine database

🧠 Improved medicine verification models



---

🏆 Hackathon Project

MediLens was developed as a collaborative hackathon project focused on exploring the practical use of:

Artificial Intelligence
Computer Vision
OCR
Natural Language Processing
Web Development
Database Systems
API Integration
Prompt Engineering

The project allowed the team to gain hands-on experience building and integrating multiple technologies into a complete working application.


---

📚 Learning Outcomes

Through MediLens, the team gained practical experience in:

Python backend development

Flask application architecture

Image preprocessing

OCR systems

AI API integration

Prompt engineering

Structured AI responses

Database management

Git and GitHub collaboration

Frontend/backend integration

Environment variables

Application deployment

Full-stack development



---

🙏 Acknowledgements

We would like to acknowledge the technologies and open-source projects that helped make MediLens possible:

Python

Flask

EasyOCR

OpenCV

Google Gemini AI

SQLAlchemy

SQLite

Pillow

NumPy



---

📄 License

This project is licensed under the MIT License.

See the LICENSE file for more information.


---

⭐ Support MediLens

If you find MediLens interesting or useful, consider giving the repository a ⭐ on GitHub.

Your support helps us continue improving the project.


---

<p align="center">💊 MediLens

Scan • Understand • Manage • Stay Informed

Built with ❤️ by Team MediLens

</p>
```📁 Then create this exact screenshot structure

MediLens/
│
├── docs/
│   └── images/
│       ├── home.png
│       ├── scanner.png
│       ├── result.png
│       ├── ai-explanation.png
│       ├── counterfeit.png
│       ├── shelf.png
│       ├── history.png
│       ├── reminders.png
│       └── about.png
│
├── assets/
│   └── logo.png
│
└── README.md

The README already has the spaces/placeholders for all of these images. Just put the screenshots in those locations and GitHub will automatically display them.

One important thing: before you push this, change only these two placeholders:

YOUR_GITHUB_REPOSITORY_URL
YOUR_LIVE_DEMO_URL

For the live demo, since MediLens is not deployed yet, you can leave "Coming Soon" exactly as it is for now.