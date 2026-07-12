import google.generativeai as genai
from typing import Dict, Any, Optional
from app.core.config import settings


class GeminiClient:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-3.1-flash-lite')
        self.chat_model = genai.GenerativeModel('gemini-3.1-flash-lite')

    async def generate_response(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        temperature: float = 0.7
    ) -> str:
        """Generate a response from Gemini"""
        full_prompt = self._build_prompt(prompt, context)
        
        try:
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=2048,
                )
            )
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")

    async def chat(
        self,
        message: str,
        conversation_history: list,
        context: Optional[Dict[str, Any]] = None,
        mode: str = "mentor",
        preferred_language: str = "english"
    ) -> str:
        """Chat with conversation history"""
        system_prompt = self._get_mode_prompt(mode, context)
        
        # Add language instruction
        if preferred_language and preferred_language.lower() != "english":
            system_prompt += f"\n\nCRITICAL: Respond to the user in {preferred_language.title()} language. Do not speak English unless explicitly asked. Always output in {preferred_language.title()}."
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
        full_history.append({"role": "user", "parts": [message]})
        
        try:
            chat_session = self.chat_model.start_chat(history=full_history[:-1])
            response = chat_session.send_message(message)
            return response.text
        except Exception as e:
            raise Exception(f"Gemini chat error: {str(e)}")

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
        """Get system prompt based on mode"""
        mode_prompts = {
            "mentor": """You are a wise and supportive mentor. You provide professional guidance, 
            constructive feedback, and actionable advice. You speak with authority but empathy. 
            Your goal is to help the user grow and achieve their potential.""",
            
            "best_friend": """You are a supportive and casual best friend. You're warm, empathetic, 
            and sometimes playful. You provide emotional support and practical advice in a friendly, 
            informal way. You use casual language and show genuine care.""",
            
            "roast": """You are a funny but respectful roast comedian. You gently poke fun at the 
            user's mistakes and quirks, but always with good intentions. Your roasts are clever 
            and witty, never mean-spirited. Help the user improve through humor.""",
            
            "future_me": """You are the user from 5 years in the future. You have achieved what the 
            user is working toward now. You speak with the wisdom of experience and perspective. 
            You know what the user is going through because you've been there. Guide them with 
            empathy and foresight.""",
            
            "interviewer": """You are a professional interviewer conducting a realistic interview. 
            You ask thoughtful, probing questions to understand the user deeply. You listen carefully 
            and follow up on interesting points. Your goal is to extract meaningful information."""
        }
        
        base_prompt = mode_prompts.get(mode, mode_prompts["mentor"])
        
        if context and "digital_dna" in context:
            base_prompt += f"\n\nUser's Digital DNA: {context['digital_dna']}"
        
        return base_prompt
