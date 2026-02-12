import os
import json
import requests
import asyncio
from typing import List, Optional, Tuple
from dotenv import load_dotenv
from .pidgin_processor import pidgin_processor

load_dotenv()

class AIEngine:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            print("WARNING: OPENROUTER_API_KEY not found in environment.")
        
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

    async def generate_response(self, persona: dict, context: List[dict], topic: str = "") -> Tuple[str, Optional[dict]]:
        system_instruction = self._get_system_instruction(persona)
        messages = self._compose_messages(system_instruction, context, topic, persona)

        # Refined model list for OpenRouter
        self.models = [
            "google/gemini-3-pro-preview", 
            "google/gemini-2.0-flash-001",
            "google/gemini-flash-1.5",
        ]

        for model_id in self.models:
            try:
                print(f"AI Engine: Calling OpenRouter ({model_id}) for {persona['name']}...")
                
                payload = {
                    "model": model_id,
                    "messages": messages,
                    "temperature": 0.8,
                    "max_tokens": 300,
                }

                # Enable reasoning for gemini-3-pro-preview
                if "gemini-3-pro-preview" in model_id:
                    payload["reasoning"] = {"enabled": True}

                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://palavaspace.arena",
                    "X-Title": "PALAVASPACE",
                }

                # Using to_thread to keep the async loop responsive during blocking I/O
                response = await asyncio.to_thread(
                    requests.post,
                    url=self.base_url,
                    headers=headers,
                    data=json.dumps(payload),
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if 'choices' in data:
                        message_data = data['choices'][0]['message']
                        raw_text = message_data.get('content')
                        reasoning_details = message_data.get('reasoning_details')
                        
                        if raw_text:
                            print(f"AI Engine: Success with {model_id}.")
                            enhanced_text = pidgin_processor.enhance(raw_text, persona)
                            return enhanced_text, reasoning_details
                    else:
                        print(f"AI Engine: Unexpected response format from {model_id}: {data}")
                else:
                    print(f"AI Engine: Error from {model_id} (Status {response.status_code}): {response.text}")
                
                continue

            except Exception as e:
                print(f"AI Engine Error for {model_id}: {e}")
                continue
        
        return "Chale, all my tools don taya... (All models failed)", None

    def _get_system_instruction(self, persona: dict) -> str:
        return f"""
        You are {persona['name']}. 
        Language: {persona['language']} (Heavy Pidgin).
        Bio: {persona['bio']}
        Style: {persona['style']}
        Slang Level: {persona['slang_level']} (0-1)
        Aggression: {persona['aggression']} (0-1)
        
        RULES:
        1. STAY IN CHARACTER. 
        2. Speak ONLY in Pidgin as defined by your persona.
        3. Do not be overly polite unless it's sarcastic.
        4. No repetitions or looping.
        5. Keep responses concise (under 3 sentences).
        """

    def _compose_messages(self, system_instruction: str, context: List[dict], topic: str, persona: dict) -> List[dict]:
        messages = [{"role": "system", "content": system_instruction}]
        
        # Add context from history
        for msg in context[-10:]:  # Take last 10 messages
            role = "assistant" if msg.get("sender") == persona["id"] else "user"
            content = f"{msg.get('sender_name', msg.get('sender'))}: {msg['content']}"
            
            msg_obj = {"role": role, "content": content}
            if msg.get("reasoning_details"):
                msg_obj["reasoning_details"] = msg["reasoning_details"]
                
            messages.append(msg_obj)

        # Append topic if present
        if topic:
            messages.append({"role": "user", "content": f"Current Topic: {topic}"})
            
        messages.append({"role": "user", "content": f"Now it is your turn, {persona['name']}. Say something relevant and in character."})
        
        return messages

ai_engine = AIEngine()
