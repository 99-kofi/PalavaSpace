import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "palava-secret-123")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./prisma/dev.db")
    
    # AI Settings
    MODELS = [
        "claude-sonnet-4-5",
        "gemini-3-flash-preview",
        "gemini-2.0-flash",
        "gemini-flash-latest",
        "meta-llama/Llama-3.2-1B-Instruct"
    ]
    
    # Room Settings
    DEFAULT_ROOM = "street-vibes"
    CHAT_COOLDOWN = (5, 12) # seconds
