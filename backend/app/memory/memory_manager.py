from typing import List, Dict, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.memory import Memory, MemoryEvolution
from app.models.user import User
from datetime import datetime
import json


class MemoryManager:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_memory(
        self,
        user_id: int,
        memory_type: str,
        content: str,
        metadata: Optional[Dict] = None,
        importance: int = 5
    ) -> Memory:
        memory = Memory(
            user_id=user_id,
            memory_type=memory_type,
            content=content,
            meta_data=metadata or {},
            importance=importance
        )
        self.db.add(memory)
        await self.db.commit()
        await self.db.refresh(memory)
        return memory

    async def get_memories(
        self,
        user_id: int,
        memory_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Memory]:
        query = select(Memory).where(Memory.user_id == user_id)
        if memory_type:
            query = query.where(Memory.memory_type == memory_type)
        query = query.order_by(Memory.importance.desc(), Memory.created_at.desc())
        query = query.limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_memory(
        self,
        memory_id: int,
        new_content: str,
        new_metadata: Optional[Dict] = None,
        change_reason: Optional[str] = None
    ) -> Memory:
        memory = await self.db.get(Memory, memory_id)
        if not memory:
            raise ValueError("Memory not found")
        
        old_value = {
            "content": memory.content,
            "metadata": memory.meta_data
        }
        
        memory.content = new_content
        if new_metadata:
            memory.meta_data = new_metadata
        
        # Track evolution
        evolution = MemoryEvolution(
            user_id=memory.user_id,
            old_value=old_value,
            new_value={"content": new_content, "metadata": new_metadata or {}},
            change_reason=change_reason
        )
        self.db.add(evolution)
        
        await self.db.commit()
        await self.db.refresh(memory)
        return memory

    async def delete_memory(self, memory_id: int) -> bool:
        memory = await self.db.get(Memory, memory_id)
        if not memory:
            return False
        await self.db.delete(memory)
        await self.db.commit()
        return True

    async def search_memories(
        self,
        user_id: int,
        query: str,
        limit: int = 20
    ) -> List[Memory]:
        # Simple text search - in production, use full-text search
        memories = await self.get_memories(user_id, limit=limit)
        results = [
            m for m in memories
            if query.lower() in m.content.lower()
        ]
        return results

    async def get_digital_dna(self, user_id: int) -> Dict[str, Any]:
        """Compile user's digital DNA from all memories"""
        memories = await self.get_memories(user_id)
        
        dna = {
            "personality": [],
            "goals": [],
            "habits": [],
            "preferences": [],
            "communication_style": [],
            "strengths": [],
            "weaknesses": []
        }
        
        for memory in memories:
            if memory.memory_type in dna:
                dna[memory.memory_type].append({
                    "content": memory.content,
                    "importance": memory.importance,
                    "metadata": memory.meta_data
                })
        
        return dna

    async def should_evolve(self, user_id: int) -> bool:
        """Check if memory should evolve (every 10 conversations)"""
        from app.models.memory import Conversation
        result = await self.db.execute(
            select(Conversation).where(Conversation.user_id == user_id)
        )
        conversations = result.scalars().all()
        return len(conversations) > 0 and len(conversations) % 10 == 0

    async def get_context_for_agent(
        self,
        user_id: int,
        max_memories: int = 20
    ) -> Dict[str, Any]:
        """Get relevant context for AI agent"""
        memories = await self.get_memories(user_id, limit=max_memories)
        
        context = {
            "recent_memories": [],
            "personality_traits": [],
            "current_goals": [],
            "active_habits": [],
            "preferences": []
        }
        
        for memory in memories:
            if memory.memory_type == "personality":
                context["personality_traits"].append(memory.content)
            elif memory.memory_type == "goal":
                context["current_goals"].append(memory.content)
            elif memory.memory_type == "habit":
                context["active_habits"].append(memory.content)
            elif memory.memory_type == "preference":
                context["preferences"].append(memory.content)
            
            context["recent_memories"].append({
                "type": memory.memory_type,
                "content": memory.content,
                "importance": memory.importance
            })
        
        return context
