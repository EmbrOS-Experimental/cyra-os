"""
Plugin: romanian
Romanian language support — translation, RO TTS, RO STT hints.
"""
import json

RO_PHRASES = {
    "salut": "hello",
    "bună": "hello",
    "mulțumesc": "thank you",
    "da": "yes",
    "nu": "no",
    "ce faci": "how are you",
    "bine": "good",
    "rău": "bad",
    "la revedere": "goodbye",
    "pa": "bye",
    "te rog": "please",
    "scuze": "sorry",
    "nu înțeleg": "I don't understand",
    "înțeleg": "I understand",
    "corect": "correct",
    "greșit": "wrong",
    "foarte": "very",
    "mai mult": "more",
    "mai puțin": "less",
    "acum": "now",
    "mai târziu": "later",
}

def translate_to_english(text: str):
    """Simple Romanian to English translation for common phrases."""
    words = text.lower().split()
    translated = []
    for word in words:
        clean = word.strip(".,!?;:")
        if clean in RO_PHRASES:
            translated.append(RO_PHRASES[clean])
        else:
            translated.append(word)
    return {"original": text, "translated": " ".join(translated)}

def detect_language(text: str):
    """Detect if text is likely Romanian."""
    words = text.lower().split()
    ro_count = sum(1 for w in words if w.strip(".,!?;:") in RO_PHRASES)
    ratio = ro_count / max(len(words), 1)
    return {
        "likely_romanian": ratio > 0.3,
        "confidence": round(ratio, 2),
        "ro_words_found": ro_count
    }

def get_ro_voice_name():
    """Get the Romanian TTS voice name."""
    return {"voice": "ro-RO-AlinaNeural", "language": "ro-RO"}

tools = [
    {
        "type": "function",
        "function": {
            "name": "translate_to_english",
            "description": "Translate Romanian text to English (basic word-level).",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Romanian text to translate."}
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "detect_language",
            "description": "Detect if text is Romanian or English.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to analyze."}
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_ro_voice_name",
            "description": "Get the Romanian TTS voice name for Edge TTS.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    }
]
