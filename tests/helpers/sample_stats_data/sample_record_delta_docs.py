# Part of the Invenio-Stats-Dashboard extension for InvenioRDM
# Copyright (C) 2025 Mesh Research
#
# Invenio-Stats-Dashboard is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Sample record delta docs."""

MOCK_RECORD_DELTA_DOCS = [
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
            "uploaders": 1,
            "subcounts": {
                "access_statuses": [
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
                "affiliations": [
                    {
                        "files": {
                            "added": {"data_volume": 458036.0, "file_count": 1},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "03rmrcq20",
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
                    },
                ],
                "file_types": [
                    {
                        "files": {
                            "added": {"data_volume": 59117831.0, "file_count": 2},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "pdf",
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
                "funders": [],
                "languages": [
                    {
                        "files": {
                            "added": {"data_volume": 458036.0, "file_count": 1},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "eng",
                        "label": {"en": "English"},
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
                "rights": [],
                "periodicals": [],
                "publishers": [
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
                "resource_types": [
                    {
                        "files": {
                            "added": {"data_volume": 58659795.0, "file_count": 1},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "textDocument-bookSection",
                        "label": {"en": "Book Section"},
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
                        "label": {"en": "Journal Article"},
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
                "subjects": [
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
                "access_statuses": [],
                "affiliations": [],
                "file_types": [],
                "funders": [],
                "languages": [],
                "rights": [],
                "periodicals": [],
                "publishers": [],
                "resource_types": [],
                "subjects": [],
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
                "access_statuses": [],
                "affiliations": [],
                "file_types": [],
                "funders": [],
                "languages": [],
                "rights": [],
                "periodicals": [],
                "publishers": [],
                "resource_types": [],
                "subjects": [],
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
                "access_statuses": [],
                "affiliations": [],
                "file_types": [],
                "funders": [],
                "languages": [],
                "rights": [],
                "periodicals": [],
                "publishers": [],
                "resource_types": [],
                "subjects": [],
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
                "access_statuses": [
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
                "affiliations": [
                    {
                        "files": {
                            "added": {"data_volume": 1984949.0, "file_count": 1},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "03rmrcq20",
                        "label": "",
                        "parents": {
                            "added": {"metadata_only": 1, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 1, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    }
                ],
                "file_types": [
                    {
                        "files": {
                            "added": {"data_volume": 1984949.0, "file_count": 1},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "pdf",
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
                "funders": [
                    {
                        "files": {
                            "added": {"data_volume": 1984949.0, "file_count": 1},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "00k4n6c31",
                        "label": "",
                        "parents": {
                            "added": {"metadata_only": 1, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 1, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    }
                ],
                "languages": [
                    {
                        "files": {
                            "added": {"data_volume": 1984949.0, "file_count": 1},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "eng",
                        "label": {"en": "English"},
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
                "rights": [
                    {
                        "files": {
                            "added": {"data_volume": 1984949.0, "file_count": 1},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "cc-by-sa-4.0",
                        "label": {
                            "en": (
                                "Creative Commons Attribution-ShareAlike 4.0"
                                " International"
                            )
                        },
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
                "periodicals": [
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
                "publishers": [
                    {
                        "files": {
                            "added": {"data_volume": 1984949.0, "file_count": 1},
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
                "resource_types": [
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "textDocument-book",
                        "label": {"en": "Book"},
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
                        "label": {"en": "Journal Article"},
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
                "subjects": [
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
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 0.0, "file_count": 0},
                        },
                        "id": "http://id.worldcat.org/fast/934875",
                        "label": "French-Canadian literature",
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
                "access_statuses": [
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
                "affiliations": [
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 1984949.0, "file_count": 1},
                        },
                        "id": "03rmrcq20",
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
                "file_types": [
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 1984949.0, "file_count": 1},
                        },
                        "id": "pdf",
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
                "funders": [
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 1984949.0, "file_count": 1},
                        },
                        "id": "00k4n6c31",
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
                "languages": [
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 1984949.0, "file_count": 1},
                        },
                        "id": "eng",
                        "label": {"en": "English"},
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
                "rights": [
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 1984949.0, "file_count": 1},
                        },
                        "id": "cc-by-sa-4.0",
                        "label": {
                            "en": (
                                "Creative Commons Attribution-ShareAlike 4.0"
                                " International"
                            )
                        },
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
                "periodicals": [
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
                "publishers": [
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 1984949.0, "file_count": 1},
                        },
                        "id": "Knowledge Commons",
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
                "resource_types": [
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 1984949.0, "file_count": 1},
                        },
                        "id": "textDocument-journalArticle",
                        "label": {"en": "Journal Article"},
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
                "subjects": [],
            },
            "timestamp": "2025-06-10T00:45:10",
            "updated_timestamp": "2025-06-10T00:45:10",
            "uploaders": 0,
        },
    },
]

MOCK_RECORD_DELTA_DOCS_2 = [
    {
        "period_start": "2025-05-30T00:00:00",
        "records": {
            "added": {"metadata_only": 0, "with_files": 2},
            "removed": {"metadata_only": 0, "with_files": 0},
        },
        "parents": {
            "added": {"metadata_only": 0, "with_files": 2},
            "removed": {"metadata_only": 0, "with_files": 0},
        },
        "uploaders": 1,
        "files": {
            "added": {"data_volume": 59117831.0, "file_count": 2},
            "removed": {"data_volume": 0.0, "file_count": 0},
        },
        "subcounts": {
            "access_statuses": [
                {
                    "id": "open",
                    "label": "",
                    "records": {
                        "added": {"metadata_only": 0, "with_files": 2},
                        "removed": {"metadata_only": 0, "with_files": 0},
                    },
                    "parents": {
                        "added": {"metadata_only": 0, "with_files": 2},
                        "removed": {"metadata_only": 0, "with_files": 0},
                    },
                    "files": {
                        "added": {"data_volume": 59117831.0, "file_count": 2},
                        "removed": {"data_volume": 0.0, "file_count": 0},
                    },
                }
            ],
            "resource_types": [
                {
                    "id": "textDocument-journalArticle",
                    "label": {"en": "Journal Article"},
                    "records": {
                        "added": {"metadata_only": 0, "with_files": 1},
                        "removed": {"metadata_only": 0, "with_files": 0},
                    },
                    "parents": {
                        "added": {"metadata_only": 0, "with_files": 1},
                        "removed": {"metadata_only": 0, "with_files": 0},
                    },
                    "files": {
                        "added": {"data_volume": 29558915.5, "file_count": 1},
                        "removed": {"data_volume": 0.0, "file_count": 0},
                    },
                }
            ],
            "languages": [
                {
                    "id": "eng",
                    "label": {"en": "English"},
                    "records": {
                        "added": {"metadata_only": 0, "with_files": 2},
                        "removed": {"metadata_only": 0, "with_files": 0},
                    },
                    "parents": {
                        "added": {"metadata_only": 0, "with_files": 2},
                        "removed": {"metadata_only": 0, "with_files": 0},
                    },
                    "files": {
                        "added": {"data_volume": 59117831.0, "file_count": 2},
                        "removed": {"data_volume": 0.0, "file_count": 0},
                    },
                }
            ],
            "subjects": [
                {
                    "id": "http://id.worldcat.org/fast/855500",
                    "label": "Children of prisoners--Services for",
                    "records": {
                        "added": {"metadata_only": 0, "with_files": 1},
                        "removed": {"metadata_only": 0, "with_files": 0},
                    },
                    "parents": {
                        "added": {"metadata_only": 0, "with_files": 1},
                        "removed": {"metadata_only": 0, "with_files": 0},
                    },
                    "files": {
                        "added": {"data_volume": 29558915.5, "file_count": 1},
                        "removed": {"data_volume": 0.0, "file_count": 0},
                    },
                }
            ],
            "rights": [
                {
                    "id": "cc-by-sa-4.0",
                    "label": {
                        "en": (
                            "Creative Commons Attribution-ShareAlike 4.0 International"
                        )
                    },
                    "records": {
                        "added": {"metadata_only": 0, "with_files": 2},
                        "removed": {"metadata_only": 0, "with_files": 0},
                    },
                    "parents": {
                        "added": {"metadata_only": 0, "with_files": 2},
                        "removed": {"metadata_only": 0, "with_files": 0},
                    },
                    "files": {
                        "added": {"data_volume": 59117831.0, "file_count": 2},
                        "removed": {"data_volume": 0.0, "file_count": 0},
                    },
                }
            ],
            "funders": [
                {
                    "id": "00k4n6c31",
                    "label": "",
                    "records": {
                        "added": {"metadata_only": 0, "with_files": 1},
                        "removed": {"metadata_only": 0, "with_files": 0},
                    },
                    "parents": {
                        "added": {"metadata_only": 0, "with_files": 1},
                        "removed": {"metadata_only": 0, "with_files": 0},
                    },
                    "files": {
                        "added": {"data_volume": 29558915.5, "file_count": 1},
                        "removed": {"data_volume": 0.0, "file_count": 0},
                    },
                }
            ],
            "periodicals": [
                {
                    "id": "N/A",
                    "label": "",
                    "records": {
                        "added": {"metadata_only": 0, "with_files": 1},
                        "removed": {"metadata_only": 0, "with_files": 0},
                    },
                    "parents": {
                        "added": {"metadata_only": 0, "with_files": 1},
                        "removed": {"metadata_only": 0, "with_files": 0},
                    },
                    "files": {
                        "added": {"data_volume": 29558915.5, "file_count": 1},
                        "removed": {"data_volume": 0.0, "file_count": 0},
                    },
                }
            ],
            "publishers": [
                {
                    "id": "Knowledge Commons",
                    "label": "",
                    "records": {
                        "added": {"metadata_only": 0, "with_files": 2},
                        "removed": {"metadata_only": 0, "with_files": 0},
                    },
                    "parents": {
                        "added": {"metadata_only": 0, "with_files": 2},
                        "removed": {"metadata_only": 0, "with_files": 0},
                    },
                    "files": {
                        "added": {"data_volume": 59117831.0, "file_count": 2},
                        "removed": {"data_volume": 0.0, "file_count": 0},
                    },
                }
            ],
            "affiliations": [
                {
                    "id": "013v4ng57",
                    "label": "",
                    "records": {
                        "added": {"metadata_only": 0, "with_files": 1},
                        "removed": {"metadata_only": 0, "with_files": 0},
                    },
                    "parents": {
                        "added": {"metadata_only": 0, "with_files": 1},
                        "removed": {"metadata_only": 0, "with_files": 0},
                    },
                    "files": {
                        "added": {"data_volume": 29558915.5, "file_count": 1},
                        "removed": {"data_volume": 0.0, "file_count": 0},
                    },
                },
                {
                    "id": "03rmrcq20",
                    "label": "",
                    "records": {
                        "added": {"metadata_only": 0, "with_files": 1},
                        "removed": {"metadata_only": 0, "with_files": 0},
                    },
                    "parents": {
                        "added": {"metadata_only": 0, "with_files": 1},
                        "removed": {"metadata_only": 0, "with_files": 0},
                    },
                    "files": {
                        "added": {"data_volume": 29558915.5, "file_count": 1},
                        "removed": {"data_volume": 0.0, "file_count": 0},
                    },
                },
            ],
            "file_types": [
                {
                    "id": "pdf",
                    "label": "",
                    "records": {
                        "added": {"metadata_only": 0, "with_files": 2},
                        "removed": {"metadata_only": 0, "with_files": 0},
                    },
                    "parents": {
                        "added": {"metadata_only": 0, "with_files": 2},
                        "removed": {"metadata_only": 0, "with_files": 0},
                    },
                    "files": {
                        "added": {"data_volume": 59117831.0, "file_count": 2},
                        "removed": {"data_volume": 0.0, "file_count": 0},
                    },
                }
            ],
        },
    },
    {
        "period_start": "2025-05-31T00:00:00",
        "records": {
            "added": {"metadata_only": 0, "with_files": 0},
            "removed": {"metadata_only": 0, "with_files": 0},
        },
        "parents": {
            "added": {"metadata_only": 0, "with_files": 0},
            "removed": {"metadata_only": 0, "with_files": 0},
        },
        "uploaders": 0,
        "files": {
            "added": {"data_volume": 0.0, "file_count": 0},
            "removed": {"data_volume": 0.0, "file_count": 0},
        },
        "subcounts": {
            "access_statuses": [],
            "resource_types": [],
            "languages": [],
            "subjects": [],
            "rights": [],
            "funders": [],
            "periodicals": [],
            "publishers": [],
            "affiliations": [],
            "file_types": [],
        },
    },
]
