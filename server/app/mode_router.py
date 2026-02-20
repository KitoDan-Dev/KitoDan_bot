from typing import Literal

ChatMode = Literal["friend", "sales", "creative", "automation", "auto"]

MODE_INSTRUCTIONS = {
    "friend": "Friend mode: keep it warm, practical, brief, and motivating.",
    "sales": "Sales mode: include ICP, offer, angle, proof, CTA, objections, and next steps.",
    "creative": "Creative mode: include concept, references, shot list, pipeline, risks, and alternatives.",
    "automation": "Automation mode: include logic diagram, tools, implementation steps, checklist, and validation.",
}

_KEYWORDS = {
    "sales": ["client", "budget", "proposal", "price", "pricing", "campaign", "lead", "close", "negotiation"],
    "creative": ["video", "shot", "script", "scene", "vfx", "3d", "edit", "cinematic", "prompt"],
    "automation": ["automation", "crm", "workflow", "integration", "n8n", "pipeline", "form", "zap"],
}


def resolve_mode(mode: ChatMode, message: str) -> str:
    if mode != "auto":
        return mode

    text = message.lower()
    for candidate, keys in _KEYWORDS.items():
        if any(k in text for k in keys):
            return candidate
    return "friend"


def mode_instruction(mode: ChatMode, message: str) -> str:
    resolved = resolve_mode(mode, message)
    return MODE_INSTRUCTIONS.get(resolved, MODE_INSTRUCTIONS["friend"])
