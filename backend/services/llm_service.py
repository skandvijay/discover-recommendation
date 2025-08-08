import openai
import os
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        # Initialize OpenAI client with modern API (1.x+)
        try:
            # Clean initialization without any extra parameters that might cause proxy issues
            import httpx
            
            # Create a custom HTTP client without proxy settings
            http_client = httpx.Client(
                timeout=30.0,
                limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
            )
            
            self.client = openai.OpenAI(
                api_key=api_key,
                http_client=http_client
            )
            self._client_available = True
            print("✅ OpenAI client initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize OpenAI client: {e}")
            # Try minimal initialization as fallback
            try:
                self.client = openai.OpenAI(api_key=api_key)
                self._client_available = True
                print("✅ OpenAI client initialized with fallback method")
            except Exception as e2:
                print(f"❌ Fallback also failed: {e2}")
                self.client = None
                self._client_available = False
    
    async def generate_answer(self, query: str, context: List[str] = None) -> Dict[str, any]:
        """
        Generate an answer using OpenAI GPT-3.5 based on the user query.
        Raises exception if OpenAI client is not available to prevent saving error documents.
        """
        # Check if OpenAI client is available
        if not self._client_available or not self.client:
            print(f"❌ OpenAI client not available, cannot process query: {query}")
            raise Exception("OpenAI service is currently unavailable. Please check your API key and internet connection.")
        
        try:
            # Build system prompt
            system_prompt = """You are a helpful AI assistant that provides comprehensive, 
            accurate answers to user queries. Focus on being informative and helpful.
            If you don't have enough information, say so clearly."""
            
            # Build user message with context if provided
            user_message = f"Query: {query}"
            if context:
                context_text = "\n".join(context[:3])  # Limit context to prevent token overflow
                user_message = f"Context:\n{context_text}\n\nQuery: {query}"
            
            # Modern OpenAI API call (1.x+)
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            answer = response.choices[0].message.content
            
            # Generate a title for the document
            title_response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Generate a concise, descriptive title for this content in 5-8 words."},
                    {"role": "user", "content": f"Content: {answer}"}
                ],
                max_tokens=50,
                temperature=0.5
            )
            title = title_response.choices[0].message.content.strip().strip('"')
            
            return {
                "answer": answer,
                "title": title,
                "sources": ["OpenAI GPT-3.5"],
                "confidence": 0.85,
                "success": True
            }
            
        except Exception as e:
            print(f"❌ Error calling OpenAI API: {str(e)}")
            raise Exception(f"Failed to generate answer: {str(e)}")
    
    async def detect_intent(self, query: str) -> Dict[str, any]:
        """
        Detect the intent and category of a user query for better recommendations.
        """
        if not self._client_available or not self.client:
            return {
                "category": "informational",
                "keywords": [word for word in query.split() if len(word) > 3][:5],
                "confidence": 0.5
            }
            
        try:
            system_prompt = """Analyze the user query and classify it into one of these categories:
            - informational: seeking knowledge or facts
            - procedural: how-to questions or step-by-step guidance  
            - analytical: analysis, comparison, or evaluation
            - creative: brainstorming, ideas, or creative content
            - troubleshooting: problem-solving or debugging
            
            Also extract 3-5 relevant keywords. Return as JSON:
            {"category": "...", "keywords": ["...", "..."], "confidence": 0.0-1.0}"""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"Error detecting intent: {str(e)}")
            return {
                "category": "informational",
                "keywords": [word for word in query.split() if len(word) > 3][:5],
                "confidence": 0.5
            }