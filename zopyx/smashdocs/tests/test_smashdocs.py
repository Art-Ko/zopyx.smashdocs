import os
import uuid
import pytest

from .. import api


client_id = os.environ.get('SMASHDOCS_CLIENT_ID')
client_key = os.environ.get('SMASHDOCS_CLIENT_KEY')
client_partner_url = os.environ.get('SMASHDOCS_PARTNER_URL')
group_id = str(uuid.uuid4())

def make_sd():
    return api.Smashdocs(client_partner_url, client_id, client_key, group_id)


def make_user_data():
    return dict(
        email='test@foo.com',
        firstname=u'Henry',
        lastname=u'Miller',
        userId=u'testuser',
        company=u'Dummies Ltd')

def test_create_document():

    sd = make_sd()
    result = sd.new_document(
            title=u'My document',
            description=u'My document description',
            role='editor',
            user_data=make_user_data())
    assert 'documentAccessLink' in result
    assert 'documentId' in result
    assert 'userIdSD' in result

    document_id = result['documentId']

    # archiving and duplicate archiving
    sd.archive_document(document_id)
    with pytest.raises(api.ArchiveError):
        sd.archive_document(document_id)

    # deletion and duplicated deletion
    sd.delete_document(document_id)
    with pytest.raises(api.DeletionError):
        sd.delete_document(document_id)


def test_create_document_long_title():

    sd = make_sd()
    with pytest.raises(api.CreationFailed):
        result = sd.new_document(
                title=u'My document'*500,
                description=u'My document description'*500,
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
