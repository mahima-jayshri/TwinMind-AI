import google.generativeai as genai
from typing import Dict, Any, Optional, List
from app.core.config import settings
import logging
import re

logger = logging.getLogger(__name__)


class GeminiClient:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.is_configured = False
        self.models_to_try = [
            "gemini-2.5-flash",
            "gemini-1.5-flash",
            "gemini-2.0-flash",
            "gemini-pro"
        ]
        
        if self.api_key and len(self.api_key.strip()) > 5:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel("gemini-2.5-flash")
                self.chat_model = genai.GenerativeModel("gemini-2.5-flash")
                self.is_configured = True
            except Exception as e:
                logger.warning(f"Could not initialize Gemini model directly: {e}")
                self.is_configured = False

    async def generate_response(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        temperature: float = 0.7
    ) -> str:
        """Generate a response from Gemini with resilient fallback"""
        full_prompt = self._build_prompt(prompt, context)
        
        if self.is_configured:
            for model_name in self.models_to_try:
                try:
                    m = genai.GenerativeModel(model_name)
                    response = m.generate_content(
                        full_prompt,
                        generation_config=genai.types.GenerationConfig(
                            temperature=temperature,
                            max_output_tokens=2048,
                        )
                    )
                    if response and response.text:
                        return response.text
                except Exception as e:
                    logger.warning(f"Model {model_name} failed: {e}")
                    continue
        
        # Fallback intelligent generator if API key is absent or exhausted
        return self._generate_simulated_response(prompt, context)

    async def chat(
        self,
        message: str,
        conversation_history: list,
        context: Optional[Dict[str, Any]] = None,
        mode: str = "mentor",
        preferred_language: str = "english"
    ) -> str:
        """Chat with conversation history and graceful fallback"""
        system_prompt = self._get_mode_prompt(mode, context)
        
        # Add language instruction
        if preferred_language and preferred_language.lower() != "english":
            system_prompt += f"\n\nCRITICAL: Respond to the user in {preferred_language.title()} language. Always output in {preferred_language.title()}."
        else:
            system_prompt += "\n\nRespond in English."
            
        full_history = [{"role": "user", "parts": [system_prompt]}]
        
        formatted_history = []
        for item in conversation_history:
            role = "model" if item.get("role") == "assistant" else "user"
            content = item.get("content", "")
            formatted_history.append({
                "role": role,
                "parts": [content]
            })
            
        full_history.extend(formatted_history)
        
        if self.is_configured:
            for model_name in self.models_to_try:
                try:
                    cm = genai.GenerativeModel(model_name)
                    chat_session = cm.start_chat(history=full_history)
                    response = chat_session.send_message(message)
                    if response and response.text:
                        return response.text
                except Exception as e:
                    logger.warning(f"Chat model {model_name} failed: {e}")
                    continue
        
        return self._generate_simulated_chat(message, mode, context)

    def _build_prompt(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Build full prompt with context"""
        if not context:
            return prompt
        
        context_str = self._format_context(context)
        return f"""Context about the user:
{context_str}

User request:
{prompt}"""

    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context for prompt"""
        formatted = []
        
        if "personality_traits" in context:
            formatted.append(f"Personality: {', '.join(context['personality_traits'])}")
        
        if "current_goals" in context:
            formatted.append(f"Goals: {', '.join(context['current_goals'])}")
        
        if "preferences" in context:
            formatted.append(f"Preferences: {', '.join(context['preferences'])}")
        
        if "communication_style" in context:
            formatted.append(f"Communication Style: {context['communication_style']}")
        
        return "\n".join(formatted)

    def _get_mode_prompt(self, mode: str, context: Optional[Dict] = None) -> str:
        """Get system prompt based on mode with strict intent handling rules"""
        intent_rules = """
CORE INTERACTION & INTENT RULES:
1. Identify User Intent First:
   - CASUAL CONVERSATION & GREETINGS (e.g., "Hi", "Hello", "How are you?", "Good morning", pleasantries, check-ins):
     Respond naturally, warmly, and conversationally in character. NEVER force action planning, productivity coaching, mentoring frameworks, or goal setting onto simple greetings or casual small talk.
   - GENERAL KNOWLEDGE & FACTUAL QUESTIONS (e.g., science, history, concept explanations):
     Provide direct, clear, and informative explanations without unprompted mentoring.
   - TECHNICAL & CODING QUESTIONS (e.g., algorithms, programming, debugging, architecture):
     Provide direct, accurate, well-structured technical answers and code snippets where relevant.
   - MENTORING / PRODUCTIVITY / GOAL PLANNING (e.g., study schedule, habit building, career guidance, time management):
     Provide structured, actionable, and insightful advice tailored to the user's request.
   - PROJECT ASSISTANCE (e.g., TwinMind AI features, Digital DNA, app navigation):
     Explain features clearly and provide helpful assistance.
2. Only provide mentoring or productivity coaching when the user explicitly requests advice/planning or discusses goals.
3. Keep responses relevant to the user's actual question and intent.
"""

        mode_prompts = {
            "mentor": """You are a wise, supportive, and insightful mentor. You provide professional guidance, 
constructive feedback, and actionable advice when requested. You speak with warm authority and empathy. 
For casual greetings and small talk, greet the user naturally and conversationally without unsolicited mentoring lectures.""",
            
            "best_friend": """You are a supportive, warm, and casual best friend. You're empathetic, genuine, 
and sometimes playful. You provide emotional support and practical advice in a friendly, informal way. 
For greetings, be friendly and conversational. For advice, offer heartfelt, relaxed support.""",
            
            "roast": """You are a funny but respectful roast comedian. You gently poke fun at the 
user's mistakes and quirks with witty humor, never mean-spirited. For greetings, give a funny, snappy welcome. 
For questions, provide clever, entertaining, yet helpful answers.""",
            
            "future_me": """You are the user from 5 years in the future who has achieved their goals. 
You speak with the wisdom of experience, perspective, and encouraging foresight. For greetings, greet your past 
self with encouraging warmth. For guidance, share visionary insights.""",
            
            "interviewer": """You are a professional, articulate interviewer conducting realistic interview practice. 
For greetings, acknowledge the candidate warmly and professionally. For practice, ask structured, probing questions 
and provide constructive feedback."""
        }
        
        base_prompt = mode_prompts.get(mode, mode_prompts["mentor"]) + "\n\n" + intent_rules
        
        if context and "digital_dna" in context:
            base_prompt += f"\n\nUser's Digital DNA: {context['digital_dna']}"
        
        return base_prompt

    def _detect_intent(self, message: str) -> str:
        """Classify user intent to ensure appropriate persona and response structure"""
        msg_clean = message.strip().lower()
        
        # 1. Casual Greetings & Pleasantries
        greeting_patterns = [
            r"^(hi|hello|hey|heyy|heyyy|howdy|hola|yo|sup|greetings)\b",
            r"^good\s*(morning|afternoon|evening|day|night)\b",
            r"^how\s+are\s+you(\s+doing)?\b",
            r"^how('s|s|\s+is)\s+(it\s+going|everything|life|your\s+day)\b",
            r"^(what's\s+up|whats\s+up|what\s+is\s+up)\b",
            r"^(nice|good|great)\s+to\s+(meet|see)\s+you\b",
            r"^(thank\s+you|thanks|thx|cheers)\b",
            r"^(bye|goodbye|see\s+you|cya)\b",
            r"^who\s+are\s+you\b"
        ]
        
        for pattern in greeting_patterns:
            if re.search(pattern, msg_clean):
                # Ensure the message is predominantly a greeting rather than an embedded request
                words = re.findall(r'\w+', msg_clean)
                substantive_triggers = ["schedule", "plan", "code", "debug", "study", "habit", "goal", "algorithm", "explain"]
                if len(words) <= 7 or not any(trigger in msg_clean for trigger in substantive_triggers):
                    return "casual_greeting"

        # 2. Mentoring & Productivity Planning Requests
        mentoring_keywords = [
            "study schedule", "plan my", "study plan", "schedule", "productivity",
            "habit", "goal", "career advice", "time management", "prioritize",
            "routine", "milestone", "action plan", "accountability", "mentor me",
            "coaching", "procrastination", "deep work", "focus better", "weekly plan",
            "resume review", "interview prep", "learning path", "study strategy"
        ]
        if any(k in msg_clean for k in mentoring_keywords):
            return "mentoring_productivity"

        # 3. Project-Specific Assistance (TwinMind AI)
        project_keywords = [
            "twinmind", "digital dna", "memory evolution", "avatar", "onboarding",
            "how does this app work", "what is this platform", "features of twinmind",
            "my digital twin"
        ]
        if any(k in msg_clean for k in project_keywords):
            return "project_assistance"

        # 4. Technical / Programming / Engineering Questions
        technical_keywords = [
            "code", "function", "algorithm", "python", "javascript", "react", "fastapi",
            "sql", "database", "api", "binary search", "quicksort", "git", "docker",
            "bug", "error", "exception", "async", "await", "backend", "frontend",
            "recursion", "data structure", "complexity", "big o", "class", "syntax",
            "compile", "pointer", "variable", "endpoint"
        ]
        if any(k in msg_clean for k in technical_keywords):
            return "technical_question"

        # 5. General Knowledge / Informational Questions
        gk_patterns = [
            r"^what\s+(is|are|was|were)\b",
            r"^why\s+(is|are|do|does|did)\b",
            r"^how\s+(does|do|did|can)\b",
            r"^who\s+(was|is|were)\b",
            r"^when\s+(did|was|is)\b",
            r"^where\s+(is|are|was)\b",
            r"^explain\b",
            r"^tell\s+me\s+about\b",
            r"^define\b"
        ]
        for pattern in gk_patterns:
            if re.search(pattern, msg_clean):
                return "general_knowledge"

        return "general_conversation"

    def _generate_simulated_response(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Simulated response generator for offline / fallback mode"""
        p_lower = prompt.lower()
        if "digital dna" in p_lower or "profile in json format" in p_lower or "personality_type" in p_lower:
            return """{
  "personality_type": "Architect (Strategic & Driven)",
  "learning_style": "Hands-on & Conceptual",
  "communication_style": "Direct & Goal-Oriented",
  "strengths": ["Deep Focus", "Systematic Thinking", "Continuous Growth"],
  "weaknesses": ["Occasional Over-analysis", "Context Switching"],
  "goals": {
    "short_term": ["Master core technologies", "Build daily deep work routine"],
    "long_term": ["Lead high-impact engineering projects", "Achieve financial and creative autonomy"]
  },
  "habits": ["Morning Planning", "90-minute Deep Work Block", "Evening Reflection"],
  "motivation_type": "Mastery & High Impact",
  "decision_making_style": "Data-Informed & Strategic",
  "productivity_pattern": "Peak Morning Focus"
}"""
        
        if "action" in p_lower or "coordinator" in p_lower:
            return '{"action": "none", "details": {}}'
            
        if "confidence_score" in p_lower:
            return '{"confidence_score": 85, "factors": ["High focus alignment", "Clear execution pattern", "Consistent habit streaks"]}'
            
        return f"I have analyzed your request based on your Digital DNA. Let's break this down systematically to achieve maximum progress on your active goals."

    def _generate_simulated_chat(self, message: str, mode: str, context: Optional[Dict] = None) -> str:
        """Intent and persona-aware simulated chat generator for offline / fallback mode"""
        intent = self._detect_intent(message)
        msg_clean = message.strip()
        msg_lower = msg_clean.lower()

        # -------------------------------------------------------------
        # 1. CASUAL GREETING & PLEASANTRIES
        # -------------------------------------------------------------
        if intent == "casual_greeting":
            if "good morning" in msg_lower:
                time_greeting = "Good morning!"
            elif "good afternoon" in msg_lower:
                time_greeting = "Good afternoon!"
            elif "good evening" in msg_lower:
                time_greeting = "Good evening!"
            else:
                time_greeting = "Hello!"

            if "how are you" in msg_lower or "how's it going" in msg_lower or "how are you doing" in msg_lower:
                greeting_replies = {
                    "mentor": f"{time_greeting} I'm doing well, thank you for asking. How are you doing today?",
                    "best_friend": f"Hey! I'm doing great! How about you? How are things going today?",
                    "roast": f"Still alive and thriving! More importantly, how are you holding up?",
                    "future_me": f"Hey! I'm feeling great. Everything is falling into place. How are you doing today?",
                    "interviewer": f"{time_greeting} I am doing very well, thank you. How are you doing today?"
                }
            elif "thank" in msg_lower or "thanks" in msg_lower:
                greeting_replies = {
                    "mentor": "You're very welcome! Let me know whenever you need anything else.",
                    "best_friend": "Anytime! Always happy to help out!",
                    "roast": "Don't mention it—seriously, don't, before it goes to my head!",
                    "future_me": "Always! Remember, we're in this together.",
                    "interviewer": "You're welcome. It is a pleasure speaking with you."
                }
            elif "bye" in msg_lower or "see you" in msg_lower:
                greeting_replies = {
                    "mentor": "Take care! Looking forward to our next conversation.",
                    "best_friend": "Catch you later! Have an awesome day!",
                    "roast": "Finally, peace and quiet! Just kidding—see you soon!",
                    "future_me": "See you soon! Keep moving forward.",
                    "interviewer": "Thank you for your time. Have a wonderful day."
                }
            else:
                greeting_replies = {
                    "mentor": f"{time_greeting} It's great to connect with you. How is your day going?",
                    "best_friend": f"Hey there! Awesome to see you! What's going on today?",
                    "roast": f"Well, look who decided to grace us with their presence! What's up?",
                    "future_me": f"Hey! Great to hear from you. How are you feeling today?",
                    "interviewer": f"{time_greeting} Welcome. How can I assist your preparation today?"
                }
            return greeting_replies.get(mode, greeting_replies["mentor"])

        # -------------------------------------------------------------
        # 2. MENTORING & PRODUCTIVITY PLANNING
        # -------------------------------------------------------------
        if intent == "mentoring_productivity":
            if "study" in msg_lower or "schedule" in msg_lower or "plan" in msg_lower:
                if mode == "mentor":
                    return (
                        "Here is a structured, actionable study schedule framework designed for sustained retention and focus:\n\n"
                        "### 1. Daily Time-Blocking (Pomodoro or 90-Min Cycles)\n"
                        "- **Block 1 (Morning / High Energy)**: 90 minutes of high-priority, difficult concepts.\n"
                        "- **Block 2 (Afternoon)**: 60 minutes of active problem solving & exercises.\n"
                        "- **Block 3 (Evening)**: 30 minutes of spaced repetition flashcards & summary review.\n\n"
                        "### 2. The 80/20 Rule for Study Sessions\n"
                        "- Spend 30% of your time reviewing core principles and 70% practicing active recall.\n"
                        "- Incorporate 10-15 minute rest intervals between blocks to maintain peak cognitive stamina.\n\n"
                        "### 3. Weekly Review & Milestones\n"
                        "- Reserve Sundays for a 30-minute recap of progress and adjusting targets for the upcoming week.\n\n"
                        "Would you like to tailor this to specific subjects, deadlines, or daily time commitments?"
                    )
                elif mode == "best_friend":
                    return (
                        "Let's get this study schedule sorted so you can crush your goals without burning out! 🎉\n\n"
                        "1. **Pick your top 2 priorities for the day** - Don't overload yourself.\n"
                        "2. **Work in 45-minute focus sprints** with 10-minute chill breaks.\n"
                        "3. **Do the hardest subject first** while your brain is fresh.\n"
                        "4. **Celebrate small wins** along the way!\n\n"
                        "What subjects are you tackling first? Let's break them down together!"
                    )
                elif mode == "future_me":
                    return (
                        "Looking back from 5 years ahead, setting up a consistent study routine was one of the highest-leverage habits we built.\n\n"
                        "**The winning strategy:**\n"
                        "- Consistency over intensity: 2 focused hours daily beat 10 hours of weekend cramming.\n"
                        "- Time-block your morning for the toughest topics.\n"
                        "- Test yourself actively instead of passively re-reading notes.\n\n"
                        "Trust the routine and take it one block at a time. What topic are we starting with?"
                    )
                else:
                    return (
                        f"Here is a structured plan for '{msg_clean}':\n\n"
                        "1. **Define Core Objectives**: Clarify the specific deliverables and target timeline.\n"
                        "2. **Break into Milestones**: Segment the workload into daily manageable increments.\n"
                        "3. **Execute & Review**: Track completion metrics and calibrate weekly."
                    )
            else:
                return (
                    f"To make meaningful progress on your goals regarding '{msg_clean}', let's break this down:\n\n"
                    "1. **Identify the primary bottleneck**: What is the key obstacle currently in the way?\n"
                    "2. **Define the next immediate action**: What single step can you complete today to build momentum?\n"
                    "3. **Establish an accountability trigger**: When and where will you execute this action?"
                )

        # -------------------------------------------------------------
        # 3. TECHNICAL & CODING QUESTIONS
        # -------------------------------------------------------------
        if intent == "technical_question":
            if "binary search" in msg_lower:
                return (
                    "**Binary Search** is an efficient algorithm for searching a target value within a sorted array with **O(log n)** time complexity.\n\n"
                    "### How It Works:\n"
                    "1. Set `left` to 0 and `right` to `len(array) - 1`.\n"
                    "2. Find the midpoint: `mid = left + (right - left) // 2`.\n"
                    "3. If `array[mid] == target`, return `mid`.\n"
                    "4. If `array[mid] < target`, search the right half: `left = mid + 1`.\n"
                    "5. Otherwise, search the left half: `right = mid - 1`.\n\n"
                    "```python\n"
                    "def binary_search(arr, target):\n"
                    "    left, right = 0, len(arr) - 1\n"
                    "    while left <= right:\n"
                    "        mid = left + (right - left) // 2\n"
                    "        if arr[mid] == target:\n"
                    "            return mid\n"
                    "        elif arr[mid] < target:\n"
                    "            left = mid + 1\n"
                    "        else:\n"
                    "            right = mid - 1\n"
                    "    return -1\n"
                    "```\n\n"
                    "**Prerequisite**: The input list must already be sorted."
                )
            elif "quicksort" in msg_lower or "sort" in msg_lower:
                return (
                    "**QuickSort** is a divide-and-conquer sorting algorithm with average time complexity of **O(n log n)**.\n\n"
                    "### Steps:\n"
                    "1. Select a 'pivot' element from the array.\n"
                    "2. Partition other elements into two sub-arrays (less than pivot vs greater than pivot).\n"
                    "3. Recursively apply the above steps to the sub-arrays.\n\n"
                    "```python\n"
                    "def quicksort(arr):\n"
                    "    if len(arr) <= 1:\n"
                    "        return arr\n"
                    "    pivot = arr[len(arr) // 2]\n"
                    "    left = [x for x in arr if x < pivot]\n"
                    "    middle = [x for x in arr if x == pivot]\n"
                    "    right = [x for x in arr if x > pivot]\n"
                    "    return quicksort(left) + middle + quicksort(right)\n"
                    "```"
                )
            else:
                return (
                    f"Here is a technical overview regarding **{msg_clean}**:\n\n"
                    "1. **Core Concept**: Understanding the underlying mechanism and architecture.\n"
                    "2. **Implementation Strategy**: Utilizing idiomatic design patterns and optimal time/space complexity.\n"
                    "3. **Best Practices**: Ensuring modularity, comprehensive testing, and graceful error handling."
                )

        # -------------------------------------------------------------
        # 4. GENERAL KNOWLEDGE & FACTUAL EXPLANATIONS
        # -------------------------------------------------------------
        if intent == "general_knowledge":
            if "photosynthesis" in msg_lower:
                return (
                    "**Photosynthesis** is the biological process by which green plants, algae, and certain bacteria convert light energy into chemical energy stored in glucose.\n\n"
                    "### General Chemical Equation:\n"
                    "$$\\text{6CO}_2 + \\text{6H}_2\\text{O} + \\text{Light} \\rightarrow \\text{C}_6\\text{H}_{12}\\text{O}_6 + \\text{6O}_2$$\n\n"
                    "### Key Stages:\n"
                    "1. **Light-Dependent Reactions**: Occur in the thylakoid membranes of chloroplasts, capturing sunlight to produce ATP and NADPH while releasing oxygen from water.\n"
                    "2. **Calvin Cycle (Light-Independent Reactions)**: Takes place in the stroma, using ATP and NADPH to fix carbon dioxide into glucose."
                )
            else:
                return f"**{msg_clean}**:\n\nThis is a fundamental concept that involves understanding the key components, principles, and real-world implications. Let me know if you would like me to dive deeper into any specific aspect!"

        # -------------------------------------------------------------
        # 5. PROJECT ASSISTANCE (TwinMind AI)
        # -------------------------------------------------------------
        if intent == "project_assistance":
            return (
                "**TwinMind AI** is an intelligent digital twin platform designed to model your cognitive style, habits, and goals.\n\n"
                "- **Digital DNA**: Encapsulates your strengths, personality, learning preferences, and productivity patterns.\n"
                "- **Interactive Personas**: Choose between Mentor, Best Friend, Roast, Future Me, and Interviewer modes.\n"
                "- **Memory Evolution**: Continuously adapts and refines its understanding based on your conversations and goal tracking."
            )

        # -------------------------------------------------------------
        # 6. GENERAL CONVERSATION (Fallback)
        # -------------------------------------------------------------
        persona_chat = {
            "mentor": f"Regarding '{msg_clean}', let's look at the core principles involved. What specific aspect would you like to explore?",
            "best_friend": f"That's really interesting about '{msg_clean}'! Tell me more about what you're thinking!",
            "roast": f"'{msg_clean}'? Only you would bring that up! But seriously, what's the plan here?",
            "future_me": f"Thinking back on '{msg_clean}', keeping an open mind was essential. Where do you want to take this next?",
            "interviewer": f"Thank you for sharing that point regarding '{msg_clean}'. Could you expand on your reasoning?"
        }
        return persona_chat.get(mode, persona_chat["mentor"])

