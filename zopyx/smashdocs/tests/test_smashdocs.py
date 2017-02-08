# -*- coding: utf-8 -*-*

################################################################
# zopyx.smashdocs
# (C) 2017, ZOPYX/Andreas Jung, D-72074 Tübingen
################################################################


import os
import uuid
import pytest

from zopyx.smashdocs import api


client_id = os.environ.get('SMASHDOCS_CLIENT_ID')
client_key = os.environ.get('SMASHDOCS_CLIENT_KEY')
client_partner_url = os.environ.get('SMASHDOCS_PARTNER_URL')
group_id = str(uuid.uuid4())

if not client_id:
    raise ValueError('SMASHDOCS_CLIENT_ID not set')
if not client_key:
    raise ValueError('SMASHDOCS_CLIENT_KEY not set')
if not client_partner_url:
    raise ValueError('SMASHDOCS_PARTNER_URL not set')


def make_sd():
    return api.Smashdocs(client_partner_url, client_id, client_key, group_id)


def make_user_data():
    return dict(
        email=u'test@foo.com',
        firstname=u'Henry',
        lastname=u'Miller',
        userId=u'testuser',
        company=u'Dummies Ltd')


def test_create_document():

    sd = make_sd()
    result = sd.new_document(
        title=u'My document - üöäß',
        description=u'My document description - üöäß',
        role='editor',
        user_data=make_user_data())
    assert 'documentAccessLink' in result
    assert 'documentId' in result
    assert 'userIdSD' in result

    document_id = result['documentId']

    document_info = sd.document_info(document_id)

    assert document_info['archived'] == False
    assert document_info['title'] == u'My document - üöäß'
    assert document_info['description'] == u'My document description - üöäß'
    assert document_info['hasOpenedDocument'] == False
    assert document_info['hasUnreadConversationChanges'] == False
    assert document_info['hasUnreadSectionChanges'] == False
    assert document_info['status'] == u'draft'

    result = sd.open_document(
        document_id, role='editor', user_data=make_user_data())

    # deletion and duplicated deletion
    sd.delete_document(document_id)
    with pytest.raises(api.DeletionError):
        sd.delete_document(document_id)


def test_create_and_open():

    sd = make_sd()
    result = sd.new_document(
        title=u'My document - üöäß',
        description=u'My document description - üöäß',
        role='editor',
        user_data=make_user_data())
    document_id = result['documentId']

    result = sd.open_document(
        document_id,
        'reader',
        user_data=make_user_data())

    assert 'documentAccessLink' in result


def test_open_invalid_document_id():

    sd = make_sd()

    with pytest.raises(ValueError):
        result = sd.open_document(
            'no such documentid',
            'reader',
            user_data=make_user_data())


def test_create_document_long_title():

    sd = make_sd()
    with pytest.raises(ValueError):
        result = sd.new_document(
            title=u'My document' * 500,
            description=u'My document description' * 500,
            role='editor',
            user_data=make_user_data())


def test_upload_docx():

    sd = make_sd()
    filename = os.path.join(os.path.dirname(__file__), 'test.docx')
    result = sd.upload_document(
        filename,
        title=u'My document',
        description=u'My document description',
        role='editor',
        user_data=make_user_data())
    assert 'documentAccessLink' in result
    assert 'documentId' in result
    assert 'userIdSD' in result

    document_id = result['documentId']
    sd.delete_document(document_id)


def test_upload_non_docx():

    sd = make_sd()
    filename = os.path.join(os.path.dirname(__file__), 'test_smashdocs.py')
    with pytest.raises(api.UploadError):
        result = sd.upload_document(
            filename,
            title=u'My document',
            description=u'My document description',
            role='editor',
            user_data=make_user_data())


def test_duplicate_document():

    sd = make_sd()
    result = sd.new_document(
        title=u'My document',
        description=u'My document description',
        role='editor',
        user_data=make_user_data())

    document_id = result['documentId']
    new_result = sd.duplicate_document(
        document_id,
        title=u'My new title',
        description=u'My new description',
        creator_id='testuser')

    sd.delete_document(document_id)
    sd.delete_document(new_result['documentId'])


def test_update_metadata():

    sd = make_sd()
    result = sd.new_document(
        title=u'My document',
        description=u'My document description',
        role='editor',
        user_data=make_user_data())

    document_id = result['documentId']
    sd.update_metadata(
        document_id,
        title=u'Title changed',
        description='Description changed')

    document_info = sd.document_info(document_id)
    assert document_info['title'] == u'Title changed'
    assert document_info['description'] == u'Description changed'

    sd.delete_document(document_id)


def test_document_info_unknown_doc_id():

    sd = make_sd()
    with pytest.raises(ValueError):
        document_info = sd.document_info('no such id')


def test_archiving():

    sd = make_sd()
    result = sd.new_document(
        title=u'My document',
        description=u'My document description',
        role='editor',
        user_data=make_user_data())

    document_id = result['documentId']

    # archiving and duplicate archiving
    sd.archive_document(document_id)
    with pytest.raises(api.ArchiveError):
        sd.archive_document(document_id)

    sd.unarchive_document(document_id)
    with pytest.raises(api.UnarchiveError):
        sd.unarchive_document(document_id)

    sd.delete_document(document_id)


def test_listings():

    sd = make_sd()
    result = sd.new_document(
        title=u'My document',
        description=u'My document description',
        role='editor',
        user_data=make_user_data())
    result = sd.get_documents(user_id='testuser')


def test_list_templates():

    sd = make_sd()
    result = sd.list_templates()
    assert isinstance(result, list)
    assert len(result) > 0
    assert 'id' in result[0]
    assert 'name' in result[0]
    assert 'description' in result[0]


def _make_export_document():

    sd = make_sd()

    result = sd.new_document(
        title=u'My document',
        description=u'My document description',
        role='editor',
        user_data=make_user_data())

    return result['documentId']


def test_export_docx():

    sd = make_sd()
    document_id = _make_export_document()
    user_id = 'admin'

    templates = sd.list_templates()

    out_fn = sd.export_document(
        document_id, user_id, format='docx', template_id=templates[0]['id'])
    assert out_fn.endswith('.docx')
    sd.delete_document(document_id)
    os.unlink(out_fn)


def test_export_html():

    sd = make_sd()
    document_id = _make_export_document()
    user_id = 'admin'

    out_fn = sd.export_document(document_id, user_id, format='html')
    assert out_fn.endswith('.zip')
    sd.delete_document(document_id)
    os.unlink(out_fn)


def test_export_sdxml():

    sd = make_sd()
    document_id = _make_export_document()
    user_id = 'admin'

    out_fn = sd.export_document(document_id, user_id, format='sdxml')
    assert out_fn.endswith('.zip')
    sd.delete_document(document_id)
    os.unlink(out_fn)
