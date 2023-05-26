"""
Custom fields to hold legacy metadata for records imported from the CORE
repository.

Implements the following fields:

hclegacy:collection     The CORE repository was divided into several top-level
                        collections (hcollection:1, mlacollection:1, etc.).
                        This structure is not retained in the current
                        repository, but the information has been retained as
                        legacy data.
hclegacy:committee_deposit      The HC id number of a committee if a committee
                                was associated with the original CORE deposit.
                                This did *not* indicate group *ownership*, but
                                only that the deposit was *associated* with the
                                committee.
hclegacy:file_location      The complete file path to the deposited file on
                            the original hcommons server for the CORE
                            repository.
hclegacy:file_pid           The pid of the deposited file in the CORE
                            repository. Each file had its own pid separate
                            from the pid of the metadata record.
hclegacy:groups_for_deposit     The HC groups with which the CORE deposit was
                                associated. This data is retained in a
                                legacy field because groups will not be
                                handled the same way in Invenio.
hclegacy:previously_published   Indicated that the original CORE deposit had
                                been published prior to upload.
hclegacy:publication_type       There were multiple fields in the CORE data
                                describing the resource type of the deposit.
                                These fields sometimes conflicted. So this
                                field retains data that was not judged to be
                                most reliable and was not used to determine
                                the resource_type of the imported Invenio
                                record.
hclegacy:record_change_date     The last modification date for the original
                                CORE deposit record prior to its import into
                                Invenio.
hclegacy:record_creation_date   The creation date for the original CORE
                                deposit record.
hclegacy:record_identifier      A number used in the original Solr indexing. It
                                concatenates the site ID (id number for HC, MLA, etc.) and original item id number in the
                                CORE database.
hclegacy:society            The HC societies to which the original uploader of
                            the CORE deposit belonged. It should include the society from whose site the deposit was made, although this may not be the case for bulk uploads. Possible values are: arlisna, hc, msu, ajs, hastac, sah, aseees, caa, up.
hclegacy:submitter_org_memberships  The HC organizations to which the user
                                    who uploaded the deposit belonged.
hclegacy:submitter_id       The user id number (in the HC database) for the
                            user who originally deposited the CORE upload.
"""


hclegacy:groups_for_deposit {
    "group_name": "",
    "group_identifier": ""
},