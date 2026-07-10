# Quick Start Guide

## Prerequisites
- Python 3.9+
- Node.js 18+
- Google Cloud Project (for OAuth and Gemini API)

## Backend Setup (5 minutes)

1. **Navigate to backend directory**
```bash
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
```

Edit `.env` and add:
```
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GEMINI_API_KEY=your_gemini_key
SECRET_KEY=generate_random_string_here
DATABASE_URL=sqlite+aiosqlite:///./twinmind.db
FRONTEND_URL=http://localhost:5173
```

5. **Run backend**
```bash
python main.py
```

Backend will start on `http://localhost:8000`

## Frontend Setup (3 minutes)

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Run frontend**
```bash
npm run dev
```

Frontend will start on `http://localhost:5173`

## Get API Keys

### Google OAuth
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add `http://localhost:5173` to authorized redirect URIs
6. Copy Client ID and Client Secret

### Gemini API
1. Go to [Google AI Studio](https://makersuite.google.com/)
2. Create API key
3. Copy API key

## Test the Application

1. Open `http://localhost:5173` in browser
2. Click "Continue with Google" (will use mock token for demo)
3. Complete onboarding (20 questions)
4. Explore dashboard
5. Try different chat modes
6. Set goals and track habits

## Common Issues

**Port already in use:**
- Backend: Change port in `main.py`
- Frontend: Change port in `vite.config.js`

**Import errors:**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again

**CORS errors:**
- Ensure FRONTEND_URL matches your frontend URL
- Check backend CORS settings in `main.py`

**Database errors:**
- Delete `twinmind.db` and restart backend
- Database will auto-initialize

## Development Tips

**Hot reload:**
- Backend: Auto-reloads on file changes
- Frontend: Auto-reloads on file changes

**View API docs:**
- Go to `http://localhost:8000/docs`
- Interactive API documentation

**Reset data:**
- Delete `twinmind.db` file
- Restart backend

**Test without OAuth:**
- Use mock token in Login.jsx
- Bypasses Google OAuth for development

## Next Steps

1. Configure real Google OAuth for production
2. Set up PostgreSQL for production database
3. Deploy backend to Render/Railway
4. Deploy frontend to Vercel/Netlify
5. Configure custom domain
6. Set up monitoring and analytics

## Support

For issues:
- Check README.md for detailed documentation
- Review ARCHITECTURE.md for system design
- See DEPLOYMENT.md for deployment guide

Happy building! 🚀
