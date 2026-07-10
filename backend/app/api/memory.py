from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.memory.memory_manager import MemoryManager
from app.api.auth import get_current_user
from app.models.user import User
from pydantic import BaseModel
from typing import Optional, List, Dict

router = APIRouter()


class MemoryRequest(BaseModel):
    memory_type: str
    content: str
    metadata: Optional[Dict] = None
    importance: int = 5


class MemoryUpdateRequest(BaseModel):
    content: str
    metadata: Optional[Dict] = None
    change_reason: Optional[str] = None


@router.get("/")
async def get_memories(
    memory_type: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user memories"""
    memory_manager = MemoryManager(db)
    memories = await memory_manager.get_memories(
        user_id=current_user.id,
        memory_type=memory_type,
        limit=limit
    )
    
    return [
        {
            "id": m.id,
            "type": m.memory_type,
            "content": m.content,
            "metadata": m.meta_data,
            "importance": m.importance,
            "created_at": m.created_at.isoformat()
        }
        for m in memories
    ]


@router.post("/")
async def add_memory(
    request: MemoryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a new memory"""
    memory_manager = MemoryManager(db)
    memory = await memory_manager.add_memory(
        user_id=current_user.id,
        memory_type=request.memory_type,
        content=request.content,
        metadata=request.metadata,
        importance=request.importance
    )
    
    return {
        "id": memory.id,
        "type": memory.memory_type,
        "content": memory.content,
        "metadata": memory.meta_data,
        "importance": memory.importance,
        "created_at": memory.created_at.isoformat()
    }


@router.put("/{memory_id}")
async def update_memory(
    memory_id: int,
    request: MemoryUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a memory"""
    memory_manager = MemoryManager(db)
    
    try:
        memory = await memory_manager.update_memory(
            memory_id=memory_id,
            new_content=request.content,
            new_metadata=request.metadata,
            change_reason=request.change_reason
        )
        
        return {
            "id": memory.id,
            "type": memory.memory_type,
            "content": memory.content,
            "metadata": memory.metadata,
            "importance": memory.importance,
            "updated_at": memory.updated_at.isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{memory_id}")
async def delete_memory(
    memory_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a memory"""
    memory_manager = MemoryManager(db)
    success = await memory_manager.delete_memory(memory_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    return {"message": "Memory deleted successfully"}


@router.get("/digital-dna")
async def get_digital_dna(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's Digital DNA"""
    memory_manager = MemoryManager(db)
    dna = await memory_manager.get_digital_dna(current_user.id)
    
    return dna


@router.get("/search")
async def search_memories(
    query: str,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Search memories"""
    memory_manager = MemoryManager(db)
    memories = await memory_manager.search_memories(
        user_id=current_user.id,
        query=query,
        limit=limit
    )
    
    return [
        {
            "id": m.id,
            "type": m.memory_type,
            "content": m.content,
            "metadata": m.meta_data,
            "importance": m.importance,
            "created_at": m.created_at.isoformat()
        }
        for m in memories
    ]
