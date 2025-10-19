# Part of the Invenio-Stats-Dashboard extension for InvenioRDM
# Copyright (C) 2025 Mesh Research
#
# Invenio-Stats-Dashboard is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Sample usage delta aggregation documents."""

MOCK_USAGE_DELTA_DOCS = [
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
            "resource_types": [],
            "languages": [],
            "subjects": [],
            "rights": [],
            "funders": [],
            "periodicals": [],
            "publishers": [],
            "affiliations": [],
            "countries": [],
            "referrers": [],
            "file_types": [],
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
]

MOCK_USAGE_DELTA_DOCS_2 = [
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
            "resource_types": [
                {
                    "download": {
                        "total_events": 2,
                        "total_volume": 2048.0,
                        "unique_files": 2,
                        "unique_parents": 2,
                        "unique_records": 2,
                        "unique_visitors": 2,
                    },
                    "id": "textDocument-journalArticle",
                    "label": {"en": "Journal Article"},
                    "view": {
                        "total_events": 2,
                        "unique_parents": 2,
                        "unique_records": 2,
                        "unique_visitors": 2,
                    },
                }
            ],
            "languages": [
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
                }
            ],
            "subjects": [],
            "rights": [],
            "funders": [],
            "periodicals": [],
            "publishers": [],
            "affiliations": [],
            "countries": [
                {
                    "download": {
                        "total_events": 1,
                        "total_volume": 512.0,
                        "unique_files": 1,
                        "unique_parents": 1,
                        "unique_records": 1,
                        "unique_visitors": 1,
                    },
                    "id": "US",
                    "label": "",
                    "view": {
                        "total_events": 1,
                        "unique_parents": 1,
                        "unique_records": 1,
                        "unique_visitors": 1,
                    },
                }
            ],
            "referrers": [
                {
                    "download": {
                        "total_events": 1,
                        "total_volume": 256.0,
                        "unique_files": 1,
                        "unique_parents": 1,
                        "unique_records": 1,
                        "unique_visitors": 1,
                    },
                    "id": "google.com",
                    "label": "",
                    "view": {
                        "total_events": 1,
                        "unique_parents": 1,
                        "unique_records": 1,
                        "unique_visitors": 1,
                    },
                }
            ],
            "file_types": [
                {
                    "download": {
                        "total_events": 1,
                        "total_volume": 128.0,
                        "unique_files": 1,
                        "unique_parents": 1,
                        "unique_records": 1,
                        "unique_visitors": 1,
                    },
                    "id": "pdf",
                    "label": "",
                    "view": {
                        "total_events": 1,
                        "unique_parents": 1,
                        "unique_records": 1,
                        "unique_visitors": 1,
                    },
                }
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
]
