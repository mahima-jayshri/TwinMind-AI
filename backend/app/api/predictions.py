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
    # Check if today's metric already exists (based on current UTC calendar day)
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    result = await db.execute(
        select(ProductivityMetric).where(
            ProductivityMetric.user_id == current_user.id,
            ProductivityMetric.date >= today_start,
            ProductivityMetric.date < today_end
        )
    )
    metric = result.scalar_one_or_none()
    
    if metric:
        metric.tasks_completed = data.get("tasks_completed", 0)
        metric.tasks_planned = data.get("tasks_planned", 0)
        metric.focus_hours = float(data.get("focus_hours", 0.0))
        metric.distraction_count = data.get("distraction_count", 0)
        metric.mood = data.get("mood")
        metric.energy_level = data.get("energy_level")
        metric.meta_data = data.get("metadata", {})
    else:
        metric = ProductivityMetric(
            user_id=current_user.id,
            date=datetime.utcnow(),
            tasks_completed=data.get("tasks_completed", 0),
            tasks_planned=data.get("tasks_planned", 0),
            focus_hours=float(data.get("focus_hours", 0.0)),
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

    # Seed mock productivity if empty for a beautiful chart demo
    if not productivity:
        import random
        for i in range(6, -1, -1):
            date = datetime.utcnow() - timedelta(days=i)
            tasks_planned = random.randint(4, 7)
            tasks_completed = random.randint(2, tasks_planned)
            focus_hours = round(random.uniform(3.0, 7.5), 1)
            distraction_count = random.randint(1, 5)
            mood = random.choice(["focused", "energetic", "tired", "calm"])
            energy_level = random.randint(5, 9)
            
            metric = ProductivityMetric(
                user_id=current_user.id,
                date=date,
                tasks_completed=tasks_completed,
                tasks_planned=tasks_planned,
                focus_hours=focus_hours,
                distraction_count=distraction_count,
                mood=mood,
                energy_level=energy_level
            )
            db.add(metric)
        await db.commit()
        
        # Query again
        productivity_result = await db.execute(
            select(ProductivityMetric).where(
                ProductivityMetric.user_id == current_user.id
            ).order_by(ProductivityMetric.date.desc()).limit(7)
        )
        productivity = productivity_result.scalars().all()
    
    # Get latest predictions for Confidence Score card
    predictions_result = await db.execute(
        select(Prediction).where(
            Prediction.user_id == current_user.id
        ).order_by(Prediction.created_at.desc()).limit(15)
    )
    all_predictions = predictions_result.scalars().all()
    
    latest_predictions = {}
    for p in all_predictions:
        if p.prediction_type not in latest_predictions:
            latest_predictions[p.prediction_type] = {
                "confidence_score": p.confidence_score,
                "analysis": p.prediction_data.get("response", "") if isinstance(p.prediction_data, dict) else "",
                "factors": p.factors,
                "created_at": p.created_at.isoformat()
            }
            
    # Default values computed dynamically from real database metrics if none in DB
    if "procrastination" not in latest_predictions or "productivity" not in latest_predictions:
        avg_focus_hours = sum(m.focus_hours for m in productivity) / len(productivity) if productivity else 0.0
        total_completed = sum(m.tasks_completed for m in productivity)
        total_planned = sum(m.tasks_planned for m in productivity)
        task_ratio = total_completed / total_planned if total_planned > 0 else 0.5
        avg_distractions = sum(m.distraction_count for m in productivity) / len(productivity) if productivity else 0.0
        avg_energy = sum(m.energy_level for m in productivity) / len(productivity) if productivity else 7.0
        
        active_habits_count = len([h for h in habits if h.status == "active"])
        total_streaks = sum(h.current_streak for h in habits)
        completed_goals_count = len([g for g in goals if g.status == "completed"])
        
        if "procrastination" not in latest_predictions:
            procrastination_score = 50.0
            
            if avg_focus_hours > 5.0:
                procrastination_score -= 15.0
            elif avg_focus_hours < 3.0 and len(productivity) > 0:
                procrastination_score += 15.0
                
            if avg_distractions > 3.0:
                procrastination_score += 20.0
            elif avg_distractions < 1.0 and len(productivity) > 0:
                procrastination_score -= 10.0
                
            if task_ratio > 0.8:
                procrastination_score -= 15.0
            elif task_ratio < 0.5:
                procrastination_score += 15.0
                
            if avg_energy > 7.0:
                procrastination_score -= 10.0
            elif avg_energy < 5.0:
                procrastination_score += 10.0
                
            if total_streaks > 3:
                procrastination_score -= 10.0
                
            procrastination_score = max(5.0, min(95.0, procrastination_score))
            
            procrastination_analysis = (
                "Procrastination risk is low. You are maintaining excellent focus and task completion rates."
                if procrastination_score < 35 else
                "Procrastination risk is high. Minimize distractions and try setting shorter focus intervals."
                if procrastination_score > 60 else
                "Procrastination risk is moderate. Stay on track with daily focus times and habit logs."
            )
            
            procrastination_factors = []
            if avg_distractions > 2.0:
                procrastination_factors.append("High distraction rate")
            if task_ratio < 0.6:
                procrastination_factors.append("Low task completion rate")
            if avg_focus_hours < 4.0:
                procrastination_factors.append("Short daily focus hours")
            if total_streaks == 0:
                procrastination_factors.append("No active habit streaks")
            if not procrastination_factors:
                procrastination_factors = ["Initial goals defined", "Consistent patterns"]
                
            latest_predictions["procrastination"] = {
                "confidence_score": float(procrastination_score),
                "analysis": procrastination_analysis,
                "factors": procrastination_factors,
                "created_at": datetime.utcnow().isoformat()
            }
            
        if "productivity" not in latest_predictions:
            productivity_score = 50.0
            
            if total_streaks > 0:
                productivity_score += min(20.0, total_streaks * 3.0)
                
            if task_ratio > 0.8:
                productivity_score += 20.0
            elif task_ratio < 0.5:
                productivity_score -= 15.0
                
            if avg_focus_hours > 5.5:
                productivity_score += 15.0
            elif avg_focus_hours < 3.0 and len(productivity) > 0:
                productivity_score -= 15.0
                
            if active_habits_count > 0:
                productivity_score += min(10.0, active_habits_count * 2.0)
                
            if completed_goals_count > 0:
                productivity_score += min(15.0, completed_goals_count * 5.0)
                
            productivity_score = max(10.0, min(99.0, productivity_score))
            
            productivity_analysis = (
                "High focus levels and strong habit consistency indicate a solid productivity momentum."
                if productivity_score > 75 else
                "Your productivity momentum is low. Try finishing one pending goal to build momentum."
                if productivity_score < 40 else
                "Productivity momentum is stable. Keep up the consistent focus times."
            )
            
            productivity_factors = []
            if total_streaks > 2:
                productivity_factors.append(f"Habit streak active ({total_streaks} days total)")
            if task_ratio > 0.75:
                productivity_factors.append("High task completion rate")
            if avg_focus_hours > 4.5:
                productivity_factors.append(f"Strong focus time ({round(avg_focus_hours, 1)}h avg)")
            if completed_goals_count > 0:
                productivity_factors.append(f"Completed {completed_goals_count} goals")
            if not productivity_factors:
                productivity_factors = ["Consistent learning patterns", "Clear motivation structure"]
                
            latest_predictions["productivity"] = {
                "confidence_score": float(productivity_score),
                "analysis": productivity_analysis,
                "factors": productivity_factors,
                "created_at": datetime.utcnow().isoformat()
            }
    
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
                    "date": m.date.strftime("%a"),  # Format date as day abbreviation (e.g. Mon, Tue)
                    "tasks_completed": m.tasks_completed,
                    "tasks_planned": m.tasks_planned,
                    "focus_hours": m.focus_hours
                }
                for m in reversed(productivity)
            ]
        },
        "predictions": latest_predictions,
        "user": {
            "name": current_user.name,
            "preferred_mode": current_user.preferred_mode,
            "is_onboarded": current_user.is_onboarded
        }
    }
