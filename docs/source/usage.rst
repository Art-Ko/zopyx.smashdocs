Using the Smashdocs API from Python
-----------------------------------

In order to use Smashdocs from Python you need to obtain the following data from
your Smashdocs provider:

- Partner URL (URL of Smashdocs service)
- Client ID (used for authentication)
- Client Key (used for authentication) 


Prequisite
++++++++++

The following examples are written for Python 2.7 and use unicode strings as
parameters.  In general all parameters must be passed as unicode strings (not
as UTF-8 encoded byte strings).  Unicodeness is strongly checked. There is no
implicit conversion from utf-8 parameters to unicode strings.

Creating client handle to Smashdocs
+++++++++++++++++++++++++++++++++++

.. code::

    from zopyx.smashdocs.api import Smashdocs

    # first you need to instantiate a client instance of the `Smashdocs`
    # connector class. The `group_id` is used to group all documents together
    # belonging to a particular user group (e.g. a work group working on one or more 
    # document). The `client` is from now on used for all interactions with Smashdocs.

    client = Smashdocs(partner_url, client_id, client_key, group_id)

Upload a DOCX document to Smashdocs
+++++++++++++++++++++++++++++++++++

The following code will upload a given DOCX file from the local filesystem
into Smashdocs and create a document instance inside Smashdocs. The API
call returns all relevant data including the document id of the document inside
Smashdocs and an URL that can be used open the uploaded document inside your browser
for editing.

The `filename` parameter is the path to a locally stored DOCX file. `title`
and `description` are arbitrary unicode strings (metadata length restrictions
apply and are partly checked within the module). 

The `role` parameter is one of the four roles in Smashdocs: 

- `reader`
- `commentator`
- `editor`
- `approver`    

You also need a `user_data` datastructure containing information about the current
user using the Smashdocs API. The fields of the dict structure are obvious. Please
keep in might that Smashdocs does not provide you with an explicit user management.
The `userId` field represents the user within Plone.

.. code::

    user_data = dict(
        email=u'test@foo.com',
        firstname=u'Henry',
        lastname=u'Miller',
        userId=u'testuser',
        company=u'Dummies Ltd')


    result = client.upload_document(
        filename='sample.docx',
        title=u'My document',
        description=u'My description',
        role='editor',
        user_data=user_data)
    
    # preserve the id of the document in Smashdocs for further usage
    document_id = result['documentId']

    # this URL can be used to access the uploaded document through the browser
    document_url = result['documentAccessLink']


Creating a new empty document
+++++++++++++++++++++++++++++

Creating a new empty document works exactly the same way as uploading
a DOCX file except that you do not need any document here.


.. code::    
        
    result = client.new_document(
        title=u'My document',
        description=u'My description',
        role='editor',
        user_data=user_data)
    
    # preserve the id of the document in Smashdocs for further usage
    document_id = result['documentId']

    # this URL can be used to access the uploaded document through the browser
    document_url = result['documentAccessLink']

Open an existing Smashdocs document by its ID
+++++++++++++++++++++++++++++++++++++++++++++

With a given `document_id` you can open (obtain its access URL) using the following code.
In this case we open the document for read-only access (role=reader) with a different
user context.

.. code::

    user_datai2 = dict(
        email=u'mike@foo.com',
        firstname=u'Mike',
        lastname=u'Reader',
        userId=u'mike-reader',
        company=u'Dummies Ltd')

    result = client.open_document(document_id, 'reader', user_data2)

    # this URL can be used to access the uploaded document through the browser
    document_url = result['documentAccessLink']


Archiving and unarchiving a Smashdocs document
++++++++++++++++++++++++++++++++++++++++++++++

The API provides the following two methods for archiving and unarching
a Smashdocs document given by its `document_id`.

.. code::

    client.archive_document(document_id)

    client.unarchive_document(document_id)

Trying to archive or unarchive a document twice will lead to an API exception.


Deleting a Smashdocs document
+++++++++++++++++++++++++++++

A Smashdocs document given by its `document_id` can be deleted using
`delete_document()`.

.. code ::

    client.delete_document(document_id)

Trying to delete a document twice will lead to an API exception.

Duplicating Smashdocs content
+++++++++++++++++++++++++++++

An existing Smashdocs document can be duplicated with a new `title`
and a new `description`. The API call return a new document id and
an new access URL.

.. code::

   result = client.duplicate_document(
            document_id,
            title=u'new title',
            description=u'new description',
            creator_id='some_user_id)

    new_document_id = result['documentId']
    new_document_url = result['documentAccessLink']


Listing word templates
++++++++++++++++++++++

An export to word requires a word template.  This API method returns a list of
available word templates with id, name and description. See also
https://documentation.smashdocs.net/api_guide.html#get-partner-templates-word


.. code::

   templates = client.list_templates()


Exporting content
+++++++++++++++++

You can export Smashdocs content to either HTML, SDXML or DOCX. Both HTML
and SDXML exports produce a ZIP file (index.xml + images/* subfolder).

.. code::

   output_filename = client.export_document(
            document_id,
            format='docx',
            template_id=docx_template_id, # see above)
            user_id='admin')

