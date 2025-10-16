# Part of the Invenio-Stats-Dashboard extension for InvenioRDM
# Copyright (C) 2025 Mesh Research
#
# Invenio-Stats-Dashboard is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Sample record snapshot docs."""

MOCK_RECORD_SNAPSHOT_DOCS = [
    {
        "_id": "global-2025-08-27",
        "_index": "stats-community-records-snapshot-created-2025",
        "_score": 1.0,
        "_source": {
            "community_id": "global",
            "snapshot_date": "2025-08-27",
            "total_records": {
                "metadata_only": 1,
                "with_files": 1,
            },
            "total_parents": {
                "metadata_only": 1,
                "with_files": 1,
            },
            "total_files": {
                "file_count": 1,
                "data_volume": 1984949.0,
            },
            "total_uploaders": 1,
            "subcounts": {
                "access_statuses": [
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "metadata-only",
                        "label": "",
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                    {
                        "files": {"data_volume": 1984949.0, "file_count": 1},
                        "id": "open",
                        "label": "",
                        "parents": {"metadata_only": 0, "with_files": 1},
                        "records": {"metadata_only": 0, "with_files": 1},
                    },
                ],
                "file_types": [
                    {
                        "files": {"data_volume": 1984949.0, "file_count": 1},
                        "id": "pdf",
                        "label": "",
                        "parents": {"metadata_only": 0, "with_files": 1},
                        "records": {"metadata_only": 0, "with_files": 1},
                    }
                ],
                "resource_types": [
                    {
                        "files": {"data_volume": 1984949.0, "file_count": 1},
                        "id": "textDocument-journalArticle",
                        "label": {"en": "Journal Article"},
                        "parents": {"metadata_only": 0, "with_files": 1},
                        "records": {"metadata_only": 0, "with_files": 1},
                    },
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "textDocument-book",
                        "label": {"en": "Book"},
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                ],
                "affiliations": [
                    {
                        "files": {"data_volume": 1984949.0, "file_count": 1},
                        "id": "03rmrcq20",
                        "label": "",
                        "parents": {"metadata_only": 0, "with_files": 1},
                        "records": {"metadata_only": 0, "with_files": 1},
                    },
                ],
                "funders": [
                    {
                        "files": {"data_volume": 1984949.0, "file_count": 1},
                        "id": "00k4n6c31",
                        "label": "",
                        "parents": {"metadata_only": 1, "with_files": 1},
                        "records": {"metadata_only": 1, "with_files": 1},
                    }
                ],
                "languages": [
                    {
                        "files": {"data_volume": 1984949.0, "file_count": 1},
                        "id": "eng",
                        "label": {"en": "English"},
                        "parents": {"metadata_only": 0, "with_files": 1},
                        "records": {"metadata_only": 0, "with_files": 1},
                    }
                ],
                "periodicals": [
                    {
                        "files": {"data_volume": 1984949.0, "file_count": 1},
                        "id": "N/A",
                        "label": "",
                        "parents": {"metadata_only": 0, "with_files": 1},
                        "records": {"metadata_only": 0, "with_files": 1},
                    }
                ],
                "publishers": [
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "UBC",
                        "label": "",
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                    {
                        "files": {"data_volume": 1984949.0, "file_count": 1},
                        "id": "Knowledge Commons",
                        "label": "",
                        "parents": {"metadata_only": 0, "with_files": 1},
                        "records": {"metadata_only": 0, "with_files": 1},
                    },
                ],
                "rights": [
                    {
                        "files": {"data_volume": 1984949.0, "file_count": 1},
                        "id": "cc-by-sa-4.0",
                        "label": {
                            "en": (
                                "Creative Commons "
                                "Attribution-ShareAlike "
                                "4.0 International"
                            )
                        },
                        "parents": {"metadata_only": 0, "with_files": 1},
                        "records": {"metadata_only": 0, "with_files": 1},
                    }
                ],
                "subjects": [
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "http://id.worldcat.org/fast/911979",
                        "label": "English language--Written English--History",
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "http://id.worldcat.org/fast/845111",
                        "label": "Canadian literature",
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "http://id.worldcat.org/fast/821870",
                        "label": "Authors, Canadian",
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "http://id.worldcat.org/fast/911328",
                        "label": "English language--Lexicography--History",
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "http://id.worldcat.org/fast/911660",
                        "label": "English language--Spoken English--Research",
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "http://id.worldcat.org/fast/845170",
                        "label": "Canadian periodicals",
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "http://id.worldcat.org/fast/845142",
                        "label": "Canadian literature--Periodicals",
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "http://id.worldcat.org/fast/817954",
                        "label": "Arts, Canadian",
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "http://id.worldcat.org/fast/1424786",
                        "label": "Canadian literature--Bibliography",
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "http://id.worldcat.org/fast/845184",
                        "label": "Canadian prose literature",
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "http://id.worldcat.org/fast/934875",
                        "label": "French-Canadian literature",
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                ],
            },
            "timestamp": "2025-09-01T17:21:38",
            "total_files": {"data_volume": 1984949.0, "file_count": 1},
            "total_parents": {"metadata_only": 1, "with_files": 1},
            "total_records": {"metadata_only": 1, "with_files": 1},
            "total_uploaders": 1,
            "updated_timestamp": "2025-09-01T17:21:38",
        },
    },
    {
        "_id": "3392b22f-0b0c-4727-b683-2da188c887e2-2025-08-24-zero",
        "_index": "stats-community-records-snapshot-created-2025",
        "_score": 1.0,
        "_source": {
            "community_id": "3392b22f-0b0c-4727-b683-2da188c887e2",
            "snapshot_date": "2025-08-25",
            "total_records": {
                "metadata_only": 0,
                "with_files": 0,
            },
            "total_parents": {
                "metadata_only": 0,
                "with_files": 0,
            },
            "total_files": {
                "file_count": 0,
                "data_volume": 0,
            },
            "total_uploaders": 0,
            "subcounts": {
                "access_statuses": [],
                "file_types": [],
                "resource_types": [],
                "affiliations": [],
                "funders": [],
                "languages": [],
                "periodicals": [],
                "publishers": [],
                "rights": [],
                "subjects": [],
            },
            "timestamp": "2025-08-29T23:44:23",
            "updated_timestamp": "2025-08-29T23:44:23",
        },
    },
    {
        "_id": "global-2025-08-31",
        "_index": "stats-community-records-snapshot-created-2025",
        "_score": 1.0,
        "_source": {
            "community_id": "global",
            "snapshot_date": "2025-08-31",
            "subcounts": {
                "access_statuses": [
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "metadata-only",
                        "label": "",
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                    {
                        "files": {"data_volume": 61102780.0, "file_count": 3},
                        "id": "open",
                        "label": "",
                        "parents": {"metadata_only": 0, "with_files": 3},
                        "records": {"metadata_only": 0, "with_files": 3},
                    },
                ],
                "file_types": [
                    {
                        "files": {"data_volume": 61102780.0, "file_count": 3},
                        "id": "pdf",
                        "label": "",
                        "parents": {"metadata_only": 0, "with_files": 3},
                        "records": {"metadata_only": 0, "with_files": 3},
                    }
                ],
                "resource_types": [
                    {
                        "files": {"data_volume": 2442985.0, "file_count": 2},
                        "id": "textDocument-journalArticle",
                        "label": {"en": "Journal Article"},
                        "parents": {"metadata_only": 0, "with_files": 2},
                        "records": {"metadata_only": 0, "with_files": 2},
                    },
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "textDocument-book",
                        "label": {"en": "Book"},
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                    {
                        "files": {"data_volume": 58659795.0, "file_count": 1},
                        "id": "textDocument-bookSection",
                        "label": {"en": "Book Section"},
                        "parents": {"metadata_only": 0, "with_files": 1},
                        "records": {"metadata_only": 0, "with_files": 1},
                    },
                ],
                "affiliations": [
                    {
                        "files": {"data_volume": 1984949.0, "file_count": 1},
                        "id": "03rmrcq20",
                        "label": "",
                        "parents": {"metadata_only": 0, "with_files": 1},
                        "records": {"metadata_only": 0, "with_files": 1},
                    },
                    {
                        "files": {"data_volume": 458036.0, "file_count": 1},
                        "id": "013v4ng57",
                        "label": "",
                        "parents": {"metadata_only": 0, "with_files": 1},
                        "records": {"metadata_only": 0, "with_files": 1},
                    },
                ],
                "funders": [
                    {
                        "files": {"data_volume": 1984949.0, "file_count": 1},
                        "id": "00k4n6c31",
                        "label": "",
                        "parents": {"metadata_only": 1, "with_files": 1},
                        "records": {"metadata_only": 1, "with_files": 1},
                    }
                ],
                "languages": [
                    {
                        "files": {"data_volume": 2442985.0, "file_count": 2},
                        "id": "eng",
                        "label": {"en": "English"},
                        "parents": {"metadata_only": 0, "with_files": 2},
                        "records": {"metadata_only": 0, "with_files": 2},
                    }
                ],
                "periodicals": [
                    {
                        "files": {"data_volume": 1984949.0, "file_count": 1},
                        "id": "N/A",
                        "label": "",
                        "parents": {"metadata_only": 0, "with_files": 1},
                        "records": {"metadata_only": 0, "with_files": 1},
                    }
                ],
                "publishers": [
                    {
                        "files": {"data_volume": 2442985.0, "file_count": 2},
                        "id": "Knowledge Commons",
                        "label": "",
                        "parents": {"metadata_only": 0, "with_files": 2},
                        "records": {"metadata_only": 0, "with_files": 2},
                    },
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "UBC",
                        "label": "",
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                    {
                        "files": {"data_volume": 58659795.0, "file_count": 1},
                        "id": "Apocryphile Press",
                        "label": "",
                        "parents": {"metadata_only": 0, "with_files": 1},
                        "records": {"metadata_only": 0, "with_files": 1},
                    },
                ],
                "rights": [
                    {
                        "files": {"data_volume": 1984949.0, "file_count": 1},
                        "id": "cc-by-sa-4.0",
                        "label": {
                            "en": (
                                "Creative Commons "
                                "Attribution-ShareAlike "
                                "4.0 International"
                            )
                        },
                        "parents": {"metadata_only": 0, "with_files": 1},
                        "records": {"metadata_only": 0, "with_files": 1},
                    }
                ],
                "subjects": [
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "http://id.worldcat.org/fast/911979",
                        "label": "English language--Written English--History",
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "http://id.worldcat.org/fast/845111",
                        "label": "Canadian literature",
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "http://id.worldcat.org/fast/821870",
                        "label": "Authors, Canadian",
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "http://id.worldcat.org/fast/911328",
                        "label": "English language--Lexicography--History",
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "http://id.worldcat.org/fast/911660",
                        "label": "English language--Spoken English--Research",
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "http://id.worldcat.org/fast/845170",
                        "label": "Canadian periodicals",
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "http://id.worldcat.org/fast/845142",
                        "label": "Canadian literature--Periodicals",
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "http://id.worldcat.org/fast/817954",
                        "label": "Arts, Canadian",
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "http://id.worldcat.org/fast/1424786",
                        "label": "Canadian literature--Bibliography",
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "http://id.worldcat.org/fast/845184",
                        "label": "Canadian prose literature",
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                    {
                        "files": {"data_volume": 458036.0, "file_count": 1},
                        "id": "http://id.worldcat.org/fast/997987",
                        "label": "Library science literature",
                        "parents": {"metadata_only": 0, "with_files": 1},
                        "records": {"metadata_only": 0, "with_files": 1},
                    },
                    {
                        "files": {"data_volume": 458036.0, "file_count": 1},
                        "id": "http://id.worldcat.org/fast/995415",
                        "label": "Legal assistance to prisoners--U.S. states",
                        "parents": {"metadata_only": 0, "with_files": 1},
                        "records": {"metadata_only": 0, "with_files": 1},
                    },
                    {
                        "files": {"data_volume": 458036.0, "file_count": 1},
                        "id": "http://id.worldcat.org/fast/997974",
                        "label": "Library science--Standards",
                        "parents": {"metadata_only": 0, "with_files": 1},
                        "records": {"metadata_only": 0, "with_files": 1},
                    },
                    {
                        "files": {"data_volume": 458036.0, "file_count": 1},
                        "id": "http://id.worldcat.org/fast/997916",
                        "label": "Library science",
                        "parents": {"metadata_only": 0, "with_files": 1},
                        "records": {"metadata_only": 0, "with_files": 1},
                    },
                    {
                        "files": {"data_volume": 458036.0, "file_count": 1},
                        "id": "http://id.worldcat.org/fast/2060143",
                        "label": "Mass incarceration",
                        "parents": {"metadata_only": 0, "with_files": 1},
                        "records": {"metadata_only": 0, "with_files": 1},
                    },
                    {
                        "files": {"data_volume": 58659795.0, "file_count": 1},
                        "id": "http://id.worldcat.org/fast/973589",
                        "label": "Inklings (Group of writers)",
                        "parents": {"metadata_only": 0, "with_files": 1},
                        "records": {"metadata_only": 0, "with_files": 1},
                    },
                    {
                        "files": {"data_volume": 458036.0, "file_count": 1},
                        "id": "http://id.worldcat.org/fast/855500",
                        "label": "Children of prisoners--Services for",
                        "parents": {"metadata_only": 0, "with_files": 1},
                        "records": {"metadata_only": 0, "with_files": 1},
                    },
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "http://id.worldcat.org/fast/934875",
                        "label": "French-Canadian literature",
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                ],
            },
            "timestamp": "2025-09-01T17:21:38",
            "total_files": {"data_volume": 61102780.0, "file_count": 3},
            "total_parents": {"metadata_only": 1, "with_files": 3},
            "total_records": {"metadata_only": 1, "with_files": 3},
            "total_uploaders": 2,
            "updated_timestamp": "2025-09-01T17:21:38",
        },
    },
    {
        "_id": "global-2025-09-01",
        "_index": "stats-community-records-snapshot-created-2025",
        "_score": 1.0,
        "_source": {
            "community_id": "global",
            "snapshot_date": "2025-09-01",
            "total_records": {
                "metadata_only": 1,
                "with_files": 2,
            },
            "total_parents": {
                "metadata_only": 1,
                "with_files": 2,
            },
            "total_files": {
                "file_count": 2,
                "data_volume": 2442985.0,
            },
            "total_uploaders": 2,
            "subcounts": {
                "access_statuses": [
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "metadata-only",
                        "label": "",
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                    {
                        "files": {"data_volume": 2442985.0, "file_count": 2},
                        "id": "open",
                        "label": "",
                        "parents": {"metadata_only": 0, "with_files": 2},
                        "records": {"metadata_only": 0, "with_files": 2},
                    },
                ],
                "file_types": [
                    {
                        "files": {"data_volume": 2442985.0, "file_count": 2},
                        "id": "pdf",
                        "label": "",
                        "parents": {"metadata_only": 0, "with_files": 2},
                        "records": {"metadata_only": 0, "with_files": 2},
                    }
                ],
                "resource_types": [
                    {
                        "files": {"data_volume": 2442985.0, "file_count": 2},
                        "id": "textDocument-journalArticle",
                        "label": {"en": "Journal Article"},
                        "parents": {"metadata_only": 0, "with_files": 2},
                        "records": {"metadata_only": 0, "with_files": 2},
                    },
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "textDocument-book",
                        "label": {"en": "Book"},
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "textDocument-bookSection",
                        "label": {"en": "Book Section"},
                        "parents": {"metadata_only": 0, "with_files": 0},
                        "records": {"metadata_only": 0, "with_files": 0},
                    },
                ],
                "affiliations": [
                    {
                        "files": {"data_volume": 1984949.0, "file_count": 1},
                        "id": "03rmrcq20",
                        "label": "",
                        "parents": {"metadata_only": 0, "with_files": 1},
                        "records": {"metadata_only": 0, "with_files": 1},
                    },
                    {
                        "files": {"data_volume": 458036.0, "file_count": 1},
                        "id": "013v4ng57",
                        "label": "",
                        "parents": {"metadata_only": 0, "with_files": 1},
                        "records": {"metadata_only": 0, "with_files": 1},
                    },
                ],
                "funders": [
                    {
                        "files": {"data_volume": 1984949.0, "file_count": 1},
                        "id": "00k4n6c31",
                        "label": "",
                        "parents": {"metadata_only": 1, "with_files": 1},
                        "records": {"metadata_only": 1, "with_files": 1},
                    }
                ],
                "languages": [
                    {
                        "files": {"data_volume": 2442985.0, "file_count": 2},
                        "id": "eng",
                        "label": {"en": "English"},
                        "parents": {"metadata_only": 0, "with_files": 2},
                        "records": {"metadata_only": 0, "with_files": 2},
                    }
                ],
                "periodicals": [
                    {
                        "files": {"data_volume": 1984949.0, "file_count": 1},
                        "id": "N/A",
                        "label": "",
                        "parents": {"metadata_only": 0, "with_files": 1},
                        "records": {"metadata_only": 0, "with_files": 1},
                    }
                ],
                "publishers": [
                    {
                        "files": {"data_volume": 2442985.0, "file_count": 2},
                        "id": "Knowledge Commons",
                        "label": "",
                        "parents": {"metadata_only": 0, "with_files": 2},
                        "records": {"metadata_only": 0, "with_files": 2},
                    },
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "UBC",
                        "label": "",
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                ],
                "rights": [
                    {
                        "files": {"data_volume": 1984949.0, "file_count": 1},
                        "id": "cc-by-sa-4.0",
                        "label": {
                            "en": (
                                "Creative Commons "
                                "Attribution-ShareAlike "
                                "4.0 International"
                            )
                        },
                        "parents": {"metadata_only": 0, "with_files": 1},
                        "records": {"metadata_only": 0, "with_files": 1},
                    }
                ],
                "subjects": [
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "http://id.worldcat.org/fast/911979",
                        "label": "English language--Written English--History",
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "http://id.worldcat.org/fast/845111",
                        "label": "Canadian literature",
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "http://id.worldcat.org/fast/821870",
                        "label": "Authors, Canadian",
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "http://id.worldcat.org/fast/911328",
                        "label": "English language--Lexicography--History",
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "http://id.worldcat.org/fast/911660",
                        "label": "English language--Spoken English--Research",
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "http://id.worldcat.org/fast/845170",
                        "label": "Canadian periodicals",
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "http://id.worldcat.org/fast/845142",
                        "label": "Canadian literature--Periodicals",
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "http://id.worldcat.org/fast/817954",
                        "label": "Arts, Canadian",
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "http://id.worldcat.org/fast/1424786",
                        "label": "Canadian literature--Bibliography",
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "http://id.worldcat.org/fast/845184",
                        "label": "Canadian prose literature",
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                    {
                        "files": {"data_volume": 458036.0, "file_count": 1},
                        "id": "http://id.worldcat.org/fast/997987",
                        "label": "Library science literature",
                        "parents": {"metadata_only": 0, "with_files": 1},
                        "records": {"metadata_only": 0, "with_files": 1},
                    },
                    {
                        "files": {"data_volume": 458036.0, "file_count": 1},
                        "id": "http://id.worldcat.org/fast/995415",
                        "label": "Legal assistance to prisoners--U.S. states",
                        "parents": {"metadata_only": 0, "with_files": 1},
                        "records": {"metadata_only": 0, "with_files": 1},
                    },
                    {
                        "files": {"data_volume": 458036.0, "file_count": 1},
                        "id": "http://id.worldcat.org/fast/997974",
                        "label": "Library science--Standards",
                        "parents": {"metadata_only": 0, "with_files": 1},
                        "records": {"metadata_only": 0, "with_files": 1},
                    },
                    {
                        "files": {"data_volume": 458036.0, "file_count": 1},
                        "id": "http://id.worldcat.org/fast/997916",
                        "label": "Library science",
                        "parents": {"metadata_only": 0, "with_files": 1},
                        "records": {"metadata_only": 0, "with_files": 1},
                    },
                    {
                        "files": {"data_volume": 458036.0, "file_count": 1},
                        "id": "http://id.worldcat.org/fast/2060143",
                        "label": "Mass incarceration",
                        "parents": {"metadata_only": 0, "with_files": 1},
                        "records": {"metadata_only": 0, "with_files": 1},
                    },
                    {
                        "files": {"data_volume": 458036.0, "file_count": 1},
                        "id": "http://id.worldcat.org/fast/855500",
                        "label": "Children of prisoners--Services for",
                        "parents": {"metadata_only": 0, "with_files": 1},
                        "records": {"metadata_only": 0, "with_files": 1},
                    },
                    {
                        "files": {"data_volume": 0.0, "file_count": 0},
                        "id": "http://id.worldcat.org/fast/934875",
                        "label": "French-Canadian literature",
                        "parents": {"metadata_only": 1, "with_files": 0},
                        "records": {"metadata_only": 1, "with_files": 0},
                    },
                ],
            },
            "timestamp": "2025-09-01T17:21:38",
            "updated_timestamp": "2025-09-01T17:21:38",
        },
    },
]
