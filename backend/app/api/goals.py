from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.goals import Goal, Habit, HabitLog
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

router = APIRouter()


class GoalRequest(BaseModel):
    title: str
    description: Optional[str] = None
    goal_type: str
    category: Optional[str] = None
    target_date: Optional[datetime] = None
    priority: str = "medium"
    metadata: Optional[dict] = None


class GoalUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    progress: Optional[float] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    metadata: Optional[dict] = None


class HabitRequest(BaseModel):
    name: str
    description: Optional[str] = None
    frequency: str
    target_count: int = 1
    metadata: Optional[dict] = None


class HabitLogRequest(BaseModel):
    notes: Optional[str] = None


@router.get("/goals")
async def get_goals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user goals"""
    result = await db.execute(
        select(Goal).where(Goal.user_id == current_user.id)
    )
    goals = result.scalars().all()
    
    return [
        {
            "id": g.id,
            "title": g.title,
            "description": g.description,
            "goal_type": g.goal_type,
            "category": g.category,
            "target_date": g.target_date.isoformat() if g.target_date else None,
            "progress": g.progress,
            "status": g.status,
            "priority": g.priority,
            "metadata": g.meta_data,
            "created_at": g.created_at.isoformat()
        }
        for g in goals
    ]


@router.post("/goals")
async def create_goal(
    request: GoalRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new goal"""
    goal = Goal(
        user_id=current_user.id,
        title=request.title,
        description=request.description,
        goal_type=request.goal_type,
        category=request.category,
        target_date=request.target_date,
        priority=request.priority,
        meta_data=request.metadata
    )
    db.add(goal)
    await db.commit()
    await db.refresh(goal)
    
    return {
        "id": goal.id,
        "title": goal.title,
        "message": "Goal created successfully"
    }


@router.put("/goals/{goal_id}")
async def update_goal(
    goal_id: int,
    request: GoalUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a goal"""
    result = await db.execute(
        select(Goal).where(
            Goal.id == goal_id,
            Goal.user_id == current_user.id
        )
    )
    goal = result.scalar_one_or_none()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    if request.title is not None:
        goal.title = request.title
    if request.description is not None:
        goal.description = request.description
    if request.progress is not None:
        goal.progress = request.progress
    if request.status is not None:
        goal.status = request.status
        if request.status == "completed":
            goal.completed_at = datetime.utcnow()
    if request.priority is not None:
        goal.priority = request.priority
    if request.metadata is not None:
        goal.meta_data = request.metadata
    
    await db.commit()
    await db.refresh(goal)
    
    return {"message": "Goal updated successfully"}


@router.delete("/goals/{goal_id}")
async def delete_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a goal"""
    result = await db.execute(
        select(Goal).where(
            Goal.id == goal_id,
            Goal.user_id == current_user.id
        )
    )
    goal = result.scalar_one_or_none()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    await db.delete(goal)
    await db.commit()
    
    return {"message": "Goal deleted successfully"}


@router.get("/habits")
async def get_habits(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user habits"""
    result = await db.execute(
        select(Habit).where(Habit.user_id == current_user.id)
    )
    habits = result.scalars().all()
    
    return [
        {
            "id": h.id,
            "name": h.name,
            "description": h.description,
            "frequency": h.frequency,
            "target_count": h.target_count,
            "current_streak": h.current_streak,
            "best_streak": h.best_streak,
            "status": h.status,
            "metadata": h.meta_data,
            "created_at": h.created_at.isoformat()
        }
        for h in habits
    ]


@router.post("/habits")
async def create_habit(
    request: HabitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new habit"""
    habit = Habit(
        user_id=current_user.id,
        name=request.name,
        description=request.description,
        frequency=request.frequency,
        target_count=request.target_count,
        meta_data=request.metadata
    )
    db.add(habit)
    await db.commit()
    await db.refresh(habit)
    
    return {
        "id": habit.id,
        "name": habit.name,
        "message": "Habit created successfully"
    }


@router.post("/habits/{habit_id}/log")
async def log_habit(
    habit_id: int,
    request: HabitLogRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Log habit completion"""
    result = await db.execute(
        select(Habit).where(
            Habit.id == habit_id,
            Habit.user_id == current_user.id
        )
    )
    habit = result.scalar_one_or_none()
    
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    # Create log
    log = HabitLog(
        habit_id=habit_id,
        user_id=current_user.id,
        notes=request.notes
    )
    db.add(log)
    
    # Update streak
    habit.current_streak += 1
    if habit.current_streak > habit.best_streak:
        habit.best_streak = habit.current_streak
    
    await db.commit()
    
    return {"message": "Habit logged successfully", "streak": habit.current_streak}


@router.get("/habits/{habit_id}/logs")
async def get_habit_logs(
    habit_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get habit logs"""
    result = await db.execute(
        select(HabitLog).where(
            HabitLog.habit_id == habit_id,
            HabitLog.user_id == current_user.id
        )
    )
    logs = result.scalars().all()
    
    return [
        {
            "id": l.id,
            "completed_at": l.completed_at.isoformat(),
            "notes": l.notes
        }
        for l in logs
    ]
