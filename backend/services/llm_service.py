import openai
import os
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    async def generate_answer(self, query: str, context: List[str] = None) -> Dict[str, any]:
        """
        Generate an answer using OpenAI GPT-4 based on the user query.
        Optionally include context from previous queries or documents.
        """
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
            
            response = self.client.chat.completions.create(
                model="gpt-4",
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
                "sources": ["OpenAI GPT-4"],
                "confidence": 0.85,
                "tokens_used": response.usage.total_tokens
            }
            
        except Exception as e:
            print(f"Error generating answer: {str(e)}")
            return {
                "answer": f"I apologize, but I encountered an error processing your query: {query}. Please try again.",
                "title": "Error Response",
                "sources": ["Error"],
                "confidence": 0.1,
                "tokens_used": 0
            }
    
    async def detect_intent(self, query: str) -> Dict[str, any]:
        """
        Detect the intent and category of a user query for better recommendations.
        """
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