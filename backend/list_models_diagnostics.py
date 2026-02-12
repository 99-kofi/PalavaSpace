import os
from google import genai
from dotenv import load_dotenv

def list_models():
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found")
        return

    try:
        client = genai.Client(api_key=api_key)
        print("--- Available Models ---")
        # google-genai SDK listing models
        for model in client.models.list():
            print(f"- {model.name}")
    except Exception as e:
        print(f"❌ Error listing models: {e}")

if __name__ == "__main__":
    list_models()
