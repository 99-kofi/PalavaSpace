import asyncio
import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai.engine import ai_engine
from ai.response_filter import clean_response

async def test_intelligence():
    load_dotenv()
    
    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Error: GOOGLE_API_KEY not found in .env")
        return

    persona = {
        "id": "area_chairman",
        "name": "Area Chairman",
        "language": "Hard Ghana Pidgin",
        "style": "Strict, street-smart, and zero-nonsense",
        "slang_level": 0.95,
        "aggression": 0.85,
        "beef": "He thinks Campus Big Boy is a spoiled smallie."
    }
    
    context = [
        {"sender": "campus_big_boy", "sender_name": "Campus Big Boy", "content": "Chale, I just buy new iPhone 16 Pro Max. My money too chao!"}
    ]
    
    print("--- 🧪 Testing Deep Thinking & Personality ---")
    raw_text, engine_reasoning = await ai_engine.generate_response(persona, context, topic="Money Flex")
    
    print(f"\nRAW OUTPUT:\n{raw_text}")
    
    thinking, response = clean_response(raw_text, persona['name'])
    
    print(f"\nPARSED THINKING:\n{thinking}")
    print(f"\nPARSED RESPONSE:\n{response}")
    print(f"\nENGINE REASONING (Native):\n{engine_reasoning}")

    # Assertions (Mental)
    if thinking or engine_reasoning:
        print("\n✅ SUCCESS: Thinking/Reasoning captured.")
    else:
        print("\n❌ FAILURE: No thinking captured.")

    if "<thinking>" not in response:
        print("✅ SUCCESS: Thinking tags stripped from public response.")
    else:
        print("❌ FAILURE: Thinking tags still present in public response.")

if __name__ == "__main__":
    asyncio.run(test_intelligence())
