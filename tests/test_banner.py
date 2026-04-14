from sptool.banner import render_banner


def test_banner_contains_sptool_name():
    banner = render_banner()
    assert "██████" in banner
    assert "╚══════╝" in banner
