# Part of the Invenio-Stats-Dashboard extension for InvenioRDM
# Copyright (C) 2025 Mesh Research
#
# Invenio-Stats-Dashboard is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Sample records query responses."""

# Mock delta query response for three imported records in 2025-05-30 to 2025-06-03
MOCK_RECORD_DELTA_QUERY_RESPONSE = {
    "_shards": {"failed": 0, "skipped": 0, "successful": 5, "total": 5},
    "aggregations": {
        "by_day": {
            "buckets": [
                {
                    "access_statuses": {
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
                    "affiliations": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "affiliations_1": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "file_types": {
                        "buckets": [
                            {
                                "doc_count": 1,
                                "key": "pdf",
                                "with_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                                "total_bytes": {"value": 458036.0},
                            }
                        ],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "funders_id": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "funders_keyword": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "languages": {
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
                    "rights": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "periodicals": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "publishers": {
                        "buckets": [
                            {
                                "doc_count": 1,
                                "file_count": {"value": 1},
                                "key": "Knowledge Commons",
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
                    "resource_types": {
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
                    "subjects": {
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
                    "access_statuses": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "affiliations": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "affiliations_1": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "file_types": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "funders": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "languages": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "rights": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "periodicals": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "publishers": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "resource_types": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "subjects": {
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
                    "access_statuses": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "affiliations": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "affiliations_1": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "file_types": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "funders": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "languages": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "rights": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "periodicals": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "publishers": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "resource_types": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "subjects": {
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
                    "access_statuses": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "affiliations": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "affiliations_1": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "file_types": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "funders": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "languages": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "rights": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "periodicals": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "publishers": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "resource_types": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "subjects": {
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
                    "access_statuses": {
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
                    "affiliations": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "affiliations_1": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "file_types": {
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
                    "funders_id": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "funders_keyword": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "languages": {
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
                    "rights": {
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
                    "periodicals": {
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
                    "publishers": {
                        "buckets": [
                            {
                                "doc_count": 1,
                                "file_count": {"value": 1},
                                "key": "Knowledge Commons",
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
                    "resource_types": {
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
                    "subjects": {
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
