"""
Plugin: avatar
Simple animated avatar expressions for Cyra.
Returns SVG-based face states.
"""
import random

EXPRESSIONS = {
    "neutral": {"eyes": "open", "mouth": "neutral", "eyebrows": "normal"},
    "happy": {"eyes": "open", "mouth": "smile", "eyebrows": "raised"},
    "thinking": {"eyes": "looking_up", "mouth": "neutral", "eyebrows": "raised_left"},
    "listening": {"eyes": "open", "mouth": "closed", "eyebrows": "normal"},
    "speaking": {"eyes": "open", "mouth": "talking", "eyebrows": "normal"},
    "confused": {"eyes": "open", "mouth": "frown", "eyebrows": "raised_left"},
    "sleeping": {"eyes": "closed", "mouth": "neutral", "eyebrows": "normal"},
}

def get_avatar_svg(expression: str = "neutral"):
    """Get an SVG face for the given expression."""
    expr = EXPRESSIONS.get(expression, EXPRESSIONS["neutral"])
    
    # Eye states
    eyes = {
        "open": '<circle cx="35" cy="40" r="5" fill="white"/><circle cx="65" cy="40" r="5" fill="white"/>',
        "closed": '<line x1="30" y1="40" x2="40" y2="40" stroke="white" stroke-width="2"/><line x1="60" y1="40" x2="70" y2="40" stroke="white" stroke-width="2"/>',
        "looking_up": '<circle cx="35" cy="38" r="5" fill="white"/><circle cx="65" cy="38" r="5" fill="white"/><circle cx="35" cy="36" r="2" fill="#0a0a0a"/><circle cx="65" cy="36" r="2" fill="#0a0a0a"/>',
    }
    
    # Mouth states
    mouths = {
        "neutral": '<line x1="40" y1="65" x2="60" y2="65" stroke="white" stroke-width="2"/>',
        "smile": '<path d="M 40 65 Q 50 75 60 65" stroke="white" stroke-width="2" fill="none"/>',
        "frown": '<path d="M 40 70 Q 50 60 60 70" stroke="white" stroke-width="2" fill="none"/>',
        "closed": '<line x1="45" y1="65" x2="55" y2="65" stroke="white" stroke-width="2"/>',
        "talking": '<ellipse cx="50" cy="67" rx="8" ry="5" fill="white" opacity="0.8"><animate attributeName="ry" values="3;6;3" dur="0.3s" repeatCount="indefinite"/></ellipse>',
    }
    
    # Eyebrow states
    eyebrows = {
        "normal": '<line x1="28" y1="30" x2="42" y2="30" stroke="white" stroke-width="1.5"/><line x1="58" y1="30" x2="72" y2="30" stroke="white" stroke-width="1.5"/>',
        "raised": '<line x1="28" y1="28" x2="42" y2="26" stroke="white" stroke-width="1.5"/><line x1="58" y1="26" x2="72" y2="28" stroke="white" stroke-width="1.5"/>',
        "raised_left": '<line x1="28" y1="26" x2="42" y2="28" stroke="white" stroke-width="1.5"/><line x1="58" y1="30" x2="72" y2="28" stroke="white" stroke-width="1.5"/>',
    }
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">
  <circle cx="50" cy="50" r="48" fill="#111" stroke="#333" stroke-width="2"/>
  {eyes.get(expr["eyes"], eyes["open"])}
  {eyebrows.get(expr["eyebrows"], eyebrows["normal"])}
  {mouths.get(expr["mouth"], mouths["neutral"])}
</svg>'''
    
    return {"expression": expression, "svg": svg}

def list_expressions():
    """List available avatar expressions."""
    return {"expressions": list(EXPRESSIONS.keys())}

def random_expression():
    """Get a random expression."""
    expr = random.choice(list(EXPRESSIONS.keys()))
    return get_avatar_svg(expr)

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_avatar_svg",
            "description": "Get an animated SVG face for Cyra. Expressions: neutral, happy, thinking, listening, speaking, confused, sleeping.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Expression name. Default: neutral."}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_expressions",
            "description": "List all available avatar expressions.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    }
]
