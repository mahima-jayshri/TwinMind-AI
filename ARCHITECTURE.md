# TwinMind AI Architecture

## System Overview

TwinMind AI is a full-stack application consisting of a React frontend, FastAPI backend, and intelligent agent system powered by Google's Gemini API.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│  React + Tailwind CSS + Framer Motion + Lucide React       │
│  Pages: Login, Onboarding, Dashboard, Chat, Profile         │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST API
┌──────────────────────▼──────────────────────────────────────┐
│                         Backend                              │
│  FastAPI + SQLAlchemy + Python                               │
│  Layers: API → Services → Agent → Memory → Database        │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                    Agent System                               │
│  Gemini Client | Memory Manager | TwinMind Agent             │
│  - Context Building | - Memory Operations | - Reasoning      │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                    External Services                          │
│  Google Gemini API | Google OAuth | Database (SQLite)        │
└─────────────────────────────────────────────────────────────┘
```

## Backend Architecture

### Layer Structure

```
backend/
├── main.py                    # Application entry point
├── app/
│   ├── api/                   # API Routes Layer
│   │   ├── auth.py           # Authentication endpoints
│   │   ├── agent.py          # Agent interaction endpoints
│   │   ├── memory.py         # Memory management endpoints
│   │   ├── goals.py          # Goals & habits endpoints
│   │   └── predictions.py    # Prediction endpoints
│   ├── agent/                # Agent Layer
│   │   ├── gemini_client.py  # LLM integration
│   │   └── twinmind_agent.py # Core agent logic
│   ├── memory/               # Memory Layer
│   │   └── memory_manager.py # Memory operations
│   ├── services/             # Business Logic Layer
│   ├── models/               # Data Models
│   │   ├── user.py          # User model
│   │   ├── memory.py        # Memory models
│   │   ├── goals.py         # Goals & habits models
│   │   └── prediction.py    # Prediction models
│   ├── core/                 # Core Configuration
│   │   ├── config.py        # Settings management
│   │   └── security.py      # Security utilities
│   └── db/                   # Database Layer
│       └── database.py      # Database connection
```

### API Layer

The API layer handles HTTP requests and responses, authentication, and input validation.

**Responsibilities:**
- Route handling
- Request validation
- Authentication middleware
- Response formatting
- Error handling

**Key Endpoints:**
- `/api/auth/*` - Authentication
- `/api/agent/*` - Agent interactions
- `/api/memory/*` - Memory operations
- `/api/goals/*` - Goals & habits
- `/api/predictions/*` - Predictions & analytics

### Agent Layer

The agent layer handles AI reasoning and LLM interactions.

**Components:**

1. **Gemini Client**
   - Manages Google Gemini API connections
   - Handles prompt engineering
   - Manages conversation history
   - Implements mode-specific prompts

2. **TwinMind Agent**
   - Orchestrates agent behavior
   - Manages onboarding flow
   - Performs agent actions
   - Coordinates with memory system

**Agent Modes:**
- Mentor: Professional guidance
- Best Friend: Casual support
- Roast: Humorous feedback
- Future Me: Perspective from future self
- Interviewer: Practice interviews

### Memory Layer

The memory layer handles all data persistence and retrieval operations.

**Memory Manager Responsibilities:**
- Add, update, delete memories
- Search and retrieve memories
- Build context for agent
- Generate Digital DNA
- Track memory evolution

**Memory Types:**
- Personality traits
- Goals (short-term, long-term)
- Habits
- Preferences
- Conversations
- Digital DNA

### Database Layer

The database layer handles data persistence using SQLAlchemy with async support.

**Models:**
- User: User accounts and settings
- Memory: Stored memories and conversations
- Goal: User goals with progress tracking
- Habit: Habits with streak tracking
- Prediction: AI predictions and analytics
- ProductivityMetric: Daily productivity data

## Frontend Architecture

### Component Structure

```
frontend/src/
├── main.jsx                 # Application entry
├── App.jsx                  # Root component with routing
├── context/                 # Context Providers
│   ├── AuthContext.jsx     # Authentication state
│   └── ThemeContext.jsx    # Theme management
├── pages/                   # Page Components
│   ├── Login.jsx           # Login page
│   ├── Onboarding.jsx      # Onboarding flow
│   ├── Dashboard.jsx       # Main dashboard
│   ├── Chat.jsx            # Chat interface
│   └── Profile.jsx         # User profile
├── services/                # API Services
│   └── api.js              # Axios instance
├── hooks/                   # Custom Hooks
├── components/              # Reusable Components
└── utils/                   # Utility Functions
```

### State Management

**Context Providers:**
- AuthContext: User authentication state
- ThemeContext: Theme (dark/light) management

**Local State:**
- Component-level state with useState
- Form state management
- UI state (modals, dropdowns)

### Routing

React Router handles client-side routing:
- `/login` - Login page
- `/onboarding` - Onboarding flow
- `/dashboard` - Main dashboard
- `/chat` - Chat interface
- `/profile` - User profile

### API Integration

Axios instance configured with:
- Base URL
- Request interceptors (auth token)
- Response interceptors (error handling)
- CORS handling

## Data Flow

### Authentication Flow

```
1. User clicks "Sign in with Google"
2. Frontend gets Google OAuth token
3. Frontend sends token to /api/auth/google
4. Backend validates token with Google
5. Backend creates/retrieves user
6. Backend generates JWT access token
7. Frontend stores token in localStorage
8. Frontend includes token in API requests
```

### Onboarding Flow

```
1. User completes onboarding (20 questions)
2. Each answer stored as memory with type
3. After completion, agent generates Digital DNA
4. Digital DNA stored as high-importance memory
5. User marked as onboarded
6. User redirected to dashboard
```

### Chat Flow

```
1. User sends message
2. Frontend sends to /api/agent/chat
3. Agent retrieves user context from memory
4. Agent builds prompt with context and mode
5. Agent sends prompt to Gemini API
6. Gemini returns response
7. Agent stores conversation in memory
8. Response returned to frontend
9. Frontend displays response
```

### Memory Evolution Flow

```
1. Every 10 conversations, agent checks evolution
2. If evolution needed, agent asks about goal changes
3. User responds with changes
4. Agent updates Digital DNA
5. Old value stored in evolution log
6. New Digital DNA becomes active
```

### Prediction Flow

```
1. User requests prediction
2. Agent retrieves recent behavior data
3. Agent builds prediction prompt
4. Agent sends to Gemini API
5. Gemini returns prediction with confidence
6. Prediction stored in database
7. Prediction returned to user
```

## Security Architecture

### Authentication
- Google OAuth 2.0
- JWT access tokens
- Token expiration handling
- Secure token storage

### Authorization
- User-scoped data access
- API route protection
- Request validation
- SQL injection prevention

### Data Security
- Environment variables for secrets
- Encrypted passwords
- HTTPS in production
- CORS configuration

## Performance Optimization

### Backend
- Async database operations
- Connection pooling
- Query optimization
- Response caching

### Frontend
- Code splitting
- Lazy loading
- Image optimization
- Debounced inputs

### Database
- Indexed queries
- Efficient joins
- Connection pooling
- Query caching

## Scalability Considerations

### Horizontal Scaling
- Stateless API design
- Load balancer ready
- Database sharding capability
- CDN for static assets

### Vertical Scaling
- Efficient memory usage
- Optimized queries
- Resource pooling
- Background task processing

## Monitoring & Logging

### Application Monitoring
- API response times
- Error tracking
- User analytics
- Performance metrics

### Logging
- Structured logging
- Error logging
- User action logging
- System health checks

## Deployment Architecture

### Development
- Local development with hot reload
- SQLite database
- Mock OAuth for testing

### Production
- Containerized deployment
- PostgreSQL database
- Redis caching
- CDN for static assets
- Load balancing

## Technology Rationale

### Backend Choices
- **FastAPI**: Modern, fast, async support
- **SQLAlchemy**: Mature ORM, async support
- **Gemini API**: Advanced reasoning capabilities
- **SQLite**: Simple, reliable for MVP

### Frontend Choices
- **React**: Large ecosystem, familiar
- **Tailwind CSS**: Rapid development, modern
- **Framer Motion**: Smooth animations
- **Vite**: Fast build times

### Integration Choices
- **Google OAuth**: Widely used, secure
- **JWT**: Standard for API auth
- **REST API**: Simple, widely supported

## Future Architecture Considerations

### Microservices
- Split agent into separate service
- Separate memory service
- Event-driven architecture
- Message queues for async tasks

### Advanced Features
- Vector database for semantic search
- Real-time with WebSockets
- Mobile app architecture
- Edge computing deployment

### Enterprise Features
- Multi-tenancy support
- Advanced security (SSO, MFA)
- Compliance features (GDPR, HIPAA)
- Admin dashboard

This architecture provides a solid foundation for TwinMind AI while allowing for future growth and enhancement.
