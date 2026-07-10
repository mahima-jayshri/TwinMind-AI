# TwinMind AI 🧠

Your Digital Twin, Evolved.

TwinMind AI is NOT a chatbot. It's an AI Agent that interviews users, builds a digital twin of them, remembers their personality, goals, habits, and communication style, then continuously evolves with every conversation.

## 🚀 Features

- **Digital DNA Profile**: Comprehensive personality and behavior analysis
- **5 Agent Modes**: Mentor, Best Friend, Roast, Future Me, Interviewer
- **Memory System**: Persistent memory that evolves over time
- **Goal Tracking**: Set and track short-term and long-term goals
- **Habit Tracking**: Build and maintain positive habits
- **Future Predictions**: AI-powered productivity and behavior predictions
- **Smart Onboarding**: 20-question interview to understand you deeply
- **Modern Dashboard**: Beautiful, minimal dark mode UI

## 🏗️ Architecture

### Backend (FastAPI + Python)
- **FastAPI**: Modern, fast web framework
- **SQLAlchemy**: Async ORM for database operations
- **Google Gemini API**: LLM for intelligent responses
- **SQLite**: Lightweight database for data persistence
- **Google OAuth**: Secure authentication

### Frontend (React + Tailwind CSS)
- **React 18**: Modern UI library
- **Tailwind CSS**: Utility-first styling
- **Framer Motion**: Smooth animations
- **Lucide React**: Beautiful icons
- **Recharts**: Data visualization

### Agent System
- **Memory Manager**: Handles all memory operations
- **Gemini Client**: Manages LLM interactions
- **TwinMind Agent**: Core agent logic and reasoning
- **Context Builder**: Builds personalized context for each interaction

## 📁 Folder Structure

```
TwinMind AI/
├── backend/
│   ├── app/
│   │   ├── agent/          # Agent logic
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Configuration & security
│   │   ├── db/             # Database setup
│   │   ├── memory/         # Memory management
│   │   ├── models/         # Database models
│   │   └── services/       # Business logic
│   ├── main.py             # Application entry point
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── context/        # React context providers
│   │   ├── hooks/          # Custom hooks
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   └── utils/          # Utility functions
│   ├── package.json        # Node dependencies
│   ├── tailwind.config.js  # Tailwind configuration
│   └── vite.config.js      # Vite configuration
└── README.md
```

## 🛠️ Installation

### Prerequisites
- Python 3.9+
- Node.js 18+
- Google Cloud Project (for OAuth and Gemini API)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file:
```bash
cp .env.example .env
```

5. Configure your environment variables in `.env`:
```
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite+aiosqlite:///./twinmind.db
FRONTEND_URL=http://localhost:5173
```

6. Run the backend server:
```bash
python main.py
```

The backend will start on `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The frontend will start on `http://localhost:5173`

## 🔐 Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Create OAuth 2.0 credentials:
   - Application type: Web application
   - Authorized redirect URIs: `http://localhost:5173`
5. Copy Client ID and Client Secret to your `.env` file

## 🤖 Gemini API Setup

1. Go to [Google AI Studio](https://makersuite.google.com/)
2. Create an API key
3. Copy the API key to your `.env` file

## 📊 API Endpoints

### Authentication
- `POST /api/auth/google` - Google OAuth login
- `GET /api/auth/me` - Get current user info

### Agent
- `POST /api/agent/chat` - Chat with the AI agent
- `POST /api/agent/onboarding` - Conduct onboarding interview
- `POST /api/agent/action` - Perform agent actions
- `POST /api/agent/evolve` - Trigger memory evolution

### Memory
- `GET /api/memory/` - Get user memories
- `POST /api/memory/` - Add a new memory
- `PUT /api/memory/{id}` - Update a memory
- `DELETE /api/memory/{id}` - Delete a memory
- `GET /api/memory/digital-dna` - Get Digital DNA
- `GET /api/memory/search` - Search memories

### Goals & Habits
- `GET /api/goals` - Get user goals
- `POST /api/goals` - Create a goal
- `PUT /api/goals/{id}` - Update a goal
- `DELETE /api/goals/{id}` - Delete a goal
- `GET /api/habits` - Get user habits
- `POST /api/habits` - Create a habit
- `POST /api/habits/{id}/log` - Log habit completion

### Predictions
- `POST /api/predictions/predict` - Generate prediction
- `GET /api/predictions/predictions` - Get recent predictions
- `POST /api/predictions/productivity` - Log productivity
- `GET /api/predictions/productivity` - Get productivity metrics
- `GET /api/predictions/dashboard` - Get dashboard data

## 🎯 Agent Modes

1. **Mentor Mode**: Professional guidance and career advice
2. **Best Friend Mode**: Supportive and casual conversations
3. **Roast Mode**: Funny but respectful feedback
4. **Future Me Mode**: Advice from your future self
5. **Interviewer Mode**: Practice realistic interviews

## 🔮 Agent Actions

- Create study plans
- Create weekly goals
- Track habits
- Review resumes
- Conduct mock interviews
- Summarize PDFs
- Recommend learning resources
- Generate reminders

## 🧠 Memory Evolution

Every 10 conversations, the AI asks if your goals have changed. If yes, it updates your Digital DNA Profile to ensure the AI stays aligned with your current self.

## 📈 Future Predictions

Based on your stored behavior, TwinMind AI predicts:
- Likelihood of completing today's tasks
- Likelihood of procrastination
- Productivity trends

## 🚀 Deployment

### Backend Deployment (Render/Railway)

1. Push code to GitHub
2. Connect your repository to Render/Railway
3. Set environment variables in the dashboard
4. Deploy

### Frontend Deployment (Vercel/Netlify)

1. Build the frontend:
```bash
cd frontend
npm run build
```

2. Deploy the `dist` folder to Vercel/Netlify
3. Set environment variables for API URL

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

Built with ❤️ by TwinMind AI Team
