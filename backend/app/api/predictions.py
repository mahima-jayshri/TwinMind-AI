from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.prediction import Prediction, ProductivityMetric
from app.agent.gemini_client import GeminiClient
from app.memory.memory_manager import MemoryManager
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta

router = APIRouter()


class PredictionRequest(BaseModel):
    prediction_type: str
    task_description: Optional[str] = None


@router.post("/predict")
async def create_prediction(
    request: PredictionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate prediction based on user behavior"""
    memory_manager = MemoryManager(db)
    gemini_client = GeminiClient()
    
    # Get user context
    context = await memory_manager.get_context_for_agent(current_user.id)
    
    # Get recent productivity data
    result = await db.execute(
        select(ProductivityMetric).where(
            ProductivityMetric.user_id == current_user.id
        ).order_by(ProductivityMetric.date.desc()).limit(7)
    )
    recent_metrics = result.scalars().all()
    
    # Build prediction prompt
    if request.prediction_type == "task_completion":
        prompt = f"""Based on the user's behavior and productivity data:
        {context}
        Recent productivity: {[m.tasks_completed for m in recent_metrics]}
        
        Task: {request.task_description}
        
        Predict the likelihood (0-100%) of completing this task today.
        Also provide key factors influencing this prediction.
        Return as JSON with keys: confidence_score, factors (array)"""
    
    elif request.prediction_type == "procrastination":
        prompt = f"""Based on the user's behavior:
        {context}
        
        Predict the likelihood (0-100%) of procrastination today.
        Return as JSON with keys: confidence_score, factors (array)"""
    
    elif request.prediction_type == "productivity":
        prompt = f"""Based on the user's behavior and recent productivity:
        {context}
        Recent metrics: {[m.tasks_completed for m in recent_metrics]}
        
        Predict today's productivity level (0-100).
        Return as JSON with keys: confidence_score, factors (array)"""
    
    else:
        return {"error": "Invalid prediction type"}
    
    try:
        response = await gemini_client.generate_response(prompt, context)
        
        # Parse response (simplified)
        confidence_score = 75  # Default fallback
        factors = ["Based on historical patterns"]
        
        # Try to extract numbers from response
        import re
        scores = re.findall(r'\d+', response)
        if scores:
            confidence_score = int(scores[0])
        
        # Store prediction
        prediction = Prediction(
            user_id=current_user.id,
            prediction_type=request.prediction_type,
            confidence_score=confidence_score,
            prediction_data={"response": response},
            factors=factors
        )
        db.add(prediction)
        await db.commit()
        
        return {
            "prediction_type": request.prediction_type,
            "confidence_score": confidence_score,
            "factors": factors,
            "analysis": response
        }
    
    except Exception as e:
        return {
            "prediction_type": request.prediction_type,
            "confidence_score": 50,
            "factors": ["Unable to analyze"],
            "error": str(e)
        }


@router.get("/predictions")
async def get_predictions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get recent predictions"""
    result = await db.execute(
        select(Prediction).where(
            Prediction.user_id == current_user.id
        ).order_by(Prediction.created_at.desc()).limit(10)
    )
    predictions = result.scalars().all()
    
    return [
        {
            "id": p.id,
            "prediction_type": p.prediction_type,
            "confidence_score": p.confidence_score,
            "prediction_data": p.prediction_data,
            "factors": p.factors,
            "created_at": p.created_at.isoformat()
        }
        for p in predictions
    ]


@router.post("/productivity")
async def log_productivity(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Log daily productivity metrics"""
    metric = ProductivityMetric(
        user_id=current_user.id,
        date=datetime.utcnow(),
        tasks_completed=data.get("tasks_completed", 0),
        tasks_planned=data.get("tasks_planned", 0),
        focus_hours=data.get("focus_hours", 0.0),
        distraction_count=data.get("distraction_count", 0),
        mood=data.get("mood"),
        energy_level=data.get("energy_level"),
        meta_data=data.get("metadata", {})
    )
    db.add(metric)
    await db.commit()
    
    return {"message": "Productivity logged successfully"}


@router.get("/productivity")
async def get_productivity(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get productivity metrics"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    result = await db.execute(
        select(ProductivityMetric).where(
            ProductivityMetric.user_id == current_user.id,
            ProductivityMetric.date >= start_date
        ).order_by(ProductivityMetric.date.asc())
    )
    metrics = result.scalars().all()
    
    return [
        {
            "date": m.date.isoformat(),
            "tasks_completed": m.tasks_completed,
            "tasks_planned": m.tasks_planned,
            "focus_hours": m.focus_hours,
            "distraction_count": m.distraction_count,
            "mood": m.mood,
            "energy_level": m.energy_level
        }
        for m in metrics
    ]


@router.get("/dashboard")
async def get_dashboard_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive dashboard data"""
    from app.models.goals import Goal, Habit
    from app.models.memory import Memory
    
    # Get goals
    goals_result = await db.execute(
        select(Goal).where(Goal.user_id == current_user.id)
    )
    goals = goals_result.scalars().all()
    
    # Get habits
    habits_result = await db.execute(
        select(Habit).where(Habit.user_id == current_user.id)
    )
    habits = habits_result.scalars().all()
    
    # Get recent memories
    memory_manager = MemoryManager(db)
    memories = await memory_manager.get_memories(current_user.id, limit=10)
    
    # Get digital DNA
    digital_dna = await memory_manager.get_digital_dna(current_user.id)
    
    # Get recent productivity
    productivity_result = await db.execute(
        select(ProductivityMetric).where(
            ProductivityMetric.user_id == current_user.id
        ).order_by(ProductivityMetric.date.desc()).limit(7)
    )
    productivity = productivity_result.scalars().all()
    
    # Calculate weekly progress
    total_tasks = sum(m.tasks_completed for m in productivity)
    avg_focus = sum(m.focus_hours for m in productivity) / len(productivity) if productivity else 0
    
    return {
        "digital_dna": digital_dna,
        "goals": {
            "total": len(goals),
            "active": len([g for g in goals if g.status == "active"]),
            "completed": len([g for g in goals if g.status == "completed"]),
            "items": [
                {
                    "id": g.id,
                    "title": g.title,
                    "progress": g.progress,
                    "status": g.status
                }
                for g in goals[:5]
            ]
        },
        "habits": {
            "total": len(habits),
            "active": len([h for h in habits if h.status == "active"]),
            "items": [
                {
                    "id": h.id,
                    "name": h.name,
                    "current_streak": h.current_streak,
                    "best_streak": h.best_streak
                }
                for h in habits[:5]
            ]
        },
        "memories": [
            {
                "id": m.id,
                "type": m.memory_type,
                "content": m.content[:100] + "..." if len(m.content) > 100 else m.content,
                "created_at": m.created_at.isoformat()
            }
            for m in memories
        ],
        "productivity": {
            "weekly_tasks_completed": total_tasks,
            "avg_focus_hours": round(avg_focus, 2),
            "recent_metrics": [
                {
                    "date": m.date.isoformat(),
                    "tasks_completed": m.tasks_completed,
                    "focus_hours": m.focus_hours
                }
                for m in productivity
            ]
        },
        "user": {
            "name": current_user.name,
            "preferred_mode": current_user.preferred_mode,
            "is_onboarded": current_user.is_onboarded
        }
    }
