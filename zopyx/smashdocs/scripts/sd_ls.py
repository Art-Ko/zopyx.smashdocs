# -*- coding: utf-8 -*-*

################################################################
# zopyx.smashdocs
# (C) 2017, ZOPYX/Andreas Jung, D-72074 Tübingen
################################################################


import os
import click

from zopyx.smashdocs.api import Smashdocs


client = Smashdocs(
        partner_url=os.environ['SMASHDOCS_PARTNER_URL'] ,
        client_id=os.environ['SMASHDOCS_CLIENT_ID'] ,
        client_key=os.environ['SMASHDOCS_CLIENT_KEY'])


@click.command()
@click.option('--user', default=None, help='Smashdocs User ID')
@click.option('--group', default=None, help='Smashdocs Group ID')
def list_documents(user=None, group=None):

    for x in client.get_documents(user_id=user, group_id=group):
        print x

if __name__ == '__main__':
    list_documents()
