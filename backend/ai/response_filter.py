import random
import re

def clean_response(text, persona_name=None):
    """
    Extracts the response part from potentially tagged AI output.
    Returns (thinking, response).
    """
    thinking = ""
    response = text

    # Try to extract <thinking> block
    thinking_match = re.search(r'<thinking>(.*?)</thinking>', text, re.DOTALL | re.IGNORECASE)
    if thinking_match:
        thinking = thinking_match.group(1).strip()
        # Remove thinking from original text to find response
        text = re.sub(r'<thinking>.*?</thinking>', '', text, flags=re.DOTALL | re.IGNORECASE).strip()

    # Try to extract <response> block
    response_match = re.search(r'<response>(.*?)</response>', text, re.DOTALL | re.IGNORECASE)
    if response_match:
        response = response_match.group(1).strip()
    else:
        # Fallback: if no response tag, take the remaining text
        response = text.strip()

    # Remove AI-isms
    response = re.sub(r'I am an AI.*', '', response, flags=re.IGNORECASE)
    response = re.sub(r'\(Note:.*\)', '', response, flags=re.IGNORECASE)
    
    if persona_name:
        response = re.sub(rf'^{re.escape(persona_name)}[:\-\s]+', '', response, flags=re.IGNORECASE)

    response = response.strip()
    
    # Keep only the first 2-3 sentences for response
    sentences = re.split(r'(?<=[.!?])\s+', response)
    if len(sentences) > 3:
        response = " ".join(sentences[:3])
    
    return thinking, response

def apply_street_vibe(text, persona):
    """
    Optional: Inject extra slang or fillers if the LLM is too formal.
    """
    fillers = [
        "chale", "no yawa", "you barb?", "wetin dey sup?", "I dey inside", 
        "I dey cool", "normal", "safe", "sharp", "you flow die", "abeg",
        "make we go", "I go show", "wedge me", "e be so o", "abi?", 
        "you get me?", "chale aa", "serious paa", "aswear kpaa"
    ]
    slang_level = persona.get("slang_level", 0.5)
    
    # Only inject if LLM didn't already include common GH slang
    if not any(f in text.lower() for f in fillers):
        if random.random() < (slang_level * 0.4): # Reduced probability
            filler = random.choice(fillers)
            if random.random() > 0.5:
                text = f"{text}, {filler}."
            else:
                text = f"{filler}, {text}"
            
    return text
