import asyncio
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path to import engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.ai_engine import ai_engine

async def test_reasoning():
    load_dotenv()
    persona = {
        "id": "test_agent",
        "name": "Kwame",
        "language": "Pidgin",
        "bio": "A blunt but funny guy from Accra.",
        "style": "Witty and slightly aggressive",
        "slang_level": 0.8,
        "aggression": 0.5
    }
    
    context = [
        {"sender": "user", "sender_name": "Admin", "content": "How many r's are in the word 'strawberry'?"}
    ]
    
    print("--- Turn 1: Asking with reasoning enabled ---")
    response, reasoning = await ai_engine.generate_response(persona, context)
    print(f"Response: {response}")
    print(f"Reasoning captured: {bool(reasoning)}")
    if reasoning:
        print(f"Reasoning sample: {str(reasoning)[:200]}...")

    # Second Turn
    context.append({
        "sender": persona["id"],
        "sender_name": persona["name"],
        "content": response,
        "reasoning_details": reasoning
    })
    context.append({
        "sender": "user",
        "sender_name": "Admin",
        "content": "Are you sure? Think carefully."
    })
    
    print("\n--- Turn 2: Follow-up with preserved reasoning ---")
    response2, reasoning2 = await ai_engine.generate_response(persona, context)
    print(f"Response 2: {response2}")
    print(f"Reasoning 2 captured: {bool(reasoning2)}")

if __name__ == "__main__":
    asyncio.run(test_reasoning())
