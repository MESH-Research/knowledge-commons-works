#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 MESH Research
#
# core-migrate is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""
Utility functions for core-migrate
"""

from datetime import datetime
import unicodedata
from isbnlib import is_isbn10, is_isbn13, clean
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import random
import re
import string
from typing import Union


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s:%(levelname)s : %(message)s")
file_handler = RotatingFileHandler(
    Path(__file__).parent / "logs" / "core_migrate.log",
    maxBytes=1000000,
    backupCount=5,
)
file_handler.setFormatter(formatter)
if logger.hasHandlers():
    logger.handlers.clear()
logger.addHandler(file_handler)


def generate_random_string(length):
    """
    Generate a random string of lowercase letters and integer numbers.
    """
    res = "".join(
        random.choices(string.ascii_lowercase + string.digits, k=length)
    )
    return res


def flatten_list(list_of_lists, flat_list=[]):
    if not list_of_lists:
        return flat_list
    else:
        for item in list_of_lists:
            if type(item) is list:
                flatten_list(item, flat_list)
            else:
                flat_list.append(item)

    return flat_list


def valid_isbn(isbn: str) -> Union[bool, str]:
    if is_isbn10(isbn) or (is_isbn13(isbn)):
        return isbn
    elif is_isbn10(clean(isbn)) or is_isbn13(clean(isbn)):
        return clean(isbn)
    else:
        return False


def valid_date(datestring: str) -> bool:
    """
    Return true if the supplied string is a valid iso8601 date.

    If it is, then this will also generally be valid for w3c and for LOC's
    Extended Date Time Format Level 0. The latter also requires hyphens
    and colons where appropriate.

    This function allows for truncated dates (just year, year-month,
    year-month-day)
    """
    try:
        datetime.fromisoformat(datestring.replace("Z", "+00:00"))
    except Exception:
        # FIXME: parse some of these datestrings
        # print(f'couldn\'t parse {datestring}')
        try:
            # TODO: This only handles single years, year-months,
            # or year-month-days. Do we need ranges?
            dtregex = (
                r"^(?P<year>[0-9]{4})(-(?P<month>1[0-2]|0[1-9])"
                r"(-(?P<day>3[0-1]|0[1-9]|[1-2][0-9]))?)?$"
            )
            assert re.search(dtregex, datestring)
        except Exception:
            return False
    return True


def compare_metadata(A: dict, B: dict) -> dict:
    """
    Compare two Invenio records and return a dictionary of differences.

    param A: The first record to compare (typically the existing record
             prior to migration)
    param B: The second record to compare (typically the record being migrated)
    return: A dictionary of differences between the two records
    rtype: dict
    """
    output = {"A": {}, "B": {}}

    def obj_list_compare(list_name, key, a, b, comparators):
        out = {}
        if list_name not in a.keys():
            a[list_name] = []
        existing_items = [_normalize_punctuation(i[key]) for i in a[list_name]]
        for i in b[list_name]:
            if _normalize_punctuation(i[key]) not in existing_items:
                out.setdefault("A", []).append({})
                out.setdefault("B", []).append(i)
            else:
                same = True
                i_2 = [
                    i2
                    for i2 in a[list_name]
                    if _normalize_punctuation(i2[key])
                    == _normalize_punctuation(i[key])
                ][0]
                for k in comparators:
                    if _normalize_punctuation(i[k]) != _normalize_punctuation(
                        i_2[k]
                    ):
                        same = False
                if not same:
                    out.setdefault("A", []).append(i_2)
                    out.setdefault("B", []).append(i)

        print("&&&&&&")
        print(a[list_name])
        print(b[list_name])
        return out

    def compare_people(list_a, list_b):
        existing_people = [
            _normalize_punctuation(c["person_or_org"]["name"]) for c in list_a
        ]
        people_diff = {}
        for c in list_b:
            if (
                _normalize_punctuation(c["person_or_org"]["name"])
                not in existing_people
            ):
                people_diff.setdefault("A", []).append({})
                people_diff.setdefault("B", []).append(c)
            else:
                same = True
                c_2 = [
                    c2
                    for c2 in list_a
                    if _normalize_punctuation(c2["person_or_org"]["name"])
                    == _normalize_punctuation(c["person_or_org"]["name"])
                ][0]
                for k in c["person_or_org"].keys():
                    if k == "identifiers":
                        if (
                            k not in c_2["person_or_org"].keys()
                            or c["person_or_org"][k] != c_2["person_or_org"][k]
                        ):
                            same = False
                    else:
                        if k not in c_2[
                            "person_or_org"
                        ].keys() or _normalize_punctuation(
                            c["person_or_org"][k]
                        ) != _normalize_punctuation(
                            c_2["person_or_org"][k]
                        ):
                            same = False
                if (
                    "role" not in c_2.keys()
                    or c["role"]["id"] != c_2["role"]["id"]
                ):
                    same = False
                if not same:
                    people_diff.setdefault("A", []).append(c_2)
                    people_diff.setdefault("B", []).append(c)
        return people_diff

    if "pids" in B.keys():
        pids_diff = {"A": {}, "B": {}}
        if B["pids"]["doi"] != A["pids"]["doi"]:
            pids_diff["A"] = {"doi": A["pids"]["doi"]}
            pids_diff["B"] = {"doi": B["pids"]["doi"]}
        if pids_diff["A"] or pids_diff["B"]:
            output["A"]["pids"] = pids_diff["A"]
            output["B"]["pids"] = pids_diff["B"]

    if "metadata" in B.keys():
        meta_diff = {"A": {}, "B": {}}
        meta_a = A["metadata"]
        meta_b = B["metadata"]

        simple_fields = [
            "title",
            "publication_date",
            "version",
            "description",
            "publisher",
        ]
        for s in simple_fields:
            if s in meta_b.keys():
                if s in meta_b.keys():
                    if _normalize_punctuation(
                        meta_b[s]
                    ) != _normalize_punctuation(meta_a[s]):
                        meta_diff["A"][s] = meta_a[s]
                        meta_diff["B"][s] = meta_b[s]
                else:
                    meta_diff["A"][s] = meta_a[s]
                    meta_diff["B"][s] = None

        if meta_b["resource_type"]["id"] != meta_a["resource_type"]["id"]:
            meta_diff["A"]["resource_type"] = meta_a["resource_type"]
            meta_diff["B"]["resource_type"] = meta_b["resource_type"]

        creators_comp = compare_people(meta_a["creators"], meta_b["creators"])
        if creators_comp:
            meta_diff["A"]["creators"] = creators_comp["A"]
            meta_diff["B"]["creators"] = creators_comp["B"]

        if "contributors" in meta_b.keys():
            if "contributors" not in meta_a.keys():
                meta_a["contributors"] = []
            comp = compare_people(
                meta_a["contributors"], meta_b["contributors"]
            )
            if comp:
                meta_diff["A"]["contributors"] = comp["A"]
                meta_diff["B"]["contributors"] = comp["B"]

        if "additional_titles" in meta_b.keys():
            if "additional_titles" not in meta_a.keys():
                meta_a["additional_titles"] = []
            existing_titles = [
                _normalize_punctuation(t["title"])
                for t in meta_a["additional_titles"]
            ]
            for t in meta_b["additional_titles"]:
                if _normalize_punctuation(t["title"]) not in existing_titles:
                    meta_diff["A"].setdefault("additional_titles", []).append(
                        {}
                    )
                    meta_diff["B"].setdefault("additional_titles", []).append(
                        t
                    )
                else:
                    same = True
                    t_2 = [
                        t2
                        for t2 in meta_a["additional_titles"]
                        if _normalize_punctuation(t2["title"])
                        == _normalize_punctuation(t["title"])
                    ][0]
                    if (
                        _normalize_punctuation(t["title"])
                        != _normalize_punctuation(t_2["title"])
                        or t["type"]["id"] != t_2["type"]["id"]
                    ):
                        same = False
                    if not same:
                        meta_diff["A"].setdefault(
                            "additional_titles", []
                        ).append(t_2)
                        meta_diff["B"].setdefault(
                            "additional_titles", []
                        ).append(t)

        if "identifiers" in meta_b.keys():
            comp = obj_list_compare(
                "identifiers",
                "identifier",
                meta_a,
                meta_b,
                ["identifier", "scheme"],
            )
            if comp:
                meta_diff["A"]["identifiers"] = comp["A"]
                meta_diff["B"]["identifiers"] = comp["B"]

        if "languages" in meta_b.keys():
            comp = obj_list_compare("languages", "id", meta_a, meta_b, ["id"])
            if comp:
                meta_diff["A"]["languages"] = comp["A"]
                meta_diff["B"]["languages"] = comp["B"]

        if "additional_descriptions" in meta_b.keys():
            comp = obj_list_compare(
                "additional_descriptions",
                "description",
                meta_a,
                meta_b,
                ["description"],
            )
            if comp:
                meta_diff["A"]["additional_descriptions"] = comp["A"]
                meta_diff["B"]["additional_descriptions"] = comp["B"]

        if "subjects" in meta_b.keys():
            comp = obj_list_compare(
                "subjects",
                "subject",
                meta_a,
                meta_b,
                ["id", "subject", "scheme"],
            )
            if comp:
                meta_diff["A"]["subjects"] = meta_a["subjects"]
                meta_diff["B"]["subjects"] = meta_b["subjects"]

        if meta_diff["A"] or meta_diff["B"]:
            output["A"]["metadata"] = meta_diff["A"]
            output["B"]["metadata"] = meta_diff["B"]

    if "custom_fields" in B.keys():
        custom_a = A["custom_fields"]
        custom_b = B["custom_fields"]
        custom_diff = {"A": {}, "B": {}}

        simple_fields = [
            "hclegacy:collection",
            "hclegacy:file_location",
            "hclegacy:file_pid",
            "hclegacy:previously_published",
            "hclegacy:record_change_date",
            "hclegacy:record_creation_date",
            "hclegacy:submitter_affiliation",
            "hclegacy:submitter_id",
            "hclegacy:submitter_org_memberships",
            "hclegacy:submitter_username",
            "kcr:ai_usage",
            "kcr:chapter_label",
            "kcr:commons_domain",
            "kcr:content_warning",
            "kcr:course_title",
            "kcr:degree",
            "kcr:discipline",
            "kcr:edition",
            "kcr:media",
            "kcr:meeting_organization",
            "kcr:notes",
            "kcr:project_title",
            "kcr:publication_url",
            "kcr:sponsoring_institution",
            "kcr:submitter_email",
            "kcr:submitter_username",
            "kcr:user_defined_tags",
            "kcr:volumes",
        ]

        for s in simple_fields:
            if s in custom_b.keys():
                same = True
                if s in custom_a.keys():
                    if type(custom_a[s]) is str:
                        if (
                            unicodedata.normalize("NFC", custom_b[s])
                            != custom_a[s]
                        ):
                            same = False
                    elif type(custom_a[s]) is list:
                        if custom_b[s] != custom_a[s]:
                            same = False
                else:
                    same = False
                    custom_a[s] = None
                if not same:
                    custom_diff["A"][s] = custom_a[s]
                    custom_diff["B"][s] = custom_b[s]

        if "hclegacy:groups_for_deposit" in custom_b.keys():
            comp = obj_list_compare(
                "hclegacy:groups_for_deposit",
                "group_name",
                custom_a,
                custom_b,
                ["group_name", "group_identifier"],
            )
            if comp:
                custom_diff["A"]["hclegacy:groups_for_deposit"] = comp["A"]
                custom_diff["B"]["hclegacy:groups_for_deposit"] = comp["B"]

        if "imprint:imprint" in custom_b.keys():
            if "imprint:imprint" not in custom_a.keys():
                custom_a["imprint:imprint"] = {}
            same = True
            for k in ["pages", "isbn", "title"]:
                if k in custom_b["imprint:imprint"].keys():
                    if k in custom_a["imprint:imprint"].keys():
                        if custom_a["imprint:imprint"][
                            k
                        ] != unicodedata.normalize(
                            "NFC", custom_b["imprint:imprint"][k]
                        ):
                            same = False
                    else:
                        same = False
                        custom_a["imprint:imprint"][k] = None

            if "creators" in B["custom_fields"]["imprint:imprint"].keys():
                ci_comp = compare_people(
                    custom_a["imprint:imprint"]["creators"],
                    custom_b["imprint:imprint"]["creators"],
                )
                if ci_comp:
                    same = False

            if not same:
                custom_diff["A"]["imprint:imprint"] = custom_a[
                    "imprint:imprint"
                ]
                custom_diff["B"]["imprint:imprint"] = custom_b[
                    "imprint:imprint"
                ]

        if "journal:journal" in custom_b.keys():
            if "journal:journal" not in custom_a.keys():
                custom_a["journal:journal"] = {}
            same = True
            for k in ["issn", "issue", "pages", "title"]:
                if k in custom_b["journal:journal"].keys():
                    if k in custom_a["journal:journal"].keys():
                        if custom_a["journal:journal"][
                            k
                        ] != unicodedata.normalize(
                            "NFC", custom_b["journal:journal"][k]
                        ):
                            same = False
                    else:
                        same = False
                        custom_a["journal:journal"][k] = None
            if not same:
                custom_diff["A"]["journal:journal"] = custom_a[
                    "journal:journal"
                ]
                custom_diff["B"]["journal:journal"] = custom_b[
                    "journal:journal"
                ]

        if custom_diff["A"] or custom_diff["B"]:
            output["A"]["custom_fields"] = custom_diff["A"]
            output["B"]["custom_fields"] = custom_diff["B"]

    return output if output["A"] or output["B"] else {}


def _normalize_string(mystring: str) -> str:
    mystring = mystring.casefold()
    mystring = _clean_string(mystring)
    mystring = _normalize_punctuation(mystring)
    try:
        if mystring[0] in ['"', "'"]:
            mystring = mystring[1:]
        if mystring[-1] in ['"', "'"]:
            mystring = mystring[:-1]
    except IndexError:
        pass
    return mystring


def _normalize_punctuation(mystring: str) -> str:
    mystring = mystring.replace("’", "'")
    mystring = mystring.replace("‘", "'")
    mystring = mystring.replace("“", '"')
    mystring = mystring.replace("”", '"')
    mystring = mystring.replace("&amp;", "&")
    mystring = mystring.replace("'", "'")
    mystring = mystring.replace('"', '"')
    mystring = mystring.replace("  ", " ")
    mystring = mystring.strip()
    mystring = unicodedata.normalize("NFC", mystring)
    return mystring


def _clean_string(mystring: str) -> str:
    """
    Remove unwanted characters from a string and return it.
    """
    if re.search(r"[\'\"]", mystring):
        mystring = re.sub(r"\\+'", r"'", mystring)
        mystring = re.sub(r'\\+"', r'"', mystring)
    else:
        mystring = re.sub(r"\\+", r"\\", mystring)
    mystring = mystring.replace("  ", " ")
    return mystring


def update_nested_dict(original, update):
    for key, value in update.items():
        if isinstance(value, dict):
            original[key] = update_nested_dict(original.get(key, {}), value)
        elif isinstance(value, list):
            original.setdefault(key, []).extend(value)
        else:
            original[key] = value
    return original
