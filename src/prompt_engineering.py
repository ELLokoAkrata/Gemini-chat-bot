# src/prompt_engineering.py
import logging

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
    "none": "no specific art style, raw user input",
    "fusion": "hyperdetailed render, ink and marker textures, digital painting",
    "photorealistic": "hyperrealistic, 8k, detailed, photorealistic render",
    "sketch": "raw ink and marker sketch, cross-hatching, gritty lines, raw textures, raw lines, frenetic energy",
    "glitch": "pure glitch art, datamoshing, pixel sorting, corrupted data aesthetic",
    "anime_fusion": "Dynamic shonen anime style, fusing the painterly backgrounds of Studio Ghibli with the iconic character design and high-energy action of Fullmetal Alchemist and Dragon Ball Z. Clean line art, vibrant colors, expressive characters.",
    "isometric": "A clean and detailed isometric diorama. Rendered in a 2.5D perspective with sharp edges and a focus on clear, geometric shapes. Often associated with vector art or low-poly design.",
    "zine": "Raw, gritty, anarcho-punk fanzine aesthetic. High contrast, photocopied textures, distressed collage, hand-drawn, aggressive linework, underground metal and hardcore vibe. Chaotic and uncompromising, DIY ethos, ink and stencil art.",
    "logo": "Bold, iconic, anarcho-punk logo design. Distressed, raw, and impactful, suitable for underground bands or movements. Strong typography, stencil elements, high contrast, black and white, with a rebellious, anti-establishment feel"
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
    "🌿": "cannabis leaf, marijuana, herb, nature, relaxation, plant-based",
    "🍺": "beer mug, ale, celebration, social gathering, tavern"
}

# --- Core Aesthetics Grimoire ---
CORE_AESTHETICS = {
    "none": "no specific core aesthetic, raw user input",
    "anarcho_punk": "anarcho-punk,rebel, leather jacket, patches, piercings, tattoos, punk rock, chaotic, DIY, gritty, raw, putrid, decay, dark circles, angry faces, spikes, fanzines, underground band posters, symbols of anarchy, chaosphere, acab",
    "chaos_magick": "Esoteric sigils, occult symbolism, ritualistic elements, astral planes, controlled chaos. A blend of ancient mysticism and modern rebellion, where intent shapes reality. Dark, mysterious, and powerful.",
    "cypherpunk": "Digital anonymity, cryptography, glitchy terminal screens, dark web aesthetic, hooded figures in shadows, flowing green code. A vision of fighting for privacy and freedom in a dystopian digital age. The aesthetic of the anonymous hacker resisting surveillance.",
    "post-anarchist": "Abstract concepts, deconstructed symbols, philosophical undertones, rhizomatic structures, questioning power in all its forms. A more academic and introspective take on anarchy, focusing on fluidity and anti-dogmatism.",
    "anarcho-syndicalist": "Collective action, solidarity, workers' symbols (gears, fists, wheat), bold propaganda poster style. Focus on community, mutual aid, and organized labor as a revolutionary force. Hopeful, powerful, and united.",
    "eco-anarchist": "Nature reclaiming urban spaces, overgrown ruins, DIY solarpunk technology, feral aesthetics. A world where humanity lives in harmony with a wild, untamed ecosystem. Lush, green, and resilient.",
    "insurrectionary": "Explosive energy, street conflict, masked and hooded figures, graffiti tags, shattered glass, a sense of immediate and uncompromising action. The aesthetic of the riot and the direct confrontation with power. Urgent, raw, and chaotic.",
    "anarcho-vaporwave": "The ruins of digital capitalism. Glitchy, nostalgic visuals of abandoned malls and forgotten web 1.0 interfaces, reclaimed by squatters and hackers. A critique of consumer culture using its own decaying aesthetic. Surreal, melancholic, and deeply subversive.",
    "cyber_gothic": "dark, futuristic, neo-gothic, tech-noir, dystopian, melancholic, advanced, intricate details",
    "existential_void": "minimalist, abstract, dark, philosophical, empty spaces, stark contrasts, introspective"
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

def engineer_prompt(user_input: str, glitch_value: float = 0.4, chaos_value: float = 0.6, style: str = "fusion", selected_core_aesthetic: str = "anarcho_punk") -> str:
    """
    Dynamically builds a prompt based on user input and creative parameters.
    """
    if not user_input.strip():
        user_input = "a chaotic and surreal vision of anarchy and chaos in anarcho punk mind"

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
    
    # Obtener la descripción de la estética central
    core_aesthetic_description = CORE_AESTHETICS.get(selected_core_aesthetic, "")


    # 4. Assemble the final prompt
    prompt_parts = [
        f"The user's vision is: '{translated_prompt}'."
    ]

    # Solo añadir modificadores si no estamos en modo "raw"
    if style != "none":
        prompt_parts.append(f"Artistic style: {style_modifier}, {chaos_modifier}, {glitch_modifier}.")
    
    prompt_parts.append("The final image must be a high-quality, visually striking piece of art.")

    if core_aesthetic_description and selected_core_aesthetic != "none": # Si se eligió una estética central
        prompt_parts.insert(1, f"Core aesthetic: {core_aesthetic_description}.")
        prompt_parts.append("Interpret the user's vision through the lens of the core aesthetic. Be creative, chaotic, and bold.")
        # Ajustar el índice del prompt final según si se añadió el estilo
        final_image_prompt_index = 2 if style == "none" else 3
        prompt_parts[final_image_prompt_index] = "The final image must be a high-quality, visually striking piece of underground DIY generative art of anarchy and chaos."


    final_prompt = "\n".join(prompt_parts)
    
    logging.info(f"Engineered Prompt: {final_prompt}")
    return final_prompt.strip()