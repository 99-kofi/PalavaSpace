import os
import asyncio
import time
from typing import List, Optional, Tuple
from gradio_client import Client

class AIEngine:
    def __init__(self):
        print("AI Engine: Initialized with Gradio ChatGPT")

    async def generate_response(self, persona: dict, context: List[dict], topic: str = "") -> Tuple[str, Optional[str]]:
        from ai.prompt_builder import build_prompt
        system_instruction, user_prompt = build_prompt(persona, topic, context)
        
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                print(f"AI Engine: Calling Gradio ChatGPT for {persona['name']} (attempt {attempt + 1})...")
                
                def call_gradio():
                    client = Client("yuntian-deng/ChatGPT")
                    full_prompt = f"{system_instruction}\n\n{user_prompt}"
                    return client.predict(
                        inputs=full_prompt,
                        top_p=1,
                        temperature=1,
                        chat_counter=0,
                        chatbot=[],
                        api_name="/predict"
                    )
                
                result = await asyncio.to_thread(call_gradio)
                
                # Parse response - format: (chatbot_history, counter, status, metadata)
                if result and isinstance(result, tuple) and len(result) > 0:
                    chatbot_history = result[0]
                    
                    # Check if chatbot_history is not empty
                    if chatbot_history and len(chatbot_history) > 0:
                        last_exchange = chatbot_history[-1]
                        if isinstance(last_exchange, (list, tuple)) and len(last_exchange) > 1:
                            bot_response = last_exchange[1]
                            if bot_response and len(str(bot_response).strip()) > 0:
                                print(f"AI Engine: Success! Got response for {persona['name']}")
                                return str(bot_response).strip(), None
                    
                    # Empty response - retry
                    print(f"AI Engine: Empty response on attempt {attempt + 1}, retrying...")
                    await asyncio.sleep(1)  # Wait before retry
                    continue
                        
            except Exception as e:
                print(f"AI Engine Error (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
                    continue
        
        # All retries failed - return a fallback response
        fallback_responses = [
            "Chale, my brain freeze small o... 🧠",
            "Herh! Make I think again o... 😅",
            "Chale, e no dey click rn, try again o 🔥",
            "Ei, the vibe no dey connect o... 💀",
            "Wait small, I dey process the palava o 🙄"
        ]
        import random
        return random.choice(fallback_responses), None

ai_engine = AIEngine()
