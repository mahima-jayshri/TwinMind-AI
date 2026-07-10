from typing import Dict, Any, Optional, List
from app.agent.gemini_client import GeminiClient
from app.memory.memory_manager import MemoryManager
from sqlalchemy.ext.asyncio import AsyncSession


class TwinMindAgent:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.memory_manager = MemoryManager(db)
        self.gemini_client = GeminiClient()

    async def process_message(
        self,
        user_id: int,
        message: str,
        mode: str = "mentor",
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Process user message and generate response"""
        
        # Get user context
        context = await self.memory_manager.get_context_for_agent(user_id)
        
        # Check if memory evolution is needed
        should_evolve = await self.memory_manager.should_evolve(user_id)
        if should_evolve:
            evolution_prompt = self._build_evolution_prompt(context)
            evolution_response = await self.gemini_client.generate_response(evolution_prompt, context)
            
            # Save a conversation entry to advance the count and avoid infinite evolution loops
            from app.models.memory import Conversation
            conversation = Conversation(
                user_id=user_id,
                mode=mode,
                messages=[
                    {"role": "system", "content": "Memory evolution triggered"},
                    {"role": "assistant", "content": evolution_response}
                ]
            )
            self.db.add(conversation)
            await self.db.commit()
            
            return {
                "response": evolution_response,
                "needs_evolution": True,
                "mode": mode
            }
        
        # Generate response
        response = await self.gemini_client.chat(
            message=message,
            conversation_history=conversation_history or [],
            context=context,
            mode=mode
        )
        
        # Store conversation memory
        await self.memory_manager.add_memory(
            user_id=user_id,
            memory_type="conversation",
            content=f"User: {message}\nAgent: {response}",
            metadata={"mode": mode},
            importance=3
        )
        
        # Also store in conversations table to trigger memory evolution count correctly
        from app.models.memory import Conversation
        conversation = Conversation(
            user_id=user_id,
            mode=mode,
            messages=[
                {"role": "user", "content": message},
                {"role": "assistant", "content": response}
            ]
        )
        self.db.add(conversation)
        await self.db.commit()
        
        return {
            "response": response,
            "needs_evolution": False,
            "mode": mode
        }

    async def conduct_onboarding(
        self,
        user_id: int,
        current_step: int,
        user_answer: Optional[str] = None
    ) -> Dict[str, Any]:
        """Conduct onboarding interview"""
        
        questions = self._get_onboarding_questions()
        
        if user_answer and current_step > 0:
            # Store answer
            question = questions[current_step - 1]
            await self.memory_manager.add_memory(
                user_id=user_id,
                memory_type=question["memory_type"],
                content=user_answer,
                metadata={"question": question["question"]},
                importance=question.get("importance", 5)
            )
            
        if current_step >= len(questions):
            # Generate Digital DNA
            return await self._generate_digital_dna(user_id)
        
        # Get next question
        next_question = questions[current_step]
        
        return {
            "question": next_question["question"],
            "question_type": next_question.get("type", "text"),
            "options": next_question.get("options"),
            "step": current_step + 1,
            "total_steps": len(questions),
            "progress": (current_step / len(questions)) * 100
        }

    async def _generate_digital_dna(self, user_id: int) -> Dict[str, Any]:
        """Generate Digital DNA profile from onboarding answers"""
        memories = await self.memory_manager.get_memories(user_id)
        
        dna_prompt = self._build_dna_prompt(memories)
        dna_response = await self.gemini_client.generate_response(dna_prompt)
        
        # Parse and store DNA
        digital_dna = self._parse_dna_response(dna_response)
        
        # Store as high-importance memory
        await self.memory_manager.add_memory(
            user_id=user_id,
            memory_type="digital_dna",
            content="Digital DNA Profile Generated",
            metadata=digital_dna,
            importance=10
        )
        
        return {
            "completed": True,
            "digital_dna": digital_dna
        }

    async def perform_action(
        self,
        user_id: int,
        action: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform agent actions"""
        
        context = await self.memory_manager.get_context_for_agent(user_id)
        
        action_prompts = {
            "create_study_plan": f"Create a detailed study plan based on: {params}",
            "create_weekly_goals": f"Create weekly goals based on: {params}",
            "track_habits": f"Analyze habit tracking data: {params}",
            "review_resume": f"Review and provide feedback on resume: {params}",
            "mock_interview": f"Conduct mock interview for: {params}",
            "summarize_pdf": f"Summarize PDF content: {params}",
            "recommend_resources": f"Recommend learning resources for: {params}",
            "generate_reminders": f"Generate reminders for: {params}"
        }
        
        prompt = action_prompts.get(action, f"Help with: {params}")
        response = await self.gemini_client.generate_response(prompt, context)
        
        return {
            "action": action,
            "result": response
        }

    def _get_onboarding_questions(self) -> List[Dict[str, Any]]:
        """Get onboarding questions"""
        return [
            {
                "question": "What's your name?",
                "type": "text",
                "memory_type": "personality",
                "importance": 10
            },
            {
                "question": "What's your age?",
                "type": "number",
                "memory_type": "personality",
                "importance": 5
            },
            {
                "question": "What's your current career or field of study?",
                "type": "text",
                "memory_type": "personality",
                "importance": 8
            },
            {
                "question": "What's your biggest career goal?",
                "type": "text",
                "memory_type": "goal",
                "importance": 10
            },
            {
                "question": "What's your dream company to work for?",
                "type": "text",
                "memory_type": "goal",
                "importance": 8
            },
            {
                "question": "What do you consider your biggest strength?",
                "type": "text",
                "memory_type": "personality",
                "importance": 9
            },
            {
                "question": "What's your biggest weakness that you're working on?",
                "type": "text",
                "memory_type": "personality",
                "importance": 9
            },
            {
                "question": "What language do you prefer for communication?",
                "type": "select",
                "options": ["English", "Spanish", "French", "German", "Other"],
                "memory_type": "preference",
                "importance": 7
            },
            {
                "question": "What tone do you prefer when receiving advice?",
                "type": "select",
                "options": ["Professional", "Casual", "Direct", "Empathetic"],
                "memory_type": "preference",
                "importance": 7
            },
            {
                "question": "Are you more of an introvert or extrovert?",
                "type": "select",
                "options": ["Introvert", "Extrovert", "Ambivert"],
                "memory_type": "personality",
                "importance": 8
            },
            {
                "question": "How do you prefer to learn new things?",
                "type": "select",
                "options": ["Reading", "Videos", "Hands-on", "Discussion", "Mixed"],
                "memory_type": "preference",
                "importance": 8
            },
            {
                "question": "What are your main hobbies or interests?",
                "type": "text",
                "memory_type": "personality",
                "importance": 7
            },
            {
                "question": "What's your biggest fear or anxiety?",
                "type": "text",
                "memory_type": "personality",
                "importance": 8
            },
            {
                "question": "What time do you usually go to sleep?",
                "type": "time",
                "memory_type": "habit",
                "importance": 6
            },
            {
                "question": "What time do you usually wake up?",
                "type": "time",
                "memory_type": "habit",
                "importance": 6
            },
            {
                "question": "What motivates you the most?",
                "type": "select",
                "options": ["Achievement", "Growth", "Recognition", "Impact", "Money"],
                "memory_type": "personality",
                "importance": 9
            },
            {
                "question": "What's your biggest distraction?",
                "type": "text",
                "memory_type": "habit",
                "importance": 7
            },
            {
                "question": "What's your short-term goal (next 3 months)?",
                "type": "text",
                "memory_type": "goal",
                "importance": 9
            },
            {
                "question": "What's your long-term goal (next 5 years)?",
                "type": "text",
                "memory_type": "goal",
                "importance": 10
            }
        ]

    def _build_evolution_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for memory evolution check"""
        return f"""Based on the user's current context:
{context}

Ask: "Have your goals or priorities changed recently? If so, what's different?"

Be conversational and natural. This is asked every 10 conversations to ensure the AI stays updated."""

    def _build_dna_prompt(self, memories: List) -> str:
        """Build prompt for Digital DNA generation"""
        memory_text = "\n".join([f"{m.memory_type}: {m.content}" for m in memories])
        
        return f"""Based on these onboarding answers:
{memory_text}

Generate a comprehensive Digital DNA Profile in JSON format with these sections:
- personality_type
- learning_style
- communication_style
- strengths (array)
- weaknesses (array)
- goals (array with short_term and long_term)
- habits (array)
- motivation_type
- decision_making_style
- productivity_pattern

Return only valid JSON."""

    def _parse_dna_response(self, response: str) -> Dict[str, Any]:
        """Parse DNA response from Gemini"""
        import json
        try:
            # Try to extract JSON from response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end != -1:
                json_str = response[start:end]
                return json.loads(json_str)
        except:
            pass
        
        # Fallback if parsing fails
        return {
            "personality_type": "analytical",
            "learning_style": "mixed",
            "communication_style": "professional",
            "strengths": ["determined", "focused"],
            "weaknesses": ["procrastination"],
            "goals": {"short_term": [], "long_term": []},
            "habits": [],
            "motivation_type": "growth",
            "decision_making_style": "analytical",
            "productivity_pattern": "variable"
        }
