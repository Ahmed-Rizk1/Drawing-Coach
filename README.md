# 🎨 Drawing Coach

A web app that analyzes your drawings, guesses what you drew, gives coaching tips, and shows you step-by-step how to draw anything with an animated live guide.

🌐 **Live Demo:** [drawing-coach-94x1.vercel.app](https://drawing-coach-94x1.vercel.app/)

## ✨ Features
- 🖌️ Free-form drawing canvas (color, size, eraser)
- 🔍 Smart drawing analysis with tips
- 🎯 Step-by-step animated drawing guide
- 🧹 Two guide modes: Start fresh or overlay on your sketch
- 📱 Responsive — works on desktop and mobile

## 🛠️ Tech Stack
- **Frontend:** HTML · CSS · Vanilla JS
- **Backend:** FastAPI (Python)
- **Vision:** Groq API

## 📁 Project Structure
```
Drawing Coach AI/
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── backend/
│   ├── main.py
│   ├── routers/
│   ├── services/
│   ├── models/
│   └── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 🚀 Local Setup

**1. Clone the repo**
```bash
git clone https://github.com/Ahmed-Rizk1/Drawing-Coach.git
cd Drawing-Coach
```

**2. Create virtual environment and install deps**
```bash
uv venv
.venv\Scripts\activate
uv pip install -r requirements.txt
```

**3. Add your Groq API key**
```bash
# Create backend/.env
GROQ_API_KEY=your_key_here
```
Get a free key at [console.groq.com](https://console.groq.com)

**4. Start the backend**
```bash
cd backend
uvicorn main:app --reload
```

**5. Open `frontend/index.html` in your browser**

## 🌐 Deployment

See [DEPLOY.md](DEPLOY.md) for full deployment guide (Vercel + Render).

## 📄 License
MIT
