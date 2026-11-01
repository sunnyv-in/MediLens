# 👥 MediLens — Team Setup Guide

This document is for MediLens team members and contributors.

Follow this guide before making changes to the project.

---

# 1. 💊 About MediLens

MediLens is an AI-powered medicine analysis application.

The current processing pipeline is:

```text
Medicine Image
      ↓
OpenCV Image Preprocessing
      ↓
PaddleOCR
      ↓
OCR Sufficiency Check
      ↓
EasyOCR Fallback (if required)
      ↓
OCR Cleaning
      ↓
OCR Ranking
      ↓
Gemini AI
      ↓
Structured Medicine Information
      ↓
Counterfeit Risk Analysis
      ↓
Final Result


````markdown
# 👥 MediLens — Team Setup

## 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd MediLens
````

---

## 2. Python Version

MediLens uses Python 3.13+.

Check your version:

```bash
python --version
```

---

## 3. Create Virtual Environment

### Windows

```powershell
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 4. Install Dependencies

After activating the virtual environment:

```bash
pip install -r requirements.txt
```

---

## 5. Create `.env`

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
SECRET_KEY=YOUR_SECRET_KEY
DATABASE_URL=sqlite:///database/medilens.db
```

Never commit `.env` to GitHub.

---

## 6. PaddleOCR Setup

MediLens uses:

```text
PaddleOCR → Primary OCR
EasyOCR   → Fallback OCR
```

The PaddleOCR worker is located at:

```text
backend/workers/paddle_worker.py
```

### Current tested PaddleOCR environment

```text
Python            3.13.15
PaddleOCR         3.7.0
PaddlePaddle-GPU  3.3.1
```

The current PaddleOCR environment is GPU-specific and is used for development/testing.

Do NOT:

* Copy another developer's virtual environment.
* Commit `paddle_venv`.
* Commit `experiments`.
* Create another `paddle_worker.py`.
* Randomly change PaddleOCR/PaddlePaddle versions.
* Randomly install different CUDA/Paddle packages.

Detailed information:

```text
docs/paddleocr-setup.md
```

---

## 7. Run MediLens

```bash
python run.py
```

Open:

```text
http://127.0.0.1:5000
```

---

## 8. Test the Scanner

Upload a medicine image and verify:

* OCR extraction
* Medicine information
* Gemini AI explanation
* Counterfeit-risk analysis
* Final result

Current OCR flow:

```text
Medicine Image
      ↓
OpenCV
      ↓
PaddleOCR
      ↓
Sufficiency Check
      ↓
EasyOCR Fallback
      ↓
OCR Cleaning
      ↓
OCR Ranking
      ↓
Gemini AI
      ↓
Medicine Information
      ↓
Counterfeit Risk Analysis
      ↓
Final Result
```

---

# 🌿 Git Workflow

## Before Starting Work

```bash
git checkout main
git pull origin main
```

Create your own branch:

```bash
git checkout -b feature/your-feature-name
```

Examples:

```bash
git checkout -b feature/medicine-history
```

```bash
git checkout -b feature/reminder-ui
```

```bash
git checkout -b fix/scan-result
```

---

## Before Committing

Check your changes:

```bash
git status
```

Review:

```bash
git diff
```

Make sure you did NOT include:

```text
.env
venv/
paddle_venv/
experiments/
backend/uploads/
backend/processed/
__pycache__/
*.pyc
```

---

## Commit

```bash
git add .
git commit -m "Describe your changes"
```

Examples:

```bash
git commit -m "Improve medicine history"
```

```bash
git commit -m "Fix scan result UI"
```

```bash
git commit -m "Add medication reminder"
```

---

## Push Your Branch

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request.

Do not directly push unfinished work to `main`.

---

# 📂 Main Project Areas

```text
backend/routes/       → Flask routes
backend/services/     → OCR, Gemini and application logic
backend/workers/      → PaddleOCR worker
backend/models/       → Database models
backend/schema/       → Data schemas
backend/utils/        → Utility functions

frontend/templates/   → HTML pages
frontend/static/css/  → CSS
frontend/static/js/   → JavaScript

docs/                 → Documentation
```

---

# 🚫 Important Rules

Never commit:

```text
.env
venv/
paddle_venv/
experiments/
backend/uploads/
backend/processed/
__pycache__/
*.pyc
```

Never expose:

```text
API keys
Passwords
Secret keys
Private credentials
```

Do not change the core OCR architecture without discussing it with the team.

Current architecture:

```text
PaddleOCR
     ↓
Sufficiency Check
     ↓
EasyOCR Fallback
```

Do not remove EasyOCR because it is currently the fallback engine.

Do not randomly upgrade/downgrade PaddleOCR, PaddlePaddle, CUDA, or other core dependencies.

---

# 🆘 If You Get an Error

Do not randomly reinstall packages or change versions.

Send the complete terminal error/traceback to the team.

For PaddleOCR/GPU/CUDA errors, check:

```text
docs/paddleocr-setup.md
```

and contact the person responsible for the OCR pipeline.

---

# ✅ Before Pull Request

* [ ] Application starts
* [ ] Your feature works
* [ ] Scanner still works
* [ ] No `.env` committed
* [ ] No virtual environment committed
* [ ] No experimental files committed
* [ ] No uploaded images committed
* [ ] `git diff` reviewed
* [ ] Changes are limited to your feature
* [ ] Commit message is meaningful

---

# 💊 MediLens

**Scan • Identify • Explain • Verify**

```
```
