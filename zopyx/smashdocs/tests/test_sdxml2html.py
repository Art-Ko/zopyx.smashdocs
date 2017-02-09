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
