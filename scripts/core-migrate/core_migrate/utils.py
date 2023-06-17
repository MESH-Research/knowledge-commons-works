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
from isbnlib import is_isbn10, is_isbn13, clean
import re
from typing import Union

def flatten_list(list_of_lists, flat_list=[]):
    if not list_of_lists:
        return flat_list
    else:
        for item in list_of_lists:
            if type(item) == list:
                flatten_list(item, flat_list)
            else:
                flat_list.append(item)

    return flat_list


def valid_isbn(isbn:str) -> Union[bool, str]:
    if is_isbn10(isbn) or (is_isbn13(isbn)):
        return isbn
    elif is_isbn10(clean(isbn)) or is_isbn13(clean(isbn)):
        return clean(isbn)
    else:
        return False


def valid_date(datestring:str) -> bool:
    """
    Return true if the supplied string is a valid iso8601 date.

    If it is, then this will also generally be valid for w3c and for LOC's
    Extended Date Time Format Level 0. The latter also requires hyphens
    and colons where appropriate.

    This function allows for truncated dates (just year, year-month,
    year-month-day)
    """
    try:
        datetime.fromisoformat(datestring.replace('Z', '+00:00'))
    except:
        print(f'couldn\'t parse {datestring}')
        try:
            # TODO: This only handles single years, year-months,
            # or year-month-days. Do we need ranges?
            dtregex = r'^(?P<year>[0-9]{4})(-(?P<month>1[0-2]|0[1-9])(-(?P<day>3[0-1]|0[1-9]|[1-2][0-9]))?)?$'
            assert re.search(dtregex, datestring)
        except:
            return False
    return True
