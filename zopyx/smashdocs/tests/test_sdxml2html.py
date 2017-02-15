# -*- coding: utf-8 -*-*

################################################################
# zopyx.smashdocs
# (C) 2017, ZOPYX/Andreas Jung, D-72074 Tübingen
################################################################


import os

from zopyx.smashdocs.sdxml2html import sdxml2html


def test_convert():
    in_name = os.path.join(os.path.dirname(__file__), 'test.xml')
    out_fn = sdxml2html.sdxml2html(in_name)
    assert out_fn.endswith('.html')
    with open(out_fn, 'rb') as fp:
        html = fp.read()
        assert html.startswith(b'<div id="sd-content"')
    os.unlink(out_fn)


def test_convert_data():
    in_name = os.path.join(os.path.dirname(__file__), 'test.xml')
    with open(in_name, 'rb') as fp:
        xml = fp.read()
    html = sdxml2html.sdxml2html_data(xml)
    assert html.startswith(b'<div id="sd-content"')
