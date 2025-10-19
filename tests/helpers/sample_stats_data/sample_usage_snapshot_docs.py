# Part of the Invenio-Stats-Dashboard extension for InvenioRDM
# Copyright (C) 2025 Mesh Research
#
# Invenio-Stats-Dashboard is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Sample usage snapshot aggregation docs."""

MOCK_USAGE_SNAPSHOT_DOCS = [
    {
        "community_id": "59e77d51-3758-409a-813f-efc0d2db1a5e",
        "snapshot_date": "2025-06-01T23:59:59",
        "subcounts": {
            # Regular subcount - access_statuses
            "access_statuses": [
                {
                    "id": "metadata-only",
                    "label": "Metadata Only",
                    "view": {
                        "total_events": 10,
                        "unique_parents": 5,
                        "unique_records": 8,
                        "unique_visitors": 3,
                    },
                    "download": {
                        "total_events": 5,
                        "total_volume": 5120.0,
                        "unique_files": 4,
                        "unique_parents": 3,
                        "unique_records": 5,
                        "unique_visitors": 2,
                    },
                },
                {
                    "id": "with-files",
                    "label": "With Files",
                    "view": {
                        "total_events": 15,
                        "unique_parents": 8,
                        "unique_records": 12,
                        "unique_visitors": 6,
                    },
                    "download": {
                        "total_events": 12,
                        "total_volume": 15360.0,
                        "unique_files": 10,
                        "unique_parents": 7,
                        "unique_records": 9,
                        "unique_visitors": 4,
                    },
                },
            ],
            # Top subcount - countries (has by_view and by_download)
            "countries": {
                "by_view": [
                    {
                        "id": "US",
                        "label": "United States",
                        "view": {
                            "total_events": 20,
                            "unique_parents": 10,
                            "unique_records": 15,
                            "unique_visitors": 8,
                        },
                        "download": {
                            "total_events": 8,
                            "total_volume": 8192.0,
                            "unique_files": 6,
                            "unique_parents": 5,
                            "unique_records": 7,
                            "unique_visitors": 3,
                        },
                    },
                    {
                        "id": "CA",
                        "label": "Canada",
                        "view": {
                            "total_events": 12,
                            "unique_parents": 6,
                            "unique_records": 9,
                            "unique_visitors": 4,
                        },
                        "download": {
                            "total_events": 6,
                            "total_volume": 4096.0,
                            "unique_files": 4,
                            "unique_parents": 3,
                            "unique_records": 5,
                            "unique_visitors": 2,
                        },
                    },
                ],
                "by_download": [
                    {
                        "id": "US",
                        "label": "United States",
                        "view": {
                            "total_events": 18,
                            "unique_parents": 9,
                            "unique_records": 13,
                            "unique_visitors": 7,
                        },
                        "download": {
                            "total_events": 10,
                            "total_volume": 10240.0,
                            "unique_files": 8,
                            "unique_parents": 6,
                            "unique_records": 8,
                            "unique_visitors": 4,
                        },
                    },
                    {
                        "id": "CA",
                        "label": "Canada",
                        "view": {
                            "total_events": 8,
                            "unique_parents": 4,
                            "unique_records": 6,
                            "unique_visitors": 3,
                        },
                        "download": {
                            "total_events": 4,
                            "total_volume": 2048.0,
                            "unique_files": 3,
                            "unique_parents": 2,
                            "unique_records": 3,
                            "unique_visitors": 1,
                        },
                    },
                ],
            },
        },
        "timestamp": "2025-07-03T19:37:10",
        "totals": {
            "download": {
                "total_events": 25,
                "total_volume": 20480.0,
                "unique_files": 20,
                "unique_parents": 15,
                "unique_records": 20,
                "unique_visitors": 10,
            },
            "view": {
                "total_events": 45,
                "unique_parents": 25,
                "unique_records": 35,
                "unique_visitors": 18,
            },
        },
    },
]
