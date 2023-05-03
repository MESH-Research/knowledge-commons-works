"""Handle API interactions with Fedora."""
import io
import os
import requests
from lxml import etree
from lxml.etree import XMLSyntaxError
# from swamplr.swamplr_logging import write_to_log


class FedoraApi: #pylint: disable=too-many-public-methods

    """Class for interacting with the fedora API."""

    def __init__(self, base_url="http://localhost:8080/fedora", username=None, password=None):
        """Initialize API by testing connection."""
        self.base_url = base_url
        self.url = base_url
        self.method = "GET"
        self.auth = None
        self.file = None
        if username and password:
            self.auth = (username, password)
        self.static_params = {"resultFormat": "xml"}
        self.dynamic_params = {}

    def _set_static_param(self, field, value):
        """Add static param to API call; Should remain in place for subsequent calls to same instance."""
        self.static_params[field] = value

    def _set_dynamic_param(self, field, value):
        """Add dynamic param to API call; will be reset before subsequent calls."""
        self.dynamic_params[field] = value

    def _set_url(self, extension):
        """Add extension to base url to create complete url."""
        self.url = os.path.join(self.base_url, extension)

    def _set_method(self, method):
        """Set method to use, e.g. POST, GET, DELETE."""
        self.method = method.upper()

    def _clear_dynamic_params(self):
        """Reset dynamic parameters."""
        self.dynamic_params = {}

    def _call_api(self):
        """Send completed call to API."""
        params = self.static_params.copy()
        params.update(self.dynamic_params)
        print('PARAMS')
        print(params)

        try:
            req = requests.request(self.method, self.url, timeout=60, params=params, auth=self.auth, data=self.file)
            res = (req.status_code, req.content)
            req.close()
        except requests.exceptions.HTTPError as http_error:
            res = (-1, http_error)
            write_to_log(loglevel="error", message="Fedora API Exception: {0}".format(http_error), exc_info=True)
        # Reset vars for next call
        self.dynamic_params = {}
        self._set_method("GET")

        return res

    def find_all_objects_by_id(self, term, fields=None, **kwargs):
        """Use resume operation to get all objects matching a given query."""
        self._clear_dynamic_params()
        if fields is None:
            fields = ["pid"]
        self._set_url("objects")
        self._set_dynamic_param("query", "identifier~{0}".format(term))

        for field in fields:
            self._set_dynamic_param(field, "true")

        for field, value in kwargs.items():
            self._set_dynamic_param(field, value)

        status, result = self._call_api()
        token = FedoraApi._get_token(result)
        all_objects = FedoraApi._extract_data_from_xml(result)

        while status in [200, 201] and token and all_objects:
            status, result = self._resume_find_objects(term, token, fields=fields)
            token = FedoraApi._get_token(result)
            objects = FedoraApi._extract_data_from_xml(result)
            all_objects = (all_objects + objects) if objects else None
        all_pids = [o['pid'] for o in all_objects]
        return all_pids

    def find_objects(self, term, fields=None):
        """Use findObjects API call with the "terms" argument."""
        self._clear_dynamic_params()
        if fields is None:
            fields = ["pid"]
        self._set_url("objects")
        self._set_dynamic_param("terms", term)
        for field in fields:
            self._set_dynamic_param(field, "true")
        self._set_dynamic_param("pid", "true")
        return self._call_api()

    def _resume_find_objects(self, term, token, fields=None, **kwargs):
        """Use token to resume getting results from previous search."""
        if fields is None:
            fields = ["pid"]
        self._set_url("objects")
        self._set_dynamic_param("terms", term)
        self._set_dynamic_param("sessionToken", token)
        for field, value in kwargs.items():
            self._set_dynamic_param(field, value)
        for field in fields:
            self._set_dynamic_param(field, "true")
        self._set_dynamic_param("pid", "true")
        return self._call_api()

    def get_datastream(self, pid, dsid, **kwargs):
        """Get datastream according to pid and ds id.

        Returns: data about the datastream, not the content itself. See: get_datastream_dissemination.
        """
        self._set_url("objects/{0}/datastreams/{1}".format(pid, dsid))
        for field, value in kwargs.items():
            self._set_dynamic_param(field, value)
        return self._call_api()

    def get_datastream_dissemination(self, pid, dsid, **kwargs):
        """Get datastream according to pid and ds id.

        Returns: datastream content. See get_datastream to get info about the datastream.
        """
        self._set_url("objects/{0}/datastreams/{1}/content".format(pid, dsid))
        for field, value in kwargs.items():
            self._set_dynamic_param(field, value)
        return self._call_api()


    def find_all_objects(self, term, fields=None, **kwargs):
        """Use resume operation to get all objects matching a given query."""
        self._clear_dynamic_params()
        all_objects = []

        if fields is None:
            fields = ["pid"]
        self._set_dynamic_param("terms", term)
        self._set_url("objects")

        for field in fields:
            self._set_dynamic_param(field, "true")
        for field, value in kwargs.items():
            self._set_dynamic_param(field, value)

        status, result = self._call_api()
        token = FedoraApi._get_token(result)
        if status in [200, 201]:
            objects = FedoraApi._extract_data_from_xml(result)
            all_objects += objects
        while status in [200, 201] and token:
            status, result = self._resume_find_objects(term, token, fields=fields, **kwargs)
            token = FedoraApi._get_token(result)
            objects = FedoraApi._extract_data_from_xml(result)
            all_objects += objects

        return all_objects

    def ingest_new(self, namespace, **kwargs):
        """Create new object and generate new pid.
        Returns string of pid on success.

        Allowed kwargs:
        [label] [format] [encoding] [namespace] [ownerId] [logMessage] [ignoreMime] [state]
        """
        self._set_method("POST")
        self._set_url("objects/new")
        self._set_dynamic_param("namespace", namespace)
        for field, value in kwargs.items():
            self._set_dynamic_param(field, value)
        return self._call_api()

    def purge_object(self, pid, log_message=None):
        """Purge object."""
        self._set_method("DELETE")
        self._set_url("objects/{0}".format(pid))
        if log_message:
            self._set_dynamic_param("logMessage", log_message)
        return self._call_api()

    def ingest_at_pid(self, pid, **kwargs):
        """Create new object and generate new pid.
        Returns string of pid on success.

        Allowed kwargs:
        [label] [format] [encoding] [namespace] [ownerId] [logMessage] [ignoreMime] [state]
        """
        self._set_method("POST")
        self._set_url("objects/{0}".format(pid))
        for field, value in kwargs.items():
            self._set_dynamic_param(field, value)
        return self._call_api()

    def modify_object(self, pid, **kwargs):
        """Modify existing object.

        Allowed kwargs:
        [label] [ownerId] [state] [logMessage] [lastModifiedDate]
        """
        self._set_method("PUT")
        self._set_url("objects/{0}".format(pid))
        for field, value in kwargs.items():
            self._set_dynamic_param(field, value)
        return self._call_api()

    def add_datastream(self, pid, ds_id, filepath=None, content=None, **kwargs):
        """Add datastream to specified object.

        args:
            pid(str): PID of the object to udpate.
            ds_id(str): Datastream ID to create.
        kwargs:
            filepath(str): filepath to read content from and add as datastream content. Filepath takes precedence if both
                filepath and content are passed in.
            content(str): content to add to datastream.
            Additiona allowed kwargs:
            [controlGroup] [dsLocation] [altIDs] [dsLabel] [versionable] [dsState] [formatURI] [checksumType] [checksum]
            [mimeType] [logMessage]
        """
        self._set_method("POST")
        self._set_url("objects/{0}/datastreams/{1}".format(pid, ds_id))
        for field, value in kwargs.items():
            self._set_dynamic_param(field, value)
        if filepath:
            with open(filepath, 'rb') as file_to_send:
                self.file = file_to_send
                res = self._call_api()
        elif content:
            self.file = io.BytesIO(content.encode('utf-8'))
            res = self._call_api()
        return res

    def update_datastream_content(self, pid, ds_id, file_object, **kwargs):
        """Replace content of specified datastream."""
        self._set_method("POST")
        self._set_url("objects/{0}/datastreams/{1}".format(pid, ds_id))
        for field, value in kwargs.items():
            self._set_dynamic_param(field, value)
        self.file = file_object
        return self._call_api()

    def modify_datastream(self, pid, ds_id, filepath=None, **kwargs):
        """Modify datastream of specified object.

        Allowed kwargs:
        [controlGroup] [dsLocation] [altIDs] [dsLabel] [versionable] [dsState] [formatURI] [checksumType] [checksum]
        [mimeType] [logMessage]
        """
        self._set_method("PUT")
        self._set_url("objects/{0}/datastreams/{1}".format(pid, ds_id))
        for field, value in kwargs.items():
            self._set_dynamic_param(field, value)
        if filepath:
            with open(filepath, 'rb') as file_to_send:
                self.file = file_to_send
                res = self._call_api()
        else:
            res = self._call_api()

        return res

    def purge_datastream(self, pid, ds_id, **kwargs):
        """Purge datastream!"""
        self._set_method("DELETE")
        self._set_url("objects/{0}/datastreams/{1}".format(pid, ds_id))
        for field, value in kwargs.items():
            self._set_dynamic_param(field, value)
        return self._call_api()

    def add_relationship(self, pid, predicate, obj, is_literal=False, datatype=None, api_function=None):  # pylint: disable-msg=too-many-arguments
        """Add relationship to RELS-EXT."""
        api_function = self._call_api if api_function is None else api_function
        self._set_method("POST")
        self._set_url("objects/{0}/relationships/new".format(pid))
        self._set_dynamic_param("isLiteral", "true" if is_literal else "false")
        self._set_dynamic_param("predicate", predicate)
        self._set_dynamic_param("object", obj)
        if datatype and is_literal:
            valid_datatype = FedoraApi._validate_datatype(datatype)
            if not valid_datatype:
                return -1, "Please provide valid datatype. Allowed types are: int, float, long, dateTime, and double."
            self._set_dynamic_param("datatype", valid_datatype)
        return api_function()

    def delete_relationship(self, pid, predicate, obj, is_literal=False, datatype=None):  # pylint: disable-msg=too-many-arguments
        """Delete relationship in RELS-EXT."""
        self._set_method("DELETE")
        self._set_url("objects/{0}/relationships".format(pid))
        self._set_dynamic_param("predicate", predicate)
        self._set_dynamic_param("isLiteral", "true" if is_literal else "false")
        self._set_dynamic_param("object", obj)
        if datatype and is_literal:
            valid_datatype = FedoraApi._validate_datatype(datatype)
            if not valid_datatype:
                return -1, "Please provide valid datatype. Allowed types are: int, float, long, dateTime, and double."
            self._set_dynamic_param("datatype", valid_datatype)
        return self._call_api()

    def modify_relationship(self, pid, predicate, obj, new_obj, is_literal=False, datatype=None):  # pylint: disable-msg=too-many-arguments
        """Update the triple to a new value"""
        self.delete_relationship(pid, predicate, obj, is_literal=is_literal, datatype=datatype)
        return self.add_relationship(pid, predicate, new_obj, is_literal=is_literal, datatype=datatype)

    def get_relationships(self, pid, rels_ext_format="n-triples", predicate=None):
        """Return all relationship associated with given pid, limited by predicate if supplied."""
        self._set_url("objects/{0}/relationships".format(pid))
        self._set_dynamic_param("format", rels_ext_format)
        if predicate:
            self._set_dynamic_param("predicate", predicate)
        return self._call_api()

    def get_next_pid(self, namespace):
        """Get next available pid from within given namespace."""
        self._set_method("POST")
        self._set_url("objects/nextPID")
        self._set_dynamic_param("namespace", namespace)
        self._set_dynamic_param("format", "xml")
        return self._call_api()

    def get_object_profile(self, pid):
        """Get details about a given object."""
        self._set_url("objects/{0}".format(pid))
        self._set_dynamic_param("format", "xml")
        return self._call_api()

    def get_object_xml(self, pid):
        """Get object xml aka foxml."""
        self._set_url("objects/{0}/objectXML".format(pid))
        return self._call_api()

    def list_datastreams(self, pid, **kwargs):
        """List datastreams for given object."""
        self._set_url("objects/{0}/datastreams".format(pid))
        self._set_dynamic_param("format", "xml")
        for field, value in kwargs.items():
            self._set_dynamic_param(field, value)
        return self._call_api()

    def get_extracted_data_from_xml(self, xml):
        """ Function to return the extracted data from xml
            args:
                xml (str): xml received from fedora
        """
        return self._extract_data_from_xml(xml)

    @staticmethod
    def _validate_datatype(datatype):
        """Ensure only valid datatypes are used."""
        valid_datatype = None
        valid_datatype_uris = [
            "http://www.w3.org/2001/XMLSchema#int",
            "http://www.w3.org/2001/XMLSchema#double",
            "http://www.w3.org/2001/XMLSchema#float",
            "http://www.w3.org/2001/XMLSchema#dateTime",
            "http://www.w3.org/2001/XMLSchema#long",
        ]
        for uri in valid_datatype_uris:
            type_uri = uri.split("#")[1]
            if datatype in [uri, type_uri]:
                valid_datatype = uri
        return valid_datatype

    @staticmethod
    def _get_token(xml):
        """Extract token from xml response."""
        xml = etree.fromstring(xml)
        token = xml.find(".//{http://www.fedora.info/definitions/1/0/types/}token")
        if token is not None:
            token = token.text
        return token

    @staticmethod
    def _extract_data_from_xml(xml):
        """Get data from xml for user display.
            args:
                xml (str): xml received from fedora
        """
        items = []
        try:
            xml_tree = etree.fromstring(xml)
            for record in xml_tree.iterfind(".//{http://www.fedora.info/definitions/1/0/types/}objectFields"):
                item = {}
                for child in record:
                    tag = child.tag.split("}")[1]
                    item[tag] = child.text
                items.append(item)

        except XMLSyntaxError:
            write_to_log(loglevel="error", message="Inappropriately formatted XML: {0}".format(xml), exc_info=True)
            items = None

        except ValueError:
            write_to_log(loglevel="error", message="Can only parse strings, not: {0}".format(type(xml)), exc_info=True)
            items = None

        return items
