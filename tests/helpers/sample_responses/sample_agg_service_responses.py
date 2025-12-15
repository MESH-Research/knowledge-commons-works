# Part of the Invenio-Stats-Dashboard extension for InvenioRDM
# Copyright (C) 2025 Mesh Research
#
# Invenio-Stats-Dashboard is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Sample aggregation service responses."""

MOCK_AGG_SERVICE_RESPONSE = {
    "formatted_report": (
        "============================================================\n"
        "AGGREGATION RESULTS\n"
        "============================================================\n"
        "\n"
        "community-usage-delta-agg\n"
        "-------------------------\n"
        "Duration: 0:00:00.002976\n"
        "Documents indexed: 0\n"
        "Errors: 0\n"
        "\n"
        "community-records-delta-created-agg\n"
        "-----------------------------------\n"
        "Duration: 0:00:01.864656\n"
        "Documents indexed: 11\n"
        "Errors: 0\n"
        "Communities processed: 1\n"
        "\n"
        "community-records-delta-published-agg\n"
        "-------------------------------------\n"
        "Duration: 0:00:00.149481\n"
        "Documents indexed: 11\n"
        "Errors: 0\n"
        "Communities processed: 1\n"
        "\n"
        "community-records-delta-added-agg\n"
        "---------------------------------\n"
        "Duration: 0:00:00.691871\n"
        "Documents indexed: 11\n"
        "Errors: 0\n"
        "Communities processed: 1\n"
        "\n"
        "community-records-snapshot-created-agg\n"
        "--------------------------------------\n"
        "Duration: 0:00:00.156592\n"
        "Documents indexed: 11\n"
        "Errors: 0\n"
        "Communities processed: 1\n"
        "\n"
        "community-records-snapshot-published-agg\n"
        "----------------------------------------\n"
        "Duration: 0:00:00.137746\n"
        "Documents indexed: 11\n"
        "Errors: 0\n"
        "Communities processed: 1\n"
        "\n"
        "community-records-snapshot-added-agg\n"
        "------------------------------------\n"
        "Duration: 0:00:00.224839\n"
        "Documents indexed: 11\n"
        "Errors: 0\n"
        "Communities processed: 1\n"
        "\n"
        "community-usage-snapshot-agg\n"
        "----------------------------\n"
        "Duration: 0:00:00.006061\n"
        "Documents indexed: 0\n"
        "Errors: 0\n"
        "\n"
        "============================================================\n"
        "AGGREGATION SUMMARY\n"
        "============================================================\n"
        "Total documents indexed: 66\n"
        "Total errors: 0\n"
        "Total communities processed: 1\n"
        "Total aggregation time: 0:00:03.234980\n"
        "============================================================"
    ),
    "formatted_report_verbose": (
        "============================================================\n"
        "AGGREGATION RESULTS\n"
        "============================================================\n"
        "\n"
        "community-usage-delta-agg\n"
        "-------------------------\n"
        "Duration: 0:00:00.002976\n"
        "Documents indexed: 0\n"
        "Errors: 0\n"
        "\n"
        "community-records-delta-created-agg\n"
        "-----------------------------------\n"
        "Duration: 0:00:01.864656\n"
        "Documents indexed: 11\n"
        "Errors: 0\n"
        "Communities processed: 1\n"
        "Community details:\n"
        "  Community 558a1c92-34e8-46d8-864f-56cd25e0015d "
        "(index: "
        "stats-community-records-delta-created-2025):\n"
        "    Documents: 11, Errors: 0\n"
        "    Total doc generation time: 1.137s\n"
        "    Average doc generation time: 0.103s\n"
        "      Doc "
        "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-05: "
        "0.183s (delta)\n"
        "      Doc "
        "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-06: "
        "0.133s (delta)\n"
        "      Doc "
        "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-07: "
        "0.059s (delta)\n"
        "      ... and 8 more documents\n"
        "\n"
        "community-records-delta-published-agg\n"
        "-------------------------------------\n"
        "Duration: 0:00:00.149481\n"
        "Documents indexed: 11\n"
        "Errors: 0\n"
        "Communities processed: 1\n"
        "Community details:\n"
        "  Community 558a1c92-34e8-46d8-864f-56cd25e0015d "
        "(index: "
        "stats-community-records-delta-published-2025):\n"
        "    Documents: 11, Errors: 0\n"
        "    Total doc generation time: 0.016s\n"
        "    Average doc generation time: 0.001s\n"
        "      Doc "
        "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-05: "
        "0.001s (delta)\n"
        "      Doc "
        "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-06: "
        "0.001s (delta)\n"
        "      Doc "
        "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-07: "
        "0.001s (delta)\n"
        "      ... and 8 more documents\n"
        "\n"
        "community-records-delta-added-agg\n"
        "---------------------------------\n"
        "Duration: 0:00:00.691871\n"
        "Documents indexed: 11\n"
        "Errors: 0\n"
        "Communities processed: 1\n"
        "Community details:\n"
        "  Community 558a1c92-34e8-46d8-864f-56cd25e0015d "
        "(index: "
        "stats-community-records-delta-added-2025):\n"
        "    Documents: 11, Errors: 0\n"
        "    Total doc generation time: 0.538s\n"
        "    Average doc generation time: 0.049s\n"
        "      Doc "
        "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-05: "
        "0.040s (delta)\n"
        "      Doc "
        "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-06: "
        "0.038s (delta)\n"
        "      Doc "
        "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-07: "
        "0.044s (delta)\n"
        "      ... and 8 more documents\n"
        "\n"
        "community-records-snapshot-created-agg\n"
        "--------------------------------------\n"
        "Duration: 0:00:00.156592\n"
        "Documents indexed: 11\n"
        "Errors: 0\n"
        "Communities processed: 1\n"
        "Community details:\n"
        "  Community 558a1c92-34e8-46d8-864f-56cd25e0015d "
        "(index: "
        "stats-community-records-snapshot-created-2025):\n"
        "    Documents: 11, Errors: 0\n"
        "    Total doc generation time: 0.015s\n"
        "    Average doc generation time: 0.001s\n"
        "      Doc "
        "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-05: "
        "0.002s (snapshot)\n"
        "      Doc "
        "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-06: "
        "0.002s (snapshot)\n"
        "      Doc "
        "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-07: "
        "0.002s (snapshot)\n"
        "      ... and 8 more documents\n"
        "\n"
        "community-records-snapshot-published-agg\n"
        "----------------------------------------\n"
        "Duration: 0:00:00.137746\n"
        "Documents indexed: 11\n"
        "Errors: 0\n"
        "Communities processed: 1\n"
        "Community details:\n"
        "  Community 558a1c92-34e8-46d8-864f-56cd25e0015d "
        "(index: "
        "stats-community-records-snapshot-published-2025):\n"
        "    Documents: 11, Errors: 0\n"
        "    Total doc generation time: 0.026s\n"
        "    Average doc generation time: 0.002s\n"
        "      Doc "
        "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-05: "
        "0.002s (snapshot)\n"
        "      Doc "
        "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-06: "
        "0.002s (snapshot)\n"
        "      Doc "
        "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-07: "
        "0.002s (snapshot)\n"
        "      ... and 8 more documents\n"
        "\n"
        "community-records-snapshot-added-agg\n"
        "------------------------------------\n"
        "Duration: 0:00:00.224839\n"
        "Documents indexed: 11\n"
        "Errors: 0\n"
        "Communities processed: 1\n"
        "Community details:\n"
        "  Community 558a1c92-34e8-46d8-864f-56cd25e0015d "
        "(index: "
        "stats-community-records-snapshot-added-2025):\n"
        "    Documents: 11, Errors: 0\n"
        "    Total doc generation time: 0.031s\n"
        "    Average doc generation time: 0.003s\n"
        "      Doc "
        "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-05: "
        "0.004s (snapshot)\n"
        "      Doc "
        "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-06: "
        "0.002s (snapshot)\n"
        "      Doc "
        "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-07: "
        "0.002s (snapshot)\n"
        "      ... and 8 more documents\n"
        "\n"
        "community-usage-snapshot-agg\n"
        "----------------------------\n"
        "Duration: 0:00:00.006061\n"
        "Documents indexed: 0\n"
        "Errors: 0\n"
        "\n"
        "============================================================\n"
        "AGGREGATION SUMMARY\n"
        "============================================================\n"
        "Total documents indexed: 66\n"
        "Total errors: 0\n"
        "Total communities processed: 1\n"
        "Total aggregation time: 0:00:03.234980\n"
        "============================================================\n"
        "\n"
        "Individual aggregator timings:\n"
        "--------------------------------------------------\n"
        "  community-usage-delta-agg            "
        "0:00:00.002976\n"
        "  community-records-delta-created-agg  "
        "0:00:01.864656\n"
        "  community-records-delta-published-agg  "
        "0:00:00.149481\n"
        "  community-records-delta-added-agg    "
        "0:00:00.691871\n"
        "  community-records-snapshot-created-agg  "
        "0:00:00.156592\n"
        "  community-records-snapshot-published-agg  "
        "0:00:00.137746\n"
        "  community-records-snapshot-added-agg  "
        "0:00:00.224839\n"
        "  community-usage-snapshot-agg         "
        "0:00:00.006061\n"
        "--------------------------------------------------\n"
        "Total                                "
        "0:00:03.234980\n"
        "============================================================"
    ),
    "results": [
        {
            "aggregator": "community-usage-delta-agg",
            "communities_count": 0,
            "communities_processed": [],
            "community_details": [],
            "docs_indexed": 0,
            "duration_formatted": "0:00:00.002976",
            "error_details": [],
            "errors": 0,
        },
        {
            "aggregator": "community-records-delta-created-agg",
            "communities_count": 1,
            "communities_processed": ["558a1c92-34e8-46d8-864f-56cd25e0015d"],
            "community_details": [
                {
                    "community_id": "558a1c92-34e8-46d8-864f-56cd25e0015d",
                    "date_range_requested": {
                        "end_date": "2025-09-15 " "00:00:00",
                        "start_date": "2025-09-05 " "00:00:00",
                    },
                    "docs_indexed": 11,
                    "documents": [
                        {
                            "date_info": {
                                "date_type": "delta",
                                "period_end": "2025-09-05T23:59:59",
                                "period_start": "2025-09-05T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-05"
                            ),
                            "generation_time": 0.18250417709350586,
                        },
                        {
                            "date_info": {
                                "date_type": "delta",
                                "period_end": "2025-09-06T23:59:59",
                                "period_start": "2025-09-06T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-06"
                            ),
                            "generation_time": 0.13278698921203613,
                        },
                        {
                            "date_info": {
                                "date_type": "delta",
                                "period_end": "2025-09-07T23:59:59",
                                "period_start": "2025-09-07T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-07"
                            ),
                            "generation_time": 0.058776140213012695,
                        },
                        {
                            "date_info": {
                                "date_type": "delta",
                                "period_end": "2025-09-08T23:59:59",
                                "period_start": "2025-09-08T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-08"
                            ),
                            "generation_time": 0.07382416725158691,
                        },
                        {
                            "date_info": {
                                "date_type": "delta",
                                "period_end": "2025-09-09T23:59:59",
                                "period_start": "2025-09-09T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-09"
                            ),
                            "generation_time": 0.061331987380981445,
                        },
                        {
                            "date_info": {
                                "date_type": "delta",
                                "period_end": "2025-09-10T23:59:59",
                                "period_start": "2025-09-10T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-10"
                            ),
                            "generation_time": 0.06528902053833008,
                        },
                        {
                            "date_info": {
                                "date_type": "delta",
                                "period_end": "2025-09-11T23:59:59",
                                "period_start": "2025-09-11T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-11"
                            ),
                            "generation_time": 0.052282094955444336,
                        },
                        {
                            "date_info": {
                                "date_type": "delta",
                                "period_end": "2025-09-12T23:59:59",
                                "period_start": "2025-09-12T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-12"
                            ),
                            "generation_time": 0.08538222312927246,
                        },
                        {
                            "date_info": {
                                "date_type": "delta",
                                "period_end": "2025-09-13T23:59:59",
                                "period_start": "2025-09-13T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-13"
                            ),
                            "generation_time": 0.05021476745605469,
                        },
                        {
                            "date_info": {
                                "date_type": "delta",
                                "period_end": "2025-09-14T23:59:59",
                                "period_start": "2025-09-14T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-14"
                            ),
                            "generation_time": 0.1784670352935791,
                        },
                        {
                            "date_info": {
                                "date_type": "delta",
                                "period_end": "2025-09-15T23:59:59",
                                "period_start": "2025-09-15T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-15"
                            ),
                            "generation_time": 0.1964578628540039,
                        },
                    ],
                    "error_details": [],
                    "errors": 0,
                    "index_name": "stats-community-records-delta-created-2025",
                }
            ],
            "docs_indexed": 11,
            "duration_formatted": "0:00:01.864656",
            "error_details": [],
            "errors": 0,
        },
        {
            "aggregator": "community-records-delta-published-agg",
            "communities_count": 1,
            "communities_processed": ["558a1c92-34e8-46d8-864f-56cd25e0015d"],
            "community_details": [
                {
                    "community_id": "558a1c92-34e8-46d8-864f-56cd25e0015d",
                    "date_range_requested": {
                        "end_date": "2025-09-15 " "00:00:00",
                        "start_date": "2025-09-05 " "00:00:00",
                    },
                    "docs_indexed": 11,
                    "documents": [
                        {
                            "date_info": {
                                "date_type": "delta",
                                "period_end": "2025-09-05T23:59:59",
                                "period_start": "2025-09-05T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-05"
                            ),
                            "generation_time": 0.0014629364013671875,
                        },
                        {
                            "date_info": {
                                "date_type": "delta",
                                "period_end": "2025-09-06T23:59:59",
                                "period_start": "2025-09-06T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-06"
                            ),
                            "generation_time": 0.0014460086822509766,
                        },
                        {
                            "date_info": {
                                "date_type": "delta",
                                "period_end": "2025-09-07T23:59:59",
                                "period_start": "2025-09-07T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-07"
                            ),
                            "generation_time": 0.0012199878692626953,
                        },
                        {
                            "date_info": {
                                "date_type": "delta",
                                "period_end": "2025-09-08T23:59:59",
                                "period_start": "2025-09-08T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-08"
                            ),
                            "generation_time": 0.0010411739349365234,
                        },
                        {
                            "date_info": {
                                "date_type": "delta",
                                "period_end": "2025-09-09T23:59:59",
                                "period_start": "2025-09-09T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-09"
                            ),
                            "generation_time": 0.0010340213775634766,
                        },
                        {
                            "date_info": {
                                "date_type": "delta",
                                "period_end": "2025-09-10T23:59:59",
                                "period_start": "2025-09-10T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-10"
                            ),
                            "generation_time": 0.0009341239929199219,
                        },
                        {
                            "date_info": {
                                "date_type": "delta",
                                "period_end": "2025-09-11T23:59:59",
                                "period_start": "2025-09-11T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-11"
                            ),
                            "generation_time": 0.001483917236328125,
                        },
                        {
                            "date_info": {
                                "date_type": "delta",
                                "period_end": "2025-09-12T23:59:59",
                                "period_start": "2025-09-12T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-12"
                            ),
                            "generation_time": 0.0019598007202148438,
                        },
                        {
                            "date_info": {
                                "date_type": "delta",
                                "period_end": "2025-09-13T23:59:59",
                                "period_start": "2025-09-13T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-13"
                            ),
                            "generation_time": 0.001850128173828125,
                        },
                        {
                            "date_info": {
                                "date_type": "delta",
                                "period_end": "2025-09-14T23:59:59",
                                "period_start": "2025-09-14T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-14"
                            ),
                            "generation_time": 0.0018413066864013672,
                        },
                        {
                            "date_info": {
                                "date_type": "delta",
                                "period_end": "2025-09-15T23:59:59",
                                "period_start": "2025-09-15T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-15"
                            ),
                            "generation_time": 0.002216815948486328,
                        },
                    ],
                    "error_details": [],
                    "errors": 0,
                    "index_name": "stats-community-records-delta-published-2025",
                }
            ],
            "docs_indexed": 11,
            "duration_formatted": "0:00:00.149481",
            "error_details": [],
            "errors": 0,
        },
        {
            "aggregator": "community-records-delta-added-agg",
            "communities_count": 1,
            "communities_processed": ["558a1c92-34e8-46d8-864f-56cd25e0015d"],
            "community_details": [
                {
                    "community_id": "558a1c92-34e8-46d8-864f-56cd25e0015d",
                    "date_range_requested": {
                        "end_date": "2025-09-15 " "00:00:00",
                        "start_date": "2025-09-05 " "00:00:00",
                    },
                    "docs_indexed": 11,
                    "documents": [
                        {
                            "date_info": {
                                "date_type": "delta",
                                "period_end": "2025-09-05T23:59:59",
                                "period_start": "2025-09-05T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-05"
                            ),
                            "generation_time": 0.03956913948059082,
                        },
                        {
                            "date_info": {
                                "date_type": "delta",
                                "period_end": "2025-09-06T23:59:59",
                                "period_start": "2025-09-06T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-06"
                            ),
                            "generation_time": 0.03770709037780762,
                        },
                        {
                            "date_info": {
                                "date_type": "delta",
                                "period_end": "2025-09-07T23:59:59",
                                "period_start": "2025-09-07T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-07"
                            ),
                            "generation_time": 0.04391598701477051,
                        },
                        {
                            "date_info": {
                                "date_type": "delta",
                                "period_end": "2025-09-08T23:59:59",
                                "period_start": "2025-09-08T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-08"
                            ),
                            "generation_time": 0.04549288749694824,
                        },
                        {
                            "date_info": {
                                "date_type": "delta",
                                "period_end": "2025-09-09T23:59:59",
                                "period_start": "2025-09-09T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-09"
                            ),
                            "generation_time": 0.041780948638916016,
                        },
                        {
                            "date_info": {
                                "date_type": "delta",
                                "period_end": "2025-09-10T23:59:59",
                                "period_start": "2025-09-10T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-10"
                            ),
                            "generation_time": 0.06552505493164062,
                        },
                        {
                            "date_info": {
                                "date_type": "delta",
                                "period_end": "2025-09-11T23:59:59",
                                "period_start": "2025-09-11T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-11"
                            ),
                            "generation_time": 0.04293417930603027,
                        },
                        {
                            "date_info": {
                                "date_type": "delta",
                                "period_end": "2025-09-12T23:59:59",
                                "period_start": "2025-09-12T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-12"
                            ),
                            "generation_time": 0.05936789512634277,
                        },
                        {
                            "date_info": {
                                "date_type": "delta",
                                "period_end": "2025-09-13T23:59:59",
                                "period_start": "2025-09-13T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-13"
                            ),
                            "generation_time": 0.06370210647583008,
                        },
                        {
                            "date_info": {
                                "date_type": "delta",
                                "period_end": "2025-09-14T23:59:59",
                                "period_start": "2025-09-14T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-14"
                            ),
                            "generation_time": 0.02888774871826172,
                        },
                        {
                            "date_info": {
                                "date_type": "delta",
                                "period_end": "2025-09-15T23:59:59",
                                "period_start": "2025-09-15T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-15"
                            ),
                            "generation_time": 0.0690312385559082,
                        },
                    ],
                    "error_details": [],
                    "errors": 0,
                    "index_name": "stats-community-records-delta-added-2025",
                }
            ],
            "docs_indexed": 11,
            "duration_formatted": "0:00:00.691871",
            "error_details": [],
            "errors": 0,
        },
        {
            "aggregator": "community-records-snapshot-created-agg",
            "communities_count": 1,
            "communities_processed": ["558a1c92-34e8-46d8-864f-56cd25e0015d"],
            "community_details": [
                {
                    "community_id": "558a1c92-34e8-46d8-864f-56cd25e0015d",
                    "date_range_requested": {
                        "end_date": "2025-09-15 " "00:00:00",
                        "start_date": "2025-09-05 " "00:00:00",
                    },
                    "docs_indexed": 11,
                    "documents": [
                        {
                            "date_info": {
                                "date_type": "snapshot",
                                "snapshot_date": "2025-09-05T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-05"
                            ),
                            "generation_time": 0.0017406940460205078,
                        },
                        {
                            "date_info": {
                                "date_type": "snapshot",
                                "snapshot_date": "2025-09-06T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-06"
                            ),
                            "generation_time": 0.0017228126525878906,
                        },
                        {
                            "date_info": {
                                "date_type": "snapshot",
                                "snapshot_date": "2025-09-07T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-07"
                            ),
                            "generation_time": 0.0019769668579101562,
                        },
                        {
                            "date_info": {
                                "date_type": "snapshot",
                                "snapshot_date": "2025-09-08T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-08"
                            ),
                            "generation_time": 0.0015468597412109375,
                        },
                        {
                            "date_info": {
                                "date_type": "snapshot",
                                "snapshot_date": "2025-09-09T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-09"
                            ),
                            "generation_time": 0.0010991096496582031,
                        },
                        {
                            "date_info": {
                                "date_type": "snapshot",
                                "snapshot_date": "2025-09-10T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-10"
                            ),
                            "generation_time": 0.0010998249053955078,
                        },
                        {
                            "date_info": {
                                "date_type": "snapshot",
                                "snapshot_date": "2025-09-11T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-11"
                            ),
                            "generation_time": 0.0010199546813964844,
                        },
                        {
                            "date_info": {
                                "date_type": "snapshot",
                                "snapshot_date": "2025-09-12T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-12"
                            ),
                            "generation_time": 0.0009777545928955078,
                        },
                        {
                            "date_info": {
                                "date_type": "snapshot",
                                "snapshot_date": "2025-09-13T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-13"
                            ),
                            "generation_time": 0.0010960102081298828,
                        },
                        {
                            "date_info": {
                                "date_type": "snapshot",
                                "snapshot_date": "2025-09-14T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-14"
                            ),
                            "generation_time": 0.001561880111694336,
                        },
                        {
                            "date_info": {
                                "date_type": "snapshot",
                                "snapshot_date": "2025-09-15T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-15"
                            ),
                            "generation_time": 0.0014159679412841797,
                        },
                    ],
                    "error_details": [],
                    "errors": 0,
                    "index_name": "stats-community-records-snapshot-created-2025",
                }
            ],
            "docs_indexed": 11,
            "duration_formatted": "0:00:00.156592",
            "error_details": [],
            "errors": 0,
        },
        {
            "aggregator": "community-records-snapshot-published-agg",
            "communities_count": 1,
            "communities_processed": ["558a1c92-34e8-46d8-864f-56cd25e0015d"],
            "community_details": [
                {
                    "community_id": "558a1c92-34e8-46d8-864f-56cd25e0015d",
                    "date_range_requested": {
                        "end_date": "2025-09-15 " "00:00:00",
                        "start_date": "2025-09-05 " "00:00:00",
                    },
                    "docs_indexed": 11,
                    "documents": [
                        {
                            "date_info": {
                                "date_type": "snapshot",
                                "snapshot_date": "2025-09-05T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-05"
                            ),
                            "generation_time": 0.0020780563354492188,
                        },
                        {
                            "date_info": {
                                "date_type": "snapshot",
                                "snapshot_date": "2025-09-06T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-06"
                            ),
                            "generation_time": 0.0017828941345214844,
                        },
                        {
                            "date_info": {
                                "date_type": "snapshot",
                                "snapshot_date": "2025-09-07T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-07"
                            ),
                            "generation_time": 0.0019488334655761719,
                        },
                        {
                            "date_info": {
                                "date_type": "snapshot",
                                "snapshot_date": "2025-09-08T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-08"
                            ),
                            "generation_time": 0.0019257068634033203,
                        },
                        {
                            "date_info": {
                                "date_type": "snapshot",
                                "snapshot_date": "2025-09-09T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-09"
                            ),
                            "generation_time": 0.0014798641204833984,
                        },
                        {
                            "date_info": {
                                "date_type": "snapshot",
                                "snapshot_date": "2025-09-10T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-10"
                            ),
                            "generation_time": 0.0014369487762451172,
                        },
                        {
                            "date_info": {
                                "date_type": "snapshot",
                                "snapshot_date": "2025-09-11T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-11"
                            ),
                            "generation_time": 0.0015881061553955078,
                        },
                        {
                            "date_info": {
                                "date_type": "snapshot",
                                "snapshot_date": "2025-09-12T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-12"
                            ),
                            "generation_time": 0.0016350746154785156,
                        },
                        {
                            "date_info": {
                                "date_type": "snapshot",
                                "snapshot_date": "2025-09-13T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-13"
                            ),
                            "generation_time": 0.0015990734100341797,
                        },
                        {
                            "date_info": {
                                "date_type": "snapshot",
                                "snapshot_date": "2025-09-14T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-14"
                            ),
                            "generation_time": 0.008170843124389648,
                        },
                        {
                            "date_info": {
                                "date_type": "snapshot",
                                "snapshot_date": "2025-09-15T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-15"
                            ),
                            "generation_time": 0.0022072792053222656,
                        },
                    ],
                    "error_details": [],
                    "errors": 0,
                    "index_name": "stats-community-records-snapshot-published-2025",
                }
            ],
            "docs_indexed": 11,
            "duration_formatted": "0:00:00.137746",
            "error_details": [],
            "errors": 0,
        },
        {
            "aggregator": "community-records-snapshot-added-agg",
            "communities_count": 1,
            "communities_processed": ["558a1c92-34e8-46d8-864f-56cd25e0015d"],
            "community_details": [
                {
                    "community_id": "558a1c92-34e8-46d8-864f-56cd25e0015d",
                    "date_range_requested": {
                        "end_date": "2025-09-15 " "00:00:00",
                        "start_date": "2025-09-05 " "00:00:00",
                    },
                    "docs_indexed": 11,
                    "documents": [
                        {
                            "date_info": {
                                "date_type": "snapshot",
                                "snapshot_date": "2025-09-05T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-05"
                            ),
                            "generation_time": 0.003564119338989258,
                        },
                        {
                            "date_info": {
                                "date_type": "snapshot",
                                "snapshot_date": "2025-09-06T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-06"
                            ),
                            "generation_time": 0.002359151840209961,
                        },
                        {
                            "date_info": {
                                "date_type": "snapshot",
                                "snapshot_date": "2025-09-07T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-07"
                            ),
                            "generation_time": 0.0017669200897216797,
                        },
                        {
                            "date_info": {
                                "date_type": "snapshot",
                                "snapshot_date": "2025-09-08T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-08"
                            ),
                            "generation_time": 0.002299070358276367,
                        },
                        {
                            "date_info": {
                                "date_type": "snapshot",
                                "snapshot_date": "2025-09-09T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-09"
                            ),
                            "generation_time": 0.0022292137145996094,
                        },
                        {
                            "date_info": {
                                "date_type": "snapshot",
                                "snapshot_date": "2025-09-10T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-10"
                            ),
                            "generation_time": 0.002393007278442383,
                        },
                        {
                            "date_info": {
                                "date_type": "snapshot",
                                "snapshot_date": "2025-09-11T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-11"
                            ),
                            "generation_time": 0.0031201839447021484,
                        },
                        {
                            "date_info": {
                                "date_type": "snapshot",
                                "snapshot_date": "2025-09-12T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-12"
                            ),
                            "generation_time": 0.003065824508666992,
                        },
                        {
                            "date_info": {
                                "date_type": "snapshot",
                                "snapshot_date": "2025-09-13T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-13"
                            ),
                            "generation_time": 0.0035300254821777344,
                        },
                        {
                            "date_info": {
                                "date_type": "snapshot",
                                "snapshot_date": "2025-09-14T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-14"
                            ),
                            "generation_time": 0.0024902820587158203,
                        },
                        {
                            "date_info": {
                                "date_type": "snapshot",
                                "snapshot_date": "2025-09-15T00:00:00",
                            },
                            "document_id": (
                                "558a1c92-34e8-46d8-864f-56cd25e0015d-2025-09-15"
                            ),
                            "generation_time": 0.003999948501586914,
                        },
                    ],
                    "error_details": [],
                    "errors": 0,
                    "index_name": "stats-community-records-snapshot-added-2025",
                }
            ],
            "docs_indexed": 11,
            "duration_formatted": "0:00:00.224839",
            "error_details": [],
            "errors": 0,
        },
        {
            "aggregator": "community-usage-snapshot-agg",
            "communities_count": 0,
            "communities_processed": [],
            "community_details": [],
            "docs_indexed": 0,
            "duration_formatted": "0:00:00.006061",
            "error_details": [],
            "errors": 0,
        },
    ],
    "total_duration": "0:00:03.234980",
}
