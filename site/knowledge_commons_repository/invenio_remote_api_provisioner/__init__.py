from __future__ import absolute_import, print_function
from .ext import InvenioRemoteAPIProvisioner

"""An InvenioRDM extension to provision remote APIs with record events.

Sends requests to a remote API endpoint when record events occur. For example,
it can send a POST request to a remote search indexer when a record is created,
providing the necessary metadata to index the record.

Updates are sent asynchronously using a Celery task. The task is configured
with a retry policy, so if the remote API is unavailable, the task will be
retried until it succeeds.

The extension works by providing a service component that is injected into
the RDMRecordService. As with all service components, the methods of the
component class are called during the execution of the corresponding methods
in the parent service.

Enabling the extension:

   The service component is enabled as soon as its python package is installed.
   It modifies the ``RDM_RECORDS_SERVICE_COMPONENTS`` configuration variable,
   initializing it from defaults if it doesn't exist. This variable is a list
   of components that are injected into the RDMRecordService and called in
   their listed order.

   The RemoteAPIProvisionerComponent component methods are executed *after*
   the default RDMRecordService components have executed, and after any other
   component methods injected in your instance via the
   ``RDM_RECORDS_SERVICE_COMPONENTS`` variable.

Configuring event messages:

   The extension is configured using Flask configuration variables in your
   instance configuration file (``invenio.cfg``). First, this extension
   relies on the standard config variables SITE_UI_URL and SITE_API_URL to
   construct URLs for the records. This should already be set in your instance.

   Then the ``REMOTE_API_PROVISIONER_EVENTS`` config variable should provide
   a dictionary containing the record event messages to be triggered. The
   keys of this dictionary are api endpoints to provision. For each
   endpoint, the value is a corresponding dictionary with record event names
   as its keys. Possible event names (i.e., record events in the
   RDMRecordService) are: ``create``, ``update_draft``, ``delete_record``,
   ``restore_record``, ``publish``, and ``new_version``.

   The value corresponding to each event name is a dictionary containing the
   following:

   method: the HTTP method to be used when sending the request to the
           remote API endpoint. (e.g. ``POST``, ``PUT``, ``PATCH``, ``DELETE``)
   payload: the payload to be sent to the remote API endpoint. This is
            assumed to be a dictionary that by default will be converted into a
            JSON string. In place of a static payload,
            the value may be a function that takes the service data parameters
            as its arguments and returns a dictionary. This allows the
            payload to be dynamically
            generated based on the record data.
   payload_format: the format of the payload. Currently only ``json`` is
                   supported. Defaults to ``json``.

   A full configuration might look like this::

      REMOTE_API_PROVISIONER_EVENTS = {
         "https://hcommons.org/api/v1/search_update": {
            "create": {
               "method": "POST",
               "payload": lambda rec, data, record, *args, **kwargs: {
                  "type": "work",
                  "network": "works",
                  "primary_url": f"{SITE_UI_URL}/records/{rec['id']}",
                  "other_urls": [],
                  "title": rec["metadata"]["title"],
                  "description": rec["metadata"]["description"],
                  "publication_date": rec["metadata"]["publication_date"],
                  "updated_date": rec["updated"]
               },
            },
            "update_draft": {
               "method": "PUT",
               "payload": lambda rec, data, record, *args, **kwargs: {
                  "type": "work",
                  "network": "works",
                  "primary_url": f"{SITE_UI_URL}/records/{rec['id']}",
                  "other_urls": [],
                  "title": rec["metadata"]["title"],
                  "description": rec["metadata"]["description"],
                  "publication_date": rec["metadata"]["publication_date"],
                  "updated_date": rec["updated"]
               },
            },
         },
      }

The payload formatting function receives (1) the full record object, (2) a
dictionary of information about the record owner, and
then (3) all the same arguments that are returned by the RDMRecordsService
method that was called *except the current user identity*. This includes the
record data and the record object. The payload function can also receive
any additional keyword arguments that are passed to the RDMRecordsService
method. For example, the ``update_draft`` event is triggered by the
``update_draft`` method of the RDMRecordsService. This method takes a
``revision_id`` keyword argument, which is passed to the payload function.

The dictionary of owner information contains the following keys:
   "id": the owner's InvenioRDM user id
   "email": the owner's email address
   "username": the owner's InvenioRDM username
   "authentication_source": the name of the owner's SAML authentication
   provider (if any)
   "id_from_idp": the owner's id on the SAML authentication provider (if any)
   "affiliations": a list of the owner's affiliations
   "full_name": the owner's full name
   "name_parts": a dictionary of the owner's name parts (e.g., first_name,
                 last_name, etc.)

If the payload is being generated by a function, errors in generating the
payload can be caught and passed to the provisioner by returning a
dictionary with a ``"internal_error"`` key and a string with error
details as its value. The extension will then log the error and abort
sending the signal. This prevents the extension from crashing the
application when a payload function fails.


- ``REMOTE_API_PROVISIONER_RETRY_POLICY``: A dictionary containing the retry
   policy for the Celery task. See the `Celery documentation
   <https://docs.celeryproject.org/en/stable/userguide/tasks.html#retrying>`_
   for more information.

"""

__version__ = "1.0.0a"

__all__ = ("__version__", "InvenioRemoteAPIProvisioner")
