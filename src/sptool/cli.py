from sptool import __version__
from sptool.banner import render_banner
from sptool.helptext import render_help
from sptool.modes import get_mode


def main(argv=None) -> int:
    args = list(argv or [])
    mode = get_mode()
    if not args:
        print(render_banner())
        print(render_help(mode))
        return 0
    if args == ["--help"]:
        print(render_help(mode))
        return 0
    if args == ["--version"]:
        print(__version__)
        return 0
    return 0
