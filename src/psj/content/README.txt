psj.content
***********

:Test-Layer: integration

Content types for the Plone Scholarly Journal.

The `psj.content` package currently supports the following content
types:

- ``PSJDocument``

  A document containing metadata and a word or OpenOffice.org
  document.

- ``PSJIssue``

  A representation of a magazine issue. It is folderish and accepts
  only PSJDocuments as content.

- ``PSJVolume``

  A representation of a collection of issues, most often a
  year. PSJVolumes are folderish and accept issues as content.

- ``PSJMagazine``

  A representation of a magazine or series. It is folderish and
  accepts volumes, issues and documents as content.

- ``PSJBook``

  A representation of a book (review).

- ``PSJFile``

  A representation of any media file.

Setting up and logging in
=========================

We use zope.testbrowser to simulate browser interaction in order to
show the main flow of pages. This is not a true functional test,
because we also inspect and modify the internal state of the ZODB, but
it is a useful way of making sure we test the full end-to-end process
of creating and modifying content::

   >>> from Products.Five.testbrowser import Browser
   >>> browser = Browser()
   >>> portal_url = self.portal.absolute_url()
   >>> browser.handleErrors = False
   >>> self.portal.error_log._ignored_exceptions = ()

Finally, we need to log in as the portal owner, i.e. an administrator user. We
do this from the login page::

   >>> from Products.PloneTestCase.setup import portal_owner, default_password

   >>> browser.open(portal_url + '/login_form?came_from=' + portal_url)
   >>> browser.getControl(name='__ac_name').value = portal_owner
   >>> browser.getControl(name='__ac_password').value = default_password
   >>> browser.getControl(name='submit').click()


Addable content
===============

Adding PSJDocuments
-------------------

PSJ documents can be added anywhere and contain the real documents
(office documents in odf or PDF-A format)::

   >>> browser.open(portal_url)

Verify, that we have the links to create PSJ documents, from the 'add
item menu'::

   >>> browser.getLink(id='psj-document').url.endswith(
   ...   'createObject?type_name=PSJ+Document')
   True

Now let as add a PSJ document without any file::

   >>> browser.getLink(id='psj-document').click()
   >>> browser.getControl(name='title').value = "My first document"
   >>> browser.getControl(name='description').value = "The description"
   >>> browser.getControl(name='form_submit').click()

The created document should be available in the ZODB now::

   >>> 'my-first-document' in list(self.portal.keys())
   True


Adding PSJIssues
----------------

We can add a PSJIssue object::

   >>> browser.open(portal_url)

Verify, that we have the links to create PSJ documents, from the 'add
item menu'::

   >>> browser.getLink(id='psj-issue').url.endswith(
   ...   'createObject?type_name=PSJ+Issue')
   True

Now let us add a PSJ issue::

   >>> browser.getLink(id='psj-issue').click()
   >>> browser.getControl(name='title').value = "My first issue"
   >>> browser.getControl(name='description').value = "The description"
   >>> browser.getControl(name='form_submit').click()

The created issue should be available in the ZODB now::

   >>> 'my-first-issue' in list(self.portal.keys())
   True


Adding PSJVolumes
-----------------

PSJVolumes contain PSJIssues

We can add a PSJVolume object::

   >>> browser.open(portal_url)

Verify, that we have the links to create PSJ documents, from the 'add
item menu'::

   >>> browser.getLink(id='psj-volume').url.endswith(
   ...   'createObject?type_name=PSJ+Volume')
   True

Now let us add a PSJ volume::

   >>> browser.getLink(id='psj-volume').click()
   >>> browser.getControl(name='title').value = "My first volume"
   >>> browser.getControl(name='description').value = "The description"
   >>> browser.getControl(name='form_submit').click()

The created volume should be available in the ZODB now::

   >>> 'my-first-volume' in list(self.portal.keys())
   True

Adding PSJMagazines
-------------------

PSJMagazines contain PSJVolumes or PSJIssues

We can add a PSJMagazine object::

   >>> browser.open(portal_url)

Verify, that we have the links to create PSJ documents, from the 'add
item menu'::

   >>> browser.getLink(id='psj-magazine').url.endswith(
   ...   'createObject?type_name=PSJ+Magazine')
   True

Now let us add a PSJ magazine::

   >>> browser.getLink(id='psj-magazine').click()
   >>> browser.getControl(name='title').value = "My first magazine"
   >>> browser.getControl(name='description').value = "The description"
   >>> browser.getControl(name='form_submit').click()

The created magazine should be available in the ZODB now::

   >>> 'my-first-magazine' in list(self.portal.keys())
   True


Adding PSJBooks
---------------

PSJBooks are plain content types that do not contain any other
objects.

We can add a PSJBook object::

   >>> browser.open(portal_url)

Verify, that we have the links to create PSJ documents, from the 'add
item menu'::

   >>> browser.getLink(id='psj-book').url.endswith(
   ...   'createObject?type_name=PSJ+Book')
   True

Now let us add a PSJ book::

   >>> browser.getLink(id='psj-book').click()
   >>> browser.getControl(name='title').value = "My first book"
   >>> browser.getControl(name='description').value = "The description"
   >>> browser.getControl(name='form_submit').click()

The created book should be available in the ZODB now::

   >>> 'my-first-book' in list(self.portal.keys())
   True

Get back to the portal root::

   >>> browser.open(portal_url)


Adding PSJFiles
---------------

PSJFiles are like normal Plone ATFiles, but provide additional
metadata.

We can add a PSJFile object::

   >>> browser.open(portal_url)
   >>> browser.getLink(id='psj-file').url.endswith(
   ...   'createObject?type_name=PSJ+File')
   True

Now let us add a PSJ file::

   >>> browser.getLink(id='psj-file').click()
   >>> browser.getControl(name='title').value = "My first file"
   >>> browser.getControl(name='description').value = "The description"

Here we grab the upload field, insert a locally created fake file
containing two lines of plain text and submit the whole thing::

   >>> import cStringIO
   >>> file_ctrl = browser.getControl(name="file_file")
   >>> myfile = cStringIO.StringIO("Some content\nin two lines")
   >>> file_ctrl.add_file(myfile, 'text/plain', filename='mydocument.txt')
   >>> browser.getControl(name='form_submit').click()

   >>> browser.open(portal_url)


Adding PSJPostPrints
--------------------

PSJPostPrints are like normal Plone ATFiles, but provide additional
metadata.

We can add a PSJPostPrint object::

   >>> browser.open(portal_url)
   >>> browser.getLink(id='psj-postprint').url.endswith(
   ...   'createObject?type_name=PSJ+PostPrint')
   True

Now let us add a PSJ postprint::

   >>> browser.getLink(id='psj-postprint').click()
   >>> browser.getControl(name='title').value = "My first file"
   >>> browser.getControl(name='description').value = "The description"

Here we grab the upload field, insert a locally created fake file
containing two lines of plain text and submit the whole thing::

   >>> import cStringIO
   >>> file_ctrl = browser.getControl(name="file_file")
   >>> myfile = cStringIO.StringIO("Some content\nin two lines")
   >>> file_ctrl.add_file(myfile, 'text/plain', filename='mydocument.txt')
   >>> browser.getControl(name='form_submit').click()

   >>> browser.open(portal_url)



Modifying content
=================

Modifying PSJ documents
-----------------------

The document we added was created without an 'internal' office
document to display. We now want to upload a real document and see,
whether it is displayed as HTML in default view.

For this, we first browse the edit view::

   >>> browser.open(portal_url + '/my-first-document')
   >>> doc_url = self.portal['my-first-document'].absolute_url()
   >>> browser.getLink('Edit').url == doc_url + '/edit'
   True

   >>> browser.getLink('Edit').click()

Here we grab the upload field, insert a locally created fake file
containing two lines of plain text and submit the whole thing::


   >>> import cStringIO
   >>> file_ctrl = browser.getControl(name="document_file")
   >>> myfile = cStringIO.StringIO("Some content\nin two lines")
   >>> file_ctrl.add_file(myfile, 'text/plain', filename='mydocument.txt')
   >>> browser.getControl(name='form_submit').click()

Now our little document should have an HTML representation stored in
its annotations::

   >>> doc = self.portal['my-first-document']
   >>> doc.annotations['psj.content']['html']
   u'<p>Some content<br />in two lines</p>'

Plain text transformations are not a big problem. We therefore try
somethings more elaborated and feed the example document stored in the
test/ directory::

   >>> import os
   >>> import cStringIO
   >>> browser.getLink('Edit').click()
   >>> file_ctrl = browser.getControl(name="document_file")
   >>> test_filepath = os.path.join(
   ...     os.path.dirname(__file__), 'tests', 'input1.doc')
   >>> myfile = cStringIO.StringIO(str(open(test_filepath, 'rb').read()))
   >>> file_ctrl.add_file(myfile, 'application/msword', filename='input1.doc')

Before submitting the form, we must make sure, that we enabled the
radio button for upload::

   >>> browser.getControl(name='document_delete').value = ['']
   >>> browser.getControl(name='form_submit').click()

Let's see, whether we can find an HTML representation of it in the
object::

   >>> doc = self.portal['my-first-document']
   >>> print doc.annotations['psj.content']['html']
   <BLANKLINE>
   <BLANKLINE>
   <br />
   ...
   This is a plain word document only...
   ...


The general view, which we reached by submitting the edit form, should
also display our document, but this time embedded in a complete HTML
page::

   >>> print browser.contents
   <!DOCTYPE html PUBLIC...
   <BLANKLINE>
   <BLANKLINE>
   <br />
   ...
   This is a plain word document only...
   ...
   </html>


Embedded subobjects
-------------------

Office documents often contain other media, preferably images, that
have to be stored separate from the main document. We prepared a
document with a picture in the tests/ directory and will now try to
upload this::

   >>> import os
   >>> import cStringIO
   >>> browser.getLink('Edit').click()
   >>> file_ctrl = browser.getControl(name="document_file")
   >>> test_filepath = os.path.join(
   ...     os.path.dirname(__file__), 'tests', 'input2.doc')
   >>> myfile = cStringIO.StringIO(str(open(test_filepath, 'rb').read()))
   >>> file_ctrl.add_file(myfile, 'application/msword', filename='input1.doc')

Before submitting the form, we must make sure, that we enabled the
radio button for upload::

   >>> browser.getControl(name='document_delete').value = ['']
   >>> browser.getControl(name='form_submit').click()

Now let's see, whether is provided by a link inside the HTML page we
get as response::

   >>> print browser.contents
   <!DOCTYPE html PUBLIC...
   <BLANKLINE>
   <BLANKLINE>
   <br />
   ...
   This document includes a picture:
   ...
   <img ... src="my-first-document/unknown.doc0.png" />...
   ...
   </html>

Okay. Now let's see, whether we can access the picture directly::

   >>> img_loc = portal_url + '/my-first-document/unknown.doc0.png'
   >>> browser.open(img_loc)
   >>> browser.headers['content-type']
   'image/png'

   >>> browser.headers['content-length']
   '28477'

   >>> browser.headers['content-disposition']
   'attachment; filename'

The picure was directly delivered.


Replacing subobjects upon new upload
------------------------------------

When uploading a new document or version of a document, the old
subobjects should be removed. We upload `input3.doc` which includes
two images, both different from the one in the above file::

   >>> browser.open(portal_url  + '/my-first-document')
   >>> browser.getLink('Edit').click()
   >>> file_ctrl = browser.getControl(name="document_file")
   >>> test_filepath = os.path.join(
   ...     os.path.dirname(__file__), 'tests', 'input3.doc')
   >>> myfile = cStringIO.StringIO(str(open(test_filepath, 'rb').read()))
   >>> file_ctrl.add_file(myfile, 'application/msword', filename='input3.doc')
   >>> browser.getControl(name='document_delete').value = ['']
   >>> browser.getControl(name='form_submit').click()

Now let's see, whether also the second image is provided by a link
inside the HTML page we get as response::

   >>> print browser.contents
   <!DOCTYPE html PUBLIC...
   <BLANKLINE>
   <BLANKLINE>
   <br />
   ...
   This document includes a picture:
   ...
   <img ... src="my-first-document/unknown.doc0.png" />...
   ...
   <img ... src="my-first-document/unknown.doc1.png" />...
   ...
   </html>

We make sure, the first picture is a new one::

   >>> img_loc = portal_url + '/my-first-document/unknown.doc0.png'
   >>> browser.open(img_loc)
   >>> browser.headers['content-type']
   'image/png'

   >>> browser.headers['content-length']
   '5506'

This is the prove: the only picture of the last document was bigger.

To be really sure, that old subobjects are not only replaced, but also
removed if not part of a freshly uploaded document, we upload the
first document again, which contains no images at all::

   >>> browser.open(portal_url  + '/my-first-document')
   >>> browser.getLink('Edit').click()
   >>> file_ctrl = browser.getControl(name="document_file")
   >>> test_filepath = os.path.join(
   ...     os.path.dirname(__file__), 'tests', 'input1.doc')
   >>> myfile = cStringIO.StringIO(str(open(test_filepath, 'rb').read()))
   >>> file_ctrl.add_file(myfile, 'application/msword', filename='input1.doc')
   >>> browser.getControl(name='document_delete').value = ['']
   >>> browser.getControl(name='form_submit').click()

If we now try to get the a picture, this should fail::

   >>> img_loc = portal_url + '/my-first-document/unknown.doc0.png'
   >>> browser.handleErrors = True
   >>> browser.open(img_loc)
   Traceback (most recent call last):
   ...
   HTTPError: HTTP Error 404: Not Found

   >>> browser.headers['status']
   '404 Not Found'


Handling Metadata
=================

Metadata is handles by special tool in the ZMI.

We go to the overview page. In the beginning there are no schemata
available::

   >>> browser.open(portal_url + '/metadataschemas_registry/manage_main')
   >>> print browser.contents
   <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN"...
   ...
   Registered metadata schemata (0).
   ...

Adding a new schema
-------------------

But we can add a new schema::

   >>> ctrl = browser.getControl('Add a new metadata schema')
   >>> ctrl.click()

We fill in the values for a text line field::

   >>> browser.getControl(name="text_line.title").value='Title'
   >>> browser.getControl(name="text_line.default").value='Untitled'
   >>> browser.getControl("Add text line field").click()

Afterwards we add a boolean field::

   >>> browser.getControl(name="boolean.title").value='Is Important'
   >>> browser.getControl(name="boolean.default").value=True
   >>> browser.getControl("Add boolean field").click()

We also add a relation field::

   >>> browser.getControl(name="relation.title").value='Reviewed Book'
   >>> browser.getControl("Add link field").click()

We then set a name for the whole metadataset::

   >>> browser.getControl(name="id").value='My new Schema'

and the type of object, this schema should apply to::

   >>> browser.getControl(name="objecttype").displayValue = ['PSJ Document']

Finally, we submit the whole schema as a new one::

   >>> browser.getControl("Create new schema").click()

Back on the metadata schemas overview, our new entry is listed::

   >>> print browser.contents
   <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN"...
   ...
   Registered metadata schemata (1).
   ...

The listing also includes the objecttype and the fields::

   >>> print browser.contents
   <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN"...
   ...
       <td>PSJ Document</td>
       <td>title, is_important, reviewed_book</td>
   ...

When we go back to the document we created before, this should display
the new metadata fields. We go to the document and choose the edit
tab::

   >>> browser.open(portal_url + '/my-first-document')
   >>> browser.getLink('Edit').click()
   >>> print browser.contents
   <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"...
   ...
   <fieldset id="fieldset-metadata">
   <legend id="fieldsetlegend-metadata">Metadata</legend>
   ...
   <input type="text" name="md_title"
   ...
   <input class="noborder" type="checkbox" value="on"
          checked="checked"
          name="md_is_important:boolean"
          id="md_is_important" />
   ...
   <div style="clear: both">
       <input type="button" class="searchButton"
              value="Add..."
              onclick="javascript:...,'md_reviewed_book', '/plone/my-first-document', 'md_reviewed_book')" />
   ...

   >>> browser.getControl('Save').click()


Here we can find the textline entry ('md_title') and the boolean
checkbox entry ('md_is_important'). All field names are preceded by
'md_' internally to avoid clashes with already existing fieldnames and
to distuingish metadata fields from others.



Deleting a schema
-----------------

We go to the registry screen and select the only one schema and click
on the delete button::

   >>> browser.open(portal_url + '/metadataschemas_registry/manage_main')
   >>> browser.getControl(name='ids:list', index=0).value=True
   >>> browser.getControl("Delete Selected Items").click()
   >>> print browser.contents
   <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN"...
   ...
   Registered metadata schemata (0).
   ...
