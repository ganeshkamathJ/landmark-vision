---
title: Landmark Vision
emoji: 🏛️
colorFrom: purple
colorTo: cyan
sdk: docker
app_port: 7860
pinned: true
short_description: AI-powered landmark recognition using HuggingFace Vision AI
---

# 🏛️ Landmark Vision

> **AI-powered landmark recognition** — Upload any photo of a famous world landmark and get instant identification with name, country, city, and historical description.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-green?logo=flask)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15-orange?logo=tensorflow)
![License](https://img.shields.io/badge/License-MIT-purple)

---

## ✨ Features

- 🖼️ **Drag-and-drop image upload** with live preview
- 🧠 **MobileNetV2** fine-tuned on 50 world landmarks
- 🌍 Returns **landmark name, country, city, description, year built**
- 📊 **Confidence score** with animated progress bar
- 🌙 **Dark-mode website** with glassmorphism, gradient accents
- 🚀 **Demo mode** — works out of the box before training
- 📡 **REST API** endpoint at `/api/predict`
- 📱 Fully **responsive** — mobile-first design

---

## 📁 Project Structure

```
landmark-vision/
├── app/
│   ├── __init__.py          # Flask application factory
│   ├── routes.py            # URL routes & predict endpoint
│   ├── predictor.py         # Model loading & inference
│   └── landmark_info.py     # Landmark metadata dictionary
├── model/
│   ├── train.py             # MobileNetV2 fine-tuning script
│   └── evaluate.py          # Evaluation + confusion matrix
├── static/
│   ├── css/style.css        # Main stylesheet (dark mode)
│   └── js/main.js           # Drag-drop, animations, nav
├── templates/
│   ├── base.html            # Base layout (nav, footer)
│   ├── index.html           # Homepage (hero, upload, sections)
│   ├── result.html          # Prediction result page
│   └── about.html           # About / model info page
├── uploads/                 # Temporary image uploads (gitignored)
├── data/landmarks/          # Dataset folder (gitignored)
├── config.py                # App configuration
├── run.py                   # Entry point
├── requirements.txt
└── .gitignore
```

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/ganeshkamathJ/landmark-vision.git
cd landmark-vision

python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Run in Demo Mode (no training needed)

The app works immediately without a trained model — it runs in **demo mode** using ImageNet weights so you can test the UI:

```bash
python run.py
```

Visit: **http://localhost:5000**

---

## 🗂️ Dataset Setup (Kaggle)

We use the **Pictures of Famous Places** dataset — only **~53 MB**.

### Step 1 — Set up Kaggle API

1. Go to [kaggle.com/account](https://www.kaggle.com/account) → **Create New API Token**
2. Download `kaggle.json`
3. Place it at:
   - **Windows**: `C:\Users\<YourName>\.kaggle\kaggle.json`
   - **Mac/Linux**: `~/.kaggle/kaggle.json`

### Step 2 — Download & Unzip

```bash
pip install kaggle

# Download (~53 MB)
kaggle datasets download -d vaslemon/pictures-of-famous-places -p ./data/

# Unzip (Windows PowerShell)
Expand-Archive ./data/pictures-of-famous-places.zip -DestinationPath ./data/landmarks/

# Unzip (Mac/Linux)
unzip ./data/pictures-of-famous-places.zip -d ./data/landmarks/
```

Your `data/landmarks/` folder should look like:

```
data/landmarks/
├── eiffel_tower/
│   ├── img1.jpg
│   └── ...
├── colosseum/
├── taj_mahal/
└── ...
```

---

## 🧠 Train the Model

```bash
# Default settings (recommended)
python model/train.py

# Custom options
python model/train.py \
  --data_dir  ./data/landmarks \
  --epochs_head 10 \
  --epochs_fine 10 \
  --batch_size 32

# After training, evaluate
python model/evaluate.py
```

**Training phases:**

| Phase | Description | Epochs | LR |
|-------|-------------|--------|-----|
| 1 | Train classification head (base frozen) | 10 | 1e-3 |
| 2 | Fine-tune top 30 base layers | 10 | 1e-5 |

After training, the model is saved to `model/landmark_model.h5`.

---

## ▶️ Run the App

```bash
# Development
python run.py

# Production (gunicorn)
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

Open **http://localhost:5000** in your browser.

---

## 📡 REST API

```http
POST /api/predict
Content-Type: multipart/form-data

image: <binary image file>
```

**Response:**

```json
{
  "class_name": "eiffel_tower",
  "confidence": 94.3,
  "demo_mode": false,
  "name": "Eiffel Tower",
  "country": "France",
  "city": "Paris",
  "flag": "🇫🇷",
  "description": "...",
  "year_built": "1889",
  "category": "Monument"
}
```

---

## 🔧 Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | (auto) | Flask secret key |
| `MAX_CONTENT_LENGTH` | 16 MB | Max upload size |
| `MODEL_PATH` | `model/landmark_model.h5` | Path to trained model |
| `CONFIDENCE_THRESHOLD` | 0.30 | Min confidence to show a result |
| `FLASK_DEBUG` | `False` | Enable debug mode |

Set via environment variables or edit `config.py`.

---

## 📦 Dependencies

```
Flask==3.0.3
tensorflow==2.15.0
Pillow==10.3.0
numpy==1.26.4
Werkzeug==3.0.3
gunicorn==22.0.0
kaggle==1.6.14
scikit-learn==1.4.2
matplotlib==3.9.0
seaborn==0.13.2
tqdm==4.66.4
```

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "Add my feature"`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.

---

*Built with ❤️ using Python · Flask · TensorFlow · MobileNetV2*
