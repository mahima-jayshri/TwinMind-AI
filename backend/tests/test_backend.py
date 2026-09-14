import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from main import app
from app.db.database import init_db


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Initialize test database tables before tests run"""
    await init_db()


@pytest.mark.asyncio
async def test_health_and_root():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

        root_resp = await ac.get("/")
        assert root_resp.status_code == 200
        assert root_resp.json()["status"] == "running"


@pytest.mark.asyncio
async def test_auth_and_user_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Mock Google Auth
        auth_resp = await ac.post("/api/auth/google", json={"token": "mock_google_token:testuser@twinmind.ai"})
        assert auth_resp.status_code == 200
        data = auth_resp.json()
        assert "access_token" in data
        assert data["user"]["email"] == "testuser@twinmind.ai"

        token = data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get /me
        me_resp = await ac.get("/api/auth/me", headers=headers)
        assert me_resp.status_code == 200
        assert me_resp.json()["email"] == "testuser@twinmind.ai"


@pytest.mark.asyncio
async def test_memory_crud_operations():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Login
        auth_resp = await ac.post("/api/auth/google", json={"token": "mock_google_token:memtest@twinmind.ai"})
        token = auth_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create Memory
        mem_resp = await ac.post(
            "/api/memory/",
            headers=headers,
            json={
                "memory_type": "personality",
                "content": "Prefers deep focus in morning sessions",
                "importance": 8,
                "metadata": {"source": "manual"}
            }
        )
        assert mem_resp.status_code == 200
        memory_data = mem_resp.json()
        assert memory_data["type"] == "personality"
        mem_id = memory_data["id"]

        # Update Memory (tests bug fix where memory.metadata was changed to memory.meta_data)
        update_resp = await ac.put(
            f"/api/memory/{mem_id}",
            headers=headers,
            json={
                "content": "Updated deep focus in morning",
                "metadata": {"source": "manual_update"},
                "change_reason": "Refined pattern"
            }
        )
        assert update_resp.status_code == 200
        updated_data = update_resp.json()
        assert updated_data["content"] == "Updated deep focus in morning"

        # List Memories
        list_resp = await ac.get("/api/memory/", headers=headers)
        assert list_resp.status_code == 200
        assert len(list_resp.json()) >= 1

        # Delete Memory
        del_resp = await ac.delete(f"/api/memory/{mem_id}", headers=headers)
        assert del_resp.status_code == 200


@pytest.mark.asyncio
async def test_goals_and_habits():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        auth_resp = await ac.post("/api/auth/google", json={"token": "mock_google_token:goaltest@twinmind.ai"})
        token = auth_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create Goal
        goal_resp = await ac.post(
            "/api/goals",
            headers=headers,
            json={
                "title": "Master Distributed Systems",
                "goal_type": "short_term",
                "priority": "high",
                "category": "learning"
            }
        )
        assert goal_resp.status_code == 200
        goal_id = goal_resp.json()["id"]

        # Create Habit
        habit_resp = await ac.post(
            "/api/habits",
            headers=headers,
            json={
                "name": "Daily Code Review",
                "frequency": "daily",
                "target_count": 1
            }
        )
        assert habit_resp.status_code == 200
        habit_id = habit_resp.json()["id"]

        # Log Habit
        log_resp = await ac.post(
            f"/api/habits/{habit_id}/log",
            headers=headers,
            json={"notes": "Reviewed PR #42"}
        )
        assert log_resp.status_code == 200
        assert log_resp.json()["streak"] == 1


@pytest.mark.asyncio
async def test_predictions_and_dashboard():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        auth_resp = await ac.post("/api/auth/google", json={"token": "mock_google_token:dash@twinmind.ai"})
        token = auth_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Fetch Dashboard Data
        dash_resp = await ac.get("/api/predictions/dashboard", headers=headers)
        assert dash_resp.status_code == 200
        dash_data = dash_resp.json()
        assert "goals" in dash_data
        assert "habits" in dash_data
        assert "productivity" in dash_data
        assert "predictions" in dash_data
