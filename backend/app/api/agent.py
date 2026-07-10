from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.agent.twinmind_agent import TwinMindAgent
from app.api.auth import get_current_user
from app.models.user import User
from pydantic import BaseModel
from typing import Optional, List, Dict

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    mode: str = "mentor"
    conversation_history: Optional[List[Dict]] = None


class ChatResponse(BaseModel):
    response: str
    needs_evolution: bool
    mode: str


class OnboardingRequest(BaseModel):
    answer: Optional[str] = None


class ActionRequest(BaseModel):
    action: str
    params: Dict


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Chat with the AI agent"""
    agent = TwinMindAgent(db)
    
    result = await agent.process_message(
        user_id=current_user.id,
        message=request.message,
        mode=request.mode,
        conversation_history=request.conversation_history
    )
    
    return ChatResponse(**result)


@router.post("/onboarding")
async def onboarding(
    request: OnboardingRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Conduct onboarding interview"""
    agent = TwinMindAgent(db)
    
    result = await agent.conduct_onboarding(
        user_id=current_user.id,
        current_step=current_user.onboarding_step,
        user_answer=request.answer
    )
    
    # Update user onboarding step
    if "step" in result:
        current_user.onboarding_step = result["step"]
        await db.commit()
    
    # Mark onboarding as complete
    if result.get("completed"):
        current_user.is_onboarded = True
        current_user.digital_dna = result.get("digital_dna")
        await db.commit()
    
    return result


@router.post("/action")
async def perform_action(
    request: ActionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Perform agent action"""
    agent = TwinMindAgent(db)
    
    result = await agent.perform_action(
        user_id=current_user.id,
        action=request.action,
        params=request.params
    )
    
    return result


@router.post("/evolve")
async def evolve_memory(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Trigger memory evolution"""
    from app.memory.memory_manager import MemoryManager
    
    memory_manager = MemoryManager(db)
    context = await memory_manager.get_context_for_agent(current_user.id)
    
    agent = TwinMindAgent(db)
    response = await agent.process_message(
        user_id=current_user.id,
        message="Update my profile based on our conversation",
        mode="mentor",
        conversation_history=[]
    )
    
    return response
