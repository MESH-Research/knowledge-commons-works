# Part of the Invenio-Stats-Dashboard extension for InvenioRDM
# Copyright (C) 2025 Mesh Research
#
# Invenio-Stats-Dashboard is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Sample usage delta API response."""

MOCK_USAGE_DELTA_API_RESPONSE = {
    "community-stats": [
        {
            "community_id": "59e77d51-3758-409a-813f-efc0d2db1a5e",
            "period_end": "2025-05-30T23:59:59",
            "period_start": "2025-05-30T00:00:00",
            "subcounts": {
                "access_statuses": [],
                "affiliations": [],
                "countries": [],
                "file_types": [],
                "funders": [],
                "languages": [],
                "rights": [],
                "periodicals": [],
                "publishers": [],
                "referrers": [],
                "resource_types": [],
                "subjects": [],
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
                "access_statuses": [],
                "affiliations": [],
                "countries": [],
                "file_types": [],
                "funders": [],
                "languages": [],
                "rights": [],
                "periodicals": [],
                "publishers": [],
                "referrers": [],
                "resource_types": [],
                "subjects": [],
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
                "access_statuses": [
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
                "affiliations": [],
                "countries": [
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
                "file_types": [
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
                "funders": [],
                "languages": [
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
                        "label": {"en": "Spanish"},
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
                        "label": {"en": "English"},
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                ],
                "rights": [
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
                        "label": {"en": "All Rights Reserved"},
                        "view": {
                            "total_events": 3,
                            "unique_parents": 3,
                            "unique_records": 3,
                            "unique_visitors": 3,
                        },
                    }
                ],
                "periodicals": [],
                "publishers": [
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
                        "id": "Universidad Nacional Autónoma de Mexico (UNAM)",
                        "label": "",
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                ],
                "referrers": [
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
                "resource_types": [
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
                        "label": {"en": "Book"},
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
                        "label": {"en": "Journal Article"},
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
                        "label": {"en": "Thesis"},
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                ],
                "subjects": [
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
                        "label": "Science--Study and teaching",
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
                        "label": "Technology--Study and teaching",
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
                "access_statuses": [],
                "affiliations": [],
                "countries": [],
                "file_types": [],
                "funders": [],
                "languages": [],
                "rights": [],
                "periodicals": [],
                "publishers": [],
                "referrers": [],
                "resource_types": [],
                "subjects": [],
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
                "access_statuses": [
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
                "affiliations": [],
                "countries": [
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
                "file_types": [
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
                "funders": [],
                "languages": [
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
                        "label": {"en": "Spanish"},
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
                        "label": {"en": "English"},
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                ],
                "rights": [
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
                        "label": {"en": "All Rights Reserved"},
                        "view": {
                            "total_events": 3,
                            "unique_parents": 3,
                            "unique_records": 3,
                            "unique_visitors": 3,
                        },
                    }
                ],
                "periodicals": [],
                "publishers": [
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
                        "id": "Universidad Nacional Autónoma de Mexico (UNAM)",
                        "label": "",
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                ],
                "referrers": [
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
                "resource_types": [
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
                        "label": {"en": "Book"},
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
                        "label": {"en": "Journal Article"},
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
                        "label": {"en": "Thesis"},
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                ],
                "subjects": [
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
                        "label": "Science--Study and teaching",
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
                        "label": "Technology--Study and teaching",
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
                "access_statuses": [],
                "affiliations": [],
                "countries": [],
                "file_types": [],
                "funders": [],
                "languages": [],
                "rights": [],
                "periodicals": [],
                "publishers": [],
                "referrers": [],
                "resource_types": [],
                "subjects": [],
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
                "access_statuses": [
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
                "affiliations": [],
                "countries": [
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
                "file_types": [
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
                "funders": [],
                "languages": [
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
                        "label": {"en": "Spanish"},
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
                        "label": {"en": "English"},
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                ],
                "rights": [
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
                        "label": {"en": "All Rights Reserved"},
                        "view": {
                            "total_events": 3,
                            "unique_parents": 3,
                            "unique_records": 3,
                            "unique_visitors": 3,
                        },
                    }
                ],
                "periodicals": [],
                "publishers": [
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
                        "id": "Universidad Nacional Autónoma de Mexico (UNAM)",
                        "label": "",
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                ],
                "referrers": [
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
                "resource_types": [
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
                        "label": {"en": "Book"},
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
                        "label": {"en": "Journal Article"},
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
                        "label": {"en": "Thesis"},
                        "view": {
                            "total_events": 1,
                            "unique_parents": 1,
                            "unique_records": 1,
                            "unique_visitors": 1,
                        },
                    },
                ],
                "subjects": [
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
                        "label": "Science--Study and teaching",
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
                        "label": "Technology--Study and teaching",
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
                "access_statuses": [],
                "affiliations": [],
                "countries": [],
                "file_types": [],
                "funders": [],
                "languages": [],
                "rights": [],
                "periodicals": [],
                "publishers": [],
                "referrers": [],
                "resource_types": [],
                "subjects": [],
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
                "access_statuses": [],
                "affiliations": [],
                "countries": [],
                "file_types": [],
                "funders": [],
                "languages": [],
                "rights": [],
                "periodicals": [],
                "publishers": [],
                "referrers": [],
                "resource_types": [],
                "subjects": [],
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
                "access_statuses": [],
                "affiliations": [],
                "countries": [],
                "file_types": [],
                "funders": [],
                "languages": [],
                "rights": [],
                "periodicals": [],
                "publishers": [],
                "referrers": [],
                "resource_types": [],
                "subjects": [],
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
                "access_statuses": [],
                "affiliations": [],
                "countries": [],
                "file_types": [],
                "funders": [],
                "languages": [],
                "rights": [],
                "periodicals": [],
                "publishers": [],
                "referrers": [],
                "resource_types": [],
                "subjects": [],
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
                "access_statuses": [],
                "affiliations": [],
                "countries": [],
                "file_types": [],
                "funders": [],
                "languages": [],
                "rights": [],
                "periodicals": [],
                "publishers": [],
                "referrers": [],
                "resource_types": [],
                "subjects": [],
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
                "access_statuses": [],
                "affiliations": [],
                "countries": [],
                "file_types": [],
                "funders": [],
                "languages": [],
                "rights": [],
                "periodicals": [],
                "publishers": [],
                "referrers": [],
                "resource_types": [],
                "subjects": [],
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
