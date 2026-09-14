import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from main import app
from app.db.database import init_db
from app.agent.gemini_client import GeminiClient


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Initialize test database tables before tests run"""
    await init_db()


def test_intent_detection_classification():
    """Verify that intent detection accurately categorizes various user input types"""
    client = GeminiClient()

    # Casual Greetings
    assert client._detect_intent("Hi, how are you?") == "casual_greeting"
    assert client._detect_intent("Hello") == "casual_greeting"
    assert client._detect_intent("Good morning") == "casual_greeting"
    assert client._detect_intent("Hey there!") == "casual_greeting"
    assert client._detect_intent("how are you doing") == "casual_greeting"
    assert client._detect_intent("Thanks!") == "casual_greeting"

    # Mentoring & Productivity
    assert client._detect_intent("Help me plan my study schedule.") == "mentoring_productivity"
    assert client._detect_intent("Create a study plan for my exams") == "mentoring_productivity"
    assert client._detect_intent("How can I improve my productivity and habits?") == "mentoring_productivity"
    assert client._detect_intent("Give me career advice on software engineering") == "mentoring_productivity"

    # Technical Questions
    assert client._detect_intent("Explain how binary search works") == "technical_question"
    assert client._detect_intent("How to implement quicksort algorithm in python?") == "technical_question"
    assert client._detect_intent("What is the time complexity of recursion?") == "technical_question"

    # General Knowledge
    assert client._detect_intent("What is photosynthesis?") == "general_knowledge"
    assert client._detect_intent("Why is the sky blue?") == "general_knowledge"

    # Project Assistance
    assert client._detect_intent("How does Digital DNA work in TwinMind AI?") == "project_assistance"


@pytest.mark.asyncio
async def test_case_1_casual_greeting():
    """Test Case 1: User: 'Hi, how are you?' -> Natural greeting, no unsolicited mentoring/action plan."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Auth
        auth_resp = await ac.post("/api/auth/google", json={"token": "mock_google_token:chatuser1@twinmind.ai"})
        assert auth_resp.status_code == 200
        token = auth_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Chat with casual greeting
        chat_resp = await ac.post(
            "/api/agent/chat",
            headers=headers,
            json={
                "message": "Hi, how are you?",
                "mode": "mentor",
                "conversation_history": []
            }
        )
        assert chat_resp.status_code == 200
        data = chat_resp.json()
        response_text = data["response"].lower()

        # Verify natural conversational response
        assert any(greeting in response_text for greeting in ["hello", "doing well", "how are you", "great to connect"])
        # Ensure NO forced productivity coaching or action planning on casual greeting
        assert "highest-leverage action" not in response_text
        assert "measurable progress" not in response_text
        assert "thoughtful question about 'hi, how are you?'" not in response_text


@pytest.mark.asyncio
async def test_case_2_study_schedule_mentoring():
    """Test Case 2: User: 'Help me plan my study schedule.' -> Structured mentoring / productivity response."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        auth_resp = await ac.post("/api/auth/google", json={"token": "mock_google_token:chatuser2@twinmind.ai"})
        assert auth_resp.status_code == 200
        token = auth_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        chat_resp = await ac.post(
            "/api/agent/chat",
            headers=headers,
            json={
                "message": "Help me plan my study schedule.",
                "mode": "mentor",
                "conversation_history": []
            }
        )
        assert chat_resp.status_code == 200
        data = chat_resp.json()
        response_text = data["response"].lower()

        # Verify structured planning and study strategy
        assert any(term in response_text for term in ["schedule", "time-blocking", "focus", "plan", "review", "milestones"])


@pytest.mark.asyncio
async def test_technical_question_handling():
    """Verify chatbot responds with accurate technical explanations for coding/algorithm questions."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        auth_resp = await ac.post("/api/auth/google", json={"token": "mock_google_token:techuser@twinmind.ai"})
        assert auth_resp.status_code == 200
        token = auth_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        chat_resp = await ac.post(
            "/api/agent/chat",
            headers=headers,
            json={
                "message": "Explain how binary search works",
                "mode": "mentor",
                "conversation_history": []
            }
        )
        assert chat_resp.status_code == 200
        data = chat_resp.json()
        response_text = data["response"].lower()

        # Should explain algorithm and log n complexity
        assert "binary search" in response_text
        assert "log n" in response_text or "sorted" in response_text


@pytest.mark.asyncio
async def test_general_knowledge_handling():
    """Verify chatbot responds with clear facts for general knowledge questions."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        auth_resp = await ac.post("/api/auth/google", json={"token": "mock_google_token:gkuser@twinmind.ai"})
        assert auth_resp.status_code == 200
        token = auth_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        chat_resp = await ac.post(
            "/api/agent/chat",
            headers=headers,
            json={
                "message": "What is photosynthesis?",
                "mode": "mentor",
                "conversation_history": []
            }
        )
        assert chat_resp.status_code == 200
        data = chat_resp.json()
        response_text = data["response"].lower()

        assert "photosynthesis" in response_text
        assert any(term in response_text for term in ["light", "glucose", "chloroplast", "chemical energy"])


@pytest.mark.asyncio
async def test_persona_mode_greetings():
    """Verify all persona modes respond with natural persona-appropriate greetings for casual check-ins."""
    client = GeminiClient()
    modes = ["mentor", "best_friend", "roast", "future_me", "interviewer"]

    for mode in modes:
        resp = await client.chat(
            message="Good morning!",
            conversation_history=[],
            mode=mode
        )
        assert len(resp) > 0
        resp_lower = resp.lower()
        # Should not force action plan on greetings
        assert "highest-leverage action" not in resp_lower
        assert "measurable progress" not in resp_lower
