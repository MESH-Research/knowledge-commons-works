SAMPLE_RECORDS_SNAPSHOT_AGG = {
    "timestamp": "2024-01-01T00:00:00",
    "community_id": "abcd",
    "snapshot_date": "2024-01-01",
    "total_records": {
        "metadata_only": 100,
        "with_files": 200,
    },
    "total_parents": {
        "metadata_only": 100,
        "with_files": 200,
    },
    "total_files": {
        "file_count": 100,
        "data_volume": 200.0,
    },
    "total_uploaders": 100,
    "subcounts": {
        "all_resource_types": [
            {
                "id": "123",
                "label": "Resource Type 1",
                "records": {
                    "metadata_only": 100,
                    "with_files": 200,
                },
                "parents": {
                    "metadata_only": 100,
                    "with_files": 200,
                },
                "files": {
                    "file_count": 100,
                    "data_volume": 200.0,
                },
            },
        ],
        "all_access_status": [
            {
                "id": "123",
                "label": "Access Right 1",
                "records": {
                    "metadata_only": 100,
                    "with_files": 200,
                },
                "parents": {
                    "metadata_only": 100,
                    "with_files": 200,
                },
                "files": {
                    "file_count": 100,
                    "data_volume": 200.0,
                },
            },
        ],
        "all_languages": [],
        "all_licenses": [],
        "top_affiliations_creator": [],
        "top_affiliations_contributor": [],
        "top_funders": [],
        "top_subjects": [],
        "top_publishers": [],
        "top_periodicals": [],
        "top_keywords": [],
    },
}


# Mock search response for three records in period 2025-05-30 to 2025-06-03
MOCK_RECORD_SEARCH_RESPONSE = {
    "_shards": {"failed": 0, "skipped": 0, "successful": 5, "total": 5},
    "hits": {
        "hits": [
            {
                "_id": "d78f293f-3623-4ad9-9e96-5b9ceff3ce7c",
                "_index": "rdmrecords-records-record-v6.0.0-1749066625",
                "_score": 1.0,
                "_source": {
                    "$schema": "local://records/record-v6.0.0.json",
                    "access": {
                        "embargo": {"active": False, "reason": None, "until": None},
                        "files": "public",
                        "record": "public",
                        "status": "open",
                    },
                    "created": "2025-06-03T20:51:12.325212+00:00",
                    "custom_fields": {
                        "journal:journal": {"title": "N/A"},
                        "kcr:ai_usage": {"ai_used": False},
                    },
                    "deletion_status": "P",
                    "files": {
                        "count": 1,
                        "enabled": True,
                        "entries": [
                            {
                                "checksum": "md5:334316ebfc4f91a0d860abc6ad04a69d",
                                "ext": "pdf",
                                "file_id": "1022b7b9-8331-4779-b76c-74d6ce07578a",
                                "key": "1955 in " "1947.pdf",
                                "metadata": {},
                                "mimetype": "application/pdf",
                                "object_version_id": (
                                    "8738b7f3-7354-45de-a368-9972f99bb513"
                                ),
                                "size": 1984949,
                                "uuid": "2326abbf-5224-42af-9f76-c0b4a645026d",
                                "version_id": 3,
                            }
                        ],
                        "mimetypes": ["application/pdf"],
                        "totalbytes": 1984949,
                        "types": ["pdf"],
                    },
                    "has_draft": False,
                    "id": "wg805-23c78",
                    "is_deleted": False,
                    "is_published": True,
                    "media_files": {"enabled": False},
                    "metadata": {
                        "combined_subjects": [],
                        "creators": [
                            {
                                "affiliations": [{"name": "Henry " "Ford " "College"}],
                                "person_or_org": {
                                    "family_name": "Friedman",
                                    "given_name": "Hal",
                                    "identifiers": [
                                        {
                                            "identifier": "friedman1996",
                                            "scheme": "kc_username",
                                        }
                                    ],
                                    "name": "Friedman, " "Hal",
                                    "type": "personal",
                                },
                                "role": {
                                    "@v": "5c46225e-5b2f-4614-9588-210bbe334a51::1",
                                    "id": "author",
                                    "title": {"en": "Author"},
                                },
                            }
                        ],
                        "description": (
                            "In late 1947, the "
                            "Office of the "
                            "Chief of Naval "
                            "Operations "
                            "(OPNAV) employed "
                            "historical "
                            "conjecture to "
                            "determine U.S. "
                            "Fleet "
                            "requirements for "
                            "the mid-1950s.  "
                            "Needing to be "
                            "prepared for a "
                            "war against the "
                            "U.S.S.R. as well "
                            "as for "
                            "competition from "
                            "its interservice "
                            "rivals, the "
                            "Navy's leadership "
                            "attempted as much "
                            "as possible to "
                            "anticipate what a "
                            "future war "
                            "against the "
                            "Soviet Union "
                            "might be like so "
                            "that the Naval "
                            "Operating Forces "
                            "that would be "
                            "necessary for the "
                            "U.S. could be "
                            "procured  Given "
                            "the national "
                            "security problems "
                            "in our own time "
                            "period, study of "
                            "this 1947 "
                            "historical "
                            "exercise provides "
                            "perspective on "
                            "how naval policy "
                            "was made and how "
                            "it might still be "
                            "made in the "
                            "present and "
                            "future."
                        ),
                        "languages": [
                            {
                                "@v": "5cb9da36-15e8-4291-9f4e-414578306ac1::1",
                                "id": "eng",
                                "title": {"en": "English"},
                            }
                        ],
                        "publication_date": "2025-06-02",
                        "publication_date_range": {
                            "gte": "2025-06-02",
                            "lte": "2025-06-02",
                        },
                        "publisher": "Knowledge Commons",
                        "resource_type": {
                            "@v": "7f9b4648-37d1-4cf5-a228-24d7eb51a43a::1",
                            "id": "textDocument-journalArticle",
                            "props": {
                                "subtype": "textDocument-journalArticle",
                                "type": "textDocument",
                            },
                            "title": {"en": "Journal " "Article"},
                        },
                        "rights": [
                            {
                                "@v": "41e16ef7-81ce-4a02-96f6-225080ce3777::1",
                                "description": {
                                    "en": (
                                        "The "
                                        "Creative "
                                        "Commons "
                                        "Attribution-ShareAlike "
                                        "license "
                                        "allows "
                                        "re-distribution "
                                        "and "
                                        "re-use "
                                        "of "
                                        "a "
                                        "licensed "
                                        "work "
                                        "on "
                                        "the "
                                        "condition "
                                        "that "
                                        "the "
                                        "creator "
                                        "is "
                                        "appropriately "
                                        "credited."
                                    )
                                },
                                "id": "cc-by-sa-4.0",
                                "props": {
                                    "scheme": "spdx",
                                    "url": (
                                        "https://creativecommons.org/licenses/by-sa/4.0/legalcode"
                                    ),
                                },
                                "title": {
                                    "en": (
                                        "Creative "
                                        "Commons "
                                        "Attribution-ShareAlike "
                                        "4.0 "
                                        "International"
                                    )
                                },
                            }
                        ],
                        "title": (
                            '"1955 in 1947: '
                            "Historical Conjecture "
                            "and Strategic Planning "
                            "in the Office of the "
                            "Chief of Naval "
                            'Operations"'
                        ),
                    },
                    "parent": {
                        "$schema": "local://records/parent-v3.0.0.json",
                        "access": {
                            "grant_tokens": [],
                            "grants": [],
                            "links": [],
                            "owned_by": {"user": 1},
                            "settings": {
                                "accept_conditions_text": None,
                                "allow_guest_requests": False,
                                "allow_user_requests": False,
                                "secret_link_expiration": 0,
                            },
                        },
                        "communities": {
                            "default": "8e620d7e-0739-441c-a4c7-b0bcb3e92a38",
                            "entries": [
                                {
                                    "@v": "8e620d7e-0739-441c-a4c7-b0bcb3e92a38::2",
                                    "created": "2025-06-04T19:50:33.799803+00:00",
                                    "id": "8e620d7e-0739-441c-a4c7-b0bcb3e92a38",
                                    "is_verified": True,
                                    "metadata": {
                                        "organizations": [
                                            {"name": "Organization " "1"}
                                        ],
                                        "title": "My " "Community",
                                        "type": {
                                            "@v": (
                                                "3a6489cf-e72c-4a8a-996d-8260dd628ff8::1"
                                            ),
                                            "id": "event",
                                            "title": {"en": "Event"},
                                        },
                                        "website": "https://my-community.com",
                                    },
                                    "slug": "knowledge-commons",
                                    "updated": "2025-06-04T19:50:34.002417+00:00",
                                    "uuid": "8e620d7e-0739-441c-a4c7-b0bcb3e92a38",
                                    "version_id": 3,
                                }
                            ],
                            "ids": ["8e620d7e-0739-441c-a4c7-b0bcb3e92a38"],
                        },
                        "created": "2025-06-04T19:50:36.742342+00:00",
                        "id": "qdgqq-8jm29",
                        "is_verified": True,
                        "pid": {
                            "obj_type": "rec",
                            "pid_type": "recid",
                            "pk": 110,
                            "status": "R",
                        },
                        "pids": {
                            "doi": {
                                "client": "datacite",
                                "identifier": "10.17613/qdgqq-8jm29",
                                "provider": "datacite",
                            }
                        },
                        "updated": "2025-06-04T19:50:38.457337+00:00",
                        "uuid": "4d73537a-0edd-4f3b-98ec-f6ba9b10eea9",
                        "version_id": 9,
                    },
                    "pid": {
                        "obj_type": "rec",
                        "pid_type": "recid",
                        "pk": 111,
                        "status": "R",
                    },
                    "pids": {
                        "doi": {
                            "client": "datacite",
                            "identifier": "10.17613/jthhs-g4b38",
                            "provider": "datacite",
                        },
                        "oai": {
                            "identifier": "oai:https://works.hcommons.org:jthhs-g4b38",
                            "provider": "oai",
                        },
                    },
                    "stats": {
                        "all_versions": {
                            "data_volume": 0.0,
                            "downloads": 0,
                            "unique_downloads": 0,
                            "unique_views": 0,
                            "views": 0,
                        },
                        "this_version": {
                            "data_volume": 0.0,
                            "downloads": 0,
                            "unique_downloads": 0,
                            "unique_views": 0,
                            "views": 0,
                        },
                    },
                    "updated": "2025-06-04T19:50:38.419527+00:00",
                    "uuid": "d78f293f-3623-4ad9-9e96-5b9ceff3ce7c",
                    "version_id": 8,
                    "versions": {
                        "index": 1,
                        "is_latest": True,
                        "is_latest_draft": True,
                        "latest_id": "d78f293f-3623-4ad9-9e96-5b9ceff3ce7c",
                        "latest_index": 1,
                        "next_draft_id": None,
                    },
                },
            },
            {
                "_id": "bdd5be35-855a-4967-a50b-0747ad92a5c6",
                "_index": "rdmrecords-records-record-v6.0.0-1749066625",
                "_score": 1.0,
                "_source": {
                    "$schema": "local://records/record-v6.0.0.json",
                    "access": {
                        "embargo": {"active": False, "reason": None, "until": None},
                        "files": "restricted",
                        "record": "public",
                        "status": "metadata-only",
                    },
                    "created": "2025-06-03T17:35:55.817258+00:00",
                    "custom_fields": {
                        "imprint:imprint": {
                            "pages": "Online " "publication",
                            "place": "Vancouver, " "BC",
                        },
                        "kcr:ai_usage": {"ai_used": False},
                        "kcr:edition": "3rd",
                        "kcr:user_defined_tags": [
                            "Canadian " "English",
                            "Canadian " "Studies",
                            "Language " "and " "Identity",
                            "Historical " "Lexicography",
                            "Canadian " "English " "Lexicography",
                            "Anglphone " "Canada",
                            "Dialectology",
                            "Sociolinguistics",
                        ],
                    },
                    "deletion_status": "P",
                    "files": {"enabled": False},
                    "has_draft": False,
                    "id": "g8s7m-1ph68",
                    "is_deleted": False,
                    "is_published": True,
                    "media_files": {"enabled": False},
                    "metadata": {
                        "additional_titles": [
                            {
                                "title": "DCHP-3",
                                "type": {
                                    "@v": "d402c48a-aabd-432e-b6ca-346d8d0475b6::1",
                                    "id": "alternative-title",
                                    "title": {"en": "Alternative " "title"},
                                },
                            }
                        ],
                        "combined_subjects": [
                            "FAST-topical::English "
                            "language--Written "
                            "English--History",
                            "FAST-topical::English "
                            "language--Spoken "
                            "English--Research",
                            "FAST-topical::Canadian " "literature",
                            "FAST-topical::Canadian " "literature--Periodicals",
                            "FAST-topical::Canadian " "prose " "literature",
                            "FAST-topical::Canadian " "literature--Bibliography",
                            "FAST-topical::French-Canadian " "literature",
                            "FAST-topical::Arts, " "Canadian",
                            "FAST-topical::Authors, " "Canadian",
                            "FAST-topical::Canadian " "periodicals",
                            "FAST-topical::English " "language--Lexicography--History",
                        ],
                        "creators": [
                            {
                                "affiliations": [
                                    {"name": "University " "Of " "British " "Columbia"}
                                ],
                                "person_or_org": {
                                    "family_name": "Dollinger",
                                    "given_name": "Stefan",
                                    "identifiers": [
                                        {
                                            "identifier": "stefand",
                                            "scheme": "kc_username",
                                        }
                                    ],
                                    "name": "Dollinger, " "Stefan",
                                    "type": "personal",
                                },
                                "role": {
                                    "@v": "5c46225e-5b2f-4614-9588-210bbe334a51::1",
                                    "id": "author",
                                    "title": {"en": "Author"},
                                },
                            },
                            {
                                "affiliations": [
                                    {
                                        "@v": "2f6216f9-c739-406f-9720-a1bfc7c6a302::2",
                                        "id": "03rmrcq20",
                                        "identifiers": [
                                            {"identifier": "03rmrcq20", "scheme": "ror"}
                                        ],
                                        "name": (
                                            "University " "of " "British " "Columbia"
                                        ),
                                    }
                                ],
                                "person_or_org": {
                                    "family_name": "Fee",
                                    "given_name": "Margery",
                                    "name": "Fee, " "Margery",
                                    "type": "personal",
                                },
                                "role": {
                                    "@v": "5c46225e-5b2f-4614-9588-210bbe334a51::1",
                                    "id": "author",
                                    "title": {"en": "Author"},
                                },
                            },
                        ],
                        "description": (
                            "This is the third "
                            "edition of the "
                            "1967 A Dictionary "
                            "of Canadianisms "
                            "on Historical "
                            "Principles "
                            "(DCHP-1). DCHP-3 "
                            "integrates the "
                            "legacy data of "
                            "DCHP-1 (1967) and "
                            "the updated data "
                            "of DCHP-2 (2017) "
                            "with new content "
                            "to form DCHP-3. "
                            "There are 136 new "
                            "and updated "
                            "entries in this "
                            "edition for a new "
                            "total of 12,045 "
                            "headwords with "
                            "14,586 meanings.\n"
                            "\n"
                            "DCHP-3 lists, as "
                            "did its "
                            "predecessors, "
                            "Canadianisms. A "
                            "Canadianism is "
                            'defined as "a '
                            "word, expression, "
                            "or meaning which "
                            "is native to "
                            "Canada or which "
                            "is distinctively "
                            "characteristic of "
                            "Canadian usage "
                            "though not "
                            "necessarily "
                            "exclusive to "
                            'Canada." (Walter '
                            "S. Avis in "
                            "DCHP-1, page "
                            "xiii; see DCHP-1 "
                            "Online)\n"
                            "\n"
                            "This work should "
                            "be cited as:\n"
                            "\n"
                            "Dollinger, Stefan "
                            "and Margery Fee "
                            "(eds). 2025. "
                            "DCHP-3: The "
                            "Dictionary of "
                            "Canadianisms on "
                            "Historical "
                            "Principles, Third "
                            "Edition. "
                            "Vancouver, BC: "
                            "University of "
                            "British Columbia, "
                            "www.dchp.ca/dchp3."
                        ),
                        "publication_date": "2025-06-03",
                        "publication_date_range": {
                            "gte": "2025-06-03",
                            "lte": "2025-06-03",
                        },
                        "publisher": "UBC",
                        "resource_type": {
                            "@v": "3767e0d7-ae08-4409-ba98-05bb772b2ec5::1",
                            "id": "textDocument-book",
                            "props": {
                                "subtype": "textDocument-book",
                                "type": "textDocument",
                            },
                            "title": {"en": "Book"},
                        },
                        "subjects": [
                            {
                                "@v": "e0d0ccc8-b886-48e7-9892-efe49232dfda::1",
                                "id": "http://id.worldcat.org/fast/911979",
                                "scheme": "FAST-topical",
                                "subject": (
                                    "English " "language--Written " "English--History"
                                ),
                            },
                            {
                                "@v": "6712395d-3507-4ca7-8633-4bd3dac82308::1",
                                "id": "http://id.worldcat.org/fast/911660",
                                "scheme": "FAST-topical",
                                "subject": (
                                    "English " "language--Spoken " "English--Research"
                                ),
                            },
                            {
                                "@v": "366dd33f-3dab-4372-8d99-ee1b086823bf::1",
                                "id": "http://id.worldcat.org/fast/845111",
                                "scheme": "FAST-topical",
                                "subject": "Canadian " "literature",
                            },
                            {
                                "@v": "66356207-a14a-4768-b721-e415248d4a57::1",
                                "id": "http://id.worldcat.org/fast/845142",
                                "scheme": "FAST-topical",
                                "subject": "Canadian " "literature--Periodicals",
                            },
                            {
                                "@v": "2f7e4fa7-4e07-4d91-a721-04b683cb90e3::1",
                                "id": "http://id.worldcat.org/fast/845184",
                                "scheme": "FAST-topical",
                                "subject": "Canadian " "prose " "literature",
                            },
                            {
                                "@v": "dddb9d76-40da-4253-8c53-0fb050c8fe09::1",
                                "id": "http://id.worldcat.org/fast/1424786",
                                "scheme": "FAST-topical",
                                "subject": "Canadian " "literature--Bibliography",
                            },
                            {
                                "@v": "21969c22-f3c8-4554-b55e-f7cd7be937ba::1",
                                "id": "http://id.worldcat.org/fast/934875",
                                "scheme": "FAST-topical",
                                "subject": "French-Canadian " "literature",
                            },
                            {
                                "@v": "c13d142c-70ea-4866-b464-5c29a7a4e3de::1",
                                "id": "http://id.worldcat.org/fast/817954",
                                "scheme": "FAST-topical",
                                "subject": "Arts, " "Canadian",
                            },
                            {
                                "@v": "a2ec00ca-0409-4c60-98fa-477afeee65b3::1",
                                "id": "http://id.worldcat.org/fast/821870",
                                "scheme": "FAST-topical",
                                "subject": "Authors, " "Canadian",
                            },
                            {
                                "@v": "827a7bc9-76c8-4ab8-89d0-f6d4ced99216::1",
                                "id": "http://id.worldcat.org/fast/845170",
                                "scheme": "FAST-topical",
                                "subject": "Canadian " "periodicals",
                            },
                            {
                                "@v": "5df2a4a7-ef29-4c6c-baee-5485d78afd07::1",
                                "id": "http://id.worldcat.org/fast/911328",
                                "scheme": "FAST-topical",
                                "subject": "English " "language--Lexicography--History",
                            },
                        ],
                        "title": (
                            "Dictionary of "
                            "Canadianisms on "
                            "Historical Principles, "
                            "Third Edition "
                            "(www.dchp.ca/dchp3)"
                        ),
                    },
                    "parent": {
                        "$schema": "local://records/parent-v3.0.0.json",
                        "access": {
                            "grant_tokens": [],
                            "grants": [],
                            "links": [],
                            "owned_by": {"user": 1},
                            "settings": {
                                "accept_conditions_text": None,
                                "allow_guest_requests": False,
                                "allow_user_requests": False,
                                "secret_link_expiration": 0,
                            },
                        },
                        "communities": {
                            "default": "8e620d7e-0739-441c-a4c7-b0bcb3e92a38",
                            "entries": [
                                {
                                    "@v": "8e620d7e-0739-441c-a4c7-b0bcb3e92a38::2",
                                    "created": "2025-06-04T19:50:33.799803+00:00",
                                    "id": "8e620d7e-0739-441c-a4c7-b0bcb3e92a38",
                                    "is_verified": True,
                                    "metadata": {
                                        "organizations": [
                                            {"name": "Organization " "1"}
                                        ],
                                        "title": "My " "Community",
                                        "type": {
                                            "@v": (
                                                "3a6489cf-e72c-4a8a-996d-8260dd628ff8::1"
                                            ),
                                            "id": "event",
                                            "title": {"en": "Event"},
                                        },
                                        "website": "https://my-community.com",
                                    },
                                    "slug": "knowledge-commons",
                                    "updated": "2025-06-04T19:50:34.002417+00:00",
                                    "uuid": "8e620d7e-0739-441c-a4c7-b0bcb3e92a38",
                                    "version_id": 3,
                                }
                            ],
                            "ids": ["8e620d7e-0739-441c-a4c7-b0bcb3e92a38"],
                        },
                        "created": "2025-06-04T19:50:38.691702+00:00",
                        "id": "t7px4-s5v37",
                        "is_verified": True,
                        "pid": {
                            "obj_type": "rec",
                            "pid_type": "recid",
                            "pk": 115,
                            "status": "R",
                        },
                        "pids": {
                            "doi": {
                                "client": "datacite",
                                "identifier": "10.17613/t7px4-s5v37",
                                "provider": "datacite",
                            }
                        },
                        "updated": "2025-06-04T19:50:40.042924+00:00",
                        "uuid": "bfcc8a46-3701-4806-b850-4e55689dc45e",
                        "version_id": 9,
                    },
                    "pid": {
                        "obj_type": "rec",
                        "pid_type": "recid",
                        "pk": 116,
                        "status": "R",
                    },
                    "pids": {
                        "doi": {
                            "client": "datacite",
                            "identifier": "10.17613/0dtmf-ph235",
                            "provider": "datacite",
                        },
                        "oai": {
                            "identifier": "oai:https://works.hcommons.org:0dtmf-ph235",
                            "provider": "oai",
                        },
                    },
                    "stats": {
                        "all_versions": {
                            "data_volume": 0.0,
                            "downloads": 0,
                            "unique_downloads": 0,
                            "unique_views": 0,
                            "views": 0,
                        },
                        "this_version": {
                            "data_volume": 0.0,
                            "downloads": 0,
                            "unique_downloads": 0,
                            "unique_views": 0,
                            "views": 0,
                        },
                    },
                    "updated": "2025-06-04T19:50:40.000993+00:00",
                    "uuid": "bdd5be35-855a-4967-a50b-0747ad92a5c6",
                    "version_id": 7,
                    "versions": {
                        "index": 1,
                        "is_latest": True,
                        "is_latest_draft": True,
                        "latest_id": "bdd5be35-855a-4967-a50b-0747ad92a5c6",
                        "latest_index": 1,
                        "next_draft_id": None,
                    },
                },
            },
            {
                "_id": "efaa128b-aa72-4fe9-99cc-caf08af025cd",
                "_index": "rdmrecords-records-record-v6.0.0-1749066625",
                "_score": 1.0,
                "_source": {
                    "$schema": "local://records/record-v6.0.0.json",
                    "access": {
                        "embargo": {"active": False, "reason": None, "until": None},
                        "files": "public",
                        "record": "public",
                        "status": "open",
                    },
                    "created": "2025-05-30T23:53:04.686003+00:00",
                    "custom_fields": {
                        "kcr:ai_usage": {"ai_used": False},
                        "kcr:user_defined_tags": [
                            "incarceration",
                            "library " "and " "information " "science",
                            "reentry",
                            "outreach",
                            "library " "services",
                            "incarcerated " "people",
                        ],
                    },
                    "deletion_status": "P",
                    "files": {
                        "count": 1,
                        "enabled": True,
                        "entries": [
                            {
                                "checksum": "md5:dc62cbbec9344d6b9aaca9761a2fa4e2",
                                "ext": "pdf",
                                "file_id": "1e8d256a-c4f8-462c-9096-b4af3327e379",
                                "key": (
                                    "Trends and "
                                    "Concerns in "
                                    "Library "
                                    "Services for "
                                    "Incarcerated "
                                    "People and "
                                    "People in the "
                                    "Process of "
                                    "Reentry "
                                    "Publication "
                                    "Review "
                                    "(2020-2022)-1.pdf"
                                ),
                                "metadata": {},
                                "mimetype": "application/pdf",
                                "object_version_id": (
                                    "bd8fb58e-105e-4fab-a0aa-f40b91af4dcd"
                                ),
                                "size": 458036,
                                "uuid": "6886ca0b-0533-46e0-874e-ea2303911e56",
                                "version_id": 3,
                            }
                        ],
                        "mimetypes": ["application/pdf"],
                        "totalbytes": 458036,
                        "types": ["pdf"],
                    },
                    "has_draft": False,
                    "id": "cswpd-81b75",
                    "is_deleted": False,
                    "is_published": True,
                    "media_files": {"enabled": False},
                    "metadata": {
                        "combined_subjects": [
                            "FAST-topical::Library " "science",
                            "FAST-topical::Mass " "incarceration",
                            "FAST-topical::Library " "science " "literature",
                            "FAST-topical::Library " "science--Standards",
                            "FAST-topical::Children "
                            "of "
                            "prisoners--Services "
                            "for",
                            "FAST-topical::Legal "
                            "assistance "
                            "to "
                            "prisoners--U.S. "
                            "states",
                        ],
                        "creators": [
                            {
                                "affiliations": [
                                    {"name": "San " "Francisco " "Public " "Library"}
                                ],
                                "person_or_org": {
                                    "family_name": "Austin",
                                    "given_name": "Jeanie",
                                    "identifiers": [
                                        {
                                            "identifier": "jeanieaustin",
                                            "scheme": "kc_username",
                                        },
                                        {
                                            "identifier": "0009-0008-0969-5474",
                                            "scheme": "orcid",
                                        },
                                    ],
                                    "name": "Austin, " "Jeanie",
                                    "type": "personal",
                                },
                                "role": {
                                    "@v": "5c46225e-5b2f-4614-9588-210bbe334a51::1",
                                    "id": "author",
                                    "title": {"en": "Author"},
                                },
                            },
                            {
                                "affiliations": [
                                    {"name": "San " "Francisco " "Public " "Library"}
                                ],
                                "person_or_org": {
                                    "family_name": "Ness",
                                    "given_name": "Nili",
                                    "name": "Ness, " "Nili",
                                    "type": "personal",
                                },
                                "role": {
                                    "@v": "5c46225e-5b2f-4614-9588-210bbe334a51::1",
                                    "id": "author",
                                    "title": {"en": "Author"},
                                },
                            },
                            {
                                "affiliations": [
                                    {
                                        "@v": "13078784-d2b0-4b3f-8208-6dcfe1b34d33::2",
                                        "id": "013v4ng57",
                                        "identifiers": [
                                            {"identifier": "013v4ng57", "scheme": "ror"}
                                        ],
                                        "name": "San " "Francisco " "Public " "Library",
                                    }
                                ],
                                "person_or_org": {
                                    "family_name": "Okelo",
                                    "given_name": "Bee",
                                    "name": "Okelo, " "Bee",
                                    "type": "personal",
                                },
                                "role": {
                                    "@v": "5c46225e-5b2f-4614-9588-210bbe334a51::1",
                                    "id": "author",
                                    "title": {"en": "Author"},
                                },
                            },
                            {
                                "affiliations": [
                                    {"name": "San " "Francisco " "Public " "Library"}
                                ],
                                "person_or_org": {
                                    "family_name": "Kinnon",
                                    "given_name": "Rachel",
                                    "name": "Kinnon, " "Rachel",
                                    "type": "personal",
                                },
                                "role": {
                                    "@v": "5c46225e-5b2f-4614-9588-210bbe334a51::1",
                                    "id": "author",
                                    "title": {"en": "Author"},
                                },
                            },
                        ],
                        "description": (
                            "This is a white "
                            "paper reviewing "
                            "publications from "
                            "2020-2022 that "
                            "relate to library "
                            "and information "
                            "services for "
                            "people who are "
                            "incarcerated or "
                            "in the process of "
                            "reentry. It "
                            "covers a variety "
                            "of library types, "
                            "forms of "
                            "outreach, "
                            "services to "
                            "specific "
                            "demographics, and "
                            "emerging research "
                            "concerns."
                        ),
                        "languages": [
                            {
                                "@v": "5cb9da36-15e8-4291-9f4e-414578306ac1::1",
                                "id": "eng",
                                "title": {"en": "English"},
                            }
                        ],
                        "publication_date": "2023-11-01",
                        "publication_date_range": {
                            "gte": "2023-11-01",
                            "lte": "2023-11-01",
                        },
                        "publisher": "Knowledge Commons",
                        "resource_type": {
                            "@v": "7f9b4648-37d1-4cf5-a228-24d7eb51a43a::1",
                            "id": "textDocument-journalArticle",
                            "props": {
                                "subtype": "textDocument-journalArticle",
                                "type": "textDocument",
                            },
                            "title": {"en": "Journal " "Article"},
                        },
                        "subjects": [
                            {
                                "@v": "03c6d0f1-4801-42a3-b7f1-16fc76197949::1",
                                "id": "http://id.worldcat.org/fast/997916",
                                "scheme": "FAST-topical",
                                "subject": "Library " "science",
                            },
                            {
                                "@v": "a3471e1b-59b9-47f3-ab74-3beef4a61617::1",
                                "id": "http://id.worldcat.org/fast/2060143",
                                "scheme": "FAST-topical",
                                "subject": "Mass " "incarceration",
                            },
                            {
                                "@v": "2f71621e-dd85-4283-ba81-8c768621101b::1",
                                "id": "http://id.worldcat.org/fast/997987",
                                "scheme": "FAST-topical",
                                "subject": "Library " "science " "literature",
                            },
                            {
                                "@v": "52d7861a-b506-49b8-9caa-b151ef0c3f35::1",
                                "id": "http://id.worldcat.org/fast/997974",
                                "scheme": "FAST-topical",
                                "subject": "Library " "science--Standards",
                            },
                            {
                                "@v": "5238d9aa-765a-42c5-a781-bc6ac2534780::1",
                                "id": "http://id.worldcat.org/fast/855500",
                                "scheme": "FAST-topical",
                                "subject": (
                                    "Children " "of " "prisoners--Services " "for"
                                ),
                            },
                            {
                                "@v": "be275324-5cf5-4b1a-9243-d5b2d5c002ee::1",
                                "id": "http://id.worldcat.org/fast/995415",
                                "scheme": "FAST-topical",
                                "subject": (
                                    "Legal "
                                    "assistance "
                                    "to "
                                    "prisoners--U.S. "
                                    "states"
                                ),
                            },
                        ],
                        "title": (
                            "Trends and Concerns in "
                            "Library Services for "
                            "Incarcerated People and "
                            "People in the Process "
                            "of Reentry: Publication "
                            "Review (2020-2022)"
                        ),
                    },
                    "parent": {
                        "$schema": "local://records/parent-v3.0.0.json",
                        "access": {
                            "grant_tokens": [],
                            "grants": [],
                            "links": [],
                            "owned_by": {"user": 1},
                            "settings": {
                                "accept_conditions_text": None,
                                "allow_guest_requests": False,
                                "allow_user_requests": False,
                                "secret_link_expiration": 0,
                            },
                        },
                        "communities": {
                            "default": "8e620d7e-0739-441c-a4c7-b0bcb3e92a38",
                            "entries": [
                                {
                                    "@v": "8e620d7e-0739-441c-a4c7-b0bcb3e92a38::2",
                                    "created": "2025-06-04T19:50:33.799803+00:00",
                                    "id": "8e620d7e-0739-441c-a4c7-b0bcb3e92a38",
                                    "is_verified": True,
                                    "metadata": {
                                        "organizations": [
                                            {"name": "Organization " "1"}
                                        ],
                                        "title": "My " "Community",
                                        "type": {
                                            "@v": (
                                                "3a6489cf-e72c-4a8a-996d-8260dd628ff8::1"
                                            ),
                                            "id": "event",
                                            "title": {"en": "Event"},
                                        },
                                        "website": "https://my-community.com",
                                    },
                                    "slug": "knowledge-commons",
                                    "updated": "2025-06-04T19:50:34.002417+00:00",
                                    "uuid": "8e620d7e-0739-441c-a4c7-b0bcb3e92a38",
                                    "version_id": 3,
                                }
                            ],
                            "ids": ["8e620d7e-0739-441c-a4c7-b0bcb3e92a38"],
                        },
                        "created": "2025-06-04T19:50:40.430644+00:00",
                        "id": "8kkj7-88j23",
                        "is_verified": True,
                        "pid": {
                            "obj_type": "rec",
                            "pid_type": "recid",
                            "pk": 120,
                            "status": "R",
                        },
                        "pids": {},
                        "updated": "2025-06-04T19:50:41.331660+00:00",
                        "uuid": "4826c0bd-fe59-495c-8dd1-c83ca50a1408",
                        "version_id": 9,
                    },
                    "pid": {
                        "obj_type": "rec",
                        "pid_type": "recid",
                        "pk": 121,
                        "status": "R",
                    },
                    "pids": {
                        "doi": {
                            "identifier": "10.5281/zenodo.15558284",
                            "provider": "external",
                        },
                        "oai": {
                            "identifier": "oai:https://works.hcommons.org:5ryf5-bfn20",
                            "provider": "oai",
                        },
                    },
                    "stats": {
                        "all_versions": {
                            "data_volume": 0.0,
                            "downloads": 0,
                            "unique_downloads": 0,
                            "unique_views": 0,
                            "views": 0,
                        },
                        "this_version": {
                            "data_volume": 0.0,
                            "downloads": 0,
                            "unique_downloads": 0,
                            "unique_views": 0,
                            "views": 0,
                        },
                    },
                    "updated": "2025-06-04T19:50:41.295678+00:00",
                    "uuid": "efaa128b-aa72-4fe9-99cc-caf08af025cd",
                    "version_id": 8,
                    "versions": {
                        "index": 1,
                        "is_latest": True,
                        "is_latest_draft": True,
                        "latest_id": "efaa128b-aa72-4fe9-99cc-caf08af025cd",
                        "latest_index": 1,
                        "next_draft_id": None,
                    },
                },
            },
        ],
        "max_score": 1.0,
        "total": {"relation": "eq", "value": 3},
    },
    "timed_out": False,
    "took": 41,
}

# Mock delta query response for three imported records in 2025-05-30 to 2025-06-03
MOCK_RECORD_DELTA_QUERY_RESPONSE = {
    "_shards": {"failed": 0, "skipped": 0, "successful": 5, "total": 5},
    "aggregations": {
        "by_day": {
            "buckets": [
                {
                    "by_access_status": {
                        "buckets": [
                            {
                                "doc_count": 1,
                                "file_count": {"value": 1},
                                "key": "open",
                                "total_bytes": {"value": 458036.0},
                                "with_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                                "without_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                            }
                        ],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_affiliation_contributor": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_affiliation_creator": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_file_type": {
                        "buckets": [
                            {
                                "doc_count": 1,
                                "key": "pdf",
                                "total_bytes": {"value": 458036.0},
                                "unique_parents": {"value": 1},
                                "unique_records": {"value": 1},
                            }
                        ],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_funder": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_language": {
                        "buckets": [
                            {
                                "doc_count": 1,
                                "file_count": {"value": 1},
                                "key": "eng",
                                "total_bytes": {"value": 458036.0},
                                "with_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                                "without_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                            }
                        ],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_license": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_periodical": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_publisher": {
                        "buckets": [
                            {
                                "doc_count": 1,
                                "file_count": {"value": 1},
                                "key": "Knowledge " "Commons",
                                "total_bytes": {"value": 458036.0},
                                "with_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                                "without_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                            }
                        ],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_resource_type": {
                        "buckets": [
                            {
                                "doc_count": 1,
                                "file_count": {"value": 1},
                                "key": "textDocument-journalArticle",
                                "total_bytes": {"value": 458036.0},
                                "with_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                                "without_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                            }
                        ],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_subject": {
                        "buckets": [
                            {
                                "doc_count": 1,
                                "file_count": {"value": 1},
                                "key": "http://id.worldcat.org/fast/2060143",
                                "total_bytes": {"value": 458036.0},
                                "with_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                                "without_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                            },
                            {
                                "doc_count": 1,
                                "file_count": {"value": 1},
                                "key": "http://id.worldcat.org/fast/855500",
                                "total_bytes": {"value": 458036.0},
                                "with_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                                "without_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                            },
                            {
                                "doc_count": 1,
                                "file_count": {"value": 1},
                                "key": "http://id.worldcat.org/fast/995415",
                                "total_bytes": {"value": 458036.0},
                                "with_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                                "without_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                            },
                            {
                                "doc_count": 1,
                                "file_count": {"value": 1},
                                "key": "http://id.worldcat.org/fast/997916",
                                "total_bytes": {"value": 458036.0},
                                "with_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                                "without_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                            },
                            {
                                "doc_count": 1,
                                "file_count": {"value": 1},
                                "key": "http://id.worldcat.org/fast/997974",
                                "total_bytes": {"value": 458036.0},
                                "with_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                                "without_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                            },
                            {
                                "doc_count": 1,
                                "file_count": {"value": 1},
                                "key": "http://id.worldcat.org/fast/997987",
                                "total_bytes": {"value": 458036.0},
                                "with_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                                "without_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                            },
                        ],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": 1748563200000,
                    "key_as_string": "2025-05-30",
                    "total_bytes": {"value": 458036.0},
                    "total_records": {"value": 1},
                    "uploaders": {"value": 1},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "by_access_status": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_affiliation_contributor": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_affiliation_creator": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_file_type": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_funder": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_language": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_license": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_periodical": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_publisher": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_resource_type": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_subject": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "doc_count": 0,
                    "file_count": {"value": 0},
                    "key": 1748649600000,
                    "key_as_string": "2025-05-31",
                    "total_bytes": {"value": 0.0},
                    "total_records": {"value": 0},
                    "uploaders": {"value": 0},
                    "with_files": {
                        "doc_count": 0,
                        "meta": {},
                        "unique_parents": {"value": 0},
                    },
                    "without_files": {
                        "doc_count": 0,
                        "meta": {},
                        "unique_parents": {"value": 0},
                    },
                },
                {
                    "by_access_status": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_affiliation_contributor": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_affiliation_creator": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_file_type": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_funder": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_language": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_license": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_periodical": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_publisher": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_resource_type": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_subject": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "doc_count": 0,
                    "file_count": {"value": 0},
                    "key": 1748736000000,
                    "key_as_string": "2025-06-01",
                    "total_bytes": {"value": 0.0},
                    "total_records": {"value": 0},
                    "uploaders": {"value": 0},
                    "with_files": {
                        "doc_count": 0,
                        "meta": {},
                        "unique_parents": {"value": 0},
                    },
                    "without_files": {
                        "doc_count": 0,
                        "meta": {},
                        "unique_parents": {"value": 0},
                    },
                },
                {
                    "by_access_status": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_affiliation_contributor": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_affiliation_creator": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_file_type": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_funder": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_language": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_license": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_periodical": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_publisher": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_resource_type": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_subject": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "doc_count": 0,
                    "file_count": {"value": 0},
                    "key": 1748822400000,
                    "key_as_string": "2025-06-02",
                    "total_bytes": {"value": 0.0},
                    "total_records": {"value": 0},
                    "uploaders": {"value": 0},
                    "with_files": {
                        "doc_count": 0,
                        "meta": {},
                        "unique_parents": {"value": 0},
                    },
                    "without_files": {
                        "doc_count": 0,
                        "meta": {},
                        "unique_parents": {"value": 0},
                    },
                },
                {
                    "by_access_status": {
                        "buckets": [
                            {
                                "doc_count": 1,
                                "file_count": {"value": 0},
                                "key": "metadata-only",
                                "total_bytes": {"value": 0.0},
                                "with_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                                "without_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                            },
                            {
                                "doc_count": 1,
                                "file_count": {"value": 1},
                                "key": "open",
                                "total_bytes": {"value": 1984949.0},
                                "with_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                                "without_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                            },
                        ],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_affiliation_contributor": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_affiliation_creator": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_file_type": {
                        "buckets": [
                            {
                                "doc_count": 1,
                                "key": "pdf",
                                "total_bytes": {"value": 1984949.0},
                                "unique_parents": {"value": 1},
                                "unique_records": {"value": 1},
                            }
                        ],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_funder": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_language": {
                        "buckets": [
                            {
                                "doc_count": 1,
                                "file_count": {"value": 1},
                                "key": "eng",
                                "total_bytes": {"value": 1984949.0},
                                "with_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                                "without_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                            }
                        ],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_license": {
                        "buckets": [
                            {
                                "doc_count": 1,
                                "file_count": {"value": 1},
                                "key": "cc-by-sa-4.0",
                                "total_bytes": {"value": 1984949.0},
                                "with_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                                "without_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                            }
                        ],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_periodical": {
                        "buckets": [
                            {
                                "doc_count": 1,
                                "file_count": {"value": 1},
                                "key": "N/A",
                                "total_bytes": {"value": 1984949.0},
                                "with_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                                "without_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                            }
                        ],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_publisher": {
                        "buckets": [
                            {
                                "doc_count": 1,
                                "file_count": {"value": 1},
                                "key": "Knowledge " "Commons",
                                "total_bytes": {"value": 1984949.0},
                                "with_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                                "without_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                            },
                            {
                                "doc_count": 1,
                                "file_count": {"value": 0},
                                "key": "UBC",
                                "total_bytes": {"value": 0.0},
                                "with_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                                "without_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                            },
                        ],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_resource_type": {
                        "buckets": [
                            {
                                "doc_count": 1,
                                "file_count": {"value": 0},
                                "key": "textDocument-book",
                                "total_bytes": {"value": 0.0},
                                "with_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                                "without_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                            },
                            {
                                "doc_count": 1,
                                "file_count": {"value": 1},
                                "key": "textDocument-journalArticle",
                                "total_bytes": {"value": 1984949.0},
                                "with_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                                "without_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                            },
                        ],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_subject": {
                        "buckets": [
                            {
                                "doc_count": 1,
                                "file_count": {"value": 0},
                                "key": "http://id.worldcat.org/fast/1424786",
                                "total_bytes": {"value": 0.0},
                                "with_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                                "without_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                            },
                            {
                                "doc_count": 1,
                                "file_count": {"value": 0},
                                "key": "http://id.worldcat.org/fast/817954",
                                "total_bytes": {"value": 0.0},
                                "with_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                                "without_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                            },
                            {
                                "doc_count": 1,
                                "file_count": {"value": 0},
                                "key": "http://id.worldcat.org/fast/821870",
                                "total_bytes": {"value": 0.0},
                                "with_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                                "without_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                            },
                            {
                                "doc_count": 1,
                                "file_count": {"value": 0},
                                "key": "http://id.worldcat.org/fast/845111",
                                "total_bytes": {"value": 0.0},
                                "with_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                                "without_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                            },
                            {
                                "doc_count": 1,
                                "file_count": {"value": 0},
                                "key": "http://id.worldcat.org/fast/845142",
                                "total_bytes": {"value": 0.0},
                                "with_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                                "without_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                            },
                            {
                                "doc_count": 1,
                                "file_count": {"value": 0},
                                "key": "http://id.worldcat.org/fast/845170",
                                "total_bytes": {"value": 0.0},
                                "with_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                                "without_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                            },
                            {
                                "doc_count": 1,
                                "file_count": {"value": 0},
                                "key": "http://id.worldcat.org/fast/845184",
                                "total_bytes": {"value": 0.0},
                                "with_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                                "without_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                            },
                            {
                                "doc_count": 1,
                                "file_count": {"value": 0},
                                "key": "http://id.worldcat.org/fast/911328",
                                "total_bytes": {"value": 0.0},
                                "with_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                                "without_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                            },
                            {
                                "doc_count": 1,
                                "file_count": {"value": 0},
                                "key": "http://id.worldcat.org/fast/911660",
                                "total_bytes": {"value": 0.0},
                                "with_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                                "without_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                            },
                            {
                                "doc_count": 1,
                                "file_count": {"value": 0},
                                "key": "http://id.worldcat.org/fast/911979",
                                "total_bytes": {"value": 0.0},
                                "with_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                                "without_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                            },
                        ],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 1,
                    },
                    "doc_count": 2,
                    "file_count": {"value": 1},
                    "key": 1748908800000,
                    "key_as_string": "2025-06-03",
                    "total_bytes": {"value": 1984949.0},
                    "total_records": {"value": 2},
                    "uploaders": {"value": 1},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                },
            ],
            "meta": {},
        }
    },
    "hits": {"hits": [], "max_score": None, "total": {"relation": "eq", "value": 3}},
    "timed_out": False,
    "took": 121,
}

MOCK_RECORD_DELTA_AGGREGATION_DOCS = [
    {
        "_id": "5733deff-2f76-4f8c-bb99-8df48bdd725f-2025-05-30",
        "_index": "stats-community-records-delta-2025",
        "_score": 1.0,
        "_source": {
            "community_id": "5733deff-2f76-4f8c-bb99-8df48bdd725f",
            "files": {
                "added": {"data_volume": 59117831.0, "file_count": 2},
                "removed": {"data_volume": 0.0, "file_count": 0},
            },
            "parents": {
                "added": {"metadata_only": 0, "with_files": 2},
                "removed": {"metadata_only": 0, "with_files": 0},
            },
            "period_end": "2025-05-30T23:59:59",
            "period_start": "2025-05-30T00:00:00",
            "records": {
                "added": {"metadata_only": 0, "with_files": 2},
                "removed": {"metadata_only": 0, "with_files": 0},
            },
            "subcounts": {
                "by_access_status": [
                    {
                        "files": {
                            "added": {"data_volume": 59117831.0, "file_count": 2},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "open",
                        "label": "",
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 2},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 2},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    }
                ],
                "by_affiliation_contributor": [],
                "by_affiliation_creator": [
                    {
                        "files": {
                            "added": {"data_volume": 458036.0, "file_count": 1},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "013v4ng57",
                        "label": "",
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    }
                ],
                "by_file_type": [
                    {
                        "added": {
                            "data_volume": 59117831.0,
                            "files": 2,
                            "parents": 2,
                            "records": 2,
                        },
                        "id": "pdf",
                        "label": "",
                        "removed": {
                            "data_volume": 0.0,
                            "files": 0,
                            "parents": 0,
                            "records": 0,
                        },
                    }
                ],
                "by_funder": [],
                "by_language": [
                    {
                        "files": {
                            "added": {"data_volume": 458036.0, "file_count": 1},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "eng",
                        "label": "English",
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    }
                ],
                "by_license": [],
                "by_periodical": [],
                "by_publisher": [
                    {
                        "files": {
                            "added": {"data_volume": 58659795.0, "file_count": 1},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "Apocryphile Press",
                        "label": "",
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 458036.0, "file_count": 1},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "Knowledge Commons",
                        "label": "",
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                ],
                "by_resource_type": [
                    {
                        "files": {
                            "added": {"data_volume": 58659795.0, "file_count": 1},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "textDocument-bookSection",
                        "label": "Book Section",
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 458036.0, "file_count": 1},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "textDocument-journalArticle",
                        "label": "Journal Article",
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                ],
                "by_subject": [
                    {
                        "files": {
                            "added": {"data_volume": 58659795.0, "file_count": 1},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "http://id.worldcat.org/fast/973589",
                        "label": "Inklings (Group of writers)",
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 458036.0, "file_count": 1},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "http://id.worldcat.org/fast/855500",
                        "label": "Children of prisoners--Services for",
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 458036.0, "file_count": 1},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "http://id.worldcat.org/fast/997916",
                        "label": "Library science",
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 458036.0, "file_count": 1},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "http://id.worldcat.org/fast/2060143",
                        "label": "Mass incarceration",
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 458036.0, "file_count": 1},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "http://id.worldcat.org/fast/997974",
                        "label": "Library science--Standards",
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 458036.0, "file_count": 1},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "http://id.worldcat.org/fast/997987",
                        "label": "Library science literature",
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 458036.0, "file_count": 1},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "http://id.worldcat.org/fast/995415",
                        "label": "Legal assistance to prisoners--U.S. states",
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                ],
            },
            "timestamp": "2025-06-05T18:45:58",
            "updated_timestamp": "2025-06-05T18:45:58",
            "uploaders": 1,
        },
    },
    {
        "_id": "5733deff-2f76-4f8c-bb99-8df48bdd725f-2025-05-31",
        "_index": "stats-community-records-delta-2025",
        "_score": 1.0,
        "_source": {
            "community_id": "5733deff-2f76-4f8c-bb99-8df48bdd725f",
            "files": {
                "added": {"data_volume": 0.0, "file_count": 0},
                "removed": {"data_volume": 0.0, "file_count": 0},
            },
            "parents": {
                "added": {"metadata_only": 0, "with_files": 0},
                "removed": {"metadata_only": 0, "with_files": 0},
            },
            "period_end": "2025-05-31T23:59:59",
            "period_start": "2025-05-31T00:00:00",
            "records": {
                "added": {"metadata_only": 0, "with_files": 0},
                "removed": {"metadata_only": 0, "with_files": 0},
            },
            "subcounts": {
                "by_access_status": [],
                "by_affiliation_contributor": [],
                "by_affiliation_creator": [],
                "by_file_type": [],
                "by_funder": [],
                "by_language": [],
                "by_license": [],
                "by_periodical": [],
                "by_publisher": [],
                "by_resource_type": [],
                "by_subject": [],
            },
            "timestamp": "2025-06-05T18:45:58",
            "updated_timestamp": "2025-06-05T18:45:58",
            "uploaders": 0,
        },
    },
    {
        "_id": "5733deff-2f76-4f8c-bb99-8df48bdd725f-2025-06-01",
        "_index": "stats-community-records-delta-2025",
        "_score": 1.0,
        "_source": {
            "community_id": "5733deff-2f76-4f8c-bb99-8df48bdd725f",
            "files": {
                "added": {"data_volume": 0.0, "file_count": 0},
                "removed": {"data_volume": 0.0, "file_count": 0},
            },
            "parents": {
                "added": {"metadata_only": 0, "with_files": 0},
                "removed": {"metadata_only": 0, "with_files": 0},
            },
            "period_end": "2025-06-01T23:59:59",
            "period_start": "2025-06-01T00:00:00",
            "records": {
                "added": {"metadata_only": 0, "with_files": 0},
                "removed": {"metadata_only": 0, "with_files": 0},
            },
            "subcounts": {
                "by_access_status": [],
                "by_affiliation_contributor": [],
                "by_affiliation_creator": [],
                "by_file_type": [],
                "by_funder": [],
                "by_language": [],
                "by_license": [],
                "by_periodical": [],
                "by_publisher": [],
                "by_resource_type": [],
                "by_subject": [],
            },
            "timestamp": "2025-06-05T18:45:58",
            "updated_timestamp": "2025-06-05T18:45:58",
            "uploaders": 0,
        },
    },
    {
        "_id": "5733deff-2f76-4f8c-bb99-8df48bdd725f-2025-06-02",
        "_index": "stats-community-records-delta-2025",
        "_score": 1.0,
        "_source": {
            "community_id": "5733deff-2f76-4f8c-bb99-8df48bdd725f",
            "files": {
                "added": {"data_volume": 0.0, "file_count": 0},
                "removed": {"data_volume": 0.0, "file_count": 0},
            },
            "parents": {
                "added": {"metadata_only": 0, "with_files": 0},
                "removed": {"metadata_only": 0, "with_files": 0},
            },
            "period_end": "2025-06-02T23:59:59",
            "period_start": "2025-06-02T00:00:00",
            "records": {
                "added": {"metadata_only": 0, "with_files": 0},
                "removed": {"metadata_only": 0, "with_files": 0},
            },
            "subcounts": {
                "by_access_status": [],
                "by_affiliation_contributor": [],
                "by_affiliation_creator": [],
                "by_file_type": [],
                "by_funder": [],
                "by_language": [],
                "by_license": [],
                "by_periodical": [],
                "by_publisher": [],
                "by_resource_type": [],
                "by_subject": [],
            },
            "timestamp": "2025-06-05T18:45:58",
            "updated_timestamp": "2025-06-05T18:45:58",
            "uploaders": 0,
        },
    },
    {
        "_id": "5733deff-2f76-4f8c-bb99-8df48bdd725f-2025-06-03",
        "_index": "stats-community-records-delta-2025",
        "_score": 1.0,
        "_source": {
            "community_id": "5733deff-2f76-4f8c-bb99-8df48bdd725f",
            "files": {
                "added": {"data_volume": 1984949.0, "file_count": 1},
                "removed": {"data_volume": 0.0, "file_count": 0},
            },
            "parents": {
                "added": {"metadata_only": 1, "with_files": 1},
                "removed": {"metadata_only": 0, "with_files": 0},
            },
            "period_end": "2025-06-03T23:59:59",
            "period_start": "2025-06-03T00:00:00",
            "records": {
                "added": {"metadata_only": 1, "with_files": 1},
                "removed": {"metadata_only": 0, "with_files": 0},
            },
            "subcounts": {
                "by_access_status": [
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "metadata-only",
                        "label": "",
                        "parents": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 1984949.0, "file_count": 1},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "open",
                        "label": "",
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                ],
                "by_affiliation_contributor": [],
                "by_affiliation_creator": [
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "03rmrcq20",
                        "label": "",
                        "parents": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    }
                ],
                "by_file_type": [
                    {
                        "added": {
                            "data_volume": 1984949.0,
                            "files": 1,
                            "parents": 1,
                            "records": 1,
                        },
                        "id": "pdf",
                        "label": "",
                        "removed": {
                            "data_volume": 0.0,
                            "files": 0,
                            "parents": 0,
                            "records": 0,
                        },
                    }
                ],
                "by_funder": [],
                "by_language": [
                    {
                        "files": {
                            "added": {"data_volume": 1984949.0, "file_count": 1},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "eng",
                        "label": "English",
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    }
                ],
                "by_license": [
                    {
                        "files": {
                            "added": {"data_volume": 1984949.0, "file_count": 1},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "cc-by-sa-4.0",
                        "label": (
                            "Creative Commons Attribution-ShareAlike 4.0 International"
                        ),
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    }
                ],
                "by_periodical": [
                    {
                        "files": {
                            "added": {"data_volume": 1984949.0, "file_count": 1},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "N/A",
                        "label": "",
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    }
                ],
                "by_publisher": [
                    {
                        "files": {
                            "added": {"data_volume": 1984949.0, "file_count": 1},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "Knowledge " "Commons",
                        "label": "",
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "UBC",
                        "label": "",
                        "parents": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                ],
                "by_resource_type": [
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "textDocument-book",
                        "label": "Book",
                        "parents": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 1984949.0, "file_count": 1},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "textDocument-journalArticle",
                        "label": "Journal Article",
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                ],
                "by_subject": [
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "http://id.worldcat.org/fast/1424786",
                        "label": "Canadian literature--Bibliography",
                        "parents": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "http://id.worldcat.org/fast/817954",
                        "label": "Arts, Canadian",
                        "parents": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "http://id.worldcat.org/fast/821870",
                        "label": "Authors, Canadian",
                        "parents": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "http://id.worldcat.org/fast/845111",
                        "label": "Canadian literature",
                        "parents": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "http://id.worldcat.org/fast/845142",
                        "label": "Canadian literature--Periodicals",
                        "parents": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "http://id.worldcat.org/fast/845170",
                        "label": "Canadian periodicals",
                        "parents": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "http://id.worldcat.org/fast/845184",
                        "label": "Canadian prose literature",
                        "parents": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "http://id.worldcat.org/fast/911328",
                        "label": "English language--Lexicography--History",
                        "parents": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "http://id.worldcat.org/fast/911660",
                        "label": "English language--Spoken English--Research",
                        "parents": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "http://id.worldcat.org/fast/911979",
                        "label": "English language--Written English--History",
                        "parents": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                ],
            },
            "timestamp": "2025-06-05T18:45:58",
            "updated_timestamp": "2025-06-05T18:45:58",
            "uploaders": 1,
        },
    },
    {
        "_id": "5733deff-2f76-4f8c-bb99-8df48bdd725f-2025-06-03",
        "_index": "stats-community-records-delta-2025",
        "_score": 1.0,
        "_source": {
            "community_id": "5733deff-2f76-4f8c-bb99-8df48bdd725f",
            "files": {
                "added": {"data_volume": 0.0, "file_count": 0},
                "removed": {"data_volume": 1984949.0, "file_count": 1},
            },
            "parents": {
                "added": {"metadata_only": 0, "with_files": 0},
                "removed": {"metadata_only": 0, "with_files": 1},
            },
            "period_end": "2025-06-10T23:59:59",
            "period_start": "2025-06-10T00:00:00",
            "records": {
                "added": {"metadata_only": 0, "with_files": 0},
                "removed": {"metadata_only": 0, "with_files": 1},
            },
            "subcounts": {
                "by_access_status": [
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 1984949.0, "file_count": 1},
                        },
                        "id": "open",
                        "label": "",
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 1},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 1},
                        },
                    }
                ],
                "by_affiliation_contributor": [],
                "by_affiliation_creator": [],
                "by_file_type": [
                    {
                        "added": {
                            "data_volume": 0.0,
                            "files": 0,
                            "parents": 0,
                            "records": 0,
                        },
                        "id": "pdf",
                        "label": "",
                        "removed": {
                            "data_volume": 1984949.0,
                            "files": 1,
                            "parents": 1,
                            "records": 1,
                        },
                    }
                ],
                "by_funder": [],
                "by_language": [
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 1984949.0, "file_count": 1},
                        },
                        "id": "eng",
                        "label": "English",
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 1},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 1},
                        },
                    }
                ],
                "by_license": [
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 1984949.0, "file_count": 1},
                        },
                        "id": "cc-by-sa-4.0",
                        "label": (
                            "Creative Commons Attribution-ShareAlike 4.0 International"
                        ),
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 1},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 1},
                        },
                    }
                ],
                "by_periodical": [
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 1984949.0, "file_count": 1},
                        },
                        "id": "N/A",
                        "label": "",
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 1},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 1},
                        },
                    }
                ],
                "by_publisher": [
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 1984949.0, "file_count": 1},
                        },
                        "id": "Knowledge " "Commons",
                        "label": "",
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 1},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 1},
                        },
                    }
                ],
                "by_resource_type": [
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 1984949.0, "file_count": 1},
                        },
                        "id": "textDocument-journalArticle",
                        "label": "Journal Article",
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 1},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 1},
                        },
                    }
                ],
                "by_subject": [],
            },
            "timestamp": "2025-06-10T00:45:10",
            "updated_timestamp": "2025-06-10T00:45:10",
            "uploaders": 0,
        },
    },
]

MOCK_RECORD_SNAPSHOT_QUERY_RESPONSE = {
    "2025-05-30": {
        "by_access_status": {
            "buckets": [
                {
                    "doc_count": 2,
                    "file_count": {"value": 2},
                    "key": "open",
                    "total_bytes": {"value": 59117831.0},
                    "with_files": {"doc_count": 2, "unique_parents": {"value": 2}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_affiliation_contributor_id": {
            "buckets": [],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_affiliation_contributor_name": {
            "buckets": [],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_affiliation_creator_id": {
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "013v4ng57",
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_affiliation_creator_name": {
            "buckets": [],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_file_type": {
            "buckets": [
                {
                    "doc_count": 2,
                    "key": "pdf",
                    "total_bytes": {"value": 59117831.0},
                    "unique_parents": {"value": 2},
                    "unique_records": {"value": 2},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_funder": {
            "buckets": [],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_language": {
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "eng",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "4fc0fe99-d3d8-4472-b9d9-93f4468c757f",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1751921634"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "languages": [
                                                {
                                                    "id": "eng",
                                                    "title": {"en": "English"},
                                                }
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_license": {
            "buckets": [],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_periodical": {
            "buckets": [],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_publisher": {
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "Apocryphile Press",
                    "total_bytes": {"value": 58659795.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "Knowledge Commons",
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_resource_type": {
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "textDocument-bookSection",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "f02dc425-a0a6-4527-80b3-c542b01bd279",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1751921634"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "resource_type": {
                                                "id": "textDocument-bookSection",
                                                "title": {"en": "Book " "Section"},
                                            }
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 58659795.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "textDocument-journalArticle",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "4fc0fe99-d3d8-4472-b9d9-93f4468c757f",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1751921634"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "resource_type": {
                                                "id": "textDocument-journalArticle",
                                                "title": {"en": "Journal " "Article"},
                                            }
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_subject": {
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/2060143",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "4fc0fe99-d3d8-4472-b9d9-93f4468c757f",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1751921634"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/855500",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "4fc0fe99-d3d8-4472-b9d9-93f4468c757f",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1751921634"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/973589",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "f02dc425-a0a6-4527-80b3-c542b01bd279",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1751921634"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/973589"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Inklings "
                                                        "(Group "
                                                        "of "
                                                        "writers)"
                                                    ),
                                                }
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 58659795.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/995415",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "4fc0fe99-d3d8-4472-b9d9-93f4468c757f",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1751921634"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/997916",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "4fc0fe99-d3d8-4472-b9d9-93f4468c757f",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1751921634"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/997974",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "4fc0fe99-d3d8-4472-b9d9-93f4468c757f",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1751921634"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/997987",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "4fc0fe99-d3d8-4472-b9d9-93f4468c757f",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1751921634"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "file_count": {"value": 2},
        "total_bytes": {"value": 59117831.0},
        "total_records": {"value": 2},
        "uploaders": {"value": 1},
        "with_files": {"doc_count": 2, "meta": {}, "unique_parents": {"value": 2}},
        "without_files": {"doc_count": 0, "meta": {}, "unique_parents": {"value": 0}},
    },
    "2025-05-31": {
        "by_access_status": {
            "buckets": [
                {
                    "doc_count": 2,
                    "file_count": {"value": 2},
                    "key": "open",
                    "total_bytes": {"value": 59117831.0},
                    "with_files": {"doc_count": 2, "unique_parents": {"value": 2}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_affiliation_contributor_id": {
            "buckets": [],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_affiliation_contributor_name": {
            "buckets": [],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_affiliation_creator_id": {
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "013v4ng57",
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_affiliation_creator_name": {
            "buckets": [],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_file_type": {
            "buckets": [
                {
                    "doc_count": 2,
                    "key": "pdf",
                    "total_bytes": {"value": 59117831.0},
                    "unique_parents": {"value": 2},
                    "unique_records": {"value": 2},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_funder": {
            "buckets": [],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_language": {
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "eng",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "d70ef03f-7fc8-45d6-b182-b077dd540e63",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1751922859"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "languages": [
                                                {
                                                    "id": "eng",
                                                    "title": {"en": "English"},
                                                }
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_license": {
            "buckets": [],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_periodical": {
            "buckets": [],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_publisher": {
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "Apocryphile Press",
                    "total_bytes": {"value": 58659795.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "Knowledge Commons",
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_resource_type": {
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "textDocument-bookSection",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "d9aced17-5bb3-4921-892c-afba7512887f",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1751922859"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "resource_type": {
                                                "id": "textDocument-bookSection",
                                                "title": {"en": "Book " "Section"},
                                            }
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 58659795.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "textDocument-journalArticle",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "d70ef03f-7fc8-45d6-b182-b077dd540e63",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1751922859"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "resource_type": {
                                                "id": "textDocument-journalArticle",
                                                "title": {"en": "Journal " "Article"},
                                            }
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_subject": {
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/2060143",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "d70ef03f-7fc8-45d6-b182-b077dd540e63",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1751922859"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/855500",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "d70ef03f-7fc8-45d6-b182-b077dd540e63",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1751922859"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/973589",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "d9aced17-5bb3-4921-892c-afba7512887f",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1751922859"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/973589"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Inklings "
                                                        "(Group "
                                                        "of "
                                                        "writers)"
                                                    ),
                                                }
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 58659795.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/995415",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "d70ef03f-7fc8-45d6-b182-b077dd540e63",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1751922859"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/997916",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "d70ef03f-7fc8-45d6-b182-b077dd540e63",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1751922859"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/997974",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "d70ef03f-7fc8-45d6-b182-b077dd540e63",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1751922859"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/997987",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "d70ef03f-7fc8-45d6-b182-b077dd540e63",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1751922859"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "file_count": {"value": 2},
        "total_bytes": {"value": 59117831.0},
        "total_records": {"value": 2},
        "uploaders": {"value": 1},
        "with_files": {"doc_count": 2, "meta": {}, "unique_parents": {"value": 2}},
        "without_files": {"doc_count": 0, "meta": {}, "unique_parents": {"value": 0}},
    },
    "2025-06-03": {
        "by_access_status": {
            "buckets": [
                {
                    "doc_count": 3,
                    "file_count": {"value": 3},
                    "key": "open",
                    "total_bytes": {"value": 61102780.0},
                    "with_files": {"doc_count": 3, "unique_parents": {"value": 3}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 0},
                    "key": "metadata-only",
                    "total_bytes": {"value": 0.0},
                    "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                    "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_affiliation_contributor_id": {
            "buckets": [],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_affiliation_contributor_name": {
            "buckets": [],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_affiliation_creator_id": {
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "013v4ng57",
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 0},
                    "key": "03rmrcq20",
                    "total_bytes": {"value": 0.0},
                    "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                    "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_affiliation_creator_name": {
            "buckets": [],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_file_type": {
            "buckets": [
                {
                    "doc_count": 3,
                    "key": "pdf",
                    "total_bytes": {"value": 61102780.0},
                    "unique_parents": {"value": 3},
                    "unique_records": {"value": 3},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_funder": {
            "buckets": [],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_language": {
            "buckets": [
                {
                    "doc_count": 2,
                    "file_count": {"value": 2},
                    "key": "eng",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "6ed0b920-a37a-4eec-a4e5-929852b00c8f",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1751923343"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "languages": [
                                                {
                                                    "id": "eng",
                                                    "title": {"en": "English"},
                                                }
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 2},
                        }
                    },
                    "total_bytes": {"value": 2442985.0},
                    "with_files": {"doc_count": 2, "unique_parents": {"value": 2}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_license": {
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "cc-by-sa-4.0",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "6ed0b920-a37a-4eec-a4e5-929852b00c8f",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1751923343"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "rights": [
                                                {
                                                    "id": "cc-by-sa-4.0",
                                                    "title": {
                                                        "en": (
                                                            "Creative "
                                                            "Commons "
                                                            "Attribution-ShareAlike "
                                                            "4.0 "
                                                            "International"
                                                        )
                                                    },
                                                }
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 1984949.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_periodical": {
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "N/A",
                    "total_bytes": {"value": 1984949.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_publisher": {
            "buckets": [
                {
                    "doc_count": 2,
                    "file_count": {"value": 2},
                    "key": "Knowledge Commons",
                    "total_bytes": {"value": 2442985.0},
                    "with_files": {"doc_count": 2, "unique_parents": {"value": 2}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "Apocryphile Press",
                    "total_bytes": {"value": 58659795.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 0},
                    "key": "UBC",
                    "total_bytes": {"value": 0.0},
                    "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                    "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_resource_type": {
            "buckets": [
                {
                    "doc_count": 2,
                    "file_count": {"value": 2},
                    "key": "textDocument-journalArticle",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "6ed0b920-a37a-4eec-a4e5-929852b00c8f",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1751923343"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "resource_type": {
                                                "id": "textDocument-journalArticle",
                                                "title": {"en": "Journal " "Article"},
                                            }
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 2},
                        }
                    },
                    "total_bytes": {"value": 2442985.0},
                    "with_files": {"doc_count": 2, "unique_parents": {"value": 2}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 0},
                    "key": "textDocument-book",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "ce1cd47b-12e6-4224-9716-cf33149f7d9e",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1751923343"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "resource_type": {
                                                "id": "textDocument-book",
                                                "title": {"en": "Book"},
                                            }
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 0.0},
                    "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                    "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "textDocument-bookSection",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "4b52a144-4533-4e06-890c-89c6fc5d9839",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1751923343"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "resource_type": {
                                                "id": "textDocument-bookSection",
                                                "title": {"en": "Book " "Section"},
                                            }
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 58659795.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_subject": {
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 0},
                    "key": "http://id.worldcat.org/fast/1424786",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "ce1cd47b-12e6-4224-9716-cf33149f7d9e",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1751923343"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911979"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Written "
                                                        "English--History"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911660"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Spoken "
                                                        "English--Research"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845111"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Canadian " "literature",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845142"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Periodicals"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845184"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "prose "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/1424786"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Bibliography"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/934875"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "French-Canadian " "literature"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/817954"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Arts, " "Canadian",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/821870"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Authors, " "Canadian",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845170"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian " "periodicals"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911328"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Lexicography--History"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 0.0},
                    "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                    "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/2060143",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "4aeb8474-c87e-45c2-a7f2-dbd937459063",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1751923343"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 0},
                    "key": "http://id.worldcat.org/fast/817954",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "ce1cd47b-12e6-4224-9716-cf33149f7d9e",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1751923343"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911979"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Written "
                                                        "English--History"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911660"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Spoken "
                                                        "English--Research"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845111"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Canadian " "literature",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845142"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Periodicals"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845184"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "prose "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/1424786"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Bibliography"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/934875"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "French-Canadian " "literature"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/817954"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Arts, " "Canadian",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/821870"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Authors, " "Canadian",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845170"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian " "periodicals"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911328"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Lexicography--History"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 0.0},
                    "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                    "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 0},
                    "key": "http://id.worldcat.org/fast/821870",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "ce1cd47b-12e6-4224-9716-cf33149f7d9e",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1751923343"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911979"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Written "
                                                        "English--History"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911660"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Spoken "
                                                        "English--Research"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845111"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Canadian " "literature",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845142"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Periodicals"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845184"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "prose "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/1424786"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Bibliography"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/934875"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "French-Canadian " "literature"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/817954"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Arts, " "Canadian",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/821870"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Authors, " "Canadian",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845170"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian " "periodicals"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911328"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Lexicography--History"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 0.0},
                    "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                    "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 0},
                    "key": "http://id.worldcat.org/fast/845111",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "ce1cd47b-12e6-4224-9716-cf33149f7d9e",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1751923343"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911979"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Written "
                                                        "English--History"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911660"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Spoken "
                                                        "English--Research"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845111"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Canadian " "literature",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845142"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Periodicals"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845184"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "prose "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/1424786"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Bibliography"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/934875"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "French-Canadian " "literature"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/817954"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Arts, " "Canadian",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/821870"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Authors, " "Canadian",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845170"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian " "periodicals"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911328"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Lexicography--History"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 0.0},
                    "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                    "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 0},
                    "key": "http://id.worldcat.org/fast/845142",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "ce1cd47b-12e6-4224-9716-cf33149f7d9e",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1751923343"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911979"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Written "
                                                        "English--History"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911660"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Spoken "
                                                        "English--Research"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845111"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Canadian " "literature",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845142"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Periodicals"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845184"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "prose "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/1424786"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Bibliography"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/934875"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "French-Canadian " "literature"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/817954"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Arts, " "Canadian",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/821870"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Authors, " "Canadian",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845170"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian " "periodicals"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911328"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Lexicography--History"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 0.0},
                    "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                    "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 0},
                    "key": "http://id.worldcat.org/fast/845170",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "ce1cd47b-12e6-4224-9716-cf33149f7d9e",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1751923343"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911979"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Written "
                                                        "English--History"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911660"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Spoken "
                                                        "English--Research"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845111"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Canadian " "literature",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845142"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Periodicals"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845184"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "prose "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/1424786"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Bibliography"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/934875"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "French-Canadian " "literature"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/817954"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Arts, " "Canadian",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/821870"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Authors, " "Canadian",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845170"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian " "periodicals"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911328"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Lexicography--History"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 0.0},
                    "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                    "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 0},
                    "key": "http://id.worldcat.org/fast/845184",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "ce1cd47b-12e6-4224-9716-cf33149f7d9e",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1751923343"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911979"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Written "
                                                        "English--History"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911660"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Spoken "
                                                        "English--Research"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845111"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Canadian " "literature",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845142"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Periodicals"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845184"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "prose "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/1424786"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Bibliography"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/934875"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "French-Canadian " "literature"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/817954"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Arts, " "Canadian",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/821870"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Authors, " "Canadian",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845170"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian " "periodicals"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911328"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Lexicography--History"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 0.0},
                    "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                    "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/855500",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "4aeb8474-c87e-45c2-a7f2-dbd937459063",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1751923343"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 0},
                    "key": "http://id.worldcat.org/fast/911328",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "ce1cd47b-12e6-4224-9716-cf33149f7d9e",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1751923343"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911979"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Written "
                                                        "English--History"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911660"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Spoken "
                                                        "English--Research"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845111"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Canadian " "literature",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845142"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Periodicals"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845184"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "prose "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/1424786"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Bibliography"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/934875"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "French-Canadian " "literature"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/817954"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Arts, " "Canadian",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/821870"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Authors, " "Canadian",
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845170"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian " "periodicals"
                                                    ),
                                                },
                                                {
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911328"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Lexicography--History"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 0.0},
                    "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                    "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 8,
        },
        "file_count": {"value": 3},
        "total_bytes": {"value": 61102780.0},
        "total_records": {"value": 4},
        "uploaders": {"value": 1},
        "with_files": {"doc_count": 3, "meta": {}, "unique_parents": {"value": 3}},
        "without_files": {"doc_count": 1, "meta": {}, "unique_parents": {"value": 1}},
    },
}

MOCK_RECORD_SNAPSHOT_AGGREGATIONS = {
    "2025-05-30": {
        "by_access_status": {
            "buckets": [
                {
                    "doc_count": 2,
                    "file_count": {"value": 2},
                    "key": "open",
                    "total_bytes": {"value": 59117831.0},
                    "with_files": {"doc_count": 2, "unique_parents": {"value": 2}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_affiliation_contributor": {
            "after_key": {"id": None, "label": None},
            "buckets": [
                {
                    "doc_count": 2,
                    "file_count": {"value": 2},
                    "key": {"id": None, "label": None},
                    "total_bytes": {"value": 59117831.0},
                    "with_files": {"doc_count": 2, "unique_parents": {"value": 2}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                }
            ],
            "meta": {},
        },
        "by_affiliation_creator": {
            "after_key": {"id": "013v4ng57", "label": None},
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": {"id": None, "label": None},
                    "total_bytes": {"value": 58659795.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": {"id": "013v4ng57", "label": None},
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
            ],
            "meta": {},
        },
        "by_file_type": {
            "buckets": [
                {
                    "doc_count": 2,
                    "key": "pdf",
                    "total_bytes": {"value": 59117831.0},
                    "unique_parents": {"value": 2},
                    "unique_records": {"value": 2},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_funder": {
            "buckets": [],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_language": {
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "eng",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "86856332-b1d1-4f60-81f6-801442b9fea2",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749585565"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "languages": [
                                                {
                                                    "id": "eng",
                                                    "title": {"en": "English"},
                                                }
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_license": {
            "buckets": [],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_periodical": {
            "buckets": [],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_publisher": {
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "Apocryphile Press",
                    "total_bytes": {"value": 58659795.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "Knowledge Commons",
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_resource_type": {
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "textDocument-bookSection",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "8c11a8b2-17fa-43b4-952c-d0756852ec7f",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749585565"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "resource_type": {
                                                "id": "textDocument-bookSection",
                                                "title": {"en": "Book " "Section"},
                                            }
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 58659795.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "textDocument-journalArticle",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "86856332-b1d1-4f60-81f6-801442b9fea2",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749585565"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "resource_type": {
                                                "id": "textDocument-journalArticle",
                                                "title": {"en": "Journal " "Article"},
                                            }
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_subject": {
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/2060143",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "86856332-b1d1-4f60-81f6-801442b9fea2",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749585565"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "8b79f179-aa1b-4a41-bed4-12c60c2c5c18::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "@v": (
                                                        "febbebcb-e794-458c-8022-086ad58f086f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "@v": (
                                                        "bf6efa0a-7a15-452c-a9d3-250601beb4c6::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "beb9e9ac-1793-45f4-abc0-d9982eed0e4b::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "347bceb2-19d7-4d38-b76b-c6ba6b44a3dc::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "4d0dcfd5-dfad-417b-847a-90c8326b3e1e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/855500",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "86856332-b1d1-4f60-81f6-801442b9fea2",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749585565"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "8b79f179-aa1b-4a41-bed4-12c60c2c5c18::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "@v": (
                                                        "febbebcb-e794-458c-8022-086ad58f086f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "@v": (
                                                        "bf6efa0a-7a15-452c-a9d3-250601beb4c6::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "beb9e9ac-1793-45f4-abc0-d9982eed0e4b::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "347bceb2-19d7-4d38-b76b-c6ba6b44a3dc::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "4d0dcfd5-dfad-417b-847a-90c8326b3e1e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/973589",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "8c11a8b2-17fa-43b4-952c-d0756852ec7f",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749585565"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "c490b6d8-1a1a-4f3d-b4a4-a2b93b02813f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/973589"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Inklings "
                                                        "(Group "
                                                        "of "
                                                        "writers)"
                                                    ),
                                                }
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 58659795.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/995415",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "86856332-b1d1-4f60-81f6-801442b9fea2",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749585565"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "8b79f179-aa1b-4a41-bed4-12c60c2c5c18::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "@v": (
                                                        "febbebcb-e794-458c-8022-086ad58f086f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "@v": (
                                                        "bf6efa0a-7a15-452c-a9d3-250601beb4c6::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "beb9e9ac-1793-45f4-abc0-d9982eed0e4b::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "347bceb2-19d7-4d38-b76b-c6ba6b44a3dc::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "4d0dcfd5-dfad-417b-847a-90c8326b3e1e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/997916",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "86856332-b1d1-4f60-81f6-801442b9fea2",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749585565"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "8b79f179-aa1b-4a41-bed4-12c60c2c5c18::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "@v": (
                                                        "febbebcb-e794-458c-8022-086ad58f086f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "@v": (
                                                        "bf6efa0a-7a15-452c-a9d3-250601beb4c6::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "beb9e9ac-1793-45f4-abc0-d9982eed0e4b::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "347bceb2-19d7-4d38-b76b-c6ba6b44a3dc::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "4d0dcfd5-dfad-417b-847a-90c8326b3e1e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/997974",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "86856332-b1d1-4f60-81f6-801442b9fea2",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749585565"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "8b79f179-aa1b-4a41-bed4-12c60c2c5c18::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "@v": (
                                                        "febbebcb-e794-458c-8022-086ad58f086f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "@v": (
                                                        "bf6efa0a-7a15-452c-a9d3-250601beb4c6::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "beb9e9ac-1793-45f4-abc0-d9982eed0e4b::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "347bceb2-19d7-4d38-b76b-c6ba6b44a3dc::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "4d0dcfd5-dfad-417b-847a-90c8326b3e1e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/997987",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "86856332-b1d1-4f60-81f6-801442b9fea2",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749585565"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "8b79f179-aa1b-4a41-bed4-12c60c2c5c18::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "@v": (
                                                        "febbebcb-e794-458c-8022-086ad58f086f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "@v": (
                                                        "bf6efa0a-7a15-452c-a9d3-250601beb4c6::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "beb9e9ac-1793-45f4-abc0-d9982eed0e4b::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "347bceb2-19d7-4d38-b76b-c6ba6b44a3dc::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "4d0dcfd5-dfad-417b-847a-90c8326b3e1e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "date_field_max": {
            "value": 1748649184686.0,
            "value_as_string": "2025-05-30T23:53:04",
        },
        "date_field_min": {
            "value": 1748572641721.0,
            "value_as_string": "2025-05-30T02:37:21",
        },
        "file_count": {"value": 2},
        "total_bytes": {"value": 59117831.0},
        "total_records": {"value": 2},
        "uploaders": {"value": 1},
        "with_files": {"doc_count": 2, "meta": {}, "unique_parents": {"value": 2}},
        "without_files": {"doc_count": 0, "meta": {}, "unique_parents": {"value": 0}},
    },
    "2025-05-31": {
        "by_access_status": {
            "buckets": [
                {
                    "doc_count": 2,
                    "file_count": {"value": 2},
                    "key": "open",
                    "total_bytes": {"value": 59117831.0},
                    "with_files": {"doc_count": 2, "unique_parents": {"value": 2}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_affiliation_contributor": {
            "after_key": {"id": None, "label": None},
            "buckets": [
                {
                    "doc_count": 2,
                    "file_count": {"value": 2},
                    "key": {"id": None, "label": None},
                    "total_bytes": {"value": 59117831.0},
                    "with_files": {"doc_count": 2, "unique_parents": {"value": 2}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                }
            ],
            "meta": {},
        },
        "by_affiliation_creator": {
            "after_key": {"id": "013v4ng57", "label": None},
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": {"id": None, "label": None},
                    "total_bytes": {"value": 58659795.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": {"id": "013v4ng57", "label": None},
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
            ],
            "meta": {},
        },
        "by_file_type": {
            "buckets": [
                {
                    "doc_count": 2,
                    "key": "pdf",
                    "total_bytes": {"value": 59117831.0},
                    "unique_parents": {"value": 2},
                    "unique_records": {"value": 2},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_funder": {
            "buckets": [],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_language": {
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "eng",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "30aa398d-fa27-4cd2-b011-81bb35916d2a",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749590345"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "languages": [
                                                {
                                                    "id": "eng",
                                                    "title": {"en": "English"},
                                                }
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_license": {
            "buckets": [],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_periodical": {
            "buckets": [],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_publisher": {
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "Apocryphile Press",
                    "total_bytes": {"value": 58659795.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "Knowledge Commons",
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_resource_type": {
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "textDocument-bookSection",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "085bd97d-040a-462f-a8ac-b30ec9e490a5",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749590345"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "resource_type": {
                                                "id": "textDocument-bookSection",
                                                "title": {"en": "Book " "Section"},
                                            }
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 58659795.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "textDocument-journalArticle",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "30aa398d-fa27-4cd2-b011-81bb35916d2a",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749590345"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "resource_type": {
                                                "id": "textDocument-journalArticle",
                                                "title": {"en": "Journal " "Article"},
                                            }
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_subject": {
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/2060143",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "30aa398d-fa27-4cd2-b011-81bb35916d2a",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749590345"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "0442a8f9-9312-4bd9-aacc-9155b069d932::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "@v": (
                                                        "f963536a-6d3a-4cd3-bdc8-145c5ae5e919::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "@v": (
                                                        "7eab4fa0-9742-447c-8b9d-674eac660835::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "99e2f870-3381-4a64-8dc1-2dc105f99c1e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "0e06228f-4951-4617-97b5-702bd87fd27c::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "37217d57-c4d9-49b2-88fc-31b2b8e3f72e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/855500",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "30aa398d-fa27-4cd2-b011-81bb35916d2a",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749590345"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "0442a8f9-9312-4bd9-aacc-9155b069d932::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "@v": (
                                                        "f963536a-6d3a-4cd3-bdc8-145c5ae5e919::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "@v": (
                                                        "7eab4fa0-9742-447c-8b9d-674eac660835::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "99e2f870-3381-4a64-8dc1-2dc105f99c1e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "0e06228f-4951-4617-97b5-702bd87fd27c::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "37217d57-c4d9-49b2-88fc-31b2b8e3f72e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/973589",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "085bd97d-040a-462f-a8ac-b30ec9e490a5",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749590345"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "3a5ac7f4-49d1-4360-9798-"
                                                        "35fed68b4b7c::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/"
                                                        "973589"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Inklings "
                                                        "(Group "
                                                        "of "
                                                        "writers)"
                                                    ),
                                                }
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 58659795.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/995415",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "30aa398d-fa27-4cd2-b011-81bb35916d2a",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749590345"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "0442a8f9-9312-4bd9-aacc-"
                                                        "9155b069d932::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/"
                                                        "997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "@v": (
                                                        "f963536a-6d3a-4cd3-bdc8-"
                                                        "145c5ae5e919::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/"
                                                        "2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "@v": (
                                                        "7eab4fa0-9742-447c-8b9d-"
                                                        "674eac660835::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/"
                                                        "997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "99e2f870-3381-4a64-8dc1-"
                                                        "2dc105f99c1e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/"
                                                        "997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "0e06228f-4951-4617-97b5-"
                                                        "702bd87fd27c::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/"
                                                        "855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "37217d57-c4d9-49b2-88fc-"
                                                        "31b2b8e3f72e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/"
                                                        "995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/997916",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "30aa398d-fa27-4cd2-b011-81bb35916d2a",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749590345"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "0442a8f9-9312-4bd9-aacc-"
                                                        "9155b069d932::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/"
                                                        "997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "@v": (
                                                        "f963536a-6d3a-4cd3-bdc8-"
                                                        "145c5ae5e919::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/"
                                                        "2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "@v": (
                                                        "7eab4fa0-9742-447c-8b9d-"
                                                        "674eac660835::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/"
                                                        "997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "99e2f870-3381-4a64-8dc1-"
                                                        "2dc105f99c1e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/"
                                                        "997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "0e06228f-4951-4617-97b5-"
                                                        "702bd87fd27c::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/"
                                                        "855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "37217d57-c4d9-49b2-88fc-"
                                                        "31b2b8e3f72e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/"
                                                        "995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/997974",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "30aa398d-fa27-4cd2-b011-81bb35916d2a",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749590345"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "0442a8f9-9312-4bd9-aacc-"
                                                        "9155b069d932::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/"
                                                        "997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "@v": (
                                                        "f963536a-6d3a-4cd3-bdc8-"
                                                        "145c5ae5e919::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/"
                                                        "2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "@v": (
                                                        "7eab4fa0-9742-447c-8b9d-"
                                                        "674eac660835::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/"
                                                        "997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "99e2f870-3381-4a64-8dc1-"
                                                        "2dc105f99c1e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/"
                                                        "997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "0e06228f-4951-4617-97b5-"
                                                        "702bd87fd27c::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/"
                                                        "855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "37217d57-c4d9-49b2-88fc-"
                                                        "31b2b8e3f72e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/"
                                                        "995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/997987",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "30aa398d-fa27-4cd2-b011-81bb35916d2a",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749590345"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "0442a8f9-9312-4bd9-aacc-"
                                                        "9155b069d932::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/"
                                                        "997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "@v": (
                                                        "f963536a-6d3a-4cd3-bdc8-"
                                                        "145c5ae5e919::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/"
                                                        "2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "@v": (
                                                        "7eab4fa0-9742-447c-8b9d-"
                                                        "674eac660835::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/"
                                                        "997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "99e2f870-3381-4a64-8dc1-"
                                                        "2dc105f99c1e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/"
                                                        "997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "0e06228f-4951-4617-97b5-"
                                                        "702bd87fd27c::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/"
                                                        "855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "37217d57-c4d9-49b2-88fc-"
                                                        "31b2b8e3f72e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/"
                                                        "995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "date_field_max": {
            "value": 1748649184686.0,
            "value_as_string": "2025-05-30T23:53:04",
        },
        "date_field_min": {
            "value": 1748572641721.0,
            "value_as_string": "2025-05-30T02:37:21",
        },
        "file_count": {"value": 2},
        "total_bytes": {"value": 59117831.0},
        "total_records": {"value": 2},
        "uploaders": {"value": 1},
        "with_files": {"doc_count": 2, "meta": {}, "unique_parents": {"value": 2}},
        "without_files": {"doc_count": 0, "meta": {}, "unique_parents": {"value": 0}},
    },
    "2025-06-03": {
        "by_access_status": {
            "buckets": [
                {
                    "doc_count": 3,
                    "file_count": {"value": 3},
                    "key": "open",
                    "total_bytes": {"value": 61102780.0},
                    "with_files": {"doc_count": 3, "unique_parents": {"value": 3}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 0},
                    "key": "metadata-only",
                    "total_bytes": {"value": 0.0},
                    "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                    "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_affiliation_contributor": {
            "after_key": {"id": None, "label": None},
            "buckets": [
                {
                    "doc_count": 4,
                    "file_count": {"value": 3},
                    "key": {"id": None, "label": None},
                    "total_bytes": {"value": 61102780.0},
                    "with_files": {"doc_count": 3, "unique_parents": {"value": 3}},
                    "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                }
            ],
            "meta": {},
        },
        "by_affiliation_creator": {
            "after_key": {"id": "03rmrcq20", "label": None},
            "buckets": [
                {
                    "doc_count": 2,
                    "file_count": {"value": 2},
                    "key": {"id": None, "label": None},
                    "total_bytes": {"value": 60644744.0},
                    "with_files": {"doc_count": 2, "unique_parents": {"value": 2}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": {"id": "013v4ng57", "label": None},
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 0},
                    "key": {"id": "03rmrcq20", "label": None},
                    "total_bytes": {"value": 0.0},
                    "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                    "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                },
            ],
            "meta": {},
        },
        "by_file_type": {
            "buckets": [
                {
                    "doc_count": 3,
                    "key": "pdf",
                    "total_bytes": {"value": 61102780.0},
                    "unique_parents": {"value": 3},
                    "unique_records": {"value": 3},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_funder": {
            "buckets": [],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_language": {
            "buckets": [
                {
                    "doc_count": 2,
                    "file_count": {"value": 2},
                    "key": "eng",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "ed8412b3-a495-464c-8c9e-b84ed38e5be0",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749594127"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "languages": [
                                                {
                                                    "id": "eng",
                                                    "title": {"en": "English"},
                                                }
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 2},
                        }
                    },
                    "total_bytes": {"value": 2442985.0},
                    "with_files": {"doc_count": 2, "unique_parents": {"value": 2}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_license": {
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "cc-by-sa-4.0",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "ed8412b3-a495-464c-8c9e-b84ed38e5be0",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749594127"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "rights": [
                                                {
                                                    "id": "cc-by-sa-4.0",
                                                    "title": {
                                                        "en": (
                                                            "Creative "
                                                            "Commons "
                                                            "Attribution-ShareAlike "
                                                            "4.0 "
                                                            "International"
                                                        )
                                                    },
                                                }
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 1984949.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_periodical": {
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "N/A",
                    "total_bytes": {"value": 1984949.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_publisher": {
            "buckets": [
                {
                    "doc_count": 2,
                    "file_count": {"value": 2},
                    "key": "Knowledge Commons",
                    "total_bytes": {"value": 2442985.0},
                    "with_files": {"doc_count": 2, "unique_parents": {"value": 2}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "Apocryphile Press",
                    "total_bytes": {"value": 58659795.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 0},
                    "key": "UBC",
                    "total_bytes": {"value": 0.0},
                    "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                    "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_resource_type": {
            "buckets": [
                {
                    "doc_count": 2,
                    "file_count": {"value": 2},
                    "key": "textDocument-journalArticle",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "ed8412b3-a495-464c-8c9e-b84ed38e5be0",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749594127"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "resource_type": {
                                                "id": "textDocument-journalArticle",
                                                "title": {"en": "Journal " "Article"},
                                            }
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 2},
                        }
                    },
                    "total_bytes": {"value": 2442985.0},
                    "with_files": {"doc_count": 2, "unique_parents": {"value": 2}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 0},
                    "key": "textDocument-book",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "22b6fe82-7195-4218-9af7-9619786e822e",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749594127"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "resource_type": {
                                                "id": "textDocument-book",
                                                "title": {"en": "Book"},
                                            }
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 0.0},
                    "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                    "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "textDocument-bookSection",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "7ee160e5-547d-4f21-9ca5-95a93df8d8b7",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749594127"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "resource_type": {
                                                "id": "textDocument-bookSection",
                                                "title": {"en": "Book " "Section"},
                                            }
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 58659795.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_subject": {
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 0},
                    "key": "http://id.worldcat.org/fast/1424786",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "22b6fe82-7195-4218-9af7-9619786e822e",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749594127"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "cb7f5fa0-93da-41a6-868b-"
                                                        "9db610c38d6f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/"
                                                        "911979"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Written "
                                                        "English--History"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "676a9b6c-f15d-4d37-bb4b-"
                                                        "e9fbd1fa1fc8::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/"
                                                        "911660"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Spoken "
                                                        "English--Research"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "9dd254a5-f436-4d3d-b385-"
                                                        "ea56195931f7::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/"
                                                        "845111"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Canadian " "literature",
                                                },
                                                {
                                                    "@v": (
                                                        "637bba5a-1cd9-4f51-b57b-"
                                                        "29f466f74a4d::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/"
                                                        "845142"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Periodicals"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "7605afd5-6412-47c6-a144-"
                                                        "6a32ae83652f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/"
                                                        "845184"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "prose "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "d99a6371-1b8c-408e-8339-"
                                                        "001e9e0a4c7f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/"
                                                        "1424786"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Bibliography"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "a47638b8-267e-4288-8f46-"
                                                        "6df53357b092::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/"
                                                        "934875"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "French-Canadian " "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "01cd29ef-368a-4d1c-8d1f-"
                                                        "797c854950e6::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/"
                                                        "817954"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Arts, " "Canadian",
                                                },
                                                {
                                                    "@v": (
                                                        "531262ce-12b5-44dd-9b4c-"
                                                        "b684a64d8857::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/"
                                                        "821870"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Authors, " "Canadian",
                                                },
                                                {
                                                    "@v": (
                                                        "be2998f7-163e-4735-af9f-"
                                                        "8ef06dcc38bc::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/"
                                                        "845170"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian " "periodicals"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "a047af4e-9710-431a-8b7c-"
                                                        "2e0b8346fb5e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/"
                                                        "911328"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Lexicography--"
                                                        "History"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 0.0},
                    "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                    "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/2060143",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "3a1c0854-2036-418e-938f-c5af3b33794e",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749594127"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "2485b574-4ba7-4413-8ff6-56947e72236b::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "@v": (
                                                        "03e6600f-9d63-402b-8e6d-f5ef735d8c6e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "@v": (
                                                        "d39e6657-4122-458b-ac86-eecec2ad11d4::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "c77355ed-5d54-47d9-b6d9-d70f83529893::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "92d2fad8-75ec-4ca0-b25a-e9e99f31915c::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "c613000a-7373-42d8-9c04-c42af94d85df::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 0},
                    "key": "http://id.worldcat.org/fast/817954",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "22b6fe82-7195-4218-9af7-9619786e822e",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749594127"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "cb7f5fa0-93da-41a6-868b-9db610c38d6f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911979"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Written "
                                                        "English--History"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "676a9b6c-f15d-4d37-bb4b-e9fbd1fa1fc8::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911660"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Spoken "
                                                        "English--Research"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "9dd254a5-f436-4d3d-b385-ea56195931f7::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845111"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Canadian " "literature",
                                                },
                                                {
                                                    "@v": (
                                                        "637bba5a-1cd9-4f51-b57b-29f466f74a4d::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845142"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Periodicals"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "7605afd5-6412-47c6-a144-6a32ae83652f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845184"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "prose "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "d99a6371-1b8c-408e-8339-001e9e0a4c7f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/1424786"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Bibliography"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "a47638b8-267e-4288-8f46-6df53357b092::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/934875"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "French-Canadian " "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "01cd29ef-368a-4d1c-8d1f-797c854950e6::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/817954"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Arts, " "Canadian",
                                                },
                                                {
                                                    "@v": (
                                                        "531262ce-12b5-44dd-9b4c-b684a64d8857::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/821870"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Authors, " "Canadian",
                                                },
                                                {
                                                    "@v": (
                                                        "be2998f7-163e-4735-af9f-8ef06dcc38bc::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845170"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian " "periodicals"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "a047af4e-9710-431a-8b7c-2e0b8346fb5e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911328"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Lexicography--History"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 0.0},
                    "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                    "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 0},
                    "key": "http://id.worldcat.org/fast/821870",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "22b6fe82-7195-4218-9af7-9619786e822e",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749594127"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "cb7f5fa0-93da-41a6-868b-9db610c38d6f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911979"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Written "
                                                        "English--History"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "676a9b6c-f15d-4d37-bb4b-e9fbd1fa1fc8::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911660"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Spoken "
                                                        "English--Research"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "9dd254a5-f436-4d3d-b385-ea56195931f7::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845111"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Canadian " "literature",
                                                },
                                                {
                                                    "@v": (
                                                        "637bba5a-1cd9-4f51-b57b-29f466f74a4d::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845142"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Periodicals"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "7605afd5-6412-47c6-a144-6a32ae83652f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845184"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "prose "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "d99a6371-1b8c-408e-8339-001e9e0a4c7f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/1424786"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Bibliography"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "a47638b8-267e-4288-8f46-6df53357b092::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/934875"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "French-Canadian " "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "01cd29ef-368a-4d1c-8d1f-797c854950e6::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/817954"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Arts, " "Canadian",
                                                },
                                                {
                                                    "@v": (
                                                        "531262ce-12b5-44dd-9b4c-b684a64d8857::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/821870"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Authors, " "Canadian",
                                                },
                                                {
                                                    "@v": (
                                                        "be2998f7-163e-4735-af9f-8ef06dcc38bc::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845170"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian " "periodicals"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "a047af4e-9710-431a-8b7c-2e0b8346fb5e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911328"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Lexicography--History"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 0.0},
                    "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                    "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 0},
                    "key": "http://id.worldcat.org/fast/845111",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "22b6fe82-7195-4218-9af7-9619786e822e",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749594127"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "cb7f5fa0-93da-41a6-868b-9db610c38d6f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911979"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Written "
                                                        "English--History"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "676a9b6c-f15d-4d37-bb4b-e9fbd1fa1fc8::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911660"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Spoken "
                                                        "English--Research"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "9dd254a5-f436-4d3d-b385-ea56195931f7::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845111"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Canadian " "literature",
                                                },
                                                {
                                                    "@v": (
                                                        "637bba5a-1cd9-4f51-b57b-29f466f74a4d::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845142"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Periodicals"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "7605afd5-6412-47c6-a144-6a32ae83652f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845184"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "prose "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "d99a6371-1b8c-408e-8339-001e9e0a4c7f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/1424786"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Bibliography"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "a47638b8-267e-4288-8f46-6df53357b092::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/934875"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "French-Canadian " "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "01cd29ef-368a-4d1c-8d1f-797c854950e6::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/817954"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Arts, " "Canadian",
                                                },
                                                {
                                                    "@v": (
                                                        "531262ce-12b5-44dd-9b4c-b684a64d8857::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/821870"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Authors, " "Canadian",
                                                },
                                                {
                                                    "@v": (
                                                        "be2998f7-163e-4735-af9f-8ef06dcc38bc::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845170"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian " "periodicals"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "a047af4e-9710-431a-8b7c-2e0b8346fb5e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911328"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Lexicography--History"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 0.0},
                    "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                    "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 0},
                    "key": "http://id.worldcat.org/fast/845142",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "22b6fe82-7195-4218-9af7-9619786e822e",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749594127"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "cb7f5fa0-93da-41a6-868b-9db610c38d6f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911979"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Written "
                                                        "English--History"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "676a9b6c-f15d-4d37-bb4b-e9fbd1fa1fc8::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911660"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Spoken "
                                                        "English--Research"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "9dd254a5-f436-4d3d-b385-ea56195931f7::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845111"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Canadian " "literature",
                                                },
                                                {
                                                    "@v": (
                                                        "637bba5a-1cd9-4f51-b57b-29f466f74a4d::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845142"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Periodicals"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "7605afd5-6412-47c6-a144-6a32ae83652f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845184"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "prose "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "d99a6371-1b8c-408e-8339-001e9e0a4c7f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/1424786"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Bibliography"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "a47638b8-267e-4288-8f46-6df53357b092::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/934875"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "French-Canadian " "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "01cd29ef-368a-4d1c-8d1f-797c854950e6::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/817954"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Arts, " "Canadian",
                                                },
                                                {
                                                    "@v": (
                                                        "531262ce-12b5-44dd-9b4c-b684a64d8857::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/821870"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Authors, " "Canadian",
                                                },
                                                {
                                                    "@v": (
                                                        "be2998f7-163e-4735-af9f-8ef06dcc38bc::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845170"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian " "periodicals"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "a047af4e-9710-431a-8b7c-2e0b8346fb5e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911328"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Lexicography--History"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 0.0},
                    "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                    "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 0},
                    "key": "http://id.worldcat.org/fast/845170",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "22b6fe82-7195-4218-9af7-9619786e822e",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749594127"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "cb7f5fa0-93da-41a6-868b-9db610c38d6f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911979"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Written "
                                                        "English--History"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "676a9b6c-f15d-4d37-bb4b-e9fbd1fa1fc8::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911660"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Spoken "
                                                        "English--Research"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "9dd254a5-f436-4d3d-b385-ea56195931f7::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845111"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Canadian " "literature",
                                                },
                                                {
                                                    "@v": (
                                                        "637bba5a-1cd9-4f51-b57b-29f466f74a4d::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845142"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Periodicals"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "7605afd5-6412-47c6-a144-6a32ae83652f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845184"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "prose "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "d99a6371-1b8c-408e-8339-001e9e0a4c7f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/1424786"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Bibliography"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "a47638b8-267e-4288-8f46-6df53357b092::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/934875"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "French-Canadian " "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "01cd29ef-368a-4d1c-8d1f-797c854950e6::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/817954"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Arts, " "Canadian",
                                                },
                                                {
                                                    "@v": (
                                                        "531262ce-12b5-44dd-9b4c-b684a64d8857::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/821870"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Authors, " "Canadian",
                                                },
                                                {
                                                    "@v": (
                                                        "be2998f7-163e-4735-af9f-8ef06dcc38bc::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845170"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian " "periodicals"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "a047af4e-9710-431a-8b7c-2e0b8346fb5e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911328"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Lexicography--History"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 0.0},
                    "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                    "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 0},
                    "key": "http://id.worldcat.org/fast/845184",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "22b6fe82-7195-4218-9af7-9619786e822e",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749594127"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "cb7f5fa0-93da-41a6-868b-9db610c38d6f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911979"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Written "
                                                        "English--History"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "676a9b6c-f15d-4d37-bb4b-e9fbd1fa1fc8::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911660"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Spoken "
                                                        "English--Research"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "9dd254a5-f436-4d3d-b385-ea56195931f7::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845111"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Canadian " "literature",
                                                },
                                                {
                                                    "@v": (
                                                        "637bba5a-1cd9-4f51-b57b-29f466f74a4d::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845142"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Periodicals"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "7605afd5-6412-47c6-a144-6a32ae83652f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845184"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "prose "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "d99a6371-1b8c-408e-8339-001e9e0a4c7f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/1424786"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Bibliography"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "a47638b8-267e-4288-8f46-6df53357b092::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/934875"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "French-Canadian " "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "01cd29ef-368a-4d1c-8d1f-797c854950e6::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/817954"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Arts, " "Canadian",
                                                },
                                                {
                                                    "@v": (
                                                        "531262ce-12b5-44dd-9b4c-b684a64d8857::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/821870"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Authors, " "Canadian",
                                                },
                                                {
                                                    "@v": (
                                                        "be2998f7-163e-4735-af9f-8ef06dcc38bc::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845170"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian " "periodicals"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "a047af4e-9710-431a-8b7c-2e0b8346fb5e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911328"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Lexicography--History"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 0.0},
                    "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                    "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/855500",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "3a1c0854-2036-418e-938f-c5af3b33794e",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749594127"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "2485b574-4ba7-4413-8ff6-56947e72236b::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "@v": (
                                                        "03e6600f-9d63-402b-8e6d-f5ef735d8c6e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "@v": (
                                                        "d39e6657-4122-458b-ac86-eecec2ad11d4::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "c77355ed-5d54-47d9-b6d9-d70f83529893::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "92d2fad8-75ec-4ca0-b25a-e9e99f31915c::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "c613000a-7373-42d8-9c04-c42af94d85df::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 0},
                    "key": "http://id.worldcat.org/fast/911328",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "22b6fe82-7195-4218-9af7-9619786e822e",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749594127"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "cb7f5fa0-93da-41a6-868b-9db610c38d6f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911979"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Written "
                                                        "English--History"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "676a9b6c-f15d-4d37-bb4b-e9fbd1fa1fc8::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911660"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Spoken "
                                                        "English--Research"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "9dd254a5-f436-4d3d-b385-ea56195931f7::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845111"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Canadian " "literature",
                                                },
                                                {
                                                    "@v": (
                                                        "637bba5a-1cd9-4f51-b57b-29f466f74a4d::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845142"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Periodicals"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "7605afd5-6412-47c6-a144-6a32ae83652f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845184"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "prose "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "d99a6371-1b8c-408e-8339-001e9e0a4c7f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/1424786"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Bibliography"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "a47638b8-267e-4288-8f46-6df53357b092::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/934875"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "French-Canadian " "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "01cd29ef-368a-4d1c-8d1f-797c854950e6::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/817954"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Arts, " "Canadian",
                                                },
                                                {
                                                    "@v": (
                                                        "531262ce-12b5-44dd-9b4c-b684a64d8857::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/821870"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Authors, " "Canadian",
                                                },
                                                {
                                                    "@v": (
                                                        "be2998f7-163e-4735-af9f-8ef06dcc38bc::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845170"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian " "periodicals"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "a047af4e-9710-431a-8b7c-2e0b8346fb5e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911328"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Lexicography--History"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 0.0},
                    "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                    "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 8,
        },
        "date_field_max": {
            "value": 1748983872325.0,
            "value_as_string": "2025-06-03T20:51:12",
        },
        "date_field_min": {
            "value": 1748572641721.0,
            "value_as_string": "2025-05-30T02:37:21",
        },
        "file_count": {"value": 3},
        "total_bytes": {"value": 61102780.0},
        "total_records": {"value": 4},
        "uploaders": {"value": 1},
        "with_files": {"doc_count": 3, "meta": {}, "unique_parents": {"value": 3}},
        "without_files": {"doc_count": 1, "meta": {}, "unique_parents": {"value": 1}},
    },
}

MOCK_RECORD_SNAPSHOT_API_RESPONSE = [
    {
        "community_id": "e64dee43-6bd2-4380-b4e8-2813315cb74e",
        "snapshot_date": "2025-01-15",
        "subcounts": {
            "all_access_status": [
                {
                    "files": {"data_volume": 0.0, "file_count": 0},
                    "id": "metadata-only",
                    "label": "",
                    "parents": {"metadata_only": 1, "with_files": 0},
                    "records": {"metadata_only": 1, "with_files": 0},
                }
            ],
            "all_file_types": [],
            "all_languages": [],
            "all_licenses": [],
            "all_resource_types": [],
            "top_affiliations_contributor": [],
            "top_affiliations_creator": [],
            "top_funders": [],
            "top_periodicals": [],
            "top_publishers": [],
            "top_subjects": [],
        },
        "timestamp": "2025-07-02T14:37:33",
        "total_files": {"data_volume": 0.0, "file_count": 0},
        "total_parents": {"metadata_only": 1, "with_files": 0},
        "total_records": {"metadata_only": 1, "with_files": 0},
        "total_uploaders": 0,
        "updated_timestamp": "2025-07-02T14:37:33",
    },
    {
        "community_id": "e64dee43-6bd2-4380-b4e8-2813315cb74e",
        "snapshot_date": "2025-01-16",
        "subcounts": {
            "all_access_status": [
                {
                    "files": {"data_volume": 0.0, "file_count": 0},
                    "id": "metadata-only",
                    "label": "",
                    "parents": {"metadata_only": 2, "with_files": 0},
                    "records": {"metadata_only": 2, "with_files": 0},
                }
            ],
            "all_file_types": [],
            "all_languages": [],
            "all_licenses": [],
            "all_resource_types": [],
            "top_affiliations_contributor": [],
            "top_affiliations_creator": [],
            "top_funders": [],
            "top_periodicals": [],
            "top_publishers": [],
            "top_subjects": [],
        },
        "timestamp": "2025-07-02T14:37:33",
        "total_files": {"data_volume": 0.0, "file_count": 0},
        "total_parents": {"metadata_only": 2, "with_files": 0},
        "total_records": {"metadata_only": 2, "with_files": 0},
        "total_uploaders": 0,
        "updated_timestamp": "2025-07-02T14:37:33",
    },
    {
        "community_id": "e64dee43-6bd2-4380-b4e8-2813315cb74e",
        "snapshot_date": "2025-01-17",
        "subcounts": {
            "all_access_status": [
                {
                    "files": {"data_volume": 0.0, "file_count": 0},
                    "id": "metadata-only",
                    "label": "",
                    "parents": {"metadata_only": 3, "with_files": 0},
                    "records": {"metadata_only": 3, "with_files": 0},
                }
            ],
            "all_file_types": [],
            "all_languages": [],
            "all_licenses": [],
            "all_resource_types": [],
            "top_affiliations_contributor": [],
            "top_affiliations_creator": [],
            "top_funders": [],
            "top_periodicals": [],
            "top_publishers": [],
            "top_subjects": [],
        },
        "timestamp": "2025-07-02T14:37:33",
        "total_files": {"data_volume": 0.0, "file_count": 0},
        "total_parents": {"metadata_only": 3, "with_files": 0},
        "total_records": {"metadata_only": 3, "with_files": 0},
        "total_uploaders": 0,
        "updated_timestamp": "2025-07-02T14:37:33",
    },
]

MOCK_USAGE_QUERY_RESPONSE_VIEWS = {
    "aggregations": {
        "by_access_status": {
            "buckets": [
                {
                    "doc_count": 60,
                    "key": "open",
                    "total_events": {"value": 60},
                    "unique_parents": {"value": 3},
                    "unique_records": {"value": 3},
                    "unique_visitors": {"value": 60},
                },
                {
                    "doc_count": 20,
                    "key": "metadata-only",
                    "total_events": {"value": 20},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_affiliation_id": {
            "buckets": [],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_affiliation_name": {
            "buckets": [],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_countries": {
            "buckets": [
                {
                    "doc_count": 44,
                    "key": "NL",
                    "total_events": {"value": 44},
                    "unique_parents": {"value": 4},
                    "unique_records": {"value": 4},
                    "unique_visitors": {"value": 44},
                },
                {
                    "doc_count": 19,
                    "key": "US",
                    "total_events": {"value": 19},
                    "unique_parents": {"value": 4},
                    "unique_records": {"value": 4},
                    "unique_visitors": {"value": 19},
                },
                {
                    "doc_count": 14,
                    "key": "CN",
                    "total_events": {"value": 14},
                    "unique_parents": {"value": 4},
                    "unique_records": {"value": 4},
                    "unique_visitors": {"value": 14},
                },
                {
                    "doc_count": 2,
                    "key": "AU",
                    "total_events": {"value": 2},
                    "unique_parents": {"value": 2},
                    "unique_records": {"value": 2},
                    "unique_visitors": {"value": 2},
                },
                {
                    "doc_count": 1,
                    "key": "JP",
                    "total_events": {"value": 1},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 1},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_file_types": {
            "buckets": [
                {
                    "doc_count": 60,
                    "key": "pdf",
                    "total_events": {"value": 60},
                    "unique_parents": {"value": 3},
                    "unique_records": {"value": 3},
                    "unique_visitors": {"value": 60},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_funder_id": {
            "buckets": [
                {
                    "doc_count": 20,
                    "key": "1234567890",
                    "total_events": {"value": 20},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_funder_name": {
            "buckets": [
                {
                    "doc_count": 20,
                    "key": "Funder Name",
                    "total_events": {"value": 20},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_languages": {
            "buckets": [
                {
                    "doc_count": 40,
                    "key": "eng",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": (
                                        "2025-07-03T00:29:39-de2e0837d9e40a79b63bfeaba263a26e22d1e2a1"
                                    ),
                                    "_index": "events-stats-record-view-2025-07",
                                    "_score": 1.006192,
                                    "_source": {
                                        "languages": [
                                            {"id": "eng", "title": {"en": "English"}}
                                        ]
                                    },
                                }
                            ],
                            "max_score": 1.006192,
                            "total": {"relation": "eq", "value": 40},
                        }
                    },
                    "total_events": {"value": 40},
                    "unique_parents": {"value": 2},
                    "unique_records": {"value": 2},
                    "unique_visitors": {"value": 40},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_licenses": {
            "buckets": [
                {
                    "doc_count": 20,
                    "key": "cc-by-sa-4.0",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": (
                                        "2025-07-03T09:43:46-76c601bc7425aeced6b541686656ecd178104670"
                                    ),
                                    "_index": "events-stats-record-view-2025-07",
                                    "_score": 1.006192,
                                    "_source": {
                                        "rights": [
                                            {
                                                "id": "cc-by-sa-4.0",
                                                "title": {
                                                    "en": (
                                                        "Creative "
                                                        "Commons "
                                                        "Attribution-ShareAlike "
                                                        "4.0 "
                                                        "International"
                                                    )
                                                },
                                            }
                                        ]
                                    },
                                }
                            ],
                            "max_score": 1.006192,
                            "total": {"relation": "eq", "value": 20},
                        }
                    },
                    "total_events": {"value": 20},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_periodicals": {
            "buckets": [
                {
                    "doc_count": 20,
                    "key": "N/A",
                    "total_events": {"value": 20},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_publishers": {
            "buckets": [
                {
                    "doc_count": 40,
                    "key": "Knowledge Commons",
                    "total_events": {"value": 40},
                    "unique_parents": {"value": 2},
                    "unique_records": {"value": 2},
                    "unique_visitors": {"value": 40},
                },
                {
                    "doc_count": 20,
                    "key": "Apocryphile Press",
                    "total_events": {"value": 20},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                },
                {
                    "doc_count": 20,
                    "key": "UBC",
                    "total_events": {"value": 20},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_referrers": {
            "buckets": [
                {
                    "doc_count": 20,
                    "key": "https://example.com/records/cj7gk-ddv34",
                    "total_events": {"value": 20},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                },
                {
                    "doc_count": 20,
                    "key": "https://example.com/records/d2ve0-44c44",
                    "total_events": {"value": 20},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                },
                {
                    "doc_count": 20,
                    "key": "https://example.com/records/jc533-w3929",
                    "total_events": {"value": 20},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                },
                {
                    "doc_count": 20,
                    "key": "https://example.com/records/p25dc-48t61",
                    "total_events": {"value": 20},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_resource_types": {
            "buckets": [
                {
                    "doc_count": 40,
                    "key": "textDocument-journalArticle",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": (
                                        "2025-07-03T01:54:45-285f9a47a60e50b8f0fe4e96c5e16c98be4faab6"
                                    ),
                                    "_index": "events-stats-record-view-2025-07",
                                    "_score": 1.006192,
                                    "_source": {
                                        "resource_type": {
                                            "id": "textDocument-journalArticle",
                                            "title": {"en": "Journal " "Article"},
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.006192,
                            "total": {"relation": "eq", "value": 40},
                        }
                    },
                    "total_events": {"value": 40},
                    "unique_parents": {"value": 2},
                    "unique_records": {"value": 2},
                    "unique_visitors": {"value": 40},
                },
                {
                    "doc_count": 20,
                    "key": "textDocument-book",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": (
                                        "2025-07-03T06:58:37-813dbf5c74958287c46ef05b5ca31b23d72d9987"
                                    ),
                                    "_index": "events-stats-record-view-2025-07",
                                    "_score": 1.006192,
                                    "_source": {
                                        "resource_type": {
                                            "id": "textDocument-book",
                                            "title": {"en": "Book"},
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.006192,
                            "total": {"relation": "eq", "value": 20},
                        }
                    },
                    "total_events": {"value": 20},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                },
                {
                    "doc_count": 20,
                    "key": "textDocument-bookSection",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": (
                                        "2025-07-03T05:33:46-d0103c26fc80ee4dd1f6c71991e2fc0891f2016f"
                                    ),
                                    "_index": "events-stats-record-view-2025-07",
                                    "_score": 1.006192,
                                    "_source": {
                                        "resource_type": {
                                            "id": "textDocument-bookSection",
                                            "title": {"en": "Book " "Section"},
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.006192,
                            "total": {"relation": "eq", "value": 20},
                        }
                    },
                    "total_events": {"value": 20},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_subjects": {
            "buckets": [
                {
                    "doc_count": 20,
                    "key": "http://id.worldcat.org/fast/1424786",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": (
                                        "2025-07-03T13:02:55-2e451e41b611b7eba881d07bfa380cb6d68cf760"
                                    ),
                                    "_index": "events-stats-record-view-2025-07",
                                    "_score": 1.006192,
                                    "_source": {
                                        "subjects": [
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911979"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911660"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845111"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845142"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845184"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/1424786"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/934875"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/817954"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/821870"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845170"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911328"
                                                )
                                            },
                                        ]
                                    },
                                }
                            ],
                            "max_score": 1.006192,
                            "total": {"relation": "eq", "value": 20},
                        }
                    },
                    "total_events": {"value": 20},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                },
                {
                    "doc_count": 20,
                    "key": "http://id.worldcat.org/fast/2060143",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": (
                                        "2025-07-03T00:29:39-de2e0837d9e40a79b63bfeaba263a26e22d1e2a1"
                                    ),
                                    "_index": "events-stats-record-view-2025-07",
                                    "_score": 1.006192,
                                    "_source": {
                                        "subjects": [
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997916"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/2060143"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997987"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997974"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/855500"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/995415"
                                                )
                                            },
                                        ]
                                    },
                                }
                            ],
                            "max_score": 1.006192,
                            "total": {"relation": "eq", "value": 20},
                        }
                    },
                    "total_events": {"value": 20},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                },
                {
                    "doc_count": 20,
                    "key": "http://id.worldcat.org/fast/817954",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": (
                                        "2025-07-03T13:02:55-2e451e41b611b7eba881d07bfa380cb6d68cf760"
                                    ),
                                    "_index": "events-stats-record-view-2025-07",
                                    "_score": 1.006192,
                                    "_source": {
                                        "subjects": [
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911979"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911660"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845111"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845142"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845184"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/1424786"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/934875"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/817954"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/821870"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845170"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911328"
                                                )
                                            },
                                        ]
                                    },
                                }
                            ],
                            "max_score": 1.006192,
                            "total": {"relation": "eq", "value": 20},
                        }
                    },
                    "total_events": {"value": 20},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                },
                {
                    "doc_count": 20,
                    "key": "http://id.worldcat.org/fast/821870",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": (
                                        "2025-07-03T13:02:55-2e451e41b611b7eba881d07bfa380cb6d68cf760"
                                    ),
                                    "_index": "events-stats-record-view-2025-07",
                                    "_score": 1.006192,
                                    "_source": {
                                        "subjects": [
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911979"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911660"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845111"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845142"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845184"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/1424786"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/934875"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/817954"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/821870"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845170"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911328"
                                                )
                                            },
                                        ]
                                    },
                                }
                            ],
                            "max_score": 1.006192,
                            "total": {"relation": "eq", "value": 20},
                        }
                    },
                    "total_events": {"value": 20},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                },
                {
                    "doc_count": 20,
                    "key": "http://id.worldcat.org/fast/845111",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": (
                                        "2025-07-03T13:02:55-2e451e41b611b7eba881d07bfa380cb6d68cf760"
                                    ),
                                    "_index": "events-stats-record-view-2025-07",
                                    "_score": 1.006192,
                                    "_source": {
                                        "subjects": [
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911979"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911660"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845111"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845142"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845184"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/1424786"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/934875"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/817954"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/821870"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845170"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911328"
                                                )
                                            },
                                        ]
                                    },
                                }
                            ],
                            "max_score": 1.006192,
                            "total": {"relation": "eq", "value": 20},
                        }
                    },
                    "total_events": {"value": 20},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                },
                {
                    "doc_count": 20,
                    "key": "http://id.worldcat.org/fast/845142",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": (
                                        "2025-07-03T13:02:55-2e451e41b611b7eba881d07bfa380cb6d68cf760"
                                    ),
                                    "_index": "events-stats-record-view-2025-07",
                                    "_score": 1.006192,
                                    "_source": {
                                        "subjects": [
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911979"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911660"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845111"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845142"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845184"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/1424786"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/934875"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/817954"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/821870"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845170"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911328"
                                                )
                                            },
                                        ]
                                    },
                                }
                            ],
                            "max_score": 1.006192,
                            "total": {"relation": "eq", "value": 20},
                        }
                    },
                    "total_events": {"value": 20},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                },
                {
                    "doc_count": 20,
                    "key": "http://id.worldcat.org/fast/845170",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": (
                                        "2025-07-03T13:02:55-2e451e41b611b7eba881d07bfa380cb6d68cf760"
                                    ),
                                    "_index": "events-stats-record-view-2025-07",
                                    "_score": 1.006192,
                                    "_source": {
                                        "subjects": [
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911979"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911660"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845111"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845142"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845184"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/1424786"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/934875"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/817954"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/821870"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845170"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911328"
                                                )
                                            },
                                        ]
                                    },
                                }
                            ],
                            "max_score": 1.006192,
                            "total": {"relation": "eq", "value": 20},
                        }
                    },
                    "total_events": {"value": 20},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                },
                {
                    "doc_count": 20,
                    "key": "http://id.worldcat.org/fast/845184",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": (
                                        "2025-07-03T13:02:55-2e451e41b611b7eba881d07bfa380cb6d68cf760"
                                    ),
                                    "_index": "events-stats-record-view-2025-07",
                                    "_score": 1.006192,
                                    "_source": {
                                        "subjects": [
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911979"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911660"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845111"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845142"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845184"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/1424786"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/934875"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/817954"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/821870"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845170"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911328"
                                                )
                                            },
                                        ]
                                    },
                                }
                            ],
                            "max_score": 1.006192,
                            "total": {"relation": "eq", "value": 20},
                        }
                    },
                    "total_events": {"value": 20},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                },
                {
                    "doc_count": 20,
                    "key": "http://id.worldcat.org/fast/855500",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": (
                                        "2025-07-03T00:29:39-de2e0837d9e40a79b63bfeaba263a26e22d1e2a1"
                                    ),
                                    "_index": "events-stats-record-view-2025-07",
                                    "_score": 1.006192,
                                    "_source": {
                                        "subjects": [
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997916"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/2060143"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997987"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997974"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/855500"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/995415"
                                                )
                                            },
                                        ]
                                    },
                                }
                            ],
                            "max_score": 1.006192,
                            "total": {"relation": "eq", "value": 20},
                        }
                    },
                    "total_events": {"value": 20},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                },
                {
                    "doc_count": 20,
                    "key": "http://id.worldcat.org/fast/911328",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": (
                                        "2025-07-03T13:02:55-2e451e41b611b7eba881d07bfa380cb6d68cf760"
                                    ),
                                    "_index": "events-stats-record-view-2025-07",
                                    "_score": 1.006192,
                                    "_source": {
                                        "subjects": [
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911979"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911660"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845111"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845142"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845184"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/1424786"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/934875"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/817954"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/821870"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845170"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911328"
                                                )
                                            },
                                        ]
                                    },
                                }
                            ],
                            "max_score": 1.006192,
                            "total": {"relation": "eq", "value": 20},
                        }
                    },
                    "total_events": {"value": 20},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                },
                {
                    "doc_count": 20,
                    "key": "http://id.worldcat.org/fast/911660",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": (
                                        "2025-07-03T13:02:55-2e451e41b611b7eba881d07bfa380cb6d68cf760"
                                    ),
                                    "_index": "events-stats-record-view-2025-07",
                                    "_score": 1.006192,
                                    "_source": {
                                        "subjects": [
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911979"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911660"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845111"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845142"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845184"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/1424786"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/934875"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/817954"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/821870"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845170"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911328"
                                                )
                                            },
                                        ]
                                    },
                                }
                            ],
                            "max_score": 1.006192,
                            "total": {"relation": "eq", "value": 20},
                        }
                    },
                    "total_events": {"value": 20},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                },
                {
                    "doc_count": 20,
                    "key": "http://id.worldcat.org/fast/911979",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": (
                                        "2025-07-03T13:02:55-2e451e41b611b7eba881d07bfa380cb6d68cf760"
                                    ),
                                    "_index": "events-stats-record-view-2025-07",
                                    "_score": 1.006192,
                                    "_source": {
                                        "subjects": [
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911979"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911660"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845111"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845142"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845184"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/1424786"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/934875"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/817954"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/821870"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845170"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911328"
                                                )
                                            },
                                        ]
                                    },
                                }
                            ],
                            "max_score": 1.006192,
                            "total": {"relation": "eq", "value": 20},
                        }
                    },
                    "total_events": {"value": 20},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                },
                {
                    "doc_count": 20,
                    "key": "http://id.worldcat.org/fast/934875",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": (
                                        "2025-07-03T13:02:55-2e451e41b611b7eba881d07bfa380cb6d68cf760"
                                    ),
                                    "_index": "events-stats-record-view-2025-07",
                                    "_score": 1.006192,
                                    "_source": {
                                        "subjects": [
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911979"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911660"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845111"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845142"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845184"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/1424786"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/934875"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/817954"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/821870"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845170"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911328"
                                                )
                                            },
                                        ]
                                    },
                                }
                            ],
                            "max_score": 1.006192,
                            "total": {"relation": "eq", "value": 20},
                        }
                    },
                    "total_events": {"value": 20},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                },
                {
                    "doc_count": 20,
                    "key": "http://id.worldcat.org/fast/973589",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": (
                                        "2025-07-03T00:08:07-a69e246cfaa3036c877052b6bee1325a218663cb"
                                    ),
                                    "_index": "events-stats-record-view-2025-07",
                                    "_score": 1.006192,
                                    "_source": {
                                        "subjects": [
                                            {"id": "http://id.worldcat.org/fast/973589"}
                                        ]
                                    },
                                }
                            ],
                            "max_score": 1.006192,
                            "total": {"relation": "eq", "value": 20},
                        }
                    },
                    "total_events": {"value": 20},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                },
                {
                    "doc_count": 20,
                    "key": "http://id.worldcat.org/fast/995415",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": (
                                        "2025-07-03T00:29:39-de2e0837d9e40a79b63bfeaba263a26e22d1e2a1"
                                    ),
                                    "_index": "events-stats-record-view-2025-07",
                                    "_score": 1.006192,
                                    "_source": {
                                        "subjects": [
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997916"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/2060143"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997987"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997974"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/855500"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/995415"
                                                )
                                            },
                                        ]
                                    },
                                }
                            ],
                            "max_score": 1.006192,
                            "total": {"relation": "eq", "value": 20},
                        }
                    },
                    "total_events": {"value": 20},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                },
                {
                    "doc_count": 20,
                    "key": "http://id.worldcat.org/fast/997916",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": (
                                        "2025-07-03T00:29:39-de2e0837d9e40a79b63bfeaba263a26e22d1e2a1"
                                    ),
                                    "_index": "events-stats-record-view-2025-07",
                                    "_score": 1.006192,
                                    "_source": {
                                        "subjects": [
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997916"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/2060143"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997987"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997974"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/855500"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/995415"
                                                )
                                            },
                                        ]
                                    },
                                }
                            ],
                            "max_score": 1.006192,
                            "total": {"relation": "eq", "value": 20},
                        }
                    },
                    "total_events": {"value": 20},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                },
                {
                    "doc_count": 20,
                    "key": "http://id.worldcat.org/fast/997974",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": (
                                        "2025-07-03T00:29:39-de2e0837d9e40a79b63bfeaba263a26e22d1e2a1"
                                    ),
                                    "_index": "events-stats-record-view-2025-07",
                                    "_score": 1.006192,
                                    "_source": {
                                        "subjects": [
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997916"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/2060143"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997987"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997974"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/855500"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/995415"
                                                )
                                            },
                                        ]
                                    },
                                }
                            ],
                            "max_score": 1.006192,
                            "total": {"relation": "eq", "value": 20},
                        }
                    },
                    "total_events": {"value": 20},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                },
                {
                    "doc_count": 20,
                    "key": "http://id.worldcat.org/fast/997987",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": (
                                        "2025-07-03T00:29:39-de2e0837d9e40a79b63bfeaba263a26e22d1e2a1"
                                    ),
                                    "_index": "events-stats-record-view-2025-07",
                                    "_score": 1.006192,
                                    "_source": {
                                        "subjects": [
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997916"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/2060143"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997987"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997974"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/855500"
                                                )
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/995415"
                                                )
                                            },
                                        ]
                                    },
                                }
                            ],
                            "max_score": 1.006192,
                            "total": {"relation": "eq", "value": 20},
                        }
                    },
                    "total_events": {"value": 20},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "total_events": {"value": 80},
        "unique_parents": {"value": 4},
        "unique_records": {"value": 4},
        "unique_visitors": {"value": 80},
    },
    "hits": {"hits": [], "max_score": None, "total": {"relation": "eq", "value": 0}},
}

MOCK_USAGE_QUERY_RESPONSE_DOWNLOADS = {}

MOCK_USAGE_DELTA_API_RESPONSE = {
    "community-stats": [
        {
            "community_id": "59e77d51-3758-409a-813f-efc0d2db1a5e",
            "period_end": "2025-05-30T23:59:59",
            "period_start": "2025-05-30T00:00:00",
            "subcounts": {
                "by_access_status": [],
                "by_affiliations": [],
                "by_countries": [],
                "by_file_types": [],
                "by_funders": [],
                "by_languages": [],
                "by_licenses": [],
                "by_periodicals": [],
                "by_publishers": [],
                "by_referrers": [],
                "by_resource_types": [],
                "by_subjects": [],
            },
            "timestamp": "2025-07-03T19:37:10",
            "totals": {
                "download": {
                    "total_events": 0,
                    "total_volume": 0.0,
                    "unique_files": 0,
                    "unique_parents": 0,
                    "unique_records": 0,
                    "unique_visitors": 0,
                },
                "view": {
                    "total_events": 0,
                    "unique_parents": 0,
                    "unique_records": 0,
                    "unique_visitors": 0,
                },
            },
        },
        {
            "community_id": "59e77d51-3758-409a-813f-efc0d2db1a5e",
            "period_end": "2025-05-31T23:59:59",
            "period_start": "2025-05-31T00:00:00",
            "subcounts": {
                "by_access_status": [],
                "by_affiliations": [],
                "by_countries": [],
                "by_file_types": [],
                "by_funders": [],
                "by_languages": [],
                "by_licenses": [],
                "by_periodicals": [],
                "by_publishers": [],
                "by_referrers": [],
                "by_resource_types": [],
                "by_subjects": [],
            },
            "timestamp": "2025-07-03T19:37:10",
            "totals": {
                "download": {
                    "total_events": 0,
                    "total_volume": 0.0,
                    "unique_files": 0,
                    "unique_parents": 0,
                    "unique_records": 0,
                    "unique_visitors": 0,
                },
                "view": {
                    "total_events": 0,
                    "unique_parents": 0,
                    "unique_records": 0,
                    "unique_visitors": 0,
                },
            },
        },
        {
            "community_id": "59e77d51-3758-409a-813f-efc0d2db1a5e",
            "period_end": "2025-06-01T23:59:59",
            "period_start": "2025-06-01T00:00:00",
            "subcounts": {
                "by_access_status": [
                    {
                        "download": {
                            "total_events": 3,
                            "total_volume": 3072.0,
                            "unique_files": 3,
                            "unique_parents": 3,
                            "unique_records": 3,
                            "unique_visitors": 3,
                        },
                        "id": "metadata-only",
                        "label": "",
                        "view": {
                            "total_events": 3,
                            "unique_parents": 3,
                            "unique_records": 3,
                            "unique_visitors": 3,
                        },
                    }
                ],
                "by_affiliations": [],
                "by_countries": [
                    {
                        "download": {
                            "total_events": 3,
                            "total_volume": 3072.0,
                            "unique_files": 3,
                            "unique_parents": 3,
                            "unique_records": 3,
                            "unique_visitors": 3,
                        },
                        "id": "US",
                        "label": "",
                        "view": {
                            "total_events": 0,
                            "unique_parents": 0,
                            "unique_records": 0,
                            "unique_visitors": 0,
                        },
                    }
                ],
                "by_file_types": [
                    {
                        "download": {
                            "total_events": 3,
                            "total_volume": 3072.0,
                            "unique_files": 3,
                            "unique_parents": 3,
                            "unique_records": 3,
                            "unique_visitors": 3,
                        },
                        "id": "pdf",
                        "label": "",
                        "view": {
                            "total_events": 0,
                            "unique_parents": 0,
                            "unique_records": 0,
                            "unique_visitors": 0,
                        },
                    }
                ],
                "by_funders": [],
                "by_languages": [
                    {
                        "download": {
                            "total_events": 2,
                            "total_volume": 2048.0,
                            "unique_files": 2,
                            "unique_parents": 2,
                            "unique_records": 2,
                            "unique_visitors": 2,
                        },
                        "id": "spa",
                        "label": "Spanish",
                        "view": {
                            "total_events": 2,
                            "unique_parents": 2,
                            "unique_records": 2,
                            "unique_visitors": 2,
                        },
                    },
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": "eng",
                        "label": "English",
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                ],
                "by_licenses": [
                    {
                        "download": {
                            "total_events": 3,
                            "total_volume": 3072.0,
                            "unique_files": 3,
                            "unique_parents": 3,
                            "unique_records": 3,
                            "unique_visitors": 3,
                        },
                        "id": "arr",
                        "label": "All Rights " "Reserved",
                        "view": {
                            "total_events": 3,
                            "unique_parents": 3,
                            "unique_records": 3,
                            "unique_visitors": 3,
                        },
                    }
                ],
                "by_periodicals": [],
                "by_publishers": [
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": "Brill",
                        "label": "",
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": (
                            "Editorial "
                            "ACRIBIA, S. A., "
                            "Apartado 466, "
                            "50080, Zaragoza, "
                            "Espana."
                        ),
                        "label": "",
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": "Universidad " "Nacional " "Autónoma de " "Mexico (UNAM)",
                        "label": "",
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                ],
                "by_referrers": [
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": (
                            "https://works.hcommons.org/records/9qsr6-v4k38/preview/test.pdf"
                        ),
                        "label": "",
                        "view": {
                            "total_events": 0,
                            "unique_parents": 0,
                            "unique_records": 0,
                            "unique_visitors": 0,
                        },
                    },
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": (
                            "https://works.hcommons.org/records/rhk6r-p5d15/preview/test.pdf"
                        ),
                        "label": "",
                        "view": {
                            "total_events": 0,
                            "unique_parents": 0,
                            "unique_records": 0,
                            "unique_visitors": 0,
                        },
                    },
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": (
                            "https://works.hcommons.org/records/t8hjs-dzx03/preview/test.pdf"
                        ),
                        "label": "",
                        "view": {
                            "total_events": 0,
                            "unique_parents": 0,
                            "unique_records": 0,
                            "unique_visitors": 0,
                        },
                    },
                ],
                "by_resource_types": [
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": "textDocument-book",
                        "label": "Book",
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": "textDocument-journalArticle",
                        "label": "Journal " "Article",
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": "textDocument-thesis",
                        "label": "Thesis",
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                ],
                "by_subjects": [
                    {
                        "download": {
                            "total_events": 2,
                            "total_volume": 2048.0,
                            "unique_files": 2,
                            "unique_parents": 2,
                            "unique_records": 2,
                            "unique_visitors": 2,
                        },
                        "id": "http://id.worldcat.org/fast/1012163",
                        "label": "Mathematics",
                        "view": {
                            "total_events": 2,
                            "unique_parents": 2,
                            "unique_records": 2,
                            "unique_visitors": 2,
                        },
                    },
                    {
                        "download": {
                            "total_events": 2,
                            "total_volume": 2048.0,
                            "unique_files": 2,
                            "unique_parents": 2,
                            "unique_records": 2,
                            "unique_visitors": 2,
                        },
                        "id": "http://id.worldcat.org/fast/958235",
                        "label": "History",
                        "view": {
                            "total_events": 2,
                            "unique_parents": 2,
                            "unique_records": 2,
                            "unique_visitors": 2,
                        },
                    },
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": "http://id.worldcat.org/fast/1012213",
                        "label": "Mathematics--Philosophy",
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": "http://id.worldcat.org/fast/1108176",
                        "label": "Science",
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": "http://id.worldcat.org/fast/1108387",
                        "label": "Science--Study " "and teaching",
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": "http://id.worldcat.org/fast/1145221",
                        "label": "Technology--Study " "and teaching",
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": "http://id.worldcat.org/fast/902116",
                        "label": "Economics",
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                ],
            },
            "timestamp": "2025-07-03T19:37:10",
            "totals": {
                "download": {
                    "total_events": 3,
                    "total_volume": 3072.0,
                    "unique_files": 3,
                    "unique_parents": 3,
                    "unique_records": 3,
                    "unique_visitors": 3,
                },
                "view": {
                    "total_events": 3,
                    "unique_parents": 3,
                    "unique_records": 3,
                    "unique_visitors": 3,
                },
            },
        },
        {
            "community_id": "59e77d51-3758-409a-813f-efc0d2db1a5e",
            "period_end": "2025-06-02T23:59:59",
            "period_start": "2025-06-02T00:00:00",
            "subcounts": {
                "by_access_status": [],
                "by_affiliations": [],
                "by_countries": [],
                "by_file_types": [],
                "by_funders": [],
                "by_languages": [],
                "by_licenses": [],
                "by_periodicals": [],
                "by_publishers": [],
                "by_referrers": [],
                "by_resource_types": [],
                "by_subjects": [],
            },
            "timestamp": "2025-07-03T19:37:10",
            "totals": {
                "download": {
                    "total_events": 0,
                    "total_volume": 0.0,
                    "unique_files": 0,
                    "unique_parents": 0,
                    "unique_records": 0,
                    "unique_visitors": 0,
                },
                "view": {
                    "total_events": 0,
                    "unique_parents": 0,
                    "unique_records": 0,
                    "unique_visitors": 0,
                },
            },
        },
        {
            "community_id": "59e77d51-3758-409a-813f-efc0d2db1a5e",
            "period_end": "2025-06-03T23:59:59",
            "period_start": "2025-06-03T00:00:00",
            "subcounts": {
                "by_access_status": [
                    {
                        "download": {
                            "total_events": 3,
                            "total_volume": 3072.0,
                            "unique_files": 3,
                            "unique_parents": 3,
                            "unique_records": 3,
                            "unique_visitors": 3,
                        },
                        "id": "metadata-only",
                        "label": "",
                        "view": {
                            "total_events": 3,
                            "unique_parents": 3,
                            "unique_records": 3,
                            "unique_visitors": 3,
                        },
                    }
                ],
                "by_affiliations": [],
                "by_countries": [
                    {
                        "download": {
                            "total_events": 3,
                            "total_volume": 3072.0,
                            "unique_files": 3,
                            "unique_parents": 3,
                            "unique_records": 3,
                            "unique_visitors": 3,
                        },
                        "id": "US",
                        "label": "",
                        "view": {
                            "total_events": 0,
                            "unique_parents": 0,
                            "unique_records": 0,
                            "unique_visitors": 0,
                        },
                    }
                ],
                "by_file_types": [
                    {
                        "download": {
                            "total_events": 3,
                            "total_volume": 3072.0,
                            "unique_files": 3,
                            "unique_parents": 3,
                            "unique_records": 3,
                            "unique_visitors": 3,
                        },
                        "id": "pdf",
                        "label": "",
                        "view": {
                            "total_events": 0,
                            "unique_parents": 0,
                            "unique_records": 0,
                            "unique_visitors": 0,
                        },
                    }
                ],
                "by_funders": [],
                "by_languages": [
                    {
                        "download": {
                            "total_events": 2,
                            "total_volume": 2048.0,
                            "unique_files": 2,
                            "unique_parents": 2,
                            "unique_records": 2,
                            "unique_visitors": 2,
                        },
                        "id": "spa",
                        "label": "Spanish",
                        "view": {
                            "total_events": 2,
                            "unique_parents": 2,
                            "unique_records": 2,
                            "unique_visitors": 2,
                        },
                    },
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": "eng",
                        "label": "English",
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                ],
                "by_licenses": [
                    {
                        "download": {
                            "total_events": 3,
                            "total_volume": 3072.0,
                            "unique_files": 3,
                            "unique_parents": 3,
                            "unique_records": 3,
                            "unique_visitors": 3,
                        },
                        "id": "arr",
                        "label": "All Rights " "Reserved",
                        "view": {
                            "total_events": 3,
                            "unique_parents": 3,
                            "unique_records": 3,
                            "unique_visitors": 3,
                        },
                    }
                ],
                "by_periodicals": [],
                "by_publishers": [
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": "Brill",
                        "label": "",
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": (
                            "Editorial "
                            "ACRIBIA, S. A., "
                            "Apartado 466, "
                            "50080, Zaragoza, "
                            "Espana."
                        ),
                        "label": "",
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": "Universidad " "Nacional " "Autónoma de " "Mexico (UNAM)",
                        "label": "",
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                ],
                "by_referrers": [
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": (
                            "https://works.hcommons.org/records/9qsr6-v4k38/preview/test.pdf"
                        ),
                        "label": "",
                        "view": {
                            "total_events": 0,
                            "unique_parents": 0,
                            "unique_records": 0,
                            "unique_visitors": 0,
                        },
                    },
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": (
                            "https://works.hcommons.org/records/rhk6r-p5d15/preview/test.pdf"
                        ),
                        "label": "",
                        "view": {
                            "total_events": 0,
                            "unique_parents": 0,
                            "unique_records": 0,
                            "unique_visitors": 0,
                        },
                    },
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": (
                            "https://works.hcommons.org/records/t8hjs-dzx03/preview/test.pdf"
                        ),
                        "label": "",
                        "view": {
                            "total_events": 0,
                            "unique_parents": 0,
                            "unique_records": 0,
                            "unique_visitors": 0,
                        },
                    },
                ],
                "by_resource_types": [
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": "textDocument-book",
                        "label": "Book",
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": "textDocument-journalArticle",
                        "label": "Journal " "Article",
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": "textDocument-thesis",
                        "label": "Thesis",
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                ],
                "by_subjects": [
                    {
                        "download": {
                            "total_events": 2,
                            "total_volume": 2048.0,
                            "unique_files": 2,
                            "unique_parents": 2,
                            "unique_records": 2,
                            "unique_visitors": 2,
                        },
                        "id": "http://id.worldcat.org/fast/1012163",
                        "label": "Mathematics",
                        "view": {
                            "total_events": 2,
                            "unique_parents": 2,
                            "unique_records": 2,
                            "unique_visitors": 2,
                        },
                    },
                    {
                        "download": {
                            "total_events": 2,
                            "total_volume": 2048.0,
                            "unique_files": 2,
                            "unique_parents": 2,
                            "unique_records": 2,
                            "unique_visitors": 2,
                        },
                        "id": "http://id.worldcat.org/fast/958235",
                        "label": "History",
                        "view": {
                            "total_events": 2,
                            "unique_parents": 2,
                            "unique_records": 2,
                            "unique_visitors": 2,
                        },
                    },
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": "http://id.worldcat.org/fast/1012213",
                        "label": "Mathematics--Philosophy",
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": "http://id.worldcat.org/fast/1108176",
                        "label": "Science",
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": "http://id.worldcat.org/fast/1108387",
                        "label": "Science--Study " "and teaching",
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": "http://id.worldcat.org/fast/1145221",
                        "label": "Technology--Study " "and teaching",
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": "http://id.worldcat.org/fast/902116",
                        "label": "Economics",
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                ],
            },
            "timestamp": "2025-07-03T19:37:10",
            "totals": {
                "download": {
                    "total_events": 3,
                    "total_volume": 3072.0,
                    "unique_files": 3,
                    "unique_parents": 3,
                    "unique_records": 3,
                    "unique_visitors": 3,
                },
                "view": {
                    "total_events": 3,
                    "unique_parents": 3,
                    "unique_records": 3,
                    "unique_visitors": 3,
                },
            },
        },
        {
            "community_id": "59e77d51-3758-409a-813f-efc0d2db1a5e",
            "period_end": "2025-06-04T23:59:59",
            "period_start": "2025-06-04T00:00:00",
            "subcounts": {
                "by_access_status": [],
                "by_affiliations": [],
                "by_countries": [],
                "by_file_types": [],
                "by_funders": [],
                "by_languages": [],
                "by_licenses": [],
                "by_periodicals": [],
                "by_publishers": [],
                "by_referrers": [],
                "by_resource_types": [],
                "by_subjects": [],
            },
            "timestamp": "2025-07-03T19:37:11",
            "totals": {
                "download": {
                    "total_events": 0,
                    "total_volume": 0.0,
                    "unique_files": 0,
                    "unique_parents": 0,
                    "unique_records": 0,
                    "unique_visitors": 0,
                },
                "view": {
                    "total_events": 0,
                    "unique_parents": 0,
                    "unique_records": 0,
                    "unique_visitors": 0,
                },
            },
        },
        {
            "community_id": "59e77d51-3758-409a-813f-efc0d2db1a5e",
            "period_end": "2025-06-05T23:59:59",
            "period_start": "2025-06-05T00:00:00",
            "subcounts": {
                "by_access_status": [
                    {
                        "download": {
                            "total_events": 3,
                            "total_volume": 3072.0,
                            "unique_files": 3,
                            "unique_parents": 3,
                            "unique_records": 3,
                            "unique_visitors": 3,
                        },
                        "id": "metadata-only",
                        "label": "",
                        "view": {
                            "total_events": 3,
                            "unique_parents": 3,
                            "unique_records": 3,
                            "unique_visitors": 3,
                        },
                    }
                ],
                "by_affiliations": [],
                "by_countries": [
                    {
                        "download": {
                            "total_events": 3,
                            "total_volume": 3072.0,
                            "unique_files": 3,
                            "unique_parents": 3,
                            "unique_records": 3,
                            "unique_visitors": 3,
                        },
                        "id": "US",
                        "label": "",
                        "view": {
                            "total_events": 0,
                            "unique_parents": 0,
                            "unique_records": 0,
                            "unique_visitors": 0,
                        },
                    }
                ],
                "by_file_types": [
                    {
                        "download": {
                            "total_events": 3,
                            "total_volume": 3072.0,
                            "unique_files": 3,
                            "unique_parents": 3,
                            "unique_records": 3,
                            "unique_visitors": 3,
                        },
                        "id": "pdf",
                        "label": "",
                        "view": {
                            "total_events": 0,
                            "unique_parents": 0,
                            "unique_records": 0,
                            "unique_visitors": 0,
                        },
                    }
                ],
                "by_funders": [],
                "by_languages": [
                    {
                        "download": {
                            "total_events": 2,
                            "total_volume": 2048.0,
                            "unique_files": 2,
                            "unique_parents": 2,
                            "unique_records": 2,
                            "unique_visitors": 2,
                        },
                        "id": "spa",
                        "label": "Spanish",
                        "view": {
                            "total_events": 2,
                            "unique_parents": 2,
                            "unique_records": 2,
                            "unique_visitors": 2,
                        },
                    },
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": "eng",
                        "label": "English",
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                ],
                "by_licenses": [
                    {
                        "download": {
                            "total_events": 3,
                            "total_volume": 3072.0,
                            "unique_files": 3,
                            "unique_parents": 3,
                            "unique_records": 3,
                            "unique_visitors": 3,
                        },
                        "id": "arr",
                        "label": "All Rights " "Reserved",
                        "view": {
                            "total_events": 3,
                            "unique_parents": 3,
                            "unique_records": 3,
                            "unique_visitors": 3,
                        },
                    }
                ],
                "by_periodicals": [],
                "by_publishers": [
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": "Brill",
                        "label": "",
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": (
                            "Editorial "
                            "ACRIBIA, S. A., "
                            "Apartado 466, "
                            "50080, Zaragoza, "
                            "Espana."
                        ),
                        "label": "",
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": "Universidad " "Nacional " "Autónoma de " "Mexico (UNAM)",
                        "label": "",
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                ],
                "by_referrers": [
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": (
                            "https://works.hcommons.org/records/9qsr6-v4k38/preview/test.pdf"
                        ),
                        "label": "",
                        "view": {
                            "total_events": 0,
                            "unique_parents": 0,
                            "unique_records": 0,
                            "unique_visitors": 0,
                        },
                    },
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": (
                            "https://works.hcommons.org/records/rhk6r-p5d15/preview/test.pdf"
                        ),
                        "label": "",
                        "view": {
                            "total_events": 0,
                            "unique_parents": 0,
                            "unique_records": 0,
                            "unique_visitors": 0,
                        },
                    },
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": (
                            "https://works.hcommons.org/records/t8hjs-dzx03/preview/test.pdf"
                        ),
                        "label": "",
                        "view": {
                            "total_events": 0,
                            "unique_parents": 0,
                            "unique_records": 0,
                            "unique_visitors": 0,
                        },
                    },
                ],
                "by_resource_types": [
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": "textDocument-book",
                        "label": "Book",
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": "textDocument-journalArticle",
                        "label": "Journal " "Article",
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": "textDocument-thesis",
                        "label": "Thesis",
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                ],
                "by_subjects": [
                    {
                        "download": {
                            "total_events": 2,
                            "total_volume": 2048.0,
                            "unique_files": 2,
                            "unique_parents": 2,
                            "unique_records": 2,
                            "unique_visitors": 2,
                        },
                        "id": "http://id.worldcat.org/fast/1012163",
                        "label": "Mathematics",
                        "view": {
                            "total_events": 2,
                            "unique_parents": 2,
                            "unique_records": 2,
                            "unique_visitors": 2,
                        },
                    },
                    {
                        "download": {
                            "total_events": 2,
                            "total_volume": 2048.0,
                            "unique_files": 2,
                            "unique_parents": 2,
                            "unique_records": 2,
                            "unique_visitors": 2,
                        },
                        "id": "http://id.worldcat.org/fast/958235",
                        "label": "History",
                        "view": {
                            "total_events": 2,
                            "unique_parents": 2,
                            "unique_records": 2,
                            "unique_visitors": 2,
                        },
                    },
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": "http://id.worldcat.org/fast/1012213",
                        "label": "Mathematics--Philosophy",
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": "http://id.worldcat.org/fast/1108176",
                        "label": "Science",
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": "http://id.worldcat.org/fast/1108387",
                        "label": "Science--Study " "and teaching",
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": "http://id.worldcat.org/fast/1145221",
                        "label": "Technology--Study " "and teaching",
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                    {
                        "download": {
                            "total_events": 1,
                            "total_volume": 1024.0,
                            "unique_files": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                        "id": "http://id.worldcat.org/fast/902116",
                        "label": "Economics",
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                ],
            },
            "timestamp": "2025-07-03T19:37:11",
            "totals": {
                "download": {
                    "total_events": 3,
                    "total_volume": 3072.0,
                    "unique_files": 3,
                    "unique_parents": 3,
                    "unique_records": 3,
                    "unique_visitors": 3,
                },
                "view": {
                    "total_events": 3,
                    "unique_parents": 3,
                    "unique_records": 3,
                    "unique_visitors": 3,
                },
            },
        },
        {
            "community_id": "59e77d51-3758-409a-813f-efc0d2db1a5e",
            "period_end": "2025-06-06T23:59:59",
            "period_start": "2025-06-06T00:00:00",
            "subcounts": {
                "by_access_status": [],
                "by_affiliations": [],
                "by_countries": [],
                "by_file_types": [],
                "by_funders": [],
                "by_languages": [],
                "by_licenses": [],
                "by_periodicals": [],
                "by_publishers": [],
                "by_referrers": [],
                "by_resource_types": [],
                "by_subjects": [],
            },
            "timestamp": "2025-07-03T19:37:11",
            "totals": {
                "download": {
                    "total_events": 0,
                    "total_volume": 0.0,
                    "unique_files": 0,
                    "unique_parents": 0,
                    "unique_records": 0,
                    "unique_visitors": 0,
                },
                "view": {
                    "total_events": 0,
                    "unique_parents": 0,
                    "unique_records": 0,
                    "unique_visitors": 0,
                },
            },
        },
        {
            "community_id": "59e77d51-3758-409a-813f-efc0d2db1a5e",
            "period_end": "2025-06-07T23:59:59",
            "period_start": "2025-06-07T00:00:00",
            "subcounts": {
                "by_access_status": [],
                "by_affiliations": [],
                "by_countries": [],
                "by_file_types": [],
                "by_funders": [],
                "by_languages": [],
                "by_licenses": [],
                "by_periodicals": [],
                "by_publishers": [],
                "by_referrers": [],
                "by_resource_types": [],
                "by_subjects": [],
            },
            "timestamp": "2025-07-03T19:37:11",
            "totals": {
                "download": {
                    "total_events": 0,
                    "total_volume": 0.0,
                    "unique_files": 0,
                    "unique_parents": 0,
                    "unique_records": 0,
                    "unique_visitors": 0,
                },
                "view": {
                    "total_events": 0,
                    "unique_parents": 0,
                    "unique_records": 0,
                    "unique_visitors": 0,
                },
            },
        },
        {
            "community_id": "59e77d51-3758-409a-813f-efc0d2db1a5e",
            "period_end": "2025-06-08T23:59:59",
            "period_start": "2025-06-08T00:00:00",
            "subcounts": {
                "by_access_status": [],
                "by_affiliations": [],
                "by_countries": [],
                "by_file_types": [],
                "by_funders": [],
                "by_languages": [],
                "by_licenses": [],
                "by_periodicals": [],
                "by_publishers": [],
                "by_referrers": [],
                "by_resource_types": [],
                "by_subjects": [],
            },
            "timestamp": "2025-07-03T19:37:11",
            "totals": {
                "download": {
                    "total_events": 0,
                    "total_volume": 0.0,
                    "unique_files": 0,
                    "unique_parents": 0,
                    "unique_records": 0,
                    "unique_visitors": 0,
                },
                "view": {
                    "total_events": 0,
                    "unique_parents": 0,
                    "unique_records": 0,
                    "unique_visitors": 0,
                },
            },
        },
        {
            "community_id": "59e77d51-3758-409a-813f-efc0d2db1a5e",
            "period_end": "2025-06-09T23:59:59",
            "period_start": "2025-06-09T00:00:00",
            "subcounts": {
                "by_access_status": [],
                "by_affiliations": [],
                "by_countries": [],
                "by_file_types": [],
                "by_funders": [],
                "by_languages": [],
                "by_licenses": [],
                "by_periodicals": [],
                "by_publishers": [],
                "by_referrers": [],
                "by_resource_types": [],
                "by_subjects": [],
            },
            "timestamp": "2025-07-03T19:37:11",
            "totals": {
                "download": {
                    "total_events": 0,
                    "total_volume": 0.0,
                    "unique_files": 0,
                    "unique_parents": 0,
                    "unique_records": 0,
                    "unique_visitors": 0,
                },
                "view": {
                    "total_events": 0,
                    "unique_parents": 0,
                    "unique_records": 0,
                    "unique_visitors": 0,
                },
            },
        },
        {
            "community_id": "59e77d51-3758-409a-813f-efc0d2db1a5e",
            "period_end": "2025-06-10T23:59:59",
            "period_start": "2025-06-10T00:00:00",
            "subcounts": {
                "by_access_status": [],
                "by_affiliations": [],
                "by_countries": [],
                "by_file_types": [],
                "by_funders": [],
                "by_languages": [],
                "by_licenses": [],
                "by_periodicals": [],
                "by_publishers": [],
                "by_referrers": [],
                "by_resource_types": [],
                "by_subjects": [],
            },
            "timestamp": "2025-07-03T19:37:11",
            "totals": {
                "download": {
                    "total_events": 0,
                    "total_volume": 0.0,
                    "unique_files": 0,
                    "unique_parents": 0,
                    "unique_records": 0,
                    "unique_visitors": 0,
                },
                "view": {
                    "total_events": 0,
                    "unique_parents": 0,
                    "unique_records": 0,
                    "unique_visitors": 0,
                },
            },
        },
        {
            "community_id": "59e77d51-3758-409a-813f-efc0d2db1a5e",
            "period_end": "2025-06-11T23:59:59",
            "period_start": "2025-06-11T00:00:00",
            "subcounts": {
                "by_access_status": [],
                "by_affiliations": [],
                "by_countries": [],
                "by_file_types": [],
                "by_funders": [],
                "by_languages": [],
                "by_licenses": [],
                "by_periodicals": [],
                "by_publishers": [],
                "by_referrers": [],
                "by_resource_types": [],
                "by_subjects": [],
            },
            "timestamp": "2025-07-03T19:37:11",
            "totals": {
                "download": {
                    "total_events": 0,
                    "total_volume": 0.0,
                    "unique_files": 0,
                    "unique_parents": 0,
                    "unique_records": 0,
                    "unique_visitors": 0,
                },
                "view": {
                    "total_events": 0,
                    "unique_parents": 0,
                    "unique_records": 0,
                    "unique_visitors": 0,
                },
            },
        },
    ]
}

SAMPLE_RDMRECORDS_RECORDS_HIT = {
    "_index": "kcworks-rdmrecords-records-record-v6.0.0-1725995542",
    "_id": "f5faa3d6-1eb2-4bd7-8d6a-d7a5e9b510ee",
    "_score": 0,
    "_source": {
        "is_published": True,
        "parent": {
            "id": "62z0v-bdm10",
            "pid": {
                "pk": 2022364,
                "status": "R",
                "obj_type": "rec",
                "pid_type": "recid",
            },
            "pids": {
                "doi": {
                    "client": "datacite",
                    "provider": "datacite",
                    "identifier": "10.17613/62z0v-bdm10",
                }
            },
            "access": {
                "links": [],
                "grants": [],
                "owned_by": {"user": 6},
                "settings": {
                    "allow_user_requests": False,
                    "allow_guest_requests": False,
                    "accept_conditions_text": None,
                    "secret_link_expiration": 0,
                },
                "grant_tokens": [],
            },
            "$schema": "local://records/parent-v3.0.0.json",
            "communities": {
                "default": "3837b953-c66d-45a6-9b49-56e31f52bdca",
                "ids": ["3837b953-c66d-45a6-9b49-56e31f52bdca"],
                "entries": [
                    {
                        "@v": "3837b953-c66d-45a6-9b49-56e31f52bdca::4",
                        "uuid": "3837b953-c66d-45a6-9b49-56e31f52bdca",
                        "created": "2024-07-16T20:40:25.616706+00:00",
                        "updated": "2024-07-20T21:12:00.670892+00:00",
                        "id": "3837b953-c66d-45a6-9b49-56e31f52bdca",
                        "slug": "ajs",
                        "is_verified": False,
                        "version_id": 5,
                        "metadata": {
                            "title": "AJS Commons",
                            "organizations": [{"name": "AJS Commons"}],
                        },
                    }
                ],
            },
            "uuid": "2e8e36cd-5f61-4edb-aac3-c856cc4787d7",
            "version_id": 9,
            "created": "2024-07-16T22:06:30.700599+00:00",
            "updated": "2024-07-16T22:06:32.008823+00:00",
            "is_verified": True,
        },
        "versions": {
            "latest_id": "f5faa3d6-1eb2-4bd7-8d6a-d7a5e9b510ee",
            "latest_index": 1,
            "next_draft_id": None,
            "is_latest": True,
            "is_latest_draft": True,
            "index": 1,
        },
        "has_draft": False,
        "is_deleted": False,
        "deletion_status": "P",
        "id": "p54cc-4r743",
        "pid": {"pk": 2022365, "status": "R", "obj_type": "rec", "pid_type": "recid"},
        "pids": {
            "doi": {
                "client": "datacite",
                "provider": "datacite",
                "identifier": "10.17613/M66246",
            },
            "oai": {
                "provider": "oai",
                "identifier": "oai:invenio-dev.hcommons-staging.org:p54cc-4r743",
            },
        },
        "files": {
            "enabled": True,
            "count": 1,
            "mimetypes": ["application/pdf"],
            "totalbytes": 55242,
            "types": ["pdf"],
            "entries": [
                {
                    "uuid": "7e1b1cd1-33d8-4e75-9c95-a3ff862bffb4",
                    "version_id": 3,
                    "metadata": {},
                    "key": "un-discussion-papers-series-gilbert.pdf",
                    "checksum": "md5:d031c90b0e74a2b778805b533bd37f11",
                    "mimetype": "application/pdf",
                    "size": 55242,
                    "ext": "pdf",
                    "object_version_id": "71236f35-e36f-4105-abd7-e2506709d4d7",
                    "file_id": "6ff119bd-237a-4b68-b4a3-2eb4954cf13b",
                }
            ],
        },
        "access": {
            "files": "public",
            "record": "public",
            "embargo": {"until": None, "active": False, "reason": None},
            "status": "open",
        },
        "$schema": "local://records/record-v6.0.0.json",
        "metadata": {
            "title": "Music and the Holocaust",
            "rights": [
                {
                    "id": "arr",
                    "title": {"en": "All Rights Reserved"},
                    "description": {
                        "en": (
                            "Proprietary material. No permissions are granted for "
                            "any kind of copyring or re-use. All rights reserved"
                        )
                    },
                    "icon": "copyright",
                    "props": {
                        "url": "https://en.wikipedia.org/wiki/All_rights_reserved"
                    },
                    "@v": "2bf0a811-9be2-4510-ac80-4d8da2e2aee3::1",
                }
            ],
            "creators": [
                {
                    "role": {
                        "id": "author",
                        "title": {"en": "Author"},
                        "@v": "e2c3ccd5-5282-465b-9351-9244c13e572f::1",
                    },
                    "person_or_org": {
                        "name": "Gilbert, Shirli",
                        "type": "personal",
                        "given_name": "Shirli",
                        "family_name": "Gilbert",
                        "identifiers": [
                            {"scheme": "hc_username", "identifier": "sgilbert"}
                        ],
                    },
                }
            ],
            "subjects": [
                {
                    "id": "http://id.worldcat.org/fast/1030269",
                    "subject": "Music",
                    "scheme": "FAST-topical",
                    "@v": "43304c98-6686-444d-bf64-ba642d64bc77::1",
                },
                {
                    "id": "http://id.worldcat.org/fast/958866",
                    "subject": "Jewish Holocaust (1939-1945)",
                    "scheme": "FAST-event",
                    "@v": "3a5bc417-7fe2-43b1-b91f-1d74134831ed::1",
                },
                {
                    "id": "http://id.worldcat.org/fast/983364",
                    "subject": "Jews--Social life and customs",
                    "scheme": "FAST-topical",
                    "@v": "55f11b09-c892-435a-833d-f9c5b886e704::1",
                },
            ],
            "languages": [
                {
                    "id": "eng",
                    "title": {"en": "English"},
                    "@v": "aba9e894-8176-4ffa-99d9-ae7ecd7204df::1",
                }
            ],
            "publisher": "United Nations",
            "description": (
                "Text of address to the Holocaust and the United Nations "
                "Outreach Programme, April 2014."
            ),
            "identifiers": [
                {"scheme": "hclegacy-pid", "identifier": "hc:16685"},
                {"scheme": "hclegacy-record-id", "identifier": "1000361-334"},
                {
                    "scheme": "url",
                    "identifier": (
                        "http://www.un.org/en/holocaustremembrance/docs/paper26.shtml"
                    ),
                },
            ],
            "resource_type": {
                "id": "textDocument-journalArticle",
                "title": {"de": "Zeitschriftenartikel", "en": "Journal article"},
                "props": {
                    "type": "textDocument",
                    "subtype": "textDocument-journalArticle",
                },
                "@v": "58316e5b-9772-4f99-b138-c285082883a4::1",
            },
            "publication_date": "2014",
            "publication_date_range": {"gte": "2014-01-01", "lte": "2014-12-31"},
            "combined_subjects": [
                "FAST-topical::Music",
                "FAST-event::Jewish Holocaust (1939-1945)",
                "FAST-topical::Jews--Social life and customs",
            ],
        },
        "media_files": {"enabled": False},
        "custom_fields": {
            "hclegacy:file_pid": "hc:16686",
            "kcr:commons_domain": "ajs.hcommons.org",
            "hclegacy:collection": "hccollection:1",
            "kcr:submitter_email": "s.gilbert@soton.ac.uk",
            "hclegacy:total_views": 27,
            "hclegacy:submitter_id": "1011824",
            "kcr:user_defined_tags": ["Holocaust studies", "Jewish culture"],
            "hclegacy:file_location": (
                "/srv/www/commons/current/web/app/uploads/humcore/2017/12/"
                "o_1c098flonrab6j24fg16go1kqa7.pdf.un-discussion-papers-series"
                "-gilbert.pdf"
            ),
            "kcr:submitter_username": "sgilbert",
            "hclegacy:total_downloads": 29,
            "hclegacy:publication_type": "online-publication",
            "hclegacy:record_change_date": "2017-12-01T14:43:05Z",
            "hclegacy:previously_published": "published",
            "hclegacy:record_creation_date": "2017-12-01T14:43:05Z",
            "hclegacy:submitter_org_memberships": ["ajs", "hc"],
        },
        "uuid": "f5faa3d6-1eb2-4bd7-8d6a-d7a5e9b510ee",
        "version_id": 5,
        "created": "2024-07-16T22:06:31.528686+00:00",
        "updated": "2024-07-16T22:06:31.649437+00:00",
        "stats": {
            "this_version": {
                "views": 63,
                "unique_views": 62,
                "downloads": 32,
                "unique_downloads": 32,
                "data_volume": 1767744.0,
            },
            "all_versions": {
                "views": 63,
                "unique_views": 62,
                "downloads": 32,
                "unique_downloads": 32,
                "data_volume": 1767744.0,
            },
        },
    },
}

SAMPLE_EVENTS_STATS_RECORD_VIEW_HIT = {
    "_index": "kcworks-events-stats-record-view-2019-01",
    "_id": "2019-01-01T00:00:00-e84350bffaba52f09db1778b0aea50f417a004b6",
    "_score": 1,
    "_source": {
        "timestamp": "2019-01-01T00:00:00",
        "recid": "018ej-fdg48",
        "parent_recid": "27h8t-jtn14",
        "unique_id": "ui_018ej-fdg48",
        "is_robot": False,
        "country": "imported",
        "via_api": False,
        "unique_session_id": "ffacc0330577cdd0117e546b8492967cabcd4191413c3935c5d3cd37",
        "visitor_id": "7bfc797a4dcc7746f3f355cf92e312e222e1d86ecc574a301210d29a",
        "updated_timestamp": "2024-09-19T15:36:23.364823",
    },
}

SAMPLE_EVENTS_STATS_FILE_DOWNLOAD_HIT = {
    "_index": "kcworks-events-stats-file-download-2025-05",
    "_id": "2025-05-30T01:25:30-3e5907bfe89ce0a18086ea86af268f77d52fdd06",
    "_score": 1,
    "_source": {
        "timestamp": "2025-05-30T01:25:31",
        "bucket_id": "90e91a01-d336-44b2-b21d-349f0002e310",
        "file_id": "09aef148-780c-4d3b-b3ea-596228473019",
        "file_key": "undertaken-in-company.pdf",
        "size": 220417,
        "recid": "aj52y-eha16",
        "parent_recid": "3v4a1-qn507",
        "referrer": (
            "https://works.hcommons.org/records/aj52y-eha16/preview/"
            "undertaken-in-company.pdf?include_deleted=0?"
        ),
        "via_api": False,
        "is_robot": False,
        "country": None,
        "visitor_id": "136efa375fa5405c88bfa55fee84c88df111f74d0670e7db7d848ab5",
        "unique_session_id": "7967fb65501da73dc4f038e716be6d3e5acc34c0adf4fbe4e4ee317c",
        "unique_id": (
            "90e91a01-d336-44b2-b21d-349f0002e310_09aef148-780c-4d3b-b3ea-596228473019"
        ),
        "updated_timestamp": "2025-05-30T01:55:00.653624",
    },
}
