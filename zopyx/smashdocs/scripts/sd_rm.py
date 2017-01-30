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
@click.argument('documents', nargs=-1)
def remove_documents(user=None, documents=[]):

    for document_id in documents:
        client.delete_document(document_id)
        print('deleted {}'.format(document_id))

if __name__ == '__main__':
    remove_documents()
