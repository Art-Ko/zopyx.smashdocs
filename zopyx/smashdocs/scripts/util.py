# -*- coding: utf-8 -*-*

################################################################
# zopyx.smashdocs
# (C) 2017, ZOPYX/Andreas Jung, D-72074 Tübingen
################################################################

import os

from zopyx.smashdocs import api

client = api.Smashdocs(
    partner_url=os.environ['SMASHDOCS_PARTNER_URL'],
    client_id=os.environ['SMASHDOCS_CLIENT_ID'],
    client_key=os.environ['SMASHDOCS_CLIENT_KEY'])
