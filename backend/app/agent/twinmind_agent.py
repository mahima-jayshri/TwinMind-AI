from typing import Dict, Any, Optional, List
from app.agent.gemini_client import GeminiClient
from app.memory.memory_manager import MemoryManager
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime



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
        
        # Check and update goals/habits from message
        await self._check_and_update_goals_habits(user_id, message)
        
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
        
        # Get user preferred language
        from app.models.user import User
        from sqlalchemy import select
        user_result = await self.db.execute(select(User).where(User.id == user_id))
        db_user = user_result.scalar_one_or_none()
        preferred_language = db_user.preferred_language if db_user else "english"

        # Generate response
        response = await self.gemini_client.chat(
            message=message,
            conversation_history=conversation_history or [],
            context=context,
            mode=mode,
            preferred_language=preferred_language
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
        
        # Initialize goals and habits in database tables
        from app.models.goals import Goal, Habit
        try:
            # Add goals
            goals_data = digital_dna.get("goals", {})
            if isinstance(goals_data, dict):
                for term, titles in goals_data.items():
                    goal_type = "short_term" if "short" in term else "long_term"
                    for title in titles:
                        g = Goal(
                            user_id=user_id,
                            title=title,
                            goal_type=goal_type,
                            category="career",
                            progress=0.0,
                            status="active"
                        )
                        self.db.add(g)
            elif isinstance(goals_data, list):
                for title in goals_data:
                    g = Goal(
                        user_id=user_id,
                        title=title,
                        goal_type="short_term",
                        category="career",
                        progress=0.0,
                        status="active"
                    )
                    self.db.add(g)

            # Add habits
            habits_data = digital_dna.get("habits", [])
            if isinstance(habits_data, list):
                for habit_name in habits_data:
                    h = Habit(
                        user_id=user_id,
                        name=habit_name,
                        frequency="daily",
                        status="active"
                    )
                    self.db.add(h)
            
            await self.db.commit()
        except Exception as e:
            print("Error initializing goals/habits in database:", e)
        
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
        """Parse DNA response from Gemini with markdown codeblock support"""
        import json
        import re

        clean_response = response.strip()
        # Remove ```json ... ``` blocks if present
        if "```" in clean_response:
            matches = re.findall(r"```(?:json)?\s*([\s\S]*?)\s*```", clean_response)
            if matches:
                clean_response = matches[0].strip()

        try:
            start = clean_response.find("{")
            end = clean_response.rfind("}") + 1
            if start != -1 and end != -1:
                json_str = clean_response[start:end]
                return json.loads(json_str)
        except Exception:
            pass
        
        # Fallback if parsing fails
        return {
            "personality_type": "Architect (Strategic & Driven)",
            "learning_style": "Hands-on & Conceptual",
            "communication_style": "Direct & Goal-Oriented",
            "strengths": ["Deep Focus", "Systematic Thinking", "Continuous Growth"],
            "weaknesses": ["Occasional Over-analysis", "Context Switching"],
            "goals": {
                "short_term": ["Master core technologies", "Build daily deep work routine"],
                "long_term": ["Lead high-impact engineering projects", "Achieve creative autonomy"]
            },
            "habits": ["Morning Planning", "90-minute Deep Work Block", "Evening Reflection"],
            "motivation_type": "Mastery & High Impact",
            "decision_making_style": "Data-Informed & Strategic",
            "productivity_pattern": "Peak Morning Focus"
        }

    async def _check_and_update_goals_habits(self, user_id: int, message: str) -> None:
        """Analyze if user wants to update goals/habits via natural language and execute the changes"""
        # Fast-path: Casual greetings and small talk do not update goals or habits
        if self.gemini_client._detect_intent(message) == "casual_greeting":
            return

        from app.models.goals import Goal, Habit, HabitLog
        from sqlalchemy import select
        import json

        try:
            # 1. Fetch current goals and habits for reference in matching
            goals_result = await self.db.execute(
                select(Goal).where(Goal.user_id == user_id)
            )
            goals = goals_result.scalars().all()

            habits_result = await self.db.execute(
                select(Habit).where(Habit.user_id == user_id)
            )
            habits = habits_result.scalars().all()

            # 2. Call Gemini to parse the user request
            prompt = f"""You are TwinMind AI's backend coordinator. Analyze this user chat message: "{message}"
Current User Goals:
{[{"id": g.id, "title": g.title, "status": g.status, "progress": g.progress} for g in goals]}
Current User Habits:
{[{"id": h.id, "name": h.name, "status": h.status, "current_streak": h.current_streak} for h in habits]}

Does the user want to perform one of the following operations on their goals or habits?
Operations:
- "create_goal" (wants to add a new goal)
- "update_goal" (wants to change progress, complete, or update an existing goal)
- "delete_goal" (wants to delete or remove a goal)
- "create_habit" (wants to add a new habit to track)
- "delete_habit" (wants to delete or remove a habit)
- "log_habit" (completed or logged their habit)
- "none" (none of the above/normal chat)

Choose the single best matching operation. If the message matches an action, return a JSON object with this exact structure:
{{
    "action": "create_goal" | "update_goal" | "delete_goal" | "create_habit" | "delete_habit" | "log_habit" | "none",
    "details": {{
        "id": integer_id_of_existing_goal_or_habit_or_null,
        "title": "exact title of goal or habit (if creating or searching)",
        "progress": number_0_to_100_or_null,
        "status": "active" | "completed" | "paused" | null,
        "priority": "low" | "medium" | "high" | null,
        "frequency": "daily" | "weekly" | null
    }}
}}
If the user refers to an existing goal/habit, select the correct id from the lists. Return ONLY valid JSON, no other text."""

            response = await self.gemini_client.generate_response(prompt)
            # Clean response text to extract json
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end != -1:
                data = json.loads(response[start:end])
                action = data.get("action", "none")
                details = data.get("details", {})
                
                if action == "none":
                    return

                if action == "create_goal" and details.get("title"):
                    # Create Goal
                    g = Goal(
                        user_id=user_id,
                        title=details.get("title"),
                        goal_type=details.get("goal_type") or "short_term",
                        category=details.get("category") or "personal",
                        priority=details.get("priority") or "medium",
                        progress=0.0,
                        status="active"
                    )
                    self.db.add(g)
                    await self.db.commit()

                elif action == "update_goal":
                    goal_id = details.get("id")
                    title = details.get("title")
                    
                    goal = None
                    if goal_id:
                        goal = await self.db.get(Goal, goal_id)
                    elif title:
                        # Try case-insensitive matching
                        for g in goals:
                            if title.lower() in g.title.lower():
                                goal = g
                                break
                    
                    if goal:
                        if details.get("progress") is not None:
                            goal.progress = float(details.get("progress"))
                        if details.get("status") is not None:
                            goal.status = details.get("status")
                            if goal.status == "completed":
                                goal.progress = 100.0
                                goal.completed_at = datetime.utcnow()
                        if details.get("priority") is not None:
                            goal.priority = details.get("priority")
                        await self.db.commit()

                elif action == "delete_goal":
                    goal_id = details.get("id")
                    title = details.get("title")
                    
                    goal = None
                    if goal_id:
                        goal = await self.db.get(Goal, goal_id)
                    elif title:
                        for g in goals:
                            if title.lower() in g.title.lower():
                                goal = g
                                break
                    
                    if goal:
                        await self.db.delete(goal)
                        await self.db.commit()

                elif action == "create_habit" and details.get("title"):
                    h = Habit(
                        user_id=user_id,
                        name=details.get("title"),
                        frequency=details.get("frequency") or "daily",
                        status="active"
                    )
                    self.db.add(h)
                    await self.db.commit()

                elif action == "delete_habit":
                    habit_id = details.get("id")
                    title = details.get("title")
                    
                    habit = None
                    if habit_id:
                        habit = await self.db.get(Habit, habit_id)
                    elif title:
                        for h in habits:
                            if title.lower() in h.name.lower():
                                habit = h
                                break
                    
                    if habit:
                        # Also delete logs
                        logs_result = await self.db.execute(
                            select(HabitLog).where(HabitLog.habit_id == habit.id)
                        )
                        for log in logs_result.scalars().all():
                            await self.db.delete(log)
                        await self.db.delete(habit)
                        await self.db.commit()

                elif action == "log_habit":
                    habit_id = details.get("id")
                    title = details.get("title")
                    
                    habit = None
                    if habit_id:
                        habit = await self.db.get(Habit, habit_id)
                    elif title:
                        for h in habits:
                            if title.lower() in h.name.lower():
                                habit = h
                                break
                    
                    if habit:
                        # Log completion
                        log = HabitLog(
                            habit_id=habit.id,
                            user_id=user_id,
                            notes="Logged via Chat Agent"
                        )
                        self.db.add(log)
                        
                        habit.current_streak += 1
                        if habit.current_streak > habit.best_streak:
                            habit.best_streak = habit.current_streak
                        
                        await self.db.commit()

        except Exception as e:
            print("Error parsing user goals/habits intent from message:", e)

