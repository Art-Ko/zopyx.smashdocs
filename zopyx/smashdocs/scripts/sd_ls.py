# -*- coding: utf-8 -*-*

################################################################
# zopyx.smashdocs
# (C) 2017, ZOPYX/Andreas Jung, D-72074 Tübingen
################################################################


import click
import pprint

from .util import client


@click.command()
@click.option('--user', default=None, help='Smashdocs User ID')
@click.option('--group', default=None, help='Smashdocs Group ID')
def list_documents(user=None, group=None):

    if not group and not user:
        raise ValueError('You specify at least --group and/or --user')

    for x in client.get_documents(user_id=user, group_id=group):
        pprint.pprint(x)


if __name__ == '__main__':
    list_documents()
