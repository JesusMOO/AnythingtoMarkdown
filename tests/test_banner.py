from sptool.banner import render_banner


def test_banner_contains_sptool_name():
    assert "SPTOOL" in render_banner().upper()
