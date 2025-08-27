# src/prompt_engineering.py

META_PROMPT_TEMPLATE = """
A high-quality, visually striking image in a fusion style of anarcho-punk, psycho-rebel, cyberpunk, street hacker, DIY, gritty, raw, chaotic.
Artistic style: photorealistic render, ink and marker sketch, controlled glitch art.
The user's vision is: {user_prompt_here}.
Interpret the user's vision through the lens of the core aesthetic. Be creative, chaotic, and bold. The final image must feel like a piece of underground art.
"""

EMOJI_GRIMOIRE = {
    "👨": "a male figure, a man, a boy",
    "👩": "a female figure, a woman, a girl",
    "💀": "memento mori, skull, death, gothic, danger, skeletal",
    "🤖": "a robot, cyborg, android, artificial intelligence, machine",
    "🔥": "infused with fire, chaos, passion, destruction, creative energy, flames",
    "🖤": "a black heart, dark essence, rebellion, sorrow, anti-love",
    "⚡️": "electric, high-energy, neon glow, power, speed, lightning",
    "⛓️": "chains, bondage, oppression, connection, industrial, metallic links",
    "Ⓐ": "anarchy symbol, anti-authoritarian, punk rock, chaos magic sigil",
    "💻": "hacker, computer, digital realm, cyberspace, terminal screen",
    "🧠": "psychedelic, consciousness, mind-bending, intelligence, trippy visuals",
    "💊": "a pill, drugs, medicine, altered state, transhumanism",
    "👁️": "an eye, seeing, surveillance, esoteric knowledge, all-seeing eye",
    "🔪": "a knife, blade, danger, sharp, cutting edge, violence",
    "💥": "explosion, impact, breakthrough, sudden change",
    "🍄": "mushroom, psychedelic trip, nature, fungus, magic mushrooms",
}

def translate_emojis(text: str) -> str:
    """Replaces emojis in a string with their textual meanings from the grimoire."""
    for emoji, meaning in EMOJI_GRIMOIRE.items():
        text = text.replace(emoji, f"({meaning}) ")
    return text

def engineer_prompt(user_input: str) -> str:
    """
    Translates emojis from user input and wraps it in the meta-prompt template.
    """
    if not user_input.strip():
        # If the user input is empty, we still want to generate something cool.
        user_input = "a chaotic and surreal vision"

    # First, translate any emojis into their textual representations.
    translated_prompt = translate_emojis(user_input)

    # Then, inject the user's vision into the master template.
    final_prompt = META_PROMPT_TEMPLATE.format(user_prompt_here=translated_prompt)
    
    return final_prompt.strip()
