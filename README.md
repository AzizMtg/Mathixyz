# MathXyz 📸➡️📚

<div align="center">
  <img src="https://media.giphy.com/media/WRQBXSCnEFJIuxktnw/giphy.gif" alt="Confused math student" width="400"/>
  <br>
  <em>Me trying to understand what the professor just wrote</em>
</div>


## The Struggle is Real 😅

You know that feeling when:
- Professor writes hieroglyphics on the board ✍️🔮
- You frantically take photos hoping they'll make sense later 📸📸📸
- You get home and stare at blurry math pics like you're decoding ancient scrolls 🗞️🔍
- *"What does this even mean???"* 😵‍💫

**MathXyz to the rescue!** 🦸‍♂️ Turn those mysterious math photos into actual lessons that make sense.

## Features

- **Multi-image upload** with optional tagging (because chaos needs organization)
- **OCR processing** using local LaTeX-OCR with Mathpix API fallback (we read the unreadable)
- **Symbolic validation** with SymPy (making sure math is actually math)
- **LLM-powered explanations** using Nemotron via OpenRouter (your personal math tutor)
- **Interactive lesson viewer** with KaTeX math rendering (pretty equations that actually work)

## Coming Soon™ 🚀

- **Notion integration** - Sync your lessons directly to your study workspace
- **Audio transcription** - Record lectures and get synchronized text with your photos
- **Enhanced OCR** - Even better at reading your professor's handwriting (yes, even Dr. Smith's)

## Project Structure

```
/
├── frontend/          # React + TypeScript + Tailwind
├── backend/           # FastAPI + SQLite
│   ├── services/      # OCR, LLM, SymPy, lesson builder
│   ├── db/           # Database models and migrations
│   └── uploads/      # File storage
└── sample_data/      # Test images and mock responses
```

## Setup Instructions

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables (create `.env` file):
```env
MATHPIX_APP_ID=your_mathpix_app_id
MATHPIX_APP_KEY=your_mathpix_app_key
OPENAI_API_KEY=your_openai_api_key
```

5. Initialize database:
```bash
python -m alembic upgrade head
```

6. Run backend server:
```bash
uvicorn main:app --reload --port 8000
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm start
```

The app will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## API Endpoints

- `POST /upload` - Upload images and start processing
- `GET /status/{job_id}` - Check processing status
- `GET /lesson/{lesson_id}` - Retrieve structured lesson data

## Development Notes

- Mock responses are included for offline development
- Mathpix API key is optional - will fallback to LaTeX-OCR
- Code is modular for future containerization
