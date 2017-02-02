# -*- coding: utf-8 -*-*

################################################################
# zopyx.smashdocs
# (C) 2017, ZOPYX/Andreas Jung, D-72074 Tübingen
################################################################

import uuid
import os
import jwt
import json
import uuid
import time
import datetime
import requests
import six


from .requests_logger import debug_requests

VERIFY = True


if six.PY2:

    def safe_unicode(s):
        if not isinstance(s, unicode):  # noqa
            return unicode(s, 'utf-8')
        return s

else:

    def safe_unicode(s):
        if not isinstance(s, str):
            return s.decode('utf-8')
        return s


class SmashdocsError(Exception):

    def __init__(self, msg, result):
        super(SmashdocsError, self).__init__(msg)
        self.msg = msg
        self.result = result


class CreationFailed(SmashdocsError):
    """ Unable to create a new document """


class UploadError(SmashdocsError):
    """ DOCX upload or import error"""


class ArchiveError(SmashdocsError):
    """ Archiving error """


class UnarchiveError(SmashdocsError):
    """ Unarchiving error """


class DeletionError(SmashdocsError):
    """ Deletion error """


class CopyError(SmashdocsError):
    """ Deletion error """


class DocumentInfoError(SmashdocsError):
    """ Error retrieving document info """


class UpdateMetadataError(SmashdocsError):
    """ Error retrieving document info """


class OpenError(SmashdocsError):
    """ Error opening file """


allowed_sd_roles = ('editor', 'reader', 'approver', 'commentator')


def check_role(role):
    if role not in allowed_sd_roles:
        raise ValueError('Unsupported role in Smashdocs: {0} (allowed: {1})'.format(
            role, allowed_sd_roles))


def check_length(s, max_len):

    if six.PY2:
        if not isinstance(s, unicode):
            raise TypeError('{0} must be unicode'.format(s))
    elif six.PY3:
        if not isinstance(s, str):
            raise TypeError('{0} must be str'.format(s))

    if len(s) > max_len:
        raise ValueError('"{0}" too long (max {1} chars)'.format(s, max_len))


def check_title(s):
    return check_length(s, 200)


def check_description(s):
    return check_length(s, 400)


def check_email(s):
    return check_length(s, 150)


def check_firstname(s):
    return check_length(s, 150)


def check_lastname(s):
    return check_length(s, 150)


def check_company(s):
    return check_length(s, 150)


def check_userid(s):
    if not s:
        raise ValueError('"userId" not specified')


def check_uuid(uuid_string):
    """ Validate that a UUID string is in fact a valid uuid4.  Happily, the uuid
        module does the actual checking for us.  It is vital that the 'version'
        kwarg be passed to the UUID() call, otherwise any 32-character hex string
        is considered valid.
    """

    try:
        val = uuid.UUID(uuid_string, version=4)
    except ValueError:
        # If it's a value error, then the string
        # is not a valid hex code for a UUID.
        raise ValueError('Invalid UUID {}'.format(uuid_string))

    # If the uuid_string is a valid hex code,
    # but an invalid uuid4,
    # the UUID.__init__ will convert it to a
    # valid uuid4. This is bad for validation purposes.

    if str(val) != uuid_string:
        raise ValueError('Invalid UUID {}'.format(uuid_string))


def check_user_data(user_data):

    check_firstname(user_data.get('firstname'))
    check_lastname(user_data.get('lastname'))
    check_email(user_data.get('email'))
    check_company(user_data.get('company'))
    check_userid(user_data.get('userId'))


class Smashdocs(object):

    def __init__(self, partner_url, client_id, client_key, group_id=None):
        """ Constructor

            :param partner_url: Smashdocs server URL
            :param client_id: Smashdocs Client ID
            :param client_key: Smashdocs Client Key
            :param group_id: Smashdoc Group ID
        """

        self.partner_url = partner_url
        self.client_id = client_id
        self.client_key = client_key
        self.group_id = group_id

    def __repr__(self):
        return '<Smashdocs {0}>'.format(self.__dict__)

    def get_token(self):

        if not self.client_key:
            raise ValueError('No client key configured or specified')

        iss = str(uuid.uuid4())
        iat = int(time.mktime(datetime.datetime.now().timetuple()))
        jwt_payload = {
            'iat': iat,
            'iss': iss,
            'jti': str(uuid.uuid4())
        }
        return jwt.encode(payload=jwt_payload, key=self.client_key, algorithm="HS256").decode('utf-8')

    def open_document(self, document_id, role=None, user_data={}):
        """ Open document

            :param document_id: Document id
            :param role: Smashdoc role: editor|reader|approver|commentator
            :param user_data: Dict with user data, see Smashdocs Partner API
        """

        check_role(role)
        check_user_data(user_data)
        check_uuid(document_id)

        headers = {
            'x-client-id': self.client_id,
            'content-type': 'application/json',
            'authorization': 'Bearer ' + self.get_token()
        }
        data = {
            'user': user_data,
            'groupId': self.group_id,
            'userRole': role,
            'sectionHistory': True
        }

        url = self.partner_url + '/partner/documents/{0}'.format(document_id)
        result = requests.post(url, headers=headers,
                               data=json.dumps(data), verify=VERIFY)
        if result.status_code != 200:
            msg = u'Error (HTTP {0}, {1})'.format(
                result.status_code, result.content)
            raise OpenError(msg, result)
        return result.json()

    def document_info(self, document_id):
        """ Get document information

            :param document_id: Smashdocs document id
        """

        check_uuid(document_id)

        headers = {
            'x-client-id': self.client_id,
            'content-type': 'application/json',
            'authorization': 'Bearer ' + self.get_token()
        }

        url = self.partner_url + '/partner/documents/{0}'.format(document_id)
        result = requests.get(url, headers=headers, verify=VERIFY)
        if result.status_code != 200:
            msg = u'Error (HTTP {0}, {1})'.format(
                result.status_code, result.content)
            raise DocumentInfoError(msg, result)
        return result.json()

    def upload_document(self, filename, title=None, description=None, role=None, user_data=None):
        """ Upload DOCX document

            :param filename: DOCX filename
            :param title: title of document
            :param description: description of document
            :param role: Smashdoch role: editor|reader|approver|commentator
            :param user_data: dict with user data
            :rtype: Smashdocs return datastructure (see Partner API docs for details)
        """

        check_title(title)
        check_description(description)
        check_role(role)
        check_user_data(user_data)

        headers = {
            'x-client-id': self.client_id,
            'authorization': 'Bearer ' + self.get_token()
        }

        data = {
            'user': user_data,
            'title': safe_unicode(title),
            'description': safe_unicode(description),
            'groupId': self.group_id,
            'userRole': role,
            'sectionHistory': True
        }

        files = {
            'data': (None, json.dumps(data), 'application/json'),
            'file': ('dummy.docx', open(filename, 'rb'), 'application/octet-stream'),
        }

        result = requests.post(
            self.partner_url + '/partner/imports/word/upload', headers=headers, files=files, verify=VERIFY)

        if result.status_code != 200:
            msg = u'Upload error (HTTP {0}, {1}'.format(
                result.status_code, result.content)
            raise UploadError(msg, result)
        return result.json()

    def new_document(self, title=None, description=None, role=None, user_data=None):
        """ Create a new document

            :param title: title of document
            :param description: description of document
            :param role: Smashdocs role: editor|reader|approver|commentator
            :param user_date: Smashdocs user data, see Smashdocs Partner API
        """

        check_title(title)
        check_description(description)
        check_role(role)
        check_user_data(user_data)

        headers = {
            'x-client-id': self.client_id,
            'content-type': 'application/json',
            'authorization': 'Bearer ' + self.get_token()
        }

        data = {
            'user': user_data,
            'title': safe_unicode(title),
            'description': safe_unicode(description),
            'groupId': self.group_id,
            'userRole': role,
            'sectionHistory': True
        }

        result = requests.post(
            self.partner_url + '/partner/documents/create', headers=headers, data=json.dumps(data), verify=VERIFY)
        if result.status_code != 200:
            msg = u'Create error (HTTP {0}, {1}'.format(
                result.status_code, result.content)
            raise CreationFailed(msg, result)
        return result.json()

    def update_metadata(self, document_id, **kw):
        """ Update metadata"""

        check_uuid(document_id)

        headers = {
            'x-client-id': self.client_id,
            'content-type': 'application/json',
            'authorization': 'Bearer ' + self.get_token()
        }

        url = self.partner_url + \
            '/partner/documents/{0}/metadata'.format(document_id)
        result = requests.post(url, headers=headers,
                               data=json.dumps(kw), verify=VERIFY)
        if result.status_code != 200:
            msg = u'Update metadata error (HTTP {0}, {1}'.format(
                result.status_code, result.content)
            raise UpdateMetadataError(msg, result)
        return result.json()

    def archive_document(self, document_id):
        """ Archive document by ``document_id``

            :param document_id: Smashdocs document id
            :rtype: None
        """

        check_uuid(document_id)

        headers = {
            'x-client-id': self.client_id,
            'content-type': 'application/json',
            'authorization': 'Bearer ' + self.get_token()
        }
        result = requests.post(
            self.partner_url + '/partner/documents/{0}/archive'.format(document_id), headers=headers, verify=VERIFY)
        if result.status_code != 200:
            msg = u'Archive error (HTTP {0}, {1}'.format(
                result.status_code, result.content)
            raise ArchiveError(msg, result)

    def delete_document(self, document_id):
        """ Delete document by ``document_id``

            :param document_id: Smashdocs document id
            :rtype: None
        """

        check_uuid(document_id)

        headers = {
            'x-client-id': self.client_id,
            'content-type': 'application/json',
            'authorization': 'Bearer ' + self.get_token()
        }

        result = requests.delete(
            self.partner_url + '/partner/documents/{0}'.format(document_id), headers=headers, verify=VERIFY)
        if result.status_code != 200:
            msg = u'DeletionError (HTTP {0}, {1}'.format(
                result.status_code, result.content)
            raise DeletionError(msg, result)

    def unarchive_document(self, document_id):
        """ Unarchive document by ``document_id``

            :param document_id: Smashdocs document id
            :rtype: None
        """

        check_uuid(document_id)

        headers = {
            'x-client-id': self.client_id,
            'content-type': 'application/json',
            'authorization': 'Bearer ' + self.get_token()
        }

        result = requests.post(
            self.partner_url + '/partner/documents/{0}/unarchive'.format(document_id), headers=headers, verify=VERIFY)
        if result.status_code != 200:
            msg = u'Archive error (HTTP {0}, {1})'.format(
                result.status_code, result.content)
            raise UnarchiveError(msg, result)

    def duplicate_document(self, document_id, title=None, description=None, creator_id=None):
        """ Duplicate document

            :param documen_id: Smashdocs document id to be duplicated
            :param title: title of new document
            :param description: description of new document
            :param creator_id: Creator id
        """

        check_title(title)
        check_description(description)
        check_uuid(document_id)

        headers = {
            'x-client-id': self.client_id,
            'content-type': 'application/json',
            'authorization': 'Bearer ' + self.get_token(),
        }

        data = {
            'title': title,
            'description': description,
            'creatorUserId': creator_id
        }

        result = requests.post(
            self.partner_url + '/partner/documents/{0}/duplicate'.format(document_id), headers=headers, data=json.dumps(data), verify=VERIFY)
        if result.status_code != 200:
            msg = u'Copy error (HTTP {0}, {1})'.format(
                result.status_code, result.content)
            raise CopyError(msg, result)
        return result.json()

    def get_documents(self, group_id=None, user_id=None):
        """ Get all document """

        headers = {
            'x-client-id': self.client_id,
            'content-type': 'application/json',
            'authorization': 'Bearer ' + self.get_token(),
        }

        data = dict()
        if group_id:
            data['groupId'] = group_id
        if user_id:
            data['userId'] = user_id

        result = requests.get(
            self.partner_url + '/partner/documents/list', headers=headers, params=data, verify=VERIFY)
        if result.status_code != 200:
            msg = u'List error (HTTP {0}, {1})'.format(
                result.status_code, result.content)
            raise SmashdocsError(msg, result)
        return result.json()
