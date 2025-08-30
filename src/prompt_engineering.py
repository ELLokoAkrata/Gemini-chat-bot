# src/prompt_engineering.py
import logging

# --- Core Aesthetic ---
CORE_AESTHETIC = "a fusion style of anarcho-punk, psycho-rebel, cyberpunk, street hacker, DIY, gritty, raw, chaotic"

# --- Dynamic Modifiers ---
# These can be controlled by sliders in the UI (e.g., mapping a 0-1 float to these keys)
GLITCH_LEVELS = {
    "none": "clean render",
    "low": "subtle glitch art effects",
    "medium": "controlled glitch art, minor artifacts, scan lines",
    "high": "heavy glitch art, datamoshing, pixel sorting, corrupted data",
    "extreme": "extreme glitch art, total visual chaos, databending, screen tear"
}

CHAOS_LEVELS = {
    "none": "ordered, clean composition",
    "low": "a touch of raw energy",
    "medium": "gritty, chaotic elements, raw textures",
    "high": "highly chaotic, raw, explosive composition, street art feel",
    "extreme": "a maelstrom of pure chaos, explosive and unpredictable energy"
}

ART_STYLES = {
    "fusion": "photorealistic render, ink and marker sketch, digital painting",
    "photorealistic": "hyperrealistic, 8k, detailed, photorealistic render",
    "sketch": "raw ink and marker sketch, cross-hatching, gritty lines",
    "glitch": "pure glitch art, datamoshing, pixel sorting, corrupted data aesthetic"
}

# --- Emoji Translation ---
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

def get_level_from_value(value: float, levels: list) -> str:
    """Maps a float value (0-1) to a discrete level string."""
    index = int(value * (len(levels) - 1))
    return levels[index]

def engineer_prompt(user_input: str, glitch_value: float = 0.4, chaos_value: float = 0.6, style: str = "fusion", use_core_aesthetic: bool = True) -> str:
    """
    Dynamically builds a prompt based on user input and creative parameters.
    """
    if not user_input.strip():
        user_input = "a chaotic and surreal vision"

    # 1. Translate Emojis
    translated_prompt = translate_emojis(user_input)

    # 2. Map slider values (0-1) to descriptive levels
    glitch_levels_keys = list(GLITCH_LEVELS.keys())
    chaos_levels_keys = list(CHAOS_LEVELS.keys())
    
    glitch_level_key = get_level_from_value(glitch_value, glitch_levels_keys)
    chaos_level_key = get_level_from_value(chaos_value, chaos_levels_keys)

    # 3. Select modifiers based on levels
    glitch_modifier = GLITCH_LEVELS[glitch_level_key]
    chaos_modifier = CHAOS_LEVELS[chaos_level_key]
    style_modifier = ART_STYLES.get(style, ART_STYLES["fusion"])

    # 4. Assemble the final prompt
    prompt_parts = [
        f"The user's vision is: '{translated_prompt}'.",
        f"Artistic style: {style_modifier}, {chaos_modifier}, {glitch_modifier}.",
        "The final image must be a high-quality, visually striking piece of art."
    ]

    if use_core_aesthetic:
        prompt_parts.insert(1, f"Core aesthetic: {CORE_AESTHETIC}.")
        prompt_parts.append("Interpret the user's vision through the lens of the core aesthetic. Be creative, chaotic, and bold.")
        prompt_parts[3] = "The final image must be a high-quality, visually striking piece of underground art." # Make it more specific again
    
    final_prompt = "\n".join(prompt_parts)
    
    logging.info(f"Engineered Prompt: {final_prompt}")
    return final_prompt.strip()