# -*- coding: utf-8 -*-

################################################################
# zopyx.plone.smashdocs
# (C) 2016,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import os
import jwt
import json
import uuid
import time
import datetime
import tempfile
import requests


def safe_unicode(s):
    if not isinstance(s, unicode):
        return unicode(s, 'utf-8')
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


class Smashdocs(object):

    def __init__(self, partner_url, client_id, client_key, group_id=None):
        self.partner_url = partner_url
        self.client_id = client_id
        self.client_key = client_key
        self.group_id = group_id

    def get_token(self, iss='ajung'):
        iss = str(uuid.uuid4())
        iat = int(time.mktime(datetime.datetime.now().timetuple()))
        jwt_payload = {
            'iat': iat,
            'iss': iss,
            'jti': str(uuid.uuid4())
        }
        return jwt.encode(payload=jwt_payload, key=self.client_key, algorithm="HS256")

    def open_document(self, document_id, title=None, description=None, smashdoc_role=None, user_data={}):

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
            'userRole': smashdoc_role,
            'sectionHistory': True
        }

        url = self.partner_url + '/partner/documents/{}'.format(document_id)
        result = requests.post(url, headers=headers, data=json.dumps(data))
        if result.status_code != 200:
            msg = u'Error (HTTP {}, {})'.format(
                result.status_code, result.content)
            raise SmashdocsError(msg, result)
        return result.json()

    def document_info(self, document_id):

        headers = {
            'x-client-id': self.client_id,
            'content-type': 'application/json',
            'authorization': 'Bearer ' + self.get_token()
        }

        url = self.partner_url + '/partner/documents/{}'.format(document_id)
        result = requests.get(url, headers=headers)
        if result.status_code != 200:
            msg = u'Error (HTTP {}, {})'.format(
                result.status_code, result.content)
            raise SmashdocsError(msg, result)
        return result.json()

    def upload_document(self, filename, title=None, description=None, role=None, user_data=None):

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
            self.partner_url + '/partner/imports/word/upload', headers=headers, files=files)

        if result.status_code != 200:
            msg = u'Upload error (HTTP {}, {}'.format(
                result.status_code, result.content)
            raise UploadError(msg, result)
        return result.json()

    def new_document(self, title=None, description=None, role=None, user_data=None):

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
            self.partner_url + '/partner/documents/create', headers=headers, data=json.dumps(data))
        if result.status_code != 200:
            msg = u'Create error (HTTP {}, {}'.format(
                result.status_code, result.content)
            raise CreationFailed(msg, result)
        return result.json()

    def archive_document(self, document_id):

        headers = {
            'x-client-id': self.client_id,
            'content-type': 'application/json',
            'authorization': 'Bearer ' + self.get_token()
        }
        result = requests.post(
            self.partner_url + '/partner/documents/{}/archive'.format(document_id), headers=headers)
        if result.status_code != 200:
            msg = u'Archive error (HTTP {}, {}'.format(
                result.status_code, result.content)
            raise ArchiveError(msg, result)

    def delete_document(self, document_id):

        headers = {
            'x-client-id': self.client_id,
            'content-type': 'application/json',
            'authorization': 'Bearer ' + self.get_token()
        }

        result = requests.delete(
            self.partner_url + '/partner/documents/{}'.format(document_id), headers=headers)
        if result.status_code != 200:
            msg = u'Deletionerror (HTTP {}, {}'.format(
                result.status_code, result.content)
            raise DeletionError(msg, result)

    def unarchive_document(self, document_id):

        headers = {
            'x-client-id': self.client_id,
            'content-type': 'application/json',
            'authorization': 'Bearer ' + self.get_token()
        }

        result = requests.post(
            self.partner_url + '/partner/documents/{}/unarchive'.format(document_id), headers=headers)
        if result.status_code != 200:
            msg  =u'Archive error (HTTP {}, {})'.format(
                result.status_code, result.content)
            raise UnarchiveError(msg, result)

    def duplicate_document(self, document_id, title=None, description=None, creator_id=None):

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
            self.partner_url + '/partner/documents/{}/duplicate'.format(document_id), headers=headers, data=json.dumps(data))
        if result.status_code != 200:
            msg = u'Copy error (HTTP {}, {})'.format(
                result.status_code, result.content)
            raise CopyError(msg, result)
        return result.json()

    def get_documents(self, group_id=None, user_id=None):

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
            self.partner_url + '/partner/documents/list', headers=headers, params=data)
        if result.status_code != 200:
            msg = _(u'List error (HTTP {}, {})'.format(
                result.status_code, result.content))
            raise SmashdocsError(msg, result)
        return result.json()
