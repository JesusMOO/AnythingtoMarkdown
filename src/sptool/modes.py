import os


def get_mode() -> str:
    return "ultra" if os.getenv("TOOL_MODE", "").lower() == "ultra" else "normal"
