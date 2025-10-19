# Part of the Invenio-Stats-Dashboard extension for InvenioRDM
# Copyright (C) 2025 Mesh Research
#
# Invenio-Stats-Dashboard is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Sample usage snapshot data series response."""

MOCK_USAGE_SNAPSHOT_DATA_SERIES = {
    "access_statuses": {
        "data_volume": [
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 5120.0],
                        "valueType": "filesize",
                    }
                ],
                "id": "metadata-only",
                "name": "Metadata Only",
                "type": "line",
                "valueType": "number",
            },
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 15360.0],
                        "valueType": "filesize",
                    }
                ],
                "id": "with-files",
                "name": "With Files",
                "type": "line",
                "valueType": "number",
            },
        ],
        "download_unique_files": [
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 4],
                        "valueType": "number",
                    }
                ],
                "id": "metadata-only",
                "name": "Metadata Only",
                "type": "line",
                "valueType": "number",
            },
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 10],
                        "valueType": "number",
                    }
                ],
                "id": "with-files",
                "name": "With Files",
                "type": "line",
                "valueType": "number",
            },
        ],
        "download_unique_parents": [
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 3],
                        "valueType": "number",
                    }
                ],
                "id": "metadata-only",
                "name": "Metadata Only",
                "type": "line",
                "valueType": "number",
            },
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 7],
                        "valueType": "number",
                    }
                ],
                "id": "with-files",
                "name": "With Files",
                "type": "line",
                "valueType": "number",
            },
        ],
        "download_unique_records": [
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 5],
                        "valueType": "number",
                    }
                ],
                "id": "metadata-only",
                "name": "Metadata Only",
                "type": "line",
                "valueType": "number",
            },
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 9],
                        "valueType": "number",
                    }
                ],
                "id": "with-files",
                "name": "With Files",
                "type": "line",
                "valueType": "number",
            },
        ],
        "download_visitors": [
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 2],
                        "valueType": "number",
                    }
                ],
                "id": "metadata-only",
                "name": "Metadata Only",
                "type": "line",
                "valueType": "number",
            },
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 4],
                        "valueType": "number",
                    }
                ],
                "id": "with-files",
                "name": "With Files",
                "type": "line",
                "valueType": "number",
            },
        ],
        "downloads": [
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 5],
                        "valueType": "number",
                    }
                ],
                "id": "metadata-only",
                "name": "Metadata Only",
                "type": "line",
                "valueType": "number",
            },
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 12],
                        "valueType": "number",
                    }
                ],
                "id": "with-files",
                "name": "With Files",
                "type": "line",
                "valueType": "number",
            },
        ],
        "view_unique_parents": [
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 5],
                        "valueType": "number",
                    }
                ],
                "id": "metadata-only",
                "name": "Metadata Only",
                "type": "line",
                "valueType": "number",
            },
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 8],
                        "valueType": "number",
                    }
                ],
                "id": "with-files",
                "name": "With Files",
                "type": "line",
                "valueType": "number",
            },
        ],
        "view_unique_records": [
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 8],
                        "valueType": "number",
                    }
                ],
                "id": "metadata-only",
                "name": "Metadata Only",
                "type": "line",
                "valueType": "number",
            },
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 12],
                        "valueType": "number",
                    }
                ],
                "id": "with-files",
                "name": "With Files",
                "type": "line",
                "valueType": "number",
            },
        ],
        "view_visitors": [
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 3],
                        "valueType": "number",
                    }
                ],
                "id": "metadata-only",
                "name": "Metadata Only",
                "type": "line",
                "valueType": "number",
            },
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 6],
                        "valueType": "number",
                    }
                ],
                "id": "with-files",
                "name": "With Files",
                "type": "line",
                "valueType": "number",
            },
        ],
        "views": [
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 10],
                        "valueType": "number",
                    }
                ],
                "id": "metadata-only",
                "name": "Metadata Only",
                "type": "line",
                "valueType": "number",
            },
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 15],
                        "valueType": "number",
                    }
                ],
                "id": "with-files",
                "name": "With Files",
                "type": "line",
                "valueType": "number",
            },
        ],
    },
    "affiliations_by_download": {
        "data_volume": [],
        "download_visitors": [],
        "downloads": [],
        "view_visitors": [],
        "views": [],
    },
    "affiliations_by_view": {
        "data_volume": [],
        "download_visitors": [],
        "downloads": [],
        "view_visitors": [],
        "views": [],
    },
    "countries_by_download": {
        "data_volume": [
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 10240.0],
                        "valueType": "filesize",
                    }
                ],
                "id": "US",
                "name": "United States",
                "type": "line",
                "valueType": "number",
            },
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 2048.0],
                        "valueType": "filesize",
                    }
                ],
                "id": "CA",
                "name": "Canada",
                "type": "line",
                "valueType": "number",
            },
        ],
        "download_visitors": [
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 4],
                        "valueType": "number",
                    }
                ],
                "id": "US",
                "name": "United States",
                "type": "line",
                "valueType": "number",
            },
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 1],
                        "valueType": "number",
                    }
                ],
                "id": "CA",
                "name": "Canada",
                "type": "line",
                "valueType": "number",
            },
        ],
        "downloads": [
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 10],
                        "valueType": "number",
                    }
                ],
                "id": "US",
                "name": "United States",
                "type": "line",
                "valueType": "number",
            },
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 4],
                        "valueType": "number",
                    }
                ],
                "id": "CA",
                "name": "Canada",
                "type": "line",
                "valueType": "number",
            },
        ],
        "view_visitors": [
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 7],
                        "valueType": "number",
                    }
                ],
                "id": "US",
                "name": "United States",
                "type": "line",
                "valueType": "number",
            },
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 3],
                        "valueType": "number",
                    }
                ],
                "id": "CA",
                "name": "Canada",
                "type": "line",
                "valueType": "number",
            },
        ],
        "views": [
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 18],
                        "valueType": "number",
                    }
                ],
                "id": "US",
                "name": "United States",
                "type": "line",
                "valueType": "number",
            },
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 8],
                        "valueType": "number",
                    }
                ],
                "id": "CA",
                "name": "Canada",
                "type": "line",
                "valueType": "number",
            },
        ],
    },
    "countries_by_view": {
        "data_volume": [
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 8192.0],
                        "valueType": "filesize",
                    }
                ],
                "id": "US",
                "name": "United States",
                "type": "line",
                "valueType": "number",
            },
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 4096.0],
                        "valueType": "filesize",
                    }
                ],
                "id": "CA",
                "name": "Canada",
                "type": "line",
                "valueType": "number",
            },
        ],
        "download_visitors": [
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 3],
                        "valueType": "number",
                    }
                ],
                "id": "US",
                "name": "United States",
                "type": "line",
                "valueType": "number",
            },
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 2],
                        "valueType": "number",
                    }
                ],
                "id": "CA",
                "name": "Canada",
                "type": "line",
                "valueType": "number",
            },
        ],
        "downloads": [
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 8],
                        "valueType": "number",
                    }
                ],
                "id": "US",
                "name": "United States",
                "type": "line",
                "valueType": "number",
            },
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 6],
                        "valueType": "number",
                    }
                ],
                "id": "CA",
                "name": "Canada",
                "type": "line",
                "valueType": "number",
            },
        ],
        "view_visitors": [
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 8],
                        "valueType": "number",
                    }
                ],
                "id": "US",
                "name": "United States",
                "type": "line",
                "valueType": "number",
            },
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 4],
                        "valueType": "number",
                    }
                ],
                "id": "CA",
                "name": "Canada",
                "type": "line",
                "valueType": "number",
            },
        ],
        "views": [
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 20],
                        "valueType": "number",
                    }
                ],
                "id": "US",
                "name": "United States",
                "type": "line",
                "valueType": "number",
            },
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 12],
                        "valueType": "number",
                    }
                ],
                "id": "CA",
                "name": "Canada",
                "type": "line",
                "valueType": "number",
            },
        ],
    },
    "file_types": {
        "data_volume": [],
        "download_unique_files": [],
        "download_unique_parents": [],
        "download_unique_records": [],
        "download_visitors": [],
        "downloads": [],
        "view_unique_parents": [],
        "view_unique_records": [],
        "view_visitors": [],
        "views": [],
    },
    "funders_by_download": {
        "data_volume": [],
        "download_unique_files": [],
        "download_unique_parents": [],
        "download_unique_records": [],
        "download_visitors": [],
        "downloads": [],
        "view_unique_parents": [],
        "view_unique_records": [],
        "view_visitors": [],
        "views": [],
    },
    "funders_by_view": {
        "data_volume": [],
        "download_unique_files": [],
        "download_unique_parents": [],
        "download_unique_records": [],
        "download_visitors": [],
        "downloads": [],
        "view_unique_parents": [],
        "view_unique_records": [],
        "view_visitors": [],
        "views": [],
    },
    "global": {
        "data_volume": [
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 20480.0],
                        "valueType": "filesize",
                    }
                ],
                "id": "global",
                "name": "Global",
                "type": "bar",
                "valueType": "number",
            }
        ],
        "download_unique_files": [
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 20],
                        "valueType": "number",
                    }
                ],
                "id": "global",
                "name": "Global",
                "type": "bar",
                "valueType": "number",
            }
        ],
        "download_unique_parents": [
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 15],
                        "valueType": "number",
                    }
                ],
                "id": "global",
                "name": "Global",
                "type": "bar",
                "valueType": "number",
            }
        ],
        "download_unique_records": [
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 20],
                        "valueType": "number",
                    }
                ],
                "id": "global",
                "name": "Global",
                "type": "bar",
                "valueType": "number",
            }
        ],
        "download_visitors": [
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 10],
                        "valueType": "number",
                    }
                ],
                "id": "global",
                "name": "Global",
                "type": "bar",
                "valueType": "number",
            }
        ],
        "downloads": [
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 25],
                        "valueType": "number",
                    }
                ],
                "id": "global",
                "name": "Global",
                "type": "bar",
                "valueType": "number",
            }
        ],
        "view_unique_parents": [
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 25],
                        "valueType": "number",
                    }
                ],
                "id": "global",
                "name": "Global",
                "type": "bar",
                "valueType": "number",
            }
        ],
        "view_unique_records": [
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 35],
                        "valueType": "number",
                    }
                ],
                "id": "global",
                "name": "Global",
                "type": "bar",
                "valueType": "number",
            }
        ],
        "view_visitors": [
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 18],
                        "valueType": "number",
                    }
                ],
                "id": "global",
                "name": "Global",
                "type": "bar",
                "valueType": "number",
            }
        ],
        "views": [
            {
                "data": [
                    {
                        "readableDate": "Jun 1, 2025",
                        "value": ["2025-06-01", 45],
                        "valueType": "number",
                    }
                ],
                "id": "global",
                "name": "Global",
                "type": "bar",
                "valueType": "number",
            }
        ],
    },
    "languages_by_download": {
        "data_volume": [],
        "download_unique_files": [],
        "download_unique_parents": [],
        "download_unique_records": [],
        "download_visitors": [],
        "downloads": [],
        "view_unique_parents": [],
        "view_unique_records": [],
        "view_visitors": [],
        "views": [],
    },
    "languages_by_view": {
        "data_volume": [],
        "download_unique_files": [],
        "download_unique_parents": [],
        "download_unique_records": [],
        "download_visitors": [],
        "downloads": [],
        "view_unique_parents": [],
        "view_unique_records": [],
        "view_visitors": [],
        "views": [],
    },
    "periodicals_by_download": {
        "data_volume": [],
        "download_unique_files": [],
        "download_unique_parents": [],
        "download_unique_records": [],
        "download_visitors": [],
        "downloads": [],
        "view_unique_parents": [],
        "view_unique_records": [],
        "view_visitors": [],
        "views": [],
    },
    "periodicals_by_view": {
        "data_volume": [],
        "download_unique_files": [],
        "download_unique_parents": [],
        "download_unique_records": [],
        "download_visitors": [],
        "downloads": [],
        "view_unique_parents": [],
        "view_unique_records": [],
        "view_visitors": [],
        "views": [],
    },
    "publishers_by_download": {
        "data_volume": [],
        "download_visitors": [],
        "downloads": [],
        "view_visitors": [],
        "views": [],
    },
    "publishers_by_view": {
        "data_volume": [],
        "download_visitors": [],
        "downloads": [],
        "view_visitors": [],
        "views": [],
    },
    "referrers_by_download": {
        "data_volume": [],
        "download_visitors": [],
        "downloads": [],
        "view_visitors": [],
        "views": [],
    },
    "referrers_by_view": {
        "data_volume": [],
        "download_visitors": [],
        "downloads": [],
        "view_visitors": [],
        "views": [],
    },
    "resource_types": {
        "data_volume": [],
        "download_unique_files": [],
        "download_unique_parents": [],
        "download_unique_records": [],
        "download_visitors": [],
        "downloads": [],
        "view_unique_parents": [],
        "view_unique_records": [],
        "view_visitors": [],
        "views": [],
    },
    "rights_by_download": {
        "data_volume": [],
        "download_visitors": [],
        "downloads": [],
        "view_visitors": [],
        "views": [],
    },
    "rights_by_view": {
        "data_volume": [],
        "download_visitors": [],
        "downloads": [],
        "view_visitors": [],
        "views": [],
    },
    "subjects_by_download": {
        "data_volume": [],
        "download_visitors": [],
        "downloads": [],
        "view_visitors": [],
        "views": [],
    },
    "subjects_by_view": {
        "data_volume": [],
        "download_visitors": [],
        "downloads": [],
        "view_visitors": [],
        "views": [],
    },
}
