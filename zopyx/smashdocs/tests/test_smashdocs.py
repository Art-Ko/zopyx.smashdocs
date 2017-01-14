import os
import uuid

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

def test_creste_document():

    sd = make_sd()
    result = sd.new_document(
            title=u'My document',
            description=u'My document description',
            role='editor',
            user_data=make_user_data())
    assert 'documentAccessLink' in result
    assert 'documentId' in result
    assert 'userIdSD' in result
