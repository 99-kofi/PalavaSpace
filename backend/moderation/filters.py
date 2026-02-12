def moderate(text):
    """
    Controlled chaos only.
    """
    forbidden = ["kill", "murder", "illegal", "drug"]
    for word in forbidden:
        if word in text.lower():
            return False
    return True
