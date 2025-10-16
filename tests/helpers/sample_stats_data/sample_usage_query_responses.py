# Part of the Invenio-Stats-Dashboard extension for InvenioRDM
# Copyright (C) 2025 Mesh Research
#
# Invenio-Stats-Dashboard is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Sample usage query responses."""

MOCK_USAGE_QUERY_RESPONSE_VIEWS = {
    "aggregations": {
        "access_statuses": {
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
        "affiliations_id": {
            "buckets": [
                {
                    "key": "013v4ng57",
                    "doc_count": 20,
                    "total_events": {"value": 20},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                    "label": {
                        "hits": {
                            "total": {"value": 20, "relation": "eq"},
                            "max_score": 1.006192,
                            "hits": [
                                {
                                    "_index": "events-stats-record-view-2025-07",
                                    "_score": 1.006192,
                                    "_source": {
                                        "affiliations": [
                                            [{"name": "San Francisco Public Library"}],
                                            [{"name": "San Francisco Public Library"}],
                                            [
                                                {
                                                    "name": (
                                                        "San Francisco Public Library"
                                                    ),
                                                    "id": "013v4ng57",
                                                }
                                            ],
                                            [{"name": "San Francisco Public Library"}],
                                        ]
                                    },
                                }
                            ],
                        }
                    },
                },
                {
                    "key": "03rmrcq20",
                    "doc_count": 20,
                    "total_events": {"value": 20},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                    "label": {
                        "hits": {
                            "total": {"value": 20, "relation": "eq"},
                            "max_score": 1.006192,
                            "hits": [
                                {
                                    "_index": "events-stats-record-view-2025-07",
                                    "_score": 1.006192,
                                    "_source": {
                                        "affiliations": [
                                            [
                                                {
                                                    "name": (
                                                        "University Of British Columbia"
                                                    )
                                                }
                                            ],
                                            [
                                                {
                                                    "name": (
                                                        "University of British Columbia"
                                                    ),
                                                    "id": "03rmrcq20",
                                                }
                                            ],
                                        ]
                                    },
                                }
                            ],
                        }
                    },
                },
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "affiliations_name": {
            "buckets": [
                {
                    "key": "Henry Ford College",
                    "doc_count": 20,
                    "total_events": {"value": 20},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                    "label": {
                        "hits": {
                            "total": {"value": 20, "relation": "eq"},
                            "max_score": 1.006192,
                            "hits": [
                                {
                                    "_index": "events-stats-record-view-2025-07",
                                    "_score": 1.006192,
                                    "_source": {
                                        "affiliations": [
                                            [{"name": "Henry Ford College"}]
                                        ]
                                    },
                                }
                            ],
                        }
                    },
                },
                {
                    "key": "San Francisco Public Library",
                    "doc_count": 20,
                    "total_events": {"value": 20},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                    "label": {
                        "hits": {
                            "total": {"value": 20, "relation": "eq"},
                            "max_score": 1.006192,
                            "hits": [
                                {
                                    "_index": "events-stats-record-view-2025-07",
                                    "_score": 1.006192,
                                    "_source": {
                                        "affiliations": [
                                            [{"name": "San Francisco Public Library"}],
                                            [{"name": "San Francisco Public Library"}],
                                            [
                                                {
                                                    "name": (
                                                        "San Francisco Public Library"
                                                    ),
                                                    "id": "013v4ng57",
                                                }
                                            ],
                                            [{"name": "San Francisco Public Library"}],
                                        ]
                                    },
                                }
                            ],
                        }
                    },
                },
                {
                    "key": "University Of British Columbia",
                    "doc_count": 20,
                    "total_events": {"value": 20},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                    "label": {
                        "hits": {
                            "total": {"value": 20, "relation": "eq"},
                            "max_score": 1.006192,
                            "hits": [
                                {
                                    "_index": "events-stats-record-view-2025-07",
                                    "_score": 1.006192,
                                    "_source": {
                                        "affiliations": [
                                            [
                                                {
                                                    "name": (
                                                        "University Of British Columbia"
                                                    )
                                                }
                                            ],
                                            [
                                                {
                                                    "name": (
                                                        "University of British Columbia"
                                                    ),
                                                    "id": "03rmrcq20",
                                                }
                                            ],
                                        ]
                                    },
                                }
                            ],
                        }
                    },
                },
                {
                    "key": "University of British Columbia",
                    "doc_count": 20,
                    "total_events": {"value": 20},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                    "label": {
                        "hits": {
                            "total": {"value": 20, "relation": "eq"},
                            "max_score": 1.006192,
                            "hits": [
                                {
                                    "_index": "events-stats-record-view-2025-07",
                                    "_score": 1.006192,
                                    "_source": {
                                        "affiliations": [
                                            [
                                                {
                                                    "name": (
                                                        "University Of British Columbia"
                                                    )
                                                }
                                            ],
                                            [
                                                {
                                                    "name": (
                                                        "University of British Columbia"
                                                    ),
                                                    "id": "03rmrcq20",
                                                }
                                            ],
                                        ]
                                    },
                                }
                            ],
                        }
                    },
                },
                {
                    "key": "University of Missouri - St. Louis",
                    "doc_count": 20,
                    "total_events": {"value": 20},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                    "label": {
                        "hits": {
                            "total": {"value": 20, "relation": "eq"},
                            "max_score": 1.006192,
                            "hits": [
                                {
                                    "_index": "events-stats-record-view-2025-07",
                                    "_score": 1.006192,
                                    "_source": {
                                        "affiliations": [
                                            [
                                                {
                                                    "name": (
                                                        "University of Missouri - St. Louis"
                                                    )
                                                }
                                            ]
                                        ]
                                    },
                                }
                            ],
                        }
                    },
                },
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "countries": {
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
        "file_types": {
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
        "funders_id": {
            "buckets": [
                {
                    "doc_count": 40,
                    "key": "00k4n6c31",
                    "total_events": {"value": 40},
                    "unique_parents": {"value": 2},
                    "unique_records": {"value": 2},
                    "unique_visitors": {"value": 40},
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_index": "events-stats-record-view-2025-07",
                                    "_score": 1.006192,
                                    "_source": {
                                        "funders": [
                                            {
                                                "id": "00k4n6c31",
                                                "name": "Funder 00k4n6c31",
                                            }
                                        ]
                                    },
                                }
                            ],
                            "max_score": 1.006192,
                            "total": {"relation": "eq", "value": 40},
                        }
                    },
                },
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "funders_name": {
            "buckets": [
                {
                    "doc_count": 40,
                    "key": "Funder 00k4n6c31",
                    "total_events": {"value": 40},
                    "unique_parents": {"value": 2},
                    "unique_records": {"value": 2},
                    "unique_visitors": {"value": 40},
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_index": "events-stats-record-view-2025-07",
                                    "_score": 1.006192,
                                    "_source": {
                                        "funders": [
                                            {
                                                "id": "00k4n6c31",
                                                "name": "Funder 00k4n6c31",
                                            }
                                        ]
                                    },
                                }
                            ],
                            "max_score": 1.006192,
                            "total": {"relation": "eq", "value": 40},
                        }
                    },
                },
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "languages": {
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
        "rights": {
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
        "periodicals": {
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
        "publishers": {
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
        "referrers": {
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
        "resource_types": {
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
                                            "title": {"en": "Journal Article"},
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
                                            "title": {"en": "Book Section"},
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
        "subjects": {
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
                                                ),
                                                "subject": (
                                                    "English language--Written English--History"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911660"
                                                ),
                                                "subject": (
                                                    "English language--Spoken English--Research"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845111"
                                                ),
                                                "subject": "Canadian literature",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845142"
                                                ),
                                                "subject": (
                                                    "Canadian literature--Periodicals"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845184"
                                                ),
                                                "subject": "Canadian prose literature",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/1424786"
                                                ),
                                                "subject": (
                                                    "Canadian literature--Bibliography"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/934875"
                                                ),
                                                "subject": "French-Canadian literature",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/817954"
                                                ),
                                                "subject": "Arts, Canadian",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/821870"
                                                ),
                                                "subject": "Authors, Canadian",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845170"
                                                ),
                                                "subject": "Canadian periodicals",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911328"
                                                ),
                                                "subject": (
                                                    "English language--Lexicography--History"
                                                ),
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
                                                ),
                                                "subject": "Library science",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/2060143"
                                                ),
                                                "subject": "Mass incarceration",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997987"
                                                ),
                                                "subject": "Library science literature",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997974"
                                                ),
                                                "subject": "Library science--Standards",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/855500"
                                                ),
                                                "subject": (
                                                    "Children of prisoners--Services for"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/995415"
                                                ),
                                                "subject": (
                                                    "Legal assistance to prisoners--U.S. states"
                                                ),
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
                                                ),
                                                "subject": (
                                                    "English language--Written English--History"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911660"
                                                ),
                                                "subject": (
                                                    "English language--Spoken English--Research"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845111"
                                                ),
                                                "subject": "Canadian literature",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845142"
                                                ),
                                                "subject": (
                                                    "Canadian literature--Periodicals"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845184"
                                                ),
                                                "subject": "Canadian prose literature",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/1424786"
                                                ),
                                                "subject": (
                                                    "Canadian literature--Bibliography"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/934875"
                                                ),
                                                "subject": "French-Canadian literature",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/817954"
                                                ),
                                                "subject": "Arts, Canadian",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/821870"
                                                ),
                                                "subject": "Authors, Canadian",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845170"
                                                ),
                                                "subject": "Canadian periodicals",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911328"
                                                ),
                                                "subject": (
                                                    "English language--Lexicography--History"
                                                ),
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
                                                ),
                                                "subject": (
                                                    "English language--Written English--History"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911660"
                                                ),
                                                "subject": (
                                                    "English language--Spoken English--Research"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845111"
                                                ),
                                                "subject": "Canadian literature",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845142"
                                                ),
                                                "subject": (
                                                    "Canadian literature--Periodicals"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845184"
                                                ),
                                                "subject": "Canadian prose literature",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/1424786"
                                                ),
                                                "subject": (
                                                    "Canadian literature--Bibliography"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/934875"
                                                ),
                                                "subject": "French-Canadian literature",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/817954"
                                                ),
                                                "subject": "Arts, Canadian",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/821870"
                                                ),
                                                "subject": "Authors, Canadian",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845170"
                                                ),
                                                "subject": "Canadian periodicals",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911328"
                                                ),
                                                "subject": (
                                                    "English language--Lexicography--History"
                                                ),
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
                                                ),
                                                "subject": (
                                                    "English language--Written English--History"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911660"
                                                ),
                                                "subject": (
                                                    "English language--Spoken English--Research"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845111"
                                                ),
                                                "subject": "Canadian literature",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845142"
                                                ),
                                                "subject": (
                                                    "Canadian literature--Periodicals"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845184"
                                                ),
                                                "subject": "Canadian prose literature",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/1424786"
                                                ),
                                                "subject": (
                                                    "Canadian literature--Bibliography"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/934875"
                                                ),
                                                "subject": "French-Canadian literature",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/817954"
                                                ),
                                                "subject": "Arts, Canadian",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/821870"
                                                ),
                                                "subject": "Authors, Canadian",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845170"
                                                ),
                                                "subject": "Canadian periodicals",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911328"
                                                ),
                                                "subject": (
                                                    "English language--Lexicography--History"
                                                ),
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
                                                ),
                                                "subject": (
                                                    "English language--Written English--History"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911660"
                                                ),
                                                "subject": (
                                                    "English language--Spoken English--Research"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845111"
                                                ),
                                                "subject": "Canadian literature",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845142"
                                                ),
                                                "subject": (
                                                    "Canadian literature--Periodicals"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845184"
                                                ),
                                                "subject": "Canadian prose literature",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/1424786"
                                                ),
                                                "subject": (
                                                    "Canadian literature--Bibliography"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/934875"
                                                ),
                                                "subject": "French-Canadian literature",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/817954"
                                                ),
                                                "subject": "Arts, Canadian",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/821870"
                                                ),
                                                "subject": "Authors, Canadian",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845170"
                                                ),
                                                "subject": "Canadian periodicals",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911328"
                                                ),
                                                "subject": (
                                                    "English language--Lexicography--History"
                                                ),
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
                                                ),
                                                "subject": (
                                                    "English language--Written English--History"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911660"
                                                ),
                                                "subject": (
                                                    "English language--Spoken English--Research"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845111"
                                                ),
                                                "subject": "Canadian literature",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845142"
                                                ),
                                                "subject": (
                                                    "Canadian literature--Periodicals"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845184"
                                                ),
                                                "subject": "Canadian prose literature",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/1424786"
                                                ),
                                                "subject": (
                                                    "Canadian literature--Bibliography"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/934875"
                                                ),
                                                "subject": "French-Canadian literature",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/817954"
                                                ),
                                                "subject": "Arts, Canadian",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/821870"
                                                ),
                                                "subject": "Authors, Canadian",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845170"
                                                ),
                                                "subject": "Canadian periodicals",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911328"
                                                ),
                                                "subject": (
                                                    "English language--Lexicography--History"
                                                ),
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
                                                ),
                                                "subject": (
                                                    "English language--Written English--History"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911660"
                                                ),
                                                "subject": (
                                                    "English language--Spoken English--Research"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845111"
                                                ),
                                                "subject": "Canadian literature",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845142"
                                                ),
                                                "subject": (
                                                    "Canadian literature--Periodicals"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845184"
                                                ),
                                                "subject": "Canadian prose literature",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/1424786"
                                                ),
                                                "subject": (
                                                    "Canadian literature--Bibliography"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/934875"
                                                ),
                                                "subject": "French-Canadian literature",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/817954"
                                                ),
                                                "subject": "Arts, Canadian",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/821870"
                                                ),
                                                "subject": "Authors, Canadian",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845170"
                                                ),
                                                "subject": "Canadian periodicals",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911328"
                                                ),
                                                "subject": (
                                                    "English language--Lexicography--History"
                                                ),
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
                                                ),
                                                "subject": "Library science",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/2060143"
                                                ),
                                                "subject": "Mass incarceration",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997987"
                                                ),
                                                "subject": "Library science literature",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997974"
                                                ),
                                                "subject": "Library science--Standards",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/855500"
                                                ),
                                                "subject": (
                                                    "Children of prisoners--Services for"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/995415"
                                                ),
                                                "subject": (
                                                    "Legal assistance to prisoners--U.S. states"
                                                ),
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
                                                ),
                                                "subject": (
                                                    "English language--Written English--History"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911660"
                                                ),
                                                "subject": (
                                                    "English language--Spoken English--Research"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845111"
                                                ),
                                                "subject": "Canadian literature",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845142"
                                                ),
                                                "subject": (
                                                    "Canadian literature--Periodicals"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845184"
                                                ),
                                                "subject": "Canadian prose literature",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/1424786"
                                                ),
                                                "subject": (
                                                    "Canadian literature--Bibliography"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/934875"
                                                ),
                                                "subject": "French-Canadian literature",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/817954"
                                                ),
                                                "subject": "Arts, Canadian",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/821870"
                                                ),
                                                "subject": "Authors, Canadian",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845170"
                                                ),
                                                "subject": "Canadian periodicals",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911328"
                                                ),
                                                "subject": (
                                                    "English language--Lexicography--History"
                                                ),
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
                                                ),
                                                "subject": (
                                                    "English language--Written English--History"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911660"
                                                ),
                                                "subject": (
                                                    "English language--Spoken English--Research"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845111"
                                                ),
                                                "subject": "Canadian literature",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845142"
                                                ),
                                                "subject": (
                                                    "Canadian literature--Periodicals"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845184"
                                                ),
                                                "subject": "Canadian prose literature",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/1424786"
                                                ),
                                                "subject": (
                                                    "Canadian literature--Bibliography"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/934875"
                                                ),
                                                "subject": "French-Canadian literature",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/817954"
                                                ),
                                                "subject": "Arts, Canadian",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/821870"
                                                ),
                                                "subject": "Authors, Canadian",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845170"
                                                ),
                                                "subject": "Canadian periodicals",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911328"
                                                ),
                                                "subject": (
                                                    "English language--Lexicography--History"
                                                ),
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
                                                ),
                                                "subject": (
                                                    "English language--Written English--History"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911660"
                                                ),
                                                "subject": (
                                                    "English language--Spoken English--Research"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845111"
                                                ),
                                                "subject": "Canadian literature",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845142"
                                                ),
                                                "subject": (
                                                    "Canadian literature--Periodicals"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845184"
                                                ),
                                                "subject": "Canadian prose literature",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/1424786"
                                                ),
                                                "subject": (
                                                    "Canadian literature--Bibliography"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/934875"
                                                ),
                                                "subject": "French-Canadian literature",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/817954"
                                                ),
                                                "subject": "Arts, Canadian",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/821870"
                                                ),
                                                "subject": "Authors, Canadian",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845170"
                                                ),
                                                "subject": "Canadian periodicals",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911328"
                                                ),
                                                "subject": (
                                                    "English language--Lexicography--History"
                                                ),
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
                                                ),
                                                "subject": (
                                                    "English language--Written English--History"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911660"
                                                ),
                                                "subject": (
                                                    "English language--Spoken English--Research"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845111"
                                                ),
                                                "subject": "Canadian literature",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845142"
                                                ),
                                                "subject": (
                                                    "Canadian literature--Periodicals"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845184"
                                                ),
                                                "subject": "Canadian prose literature",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/1424786"
                                                ),
                                                "subject": (
                                                    "Canadian literature--Bibliography"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/934875"
                                                ),
                                                "subject": "French-Canadian literature",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/817954"
                                                ),
                                                "subject": "Arts, Canadian",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/821870"
                                                ),
                                                "subject": "Authors, Canadian",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/845170"
                                                ),
                                                "subject": "Canadian periodicals",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/911328"
                                                ),
                                                "subject": (
                                                    "English language--Lexicography--History"
                                                ),
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
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/973589"
                                                ),
                                                "subject": (
                                                    "Inklings (Group of writers)"
                                                ),
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
                                                ),
                                                "subject": "Library science",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/2060143"
                                                ),
                                                "subject": "Mass incarceration",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997987"
                                                ),
                                                "subject": "Library science literature",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997974"
                                                ),
                                                "subject": "Library science--Standards",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/855500"
                                                ),
                                                "subject": (
                                                    "Children of prisoners--Services for"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/995415"
                                                ),
                                                "subject": (
                                                    "Legal assistance to prisoners--U.S. states"
                                                ),
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
                                                ),
                                                "subject": "Library science",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/2060143"
                                                ),
                                                "subject": "Mass incarceration",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997987"
                                                ),
                                                "subject": "Library science literature",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997974"
                                                ),
                                                "subject": "Library science--Standards",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/855500"
                                                ),
                                                "subject": (
                                                    "Children of prisoners--Services for"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/995415"
                                                ),
                                                "subject": (
                                                    "Legal assistance to prisoners--U.S. states"
                                                ),
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
                                                ),
                                                "subject": "Library science",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/2060143"
                                                ),
                                                "subject": "Mass incarceration",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997987"
                                                ),
                                                "subject": "Library science literature",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997974"
                                                ),
                                                "subject": "Library science--Standards",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/855500"
                                                ),
                                                "subject": (
                                                    "Children of prisoners--Services for"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/995415"
                                                ),
                                                "subject": (
                                                    "Legal assistance to prisoners--U.S. states"
                                                ),
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
                                                ),
                                                "subject": "Library science",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/2060143"
                                                ),
                                                "subject": "Mass incarceration",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997987"
                                                ),
                                                "subject": "Library science literature",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997974"
                                                ),
                                                "subject": "Library science--Standards",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/855500"
                                                ),
                                                "subject": (
                                                    "Children of prisoners--Services for"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/995415"
                                                ),
                                                "subject": (
                                                    "Legal assistance to prisoners--U.S. states"
                                                ),
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

MOCK_USAGE_QUERY_RESPONSE_DOWNLOADS = {
    "aggregations": {
        "access_statuses": {
            "buckets": [
                {
                    "doc_count": 60,
                    "key": "open",
                    "total_events": {"value": 60},
                    "total_volume": {"value": 1222055600.0},
                    "unique_files": {"value": 3},
                    "unique_parents": {"value": 3},
                    "unique_records": {"value": 3},
                    "unique_visitors": {"value": 60},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "affiliations_id": {
            "buckets": [
                {
                    "key": "013v4ng57",
                    "doc_count": 20,
                    "total_events": {"value": 20},
                    "total_volume": {"value": 9160720.0},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                    "unique_files": {"value": 1},
                    "label": {
                        "hits": {
                            "total": {"value": 20, "relation": "eq"},
                            "max_score": 1.0082304,
                            "hits": [
                                {
                                    "_index": "events-stats-file-download-2025-07",
                                    "_score": 1.0082304,
                                    "_source": {
                                        "affiliations": [
                                            [{"name": "San Francisco Public Library"}],
                                            [{"name": "San Francisco Public Library"}],
                                            [
                                                {
                                                    "name": (
                                                        "San Francisco Public Library"
                                                    ),
                                                    "id": "013v4ng57",
                                                }
                                            ],
                                            [{"name": "San Francisco Public Library"}],
                                        ]
                                    },
                                }
                            ],
                        }
                    },
                }
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "affiliations_name": {
            "buckets": [
                {
                    "key": "Henry Ford College",
                    "doc_count": 20,
                    "total_events": {"value": 20},
                    "total_volume": {"value": 39698980.0},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                    "unique_files": {"value": 1},
                    "label": {
                        "hits": {
                            "total": {"value": 20, "relation": "eq"},
                            "max_score": 1.0082304,
                            "hits": [
                                {
                                    "_index": "events-stats-file-download-2025-07",
                                    "_score": 1.0082304,
                                    "_source": {
                                        "affiliations": [
                                            [{"name": "Henry Ford College"}]
                                        ]
                                    },
                                }
                            ],
                        }
                    },
                },
                {
                    "key": "San Francisco Public Library",
                    "doc_count": 20,
                    "total_events": {"value": 20},
                    "total_volume": {"value": 9160720.0},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                    "unique_files": {"value": 1},
                    "label": {
                        "hits": {
                            "total": {"value": 20, "relation": "eq"},
                            "max_score": 1.0082304,
                            "hits": [
                                {
                                    "_index": "events-stats-file-download-2025-07",
                                    "_score": 1.0082304,
                                    "_source": {
                                        "affiliations": [
                                            [{"name": "San Francisco Public Library"}],
                                            [{"name": "San Francisco Public Library"}],
                                            [
                                                {
                                                    "name": (
                                                        "San Francisco Public Library"
                                                    ),
                                                    "id": "013v4ng57",
                                                }
                                            ],
                                            [{"name": "San Francisco Public Library"}],
                                        ]
                                    },
                                }
                            ],
                        }
                    },
                },
                {
                    "key": "University of Missouri - St. Louis",
                    "doc_count": 20,
                    "total_events": {"value": 20},
                    "total_volume": {"value": 1173195900.0},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                    "unique_files": {"value": 1},
                    "label": {
                        "hits": {
                            "total": {"value": 20, "relation": "eq"},
                            "max_score": 1.0082304,
                            "hits": [
                                {
                                    "_index": "events-stats-file-download-2025-07",
                                    "_score": 1.0082304,
                                    "_source": {
                                        "affiliations": [
                                            [
                                                {
                                                    "name": (
                                                        "University of Missouri - St. Louis"
                                                    )
                                                }
                                            ]
                                        ]
                                    },
                                }
                            ],
                        }
                    },
                },
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "countries": {
            "buckets": [
                {
                    "doc_count": 35,
                    "key": "NL",
                    "total_events": {"value": 35},
                    "total_volume": {"value": 97423133.0},
                    "unique_files": {"value": 3},
                    "unique_parents": {"value": 3},
                    "unique_records": {"value": 3},
                    "unique_visitors": {"value": 35},
                },
                {
                    "doc_count": 12,
                    "key": "US",
                    "total_events": {"value": 12},
                    "total_volume": {"value": 25424717.0},
                    "unique_files": {"value": 3},
                    "unique_parents": {"value": 3},
                    "unique_records": {"value": 3},
                    "unique_visitors": {"value": 12},
                },
                {
                    "doc_count": 9,
                    "key": "CN",
                    "total_events": {"value": 9},
                    "total_volume": {"value": 18361498.0},
                    "unique_files": {"value": 3},
                    "unique_parents": {"value": 3},
                    "unique_records": {"value": 3},
                    "unique_visitors": {"value": 9},
                },
                {
                    "doc_count": 2,
                    "key": "AU",
                    "total_events": {"value": 2},
                    "total_volume": {"value": 2791887.0},
                    "unique_files": {"value": 1},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 2},
                },
                {
                    "doc_count": 2,
                    "key": "JP",
                    "total_events": {"value": 2},
                    "total_volume": {"value": 1984949.0},
                    "unique_files": {"value": 1},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 2},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "file_types": {
            "buckets": [
                {
                    "doc_count": 60,
                    "key": "pdf",
                    "total_events": {"value": 60},
                    "total_volume": {"value": 1222055600.0},
                    "unique_files": {"value": 3},
                    "unique_parents": {"value": 3},
                    "unique_records": {"value": 3},
                    "unique_visitors": {"value": 60},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "funders_id": {
            "buckets": [
                {
                    "key": "00k4n6c31",
                    "doc_count": 20,
                    "total_events": {"value": 20},
                    "total_volume": {"value": 39698980.0},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                    "unique_files": {"value": 1},
                    "label": {
                        "hits": {
                            "total": {"value": 20, "relation": "eq"},
                            "max_score": 1.0082304,
                            "hits": [
                                {
                                    "_index": "events-stats-file-download-2025-07",
                                    "_score": 1.0082304,
                                    "_source": {
                                        "funders": [
                                            {
                                                "name": "Funder 00k4n6c31",
                                                "id": "00k4n6c31",
                                            }
                                        ]
                                    },
                                }
                            ],
                        }
                    },
                }
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "funders_name": {
            "buckets": [
                {
                    "doc_count": 20,
                    "key": "Funder 00k4n6c31",
                    "total_events": {"value": 20},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_index": "events-stats-file-download-2025-07",
                                    "_score": 1.0082304,
                                    "_source": {
                                        "funders": [
                                            {
                                                "id": "00k4n6c31",
                                                "name": "Funder 00k4n6c31",
                                            }
                                        ]
                                    },
                                }
                            ],
                            "max_score": 1.0082304,
                            "total": {"relation": "eq", "value": 20},
                        }
                    },
                    "total_volume": {"value": 39698980.0},
                    "unique_files": {"value": 1},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "languages": {
            "buckets": [
                {
                    "doc_count": 40,
                    "key": "eng",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": (
                                        "2025-07-03T22:22:03-84b1e4e885f0f768ad5b6c53995733c20ed4d8e8"
                                    ),
                                    "_index": "events-stats-file-download-2025-07",
                                    "_score": 1.0082304,
                                    "_source": {
                                        "languages": [
                                            {"id": "eng", "title": {"en": "English"}}
                                        ]
                                    },
                                }
                            ],
                            "max_score": 1.0082304,
                            "total": {"relation": "eq", "value": 40},
                        }
                    },
                    "total_events": {"value": 40},
                    "total_volume": {"value": 48859700.0},
                    "unique_files": {"value": 2},
                    "unique_parents": {"value": 2},
                    "unique_records": {"value": 2},
                    "unique_visitors": {"value": 40},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "rights": {
            "buckets": [
                {
                    "doc_count": 20,
                    "key": "cc-by-sa-4.0",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": (
                                        "2025-07-03T22:22:03-84b1e4e885f0f768ad5b6c53995733c20ed4d8e8"
                                    ),
                                    "_index": "events-stats-file-download-2025-07",
                                    "_score": 1.0082304,
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
                            "max_score": 1.0082304,
                            "total": {"relation": "eq", "value": 20},
                        }
                    },
                    "total_events": {"value": 20},
                    "total_volume": {"value": 39698980.0},
                    "unique_files": {"value": 1},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "periodicals": {
            "buckets": [
                {
                    "doc_count": 20,
                    "key": "N/A",
                    "total_events": {"value": 20},
                    "total_volume": {"value": 39698980.0},
                    "unique_files": {"value": 1},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "publishers": {
            "buckets": [
                {
                    "doc_count": 40,
                    "key": "Knowledge Commons",
                    "total_events": {"value": 40},
                    "total_volume": {"value": 48859700.0},
                    "unique_files": {"value": 2},
                    "unique_parents": {"value": 2},
                    "unique_records": {"value": 2},
                    "unique_visitors": {"value": 40},
                },
                {
                    "doc_count": 20,
                    "key": "Apocryphile Press",
                    "total_events": {"value": 20},
                    "total_volume": {"value": 1173195900.0},
                    "unique_files": {"value": 1},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "referrers": {
            "buckets": [
                {
                    "doc_count": 20,
                    "key": "https://example.com/records/4x8hh-e0g68",
                    "total_events": {"value": 20},
                    "total_volume": {"value": 9160720.0},
                    "unique_files": {"value": 1},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                },
                {
                    "doc_count": 20,
                    "key": "https://example.com/records/exhns-k5m92",
                    "total_events": {"value": 20},
                    "total_volume": {"value": 39698980.0},
                    "unique_files": {"value": 1},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                },
                {
                    "doc_count": 20,
                    "key": "https://example.com/records/sjyew-71w43",
                    "total_events": {"value": 20},
                    "total_volume": {"value": 1173195900.0},
                    "unique_files": {"value": 1},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "resource_types": {
            "buckets": [
                {
                    "doc_count": 40,
                    "key": "textDocument-journalArticle",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": (
                                        "2025-07-03T22:22:03-84b1e4e885f0f768ad5b6c53995733c20ed4d8e8"
                                    ),
                                    "_index": "events-stats-file-download-2025-07",
                                    "_score": 1.0082304,
                                    "_source": {
                                        "resource_type": {
                                            "id": "textDocument-journalArticle",
                                            "title": {"en": "Journal Article"},
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0082304,
                            "total": {"relation": "eq", "value": 40},
                        }
                    },
                    "total_events": {"value": 40},
                    "total_volume": {"value": 48859700.0},
                    "unique_files": {"value": 2},
                    "unique_parents": {"value": 2},
                    "unique_records": {"value": 2},
                    "unique_visitors": {"value": 40},
                },
                {
                    "doc_count": 20,
                    "key": "textDocument-bookSection",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": (
                                        "2025-07-03T03:34:59-56efb173eaf90a51112c5574d29a905536b39878"
                                    ),
                                    "_index": "events-stats-file-download-2025-07",
                                    "_score": 1.0082304,
                                    "_source": {
                                        "resource_type": {
                                            "id": "textDocument-bookSection",
                                            "title": {"en": "Book Section"},
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0082304,
                            "total": {"relation": "eq", "value": 20},
                        }
                    },
                    "total_events": {"value": 20},
                    "total_volume": {"value": 1173195900.0},
                    "unique_files": {"value": 1},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "subjects": {
            "buckets": [
                {
                    "doc_count": 20,
                    "key": "http://id.worldcat.org/fast/2060143",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": (
                                        "2025-07-03T08:14:55-9deb53f7a85851587f5d527760049042cbf7ccc2"
                                    ),
                                    "_index": "events-stats-file-download-2025-07",
                                    "_score": 1.0082304,
                                    "_source": {
                                        "subjects": [
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997916"
                                                ),
                                                "subject": "Library science",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/2060143"
                                                ),
                                                "subject": "Mass incarceration",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997987"
                                                ),
                                                "subject": (
                                                    "Library science literature"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997974"
                                                ),
                                                "subject": (
                                                    "Library science--Standards"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/855500"
                                                ),
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
                                                "subject": (
                                                    "Legal "
                                                    "assistance "
                                                    "to "
                                                    "prisoners--U.S. "
                                                    "states"
                                                ),
                                            },
                                        ]
                                    },
                                }
                            ],
                            "max_score": 1.0082304,
                            "total": {"relation": "eq", "value": 20},
                        }
                    },
                    "total_events": {"value": 20},
                    "total_volume": {"value": 9160720.0},
                    "unique_files": {"value": 1},
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
                                        "2025-07-03T08:14:55-9deb53f7a85851587f5d527760049042cbf7ccc2"
                                    ),
                                    "_index": "events-stats-file-download-2025-07",
                                    "_score": 1.0082304,
                                    "_source": {
                                        "subjects": [
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997916"
                                                ),
                                                "subject": "Library science",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/2060143"
                                                ),
                                                "subject": "Mass incarceration",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997987"
                                                ),
                                                "subject": (
                                                    "Library science literature"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997974"
                                                ),
                                                "subject": (
                                                    "Library science--Standards"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/855500"
                                                ),
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
                                                "subject": (
                                                    "Legal "
                                                    "assistance "
                                                    "to "
                                                    "prisoners--U.S. "
                                                    "states"
                                                ),
                                            },
                                        ]
                                    },
                                }
                            ],
                            "max_score": 1.0082304,
                            "total": {"relation": "eq", "value": 20},
                        }
                    },
                    "total_events": {"value": 20},
                    "total_volume": {"value": 9160720.0},
                    "unique_files": {"value": 1},
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
                                        "2025-07-03T03:34:59-56efb173eaf90a51112c5574d29a905536b39878"
                                    ),
                                    "_index": "events-stats-file-download-2025-07",
                                    "_score": 1.0082304,
                                    "_source": {
                                        "subjects": [
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/973589"
                                                ),
                                                "subject": (
                                                    "Inklings (Group of writers)"
                                                ),
                                            }
                                        ]
                                    },
                                }
                            ],
                            "max_score": 1.0082304,
                            "total": {"relation": "eq", "value": 20},
                        }
                    },
                    "total_events": {"value": 20},
                    "total_volume": {"value": 1173195900.0},
                    "unique_files": {"value": 1},
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
                                        "2025-07-03T08:14:55-9deb53f7a85851587f5d527760049042cbf7ccc2"
                                    ),
                                    "_index": "events-stats-file-download-2025-07",
                                    "_score": 1.0082304,
                                    "_source": {
                                        "subjects": [
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997916"
                                                ),
                                                "subject": "Library science",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/2060143"
                                                ),
                                                "subject": "Mass incarceration",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997987"
                                                ),
                                                "subject": (
                                                    "Library science literature"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997974"
                                                ),
                                                "subject": (
                                                    "Library science--Standards"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/855500"
                                                ),
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
                                                "subject": (
                                                    "Legal "
                                                    "assistance "
                                                    "to "
                                                    "prisoners--U.S. "
                                                    "states"
                                                ),
                                            },
                                        ]
                                    },
                                }
                            ],
                            "max_score": 1.0082304,
                            "total": {"relation": "eq", "value": 20},
                        }
                    },
                    "total_events": {"value": 20},
                    "total_volume": {"value": 9160720.0},
                    "unique_files": {"value": 1},
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
                                        "2025-07-03T08:14:55-9deb53f7a85851587f5d527760049042cbf7ccc2"
                                    ),
                                    "_index": "events-stats-file-download-2025-07",
                                    "_score": 1.0082304,
                                    "_source": {
                                        "subjects": [
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997916"
                                                ),
                                                "subject": "Library science",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/2060143"
                                                ),
                                                "subject": "Mass incarceration",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997987"
                                                ),
                                                "subject": (
                                                    "Library science literature"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997974"
                                                ),
                                                "subject": (
                                                    "Library science--Standards"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/855500"
                                                ),
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
                                                "subject": (
                                                    "Legal "
                                                    "assistance "
                                                    "to "
                                                    "prisoners--U.S. "
                                                    "states"
                                                ),
                                            },
                                        ]
                                    },
                                }
                            ],
                            "max_score": 1.0082304,
                            "total": {"relation": "eq", "value": 20},
                        }
                    },
                    "total_events": {"value": 20},
                    "total_volume": {"value": 9160720.0},
                    "unique_files": {"value": 1},
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
                                        "2025-07-03T08:14:55-9deb53f7a85851587f5d527760049042cbf7ccc2"
                                    ),
                                    "_index": "events-stats-file-download-2025-07",
                                    "_score": 1.0082304,
                                    "_source": {
                                        "subjects": [
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997916"
                                                ),
                                                "subject": "Library science",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/2060143"
                                                ),
                                                "subject": "Mass incarceration",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997987"
                                                ),
                                                "subject": (
                                                    "Library science literature"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997974"
                                                ),
                                                "subject": (
                                                    "Library science--Standards"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/855500"
                                                ),
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
                                                "subject": (
                                                    "Legal "
                                                    "assistance "
                                                    "to "
                                                    "prisoners--U.S. "
                                                    "states"
                                                ),
                                            },
                                        ]
                                    },
                                }
                            ],
                            "max_score": 1.0082304,
                            "total": {"relation": "eq", "value": 20},
                        }
                    },
                    "total_events": {"value": 20},
                    "total_volume": {"value": 9160720.0},
                    "unique_files": {"value": 1},
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
                                        "2025-07-03T08:14:55-9deb53f7a85851587f5d527760049042cbf7ccc2"
                                    ),
                                    "_index": "events-stats-file-download-2025-07",
                                    "_score": 1.0082304,
                                    "_source": {
                                        "subjects": [
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997916"
                                                ),
                                                "subject": "Library science",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/2060143"
                                                ),
                                                "subject": "Mass incarceration",
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997987"
                                                ),
                                                "subject": (
                                                    "Library science literature"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/997974"
                                                ),
                                                "subject": (
                                                    "Library science--Standards"
                                                ),
                                            },
                                            {
                                                "id": (
                                                    "http://id.worldcat.org/fast/855500"
                                                ),
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
                                                "subject": (
                                                    "Legal "
                                                    "assistance "
                                                    "to "
                                                    "prisoners--U.S. "
                                                    "states"
                                                ),
                                            },
                                        ]
                                    },
                                }
                            ],
                            "max_score": 1.0082304,
                            "total": {"relation": "eq", "value": 20},
                        }
                    },
                    "total_events": {"value": 20},
                    "total_volume": {"value": 9160720.0},
                    "unique_files": {"value": 1},
                    "unique_parents": {"value": 1},
                    "unique_records": {"value": 1},
                    "unique_visitors": {"value": 20},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "total_events": {"value": 60},
        "total_volume": {"value": 1222055600.0},
        "unique_files": {"value": 3},
        "unique_parents": {"value": 3},
        "unique_records": {"value": 3},
        "unique_visitors": {"value": 60},
    },
    "hits": {"hits": [], "max_score": None, "total": {"relation": "eq", "value": 0}},
}
