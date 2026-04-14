NORMAL_HELP = """usage: sptool [--help] [--version] <input> [output]
sptool ultra start
sptool ultra exit
"""


def render_help(mode: str) -> str:
    if mode == "ultra":
        return NORMAL_HELP + "\nCurrent mode: ultra\n"
    return NORMAL_HELP
