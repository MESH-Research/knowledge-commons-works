#! /usr/bin/env python

"""
Utilities for converting the OPF funders CSV file to a YAML vocabulary file.

(c) 2024 Mesh Research

Part of the Knowledge Commons Works instance of InvenioRDM. Knowledge Commons
Works is released under the MIT License and can be freely reused and adapted.
See the LICENSE file for more details.

The Open Funders Registry vocabulary is released under the Creative Commons
0 License. See the OFR website for more details:
https://www.crossref.org/services/funder-registry/

This script is intended to be run from the command line. It reads the OFR
funders CSV file, and writes a YAML vocabulary file to the app_data directory.

Usage:
    python ofr.py

The input file is hard-coded as ../../../../app_data/funderNames.csv, and the
output file is app_data/ofr.yaml.
"""

import csv
from pathlib import Path
import yaml


def opf_csv_to_yaml():
    """Convert the OFR funders CSV file to a YAML vocabulary file."""
    with open(
        Path(__file__).parent.parent.parent.parent.parent
        / "app_data"
        / "funderNames.csv",
        "r",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        reader = csv.DictReader(csv_file)
        data = []
        for row in reader:
            if len(row["primary_name_display"]) > 100:
                print(row["primary_name_display"])
            data.append(
                {
                    "id": row["uri"],
                    "name": row["primary_name_display"]
                    .replace("\n", " ")
                    .replace("\r", " ")
                    .replace("\x0d", ""),
                    "identifiers": [
                        {"identifier": row["uri"], "scheme": "ofr"}
                    ],
                }
            )

    with open(
        Path(__file__).parent.parent.parent.parent.parent
        / "app_data"
        / "vocabularies"
        / "funders_ofr.yaml",
        "w",
        encoding="utf-8",
    ) as yaml_file:
        yaml.dump(data, yaml_file, allow_unicode=True, width=1000)


if __name__ == "__main__":
    opf_csv_to_yaml()
