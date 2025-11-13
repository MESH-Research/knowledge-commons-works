# Part of the Invenio-Stats-Dashboard extension for InvenioRDM
# Copyright (C) 2025 Mesh Research
#
# Invenio-Stats-Dashboard is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Sample record snapshot data series."""

MOCK_RECORD_SNAPSHOT_DATA_SERIES = {
    "access_statuses": {
        "records": [
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "metadata-only",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 3],
                    ["09-01", 2],
                ],
                "id": "open",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
        ],
        "parents": [
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "metadata-only",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 3],
                    ["09-01", 2],
                ],
                "id": "open",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
        ],
        "data_volume": [
            {
                "data": [["08-27", 0.0], ["08-31", 0.0], ["09-01", 0.0]],
                "id": "metadata-only",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "filesize",
            },
            {
                "data": [["08-27", 1984949.0], ["08-31", 1984949.0], ["09-01", 1984949.0]],
                "id": "open",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "filesize",
            },
        ],
        "file_count": [
            {
                "data": [["08-27", 0], ["08-31", 0], ["09-01", 0]],
                "id": "metadata-only",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [["08-27", 1], ["08-31", 1], ["09-01", 1]],
                "id": "open",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
        ],
    },
    "affiliations": {
        "records": [
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "03rmrcq20",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "013v4ng57",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
        ],
        "parents": [
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "03rmrcq20",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "013v4ng57",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
        ],
        "data_volume": [
            {
                "data": [
                    ["08-27", 0.0],
                    ["08-31", 0.0],
                    ["09-01", 0.0],
                ],
                "id": "03rmrcq20",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "filesize",
            },
            {
                "data": [
                    ["08-31", 0.0],
                    ["09-01", 0.0],
                ],
                "id": "013v4ng57",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "filesize",
            },
        ],
        "file_count": [
            {
                "data": [
                    ["08-27", 0],
                    ["08-31", 0],
                    ["09-01", 0],
                ],
                "id": "03rmrcq20",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-31", 0],
                    ["09-01", 0],
                ],
                "id": "013v4ng57",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
        ],
    },
    "file_presence": {
        "records": [
            {
                "data": [
                    ["08-27", 1],
                    ["08-25", 0],
                ],
                "id": "metadata_only",
                "name": "Metadata Only",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 1],
                    ["08-25", 0],
                ],
                "id": "with_files",
                "name": "With Files",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
        ],
        "parents": [
            {
                "data": [
                    ["08-27", 1],
                    ["08-25", 0],
                ],
                "id": "metadata_only",
                "name": "Metadata Only",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 1],
                    ["08-25", 0],
                ],
                "id": "with_files",
                "name": "With Files",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
        ],
        "file_count": [
            {
                "data": [
                    ["08-27", 1],
                    ["08-25", 0],
                ],
                "id": "metadata_only",
                "name": "Metadata Only",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 1],
                    ["08-25", 0],
                ],
                "id": "with_files",
                "name": "With Files",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
        ],
        "data_volume": [
            {
                "data": [
                    ["08-27", 1984949.0],
                    ["08-25", 0.0],
                ],
                "id": "metadata_only",
                "name": "Metadata Only",
                "type": "line",
                "year": 2025,
                "valueType": "filesize",
            },
            {
                "data": [
                    ["08-27", 1984949.0],
                    ["08-25", 0.0],
                ],
                "id": "with_files",
                "name": "With Files",
                "type": "line",
                "year": 2025,
                "valueType": "filesize",
            },
        ],
    },
    "file_types": {
        "file_count": [
            {
                "data": [
                    ["08-27", 0],
                    ["08-31", 0],
                    ["09-01", 0],
                ],
                "id": "pdf",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            }
        ],
        "parents": [
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 3],
                    ["09-01", 2],
                ],
                "id": "pdf",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            }
        ],
        "records": [
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 3],
                    ["09-01", 2],
                ],
                "id": "pdf",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            }
        ],
        "data_volume": [
            {
                "data": [
                    ["08-27", 0.0],
                    ["08-31", 0.0],
                    ["09-01", 0.0],
                ],
                "id": "pdf",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "filesize",
            }
        ],
    },
    "funders": {
        "file_count": [
            {
                "data": [
                    ["08-27", 0],
                    ["08-31", 0],
                    ["09-01", 0],
                ],
                "id": "00k4n6c31",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            }
        ],
        "parents": [
            {
                "data": [
                    ["08-27", 2],
                    ["08-31", 2],
                    ["09-01", 2],
                ],
                "id": "00k4n6c31",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            }
        ],
        "records": [
            {
                "data": [
                    ["08-27", 2],
                    ["08-31", 2],
                    ["09-01", 2],
                ],
                "id": "00k4n6c31",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            }
        ],
        "data_volume": [
            {
                "data": [
                    ["08-27", 0.0],
                    ["08-31", 0.0],
                    ["09-01", 0.0],
                ],
                "id": "00k4n6c31",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "filesize",
            }
        ],
    },
    "global": {
        "file_count": [
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "global",
                "name": "Global",
                "type": "bar",
                "year": 2025,
                "valueType": "number",
            }
        ],
        "parents": [
            {
                "data": [["08-27", 2], ["08-31", 4], ["09-01", 3]],
                "id": "global",
                "name": "Global",
                "type": "bar",
                "year": 2025,
                "valueType": "number",
            }
        ],
        "records": [
            {
                "data": [["08-27", 2], ["08-31", 4], ["09-01", 3]],
                "id": "global",
                "name": "Global",
                "type": "bar",
                "year": 2025,
                "valueType": "number",
            }
        ],
        "uploaders": [
            {
                "data": [
                    ["08-27", 0],
                    ["08-31", 0],
                    ["09-01", 0],
                ],
                "id": "global",
                "name": "Global",
                "type": "bar",
                "year": 2025,
                "valueType": "number",
            }
        ],
        "data_volume": [
            {
                "data": [["08-27", 1984949.0], ["08-31", 1984949.0], ["09-01", 1984949.0]],
                "id": "global",
                "name": "Global",
                "type": "bar",
                "year": 2025,
                "valueType": "filesize",
            }
        ],
    },
    "languages": {
        "file_count": [
            {
                "data": [
                    ["08-27", 0],
                    ["08-31", 0],
                    ["09-01", 0],
                ],
                "id": "eng",
                "name": "{'en': 'English'}",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            }
        ],
        "parents": [
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 2],
                    ["09-01", 2],
                ],
                "id": "eng",
                "name": "{'en': 'English'}",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            }
        ],
        "records": [
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 2],
                    ["09-01", 2],
                ],
                "id": "eng",
                "name": "{'en': 'English'}",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            }
        ],
        "data_volume": [
            {
                "data": [
                    ["08-27", 0.0],
                    ["08-31", 0.0],
                    ["09-01", 0.0],
                ],
                "id": "eng",
                "name": "{'en': 'English'}",
                "type": "line",
                "year": 2025,
                "valueType": "filesize",
            }
        ],
    },
    "periodicals": {
        "file_count": [
            {
                "data": [
                    ["08-27", 0],
                    ["08-31", 0],
                    ["09-01", 0],
                ],
                "id": "N/A",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            }
        ],
        "parents": [
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "N/A",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            }
        ],
        "records": [
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "N/A",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            }
        ],
        "data_volume": [
            {
                "data": [
                    ["08-27", 0.0],
                    ["08-31", 0.0],
                    ["09-01", 0.0],
                ],
                "id": "N/A",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "filesize",
            }
        ],
    },
    "publishers": {
        "file_count": [
            {
                "data": [
                    ["08-27", 0],
                    ["08-31", 0],
                    ["09-01", 0],
                ],
                "id": "UBC",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 0],
                    ["08-31", 0],
                    ["09-01", 0],
                ],
                "id": "Knowledge Commons",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-31", 0],
                ],
                "id": "Apocryphile Press",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
        ],
        "parents": [
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "UBC",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 2],
                    ["09-01", 2],
                ],
                "id": "Knowledge Commons",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [["08-31", 1]],
                "id": "Apocryphile Press",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
        ],
        "records": [
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "UBC",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 2],
                    ["09-01", 2],
                ],
                "id": "Knowledge Commons",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [["08-31", 1]],
                "id": "Apocryphile Press",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
        ],
        "data_volume": [
            {
                "data": [
                    ["08-27", 0.0],
                    ["08-31", 0.0],
                    ["09-01", 0.0],
                ],
                "id": "UBC",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "filesize",
            },
            {
                "data": [
                    ["08-27", 0.0],
                    ["08-31", 0.0],
                    ["09-01", 0.0],
                ],
                "id": "Knowledge Commons",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "filesize",
            },
            {
                "data": [["08-31", 0.0]],
                "id": "Apocryphile Press",
                "name": "",
                "type": "line",
                "year": 2025,
                "valueType": "filesize",
            },
        ],
    },
    "resource_types": {
        "file_count": [
            {
                "data": [
                    ["08-27", 0],
                    ["08-31", 0],
                    ["09-01", 0],
                ],
                "id": "textDocument-journalArticle",
                "name": "{'en': 'Journal Article'}",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 0],
                    ["08-31", 0],
                    ["09-01", 0],
                ],
                "id": "textDocument-book",
                "name": "{'en': 'Book'}",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-31", 0],
                    ["09-01", 0],
                ],
                "id": "textDocument-bookSection",
                "name": "{'en': 'Book Section'}",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
        ],
        "parents": [
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 2],
                    ["09-01", 2],
                ],
                "id": "textDocument-journalArticle",
                "name": "{'en': 'Journal Article'}",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "textDocument-book",
                "name": "{'en': 'Book'}",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [["08-31", 1], ["09-01", 0]],
                "id": "textDocument-bookSection",
                "name": "{'en': 'Book Section'}",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
        ],
        "records": [
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 2],
                    ["09-01", 2],
                ],
                "id": "textDocument-journalArticle",
                "name": "{'en': 'Journal Article'}",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "textDocument-book",
                "name": "{'en': 'Book'}",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [["08-31", 1], ["09-01", 0]],
                "id": "textDocument-bookSection",
                "name": "{'en': 'Book Section'}",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
        ],
        "data_volume": [
            {
                "data": [
                    ["08-27", 0.0],
                    ["08-31", 0.0],
                    ["09-01", 0.0],
                ],
                "id": "textDocument-journalArticle",
                "name": "{'en': 'Journal Article'}",
                "type": "line",
                "year": 2025,
                "valueType": "filesize",
            },
            {
                "data": [
                    ["08-27", 0.0],
                    ["08-31", 0.0],
                    ["09-01", 0.0],
                ],
                "id": "textDocument-book",
                "name": "{'en': 'Book'}",
                "type": "line",
                "year": 2025,
                "valueType": "filesize",
            },
            {
                "data": [
                    ["08-31", 0.0],
                    ["09-01", 0.0],
                ],
                "id": "textDocument-bookSection",
                "name": "{'en': 'Book Section'}",
                "type": "line",
                "year": 2025,
                "valueType": "filesize",
            },
        ],
    },
    "rights": {
        "file_count": [
            {
                "data": [
                    ["08-27", 0],
                    ["08-31", 0],
                    ["09-01", 0],
                ],
                "id": "cc-by-sa-4.0",
                "name": "{'en': 'Creative Commons Attribution-ShareAlike "
                "4.0 International'}",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            }
        ],
        "parents": [
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "cc-by-sa-4.0",
                "name": "{'en': 'Creative Commons "
                "Attribution-ShareAlike 4.0 International'}",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            }
        ],
        "records": [
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "cc-by-sa-4.0",
                "name": "{'en': 'Creative Commons Attribution-ShareAlike "
                "4.0 International'}",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            }
        ],
        "data_volume": [
            {
                "data": [
                    ["08-27", 0.0],
                    ["08-31", 0.0],
                    ["09-01", 0.0],
                ],
                "id": "cc-by-sa-4.0",
                "name": "{'en': 'Creative Commons Attribution-ShareAlike "
                "4.0 International'}",
                "type": "line",
                "year": 2025,
                "valueType": "filesize",
            }
        ],
    },
    "subjects": {
        "file_count": [
            {
                "data": [
                    ["08-27", 0],
                    ["08-31", 0],
                    ["09-01", 0],
                ],
                "id": "http://id.worldcat.org/fast/911979",
                "name": "English language--Written English--History",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 0],
                    ["08-31", 0],
                    ["09-01", 0],
                ],
                "id": "http://id.worldcat.org/fast/845111",
                "name": "Canadian literature",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 0],
                    ["08-31", 0],
                    ["09-01", 0],
                ],
                "id": "http://id.worldcat.org/fast/821870",
                "name": "Authors, Canadian",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 0],
                    ["08-31", 0],
                    ["09-01", 0],
                ],
                "id": "http://id.worldcat.org/fast/911328",
                "name": "English language--Lexicography--History",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 0],
                    ["08-31", 0],
                    ["09-01", 0],
                ],
                "id": "http://id.worldcat.org/fast/911660",
                "name": "English language--Spoken English--Research",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 0],
                    ["08-31", 0],
                    ["09-01", 0],
                ],
                "id": "http://id.worldcat.org/fast/845170",
                "name": "Canadian periodicals",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 0],
                    ["08-31", 0],
                    ["09-01", 0],
                ],
                "id": "http://id.worldcat.org/fast/845142",
                "name": "Canadian literature--Periodicals",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 0],
                    ["08-31", 0],
                    ["09-01", 0],
                ],
                "id": "http://id.worldcat.org/fast/817954",
                "name": "Arts, Canadian",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 0],
                    ["08-31", 0],
                    ["09-01", 0],
                ],
                "id": "http://id.worldcat.org/fast/1424786",
                "name": "Canadian literature--Bibliography",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 0],
                    ["08-31", 0],
                    ["09-01", 0],
                ],
                "id": "http://id.worldcat.org/fast/845184",
                "name": "Canadian prose literature",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 0],
                    ["08-31", 0],
                    ["09-01", 0],
                ],
                "id": "http://id.worldcat.org/fast/934875",
                "name": "French-Canadian literature",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 0],
                    ["08-31", 0],
                    ["09-01", 0],
                ],
                "id": "http://id.worldcat.org/fast/997987",
                "name": "Library science literature",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 0],
                    ["08-31", 0],
                    ["09-01", 0],
                ],
                "id": "http://id.worldcat.org/fast/995415",
                "name": "Legal assistance to prisoners--U.S. states",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 0],
                    ["08-31", 0],
                    ["09-01", 0],
                ],
                "id": "http://id.worldcat.org/fast/997974",
                "name": "Library science--Standards",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 0],
                    ["08-31", 0],
                    ["09-01", 0],
                ],
                "id": "http://id.worldcat.org/fast/997916",
                "name": "Library science",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 0],
                    ["08-31", 0],
                    ["09-01", 0],
                ],
                "id": "http://id.worldcat.org/fast/2060143",
                "name": "Mass incarceration",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 0],
                    ["08-31", 0],
                    ["09-01", 0],
                ],
                "id": "http://id.worldcat.org/fast/973589",
                "name": "Inklings (Group of writers)",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 0],
                    ["08-31", 0],
                    ["09-01", 0],
                ],
                "id": "http://id.worldcat.org/fast/855500",
                "name": "Children of prisoners--Services for",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
        ],
        "parents": [
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "http://id.worldcat.org/fast/911979",
                "name": "English language--Written English--History",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "http://id.worldcat.org/fast/845111",
                "name": "Canadian literature",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "http://id.worldcat.org/fast/821870",
                "name": "Authors, Canadian",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "http://id.worldcat.org/fast/911328",
                "name": "English language--Lexicography--History",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "http://id.worldcat.org/fast/911660",
                "name": "English language--Spoken English--Research",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "http://id.worldcat.org/fast/845170",
                "name": "Canadian periodicals",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "http://id.worldcat.org/fast/845142",
                "name": "Canadian literature--Periodicals",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "http://id.worldcat.org/fast/817954",
                "name": "Arts, Canadian",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "http://id.worldcat.org/fast/1424786",
                "name": "Canadian literature--Bibliography",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "http://id.worldcat.org/fast/845184",
                "name": "Canadian prose literature",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "http://id.worldcat.org/fast/934875",
                "name": "French-Canadian literature",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "http://id.worldcat.org/fast/997987",
                "name": "Library science literature",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "http://id.worldcat.org/fast/995415",
                "name": "Legal assistance to prisoners--U.S. states",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "http://id.worldcat.org/fast/997974",
                "name": "Library science--Standards",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "http://id.worldcat.org/fast/997916",
                "name": "Library science",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "http://id.worldcat.org/fast/2060143",
                "name": "Mass incarceration",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [["08-31", 1]],
                "id": "http://id.worldcat.org/fast/973589",
                "name": "Inklings (Group of writers)",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "http://id.worldcat.org/fast/855500",
                "name": "Children of prisoners--Services for",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
        ],
        "records": [
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "http://id.worldcat.org/fast/911979",
                "name": "English language--Written English--History",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "http://id.worldcat.org/fast/845111",
                "name": "Canadian literature",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "http://id.worldcat.org/fast/821870",
                "name": "Authors, Canadian",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "http://id.worldcat.org/fast/911328",
                "name": "English language--Lexicography--History",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "http://id.worldcat.org/fast/911660",
                "name": "English language--Spoken English--Research",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "http://id.worldcat.org/fast/845170",
                "name": "Canadian periodicals",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "http://id.worldcat.org/fast/845142",
                "name": "Canadian literature--Periodicals",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "http://id.worldcat.org/fast/817954",
                "name": "Arts, Canadian",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "http://id.worldcat.org/fast/1424786",
                "name": "Canadian literature--Bibliography",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "http://id.worldcat.org/fast/845184",
                "name": "Canadian prose literature",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-27", 1],
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "http://id.worldcat.org/fast/934875",
                "name": "French-Canadian literature",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "http://id.worldcat.org/fast/997987",
                "name": "Library science literature",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "http://id.worldcat.org/fast/995415",
                "name": "Legal assistance to prisoners--U.S. states",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "http://id.worldcat.org/fast/997974",
                "name": "Library science--Standards",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "http://id.worldcat.org/fast/997916",
                "name": "Library science",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "http://id.worldcat.org/fast/2060143",
                "name": "Mass incarceration",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [["08-31", 1]],
                "id": "http://id.worldcat.org/fast/973589",
                "name": "Inklings (Group of writers)",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
            {
                "data": [
                    ["08-31", 1],
                    ["09-01", 1],
                ],
                "id": "http://id.worldcat.org/fast/855500",
                "name": "Children of prisoners--Services for",
                "type": "line",
                "year": 2025,
                "valueType": "number",
            },
        ],
        "data_volume": [
            {
                "data": [
                    ["08-27", 0.0],
                    ["08-31", 0.0],
                    ["09-01", 0.0],
                ],
                "id": "http://id.worldcat.org/fast/911979",
                "name": "English language--Written English--History",
                "type": "line",
                "year": 2025,
                "valueType": "filesize",
            },
            {
                "data": [
                    ["08-27", 0.0],
                    ["08-31", 0.0],
                    ["09-01", 0.0],
                ],
                "id": "http://id.worldcat.org/fast/845111",
                "name": "Canadian literature",
                "type": "line",
                "year": 2025,
                "valueType": "filesize",
            },
            {
                "data": [
                    ["08-27", 0.0],
                    ["08-31", 0.0],
                    ["09-01", 0.0],
                ],
                "id": "http://id.worldcat.org/fast/821870",
                "name": "Authors, Canadian",
                "type": "line",
                "year": 2025,
                "valueType": "filesize",
            },
        ],
    },
}
