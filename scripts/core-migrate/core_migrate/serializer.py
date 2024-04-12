#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 MESH Research
#
# core-migrate is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""
Functions to re-serialize legacy CORE deposits exported as json files to a
json schema consumable by InvenioRDM.

The main function `serialize_json` writes the output to a jsonl file, with
one json object per line, separated by newlines.
"""

from calendar import c
from copy import deepcopy
from datetime import datetime
from pprint import pprint
from timefhuman import timefhuman
from isbnlib import get_isbnlike
import iso639
import json
import jsonlines
from langdetect import detect_langs
from pathlib import Path
from stdnum import issn
from titlecase import titlecase
import re
import validators

from core_migrate.config import (
    DATA_DIR,
    GLOBAL_DEBUG,
)
from core_migrate.utils import (
    valid_date,
    valid_isbn,
    _normalize_string,
    _clean_string,
)

book_types = [
    "textDocument-bookChapter",
    "textDocument-bookSection",
    "textDocument-book",
    "textDocument-monograph",
    "textDocument-dissertation",
    "textDocument-report",
    "textDocument-whitePaper",
    "textDocument-bibliography",
    "presentation-conferencePaper",
    "textDocument-conferenceProceeding",
    "presentation-conferencePaper",
    "textDocument-essay",
]

article_types = [
    "textDocument-journalArticle",
    "textDocument-abstract",
    "textDocument-review",
    "textDocument-newspaperArticle",
    "textDocument-editorial",
    "textDocument-magazineArticle",
    "textDocument-onlinetextDocument",
]

ambiguous_types = [
    "textDocument-fictionalWork",
    "other",
    "textDocument-interviewTranscript",
    "textDocument-legalComment",
    "textDocument-legalResponse",
    "textDocument-poeticWork",
    "textDocument-translation",
]

licenses = {
    "All Rights Reserved": (
        "arr",
        "All Rights Reserved",
        "https://en.wikipedia.org/wiki/All_rights_reserved",
    ),
    "Attribution-NonCommercial-NoDerivatives": (
        "cc-by-nc-nd-4.0",
        (
            "Creative Commons Attribution Non Commercial No Derivatives "
            "4.0 International"
        ),
        "https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode",
    ),
    "Attribution-NonCommercial-ShareAlike": (
        "cc-by-nc-sa-4.0",
        (
            "Creative Commons Attribution Non Commercial Share "
            "Alike 4.0 International"
        ),
        "https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode",
    ),
    "Attribution": (
        "cc-by-4.0",
        "Creative Commons Attribution 4.0 International",
        "https://creativecommons.org/licenses/by/4.0/legalcode",
    ),
    "Attribution-NonCommercial": (
        "cc-by-nc-4.0",
        "Creative Commons Attribution Non Commercial 4.0 International",
        "https://creativecommons.org/licenses/by-nc/4.0/legalcode",
    ),
    "Attribution-NoDerivatives": (
        "cc-by-nd-4.0",
        "Creative Commons Attribution No Derivatives 4.0 International",
        "https://creativecommons.org/licenses/by-nd/4.0/legalcode",
    ),
    "Attribution-ShareAlike": (
        "cc-by-sa-4.0",
        "Creative Commons Attribution Share Alike 4.0 International",
        "https://creativecommons.org/licenses/by-sa/4.0/legalcode",
    ),
    "All-Rights-Granted": (
        "0bsd",
        "BSD Zero Clause License",
        "https://spdx.org/licenses/0BSD.html",
    ),
    "All Rights Granted": (
        "0bsd",
        "BSD Zero Clause License",
        "https://spdx.org/licenses/0BSD.html",
    ),
}

genres = {
    "Abstract": "textDocument-abstract",
    "Article": "textDocument-journalArticle",
    "Bibliography": "textDocument-bibliography",
    "Blog Post": "textDocument-blogPost",
    "Book": "textDocument-book",
    "Book chapter": "textDocument-bookSection",
    "Book review": "textDocument-review",
    "Book section": "textDocument-bookSection",
    "Catalog": "other-catalog",
    "Chart": "image-chart",
    "Code or software": "software-application",
    "Conference paper": "presentation-conferencePaper",
    "Conference poster": "presentation-conferencePoster",
    "Conference proceeding": "textDocument-conferenceProceeding",
    "Course material or learning objects": "instructionalResource-other",
    "Course Material or learning objects": "instructionalResource- other",
    "Data set": "dataset",
    "Dissertation": "textDocument-thesis",
    "Documentary": "audiovisual-documentary",
    "Editorial": "textDocument-editorial",
    "Essay": "textDocument-essay",
    "Fictional work": (
        "textDocument-bookSection"
    ),  # FIXME: indicate ficiontal???
    "Finding aid": "other",
    "Image": "image-other",
    "Interview": "textDocument-interviewTranscript",
    "Lecture": "presentation-presentationText",
    "Legal Comment": "textDocument-legalComment",
    "Legal response": "textDocument-legalResponse",
    "Magazine section": "textDocument-magazineArticle",
    "Map": "image-map",
    "Monograph": "textDocument-monograph",
    "Music": "audiovisual-musicalRecording",
    "Newspaper article": "textDocument-newspaperArticle",
    "Online textDocument": "textDocument-onlinePublication",
    "Online textDocument": "textDocument-onlinePublication",
    "Other": "other",
    "Performance": "audiovisual-performance",
    "Photograph": "image-other",
    "Podcast": "audiovisual-podcastEpisode",
    "Poetry": "textDocument-poeticWork",
    "Presentation": "presentation-other",
    "Report": "textDocument-report",
    "Review": "textDocument-review",
    "Sound recording-musical": "audiovisual-musicalRecording",
    "Sound recording-non musical": "audiovisual-audioRecording",
    "Syllabus": "instructionalResource-syllabus",
    "Technical report": "textDocument-report",
    "Thesis": "textDocument-thesis",
    "Translation": "textDocument-other",
    "Video": "audiovisual-videoRecording",
    "Video essay": "audiovisual-videoRecording",
    "Visual art": "image-visualArt",
    "White paper": "textDocument-whitePaper",
}

publication_types = {
    "book-chapter": "textDocument-bookSection",
    "book-review": "textDocument-review",
    "book-section": "textDocument-bookSection",
    "journal-article": "textDocument-journalArticle",
    "magazine-section": "textDocument-magazineArticle",
    "monograph": "textDocument-monograph",
    "newspaper-article": "textDocument-newspaperArticle",
    "online-publication": "textDocument-onlinePublication",
    "podcast": "audiovisual-podcastEpisode",
    "proceedings-article": "textDocument-conferenceProceeding",
}


def _append_bad_data(rowid: str, content: tuple, bad_data_dict: dict) -> dict:
    """
    Add info on bad data to dictionary of bad data
    """
    bad_data_dict.setdefault(rowid, []).append(content)
    return bad_data_dict


def _add_resource_type(
    rec: dict, row: dict, bad_data_dict: dict
) -> tuple[dict, dict]:
    """Add resource type information to the new record.

    This function adds the resource type information to the new record. It
    uses the following fields from the CORE record:
        - `publication-type`
        - `genre`
        - `filetype`

    The function uses the following dictionaries to map the CORE data to
    the InvenioRDM resource type schema:
        - `kcr_resource_types`: a dictionary mapping CORE `genre` values
        to InvenioRDM resource type ids
        - `types_of_resource`: a dictionary mapping CORE `filetype` values
        to InvenioRDM resource type ids
        - `genres`: a dictionary mapping CORE `genre` values to InvenioRDM
        resource type ids
        - `publication_types`: a dictionary mapping CORE `publication-type`
        values to InvenioRDM resource type ids

    Args:
        rec (dict): The new record being prepared for serialization
        row (dict): The CORE record being processed
        bad_data_dict (dict): A dictionary of error messages recording
                                problems with the data in the CORE record

    Returns:
        tuple[dict, dict]: The new record dict with resource type info added
    """
    bad_data = []

    pubtype = row["publication-type"]
    genre = row["genre"]
    filetype = row["filetype"]

    # kcr_resource_types = {
    #     "audiovisual": [
    #         "documentary",
    #         "interviewRecording",
    #         "videoRecording",
    #         "audioRecording",
    #         "musicalRecording",
    #         "other",
    #         "performance",
    #         "podcastEpisode",
    #     ],
    #     "dataset": [""],
    #     "image": [
    #         "chart",
    #         "diagram",
    #         "figure",
    #         "map",
    #         "visualArt",
    #         "photograph",
    #         "other",
    #     ],
    #     "instructionalResource": [
    #         "curriculum",
    #         "lessonPlan",
    #         "syllabus",
    #         "other",
    #     ],
    #     "presentation": [
    #         "slides",
    #         "conferencePaper",
    #         "conferencePoster",
    #         "presentationText",
    #         "other",
    #     ],
    #     "software": [
    #         "3DModel",
    #         "computationalModel",
    #         "computationalNotebook",
    #         "service",
    #         "application",
    #     ],
    #     "textDocument": [
    #         "abstract",
    #         "bibliography",
    #         "blogPost",
    #         "book",
    #         "bookSection",
    #         "conferenceProceeding",
    #         "dataManagementPlan",
    #         "documentation",
    #         "editorial",
    #         "essay",
    #         "interviewTranscript",
    #         "journalArticle",
    #         "legalResponse",
    #         "legalComment",
    #         "magazineArticle",
    #         "monograph",
    #         "newspaperArticle",
    #         "onlinePublication",
    #         "other",
    #         "poeticWork",
    #         "preprint",
    #         "report",
    #         "workingPaper",
    #         "review",
    #         "technicalStandard",
    #         "thesis",
    #         "whitePaper",
    #     ],
    #     "other": [
    #         "catalog",
    #         "collection",
    #         "event",
    #         "interactiveResource",
    #         "notes",
    #         "peerReview",
    #         "physicalObject",
    #         "workflow",
    #         "text",
    #     ],
    # }
    # types_of_resource = {
    #     "Audio": "audiovisual-audioRecording",
    #     "Image": "image-other",
    #     "Mixed material": "other",
    #     "Software": "software-application",
    #     "Text": "textDocument-other",
    #     "Video": "audiovisual-videoRecording",
    # }

    if genre in genres.keys():
        rec["metadata"]["resource_type"] = {"id": genres[genre]}
        if (pubtype == "Interview") and (
            filetype
            in [
                "audio/mpeg",
                "audio/ogg",
                "audio/wav",
                "video/mp4",
                "video/quicktime",
            ]
        ):
            rec["metadata"]["resource_type"] = {
                "id": "audiovisual-interviewRecording"
            }
        if (
            pubtype in publication_types.keys()
            and genres[genre] != publication_types[pubtype]
        ):
            rec["custom_fields"]["hclegacy:publication_type"] = pubtype
    else:
        rec["metadata"]["resource_type"] = {"id": ""}
        bad_data.append(("genre", genre))
        rec["custom_fields"]["hclegacy:publication_type"] = pubtype
        if pubtype in publication_types.keys():
            rec["metadata"]["resource_type"] = {
                "id": publication_types[pubtype]
            }
        else:
            bad_data.append(("publication-type", pubtype))

    if bad_data:
        for i in bad_data:
            _append_bad_data(row["id"], i, bad_data_dict)

    return rec, bad_data_dict


def _add_book_authors(
    author_string: str, bad_data_dict: dict, row_id
) -> tuple[list[dict], dict]:
    """
    Convert the "book_author" string to JSON objects for Invenio
    """
    author_list = []

    def invert_flipped_name(terms):
        return [terms[1], terms[0]]

    def find_comma_delineated_names(focus):
        # print('focus', focus)
        if focus[-1] == ",":
            focus = focus[:-1]
        focus = focus.strip()
        if ", " in focus:
            level1parts = focus.split(", ")
            # print('level1parts', level1parts)
            first = level1parts[0]
            # print('first', first)
            if len(first.split(" ")) > 1:
                focus = [f.strip().split(" ") for f in level1parts]
                # print('a focus', focus)
            elif len(first.split(" ")) == 1:
                focus = invert_flipped_name(level1parts)
                # print('b focus', focus)
            if len(level1parts) > 2:
                focus = focus + find_comma_delineated_names(
                    ", ".join(level1parts[2:])
                )
        else:
            focus = focus.strip().split(" ")
            # print('space split', focus)
            if len(focus) > 2:
                focus = [" ".join(focus[:-1]), focus[-1]]
        if isinstance(focus[0], str):
            focus = [focus]
        for i, f in enumerate(focus):
            if len(f) > 2:
                focus[i] = [" ".join(f[:-1]), f[-1]]
        return focus

    is_editor = False
    if re.search(
        r".*\(?([Hh]e?r(au)?sg(egeben)?|[Ee]d(it(or|ed( by)?)?)?s?)\.?.*",
        author_string,
    ):
        # print(row['book_author'])
        author_string = re.sub(
            r"(,? )?\(?([Hh]e?r(au)?sg(egeben)?|[Ee]d(itor)?s?\.?)\)?",
            "",
            author_string,
        )
        author_string = re.sub(
            r"^([Hh]e?r(au)?sg(egeben|eber(in)?)?|[Ee]d(it)?(ed|or)?s?("
            r" [Bb]y)?)[\.,]? ",
            "",
            author_string,
        )
        is_editor = True
    try:
        bas = author_string
        # print('***********', bas)
        if bas[-1] in [".", ";"]:
            bas = bas[:-1]
        if re.search(r"( and| y| &|;| \/) ", author_string):
            bas = re.split(r" and | y | & | \/ |;", bas)
            new_bas = []
            for focus in bas:
                new_bas = new_bas + find_comma_delineated_names(focus)
            bas = new_bas
        elif ", " in author_string:
            bas = find_comma_delineated_names(bas)
        elif len(bas.split(" ")) < 4:
            bas = find_comma_delineated_names(bas)
        if isinstance(bas, str):
            bas = [bas]
        for b in bas:
            # print(b, type(b))
            if isinstance(b, str):
                fullname = b
                given, family = "", ""
            else:
                fullname = f"{b[1]}, {b[0]}" if len(b) > 1 else b[0]
                given = b[0] if len(b) > 1 else ""
                family = b[1] if len(b) > 1 else ""
            author_list.append(
                {
                    "person_or_org": {
                        "name": _clean_string(fullname),
                        "type": "personal",
                        "given_name": _clean_string(given),
                        "family_name": (
                            _clean_string(family)
                            if family
                            else _clean_string(fullname)
                        ),
                    },
                    # FIXME: handle unlabelled editors better?
                    "role": {
                        "id": "editor" if is_editor else "other",
                        "title": {"en": "Editor" if is_editor else "Other"},
                    },
                }
            )
    except TypeError:
        _append_bad_data(row_id, ("book_author", author_string), bad_data_dict)
    # FIXME: handle simple spaced names with no delimiters
    # FIXME: last name repeated like "Kate Holland"?
    # FIXME: "Coarelli, F. Patterson, H."
    # FIXME: "Hamilton, Portnoy, Wacks"
    # FIXME: ['M. Antoni J. Üçerler', 'SJ']
    # FIXME: Edited by Koenraad Verboven, Ghent University and Christian
    # Laes, University of Antwerp, University of Tampere
    # FIXME: two last names???
    # FIXME: handle et. al.; et ali
    # FIXME: Joshua Davies and Sarah Salih, ed. by Karl Fugelso
    # FIXME: A. Pifferetti, A. & I. Dosztal (comps.)
    # FIXME: mark institution names as corporate?

    # FIXME: add in periods and spaces for initials?
    # for i, b in enumerate(bas):
    #     for l, n in enumerate(b):
    #         if re.search(r'^[A-Z]{2,}$', n):
    #             bas[i][l] = '. '.join([*n]) + '.'
    # bas = [b.strip() for b in bas]
    # print('*****', bas, type(bas))
    return author_list, bad_data_dict


def _add_author_data(
    newrec: dict, row: dict, bad_data_dict: dict
) -> tuple[dict, dict]:
    """
    Add information about authors to the supplied record from supplied row.

    Processes data from the 'authors' and 'author_info' csv export fields.
    """

    creators = []
    contributors_misplaced = []
    # creators_misplaced = []
    # FIXME: "HC Admin" showing up with "submitter" role?
    allowed_roles = [
        "author",
        "editor",
        "contributor",
        "translator",
        "creator",
        "other",
        "project director",
    ]
    if row["authors"]:
        # print(row['pid'])
        try:
            # row['authors'] = row['authors'].replace('\\', '&quot;')
            for a in row["authors"]:
                # Some records have "hcadmin" in role of "submitter"
                if a["uni"] == "hcadmin":
                    continue
                a["family"] = _clean_string(a["family"])
                a["given"] = _clean_string(a["given"])
                new_person = {}

                new_person["person_or_org"] = {
                    "type": "personal",  # FIXME: can't hard code
                    # 'name': a['fullname'],
                    "name": (
                        f'{a["family"]}, {a["given"]}'
                        if a["family"]
                        else a["fullname"]
                    ),
                    "given_name": a["given"],
                    "family_name": (
                        a["family"] if a["family"] else a["fullname"]
                    ),
                }
                if a["role"] and a["role"] in allowed_roles or not a["role"]:
                    # TODO: are null roles a problem?
                    if a["role"] == "project director":
                        new_person["role"] = {
                            "id": "projectOrTeamLeader",
                            "title": {"en": "Project or team leader"},
                        }
                    else:
                        new_person["role"] = {
                            "id": a["role"],
                            "title": {"en": a["role"].capitalize()},
                        }
                else:
                    _append_bad_data(
                        row["id"],
                        (f'authors:{a["fullname"]}:role', a["role"]),
                        bad_data_dict,
                    )
                if a["affiliation"]:
                    new_person["affiliations"] = [
                        {"name": f} for f in a["affiliation"].split("|")
                    ]
                if a["uni"]:  # uni is the hc username
                    new_person["person_or_org"]["identifiers"] = [
                        {"identifier": a["uni"], "scheme": "hc_username"}
                    ]
                if a["role"] in allowed_roles:
                    if a["role"] == "contributor":
                        new_person["role"] = {
                            "id": "other",
                            "title": {"en": "Other"},
                        }
                        contributors_misplaced.append(new_person)
                    else:
                        creators.append(new_person)
            if len(creators) > 0:
                newrec["metadata"].setdefault("creators", []).extend(creators)
                if contributors_misplaced:
                    newrec["metadata"].setdefault("contributors", []).extend(
                        contributors_misplaced
                    )
                    # append_bad_data(row['id'], ('authors', row['authors'],
                    #                             'contributor moved
                    # from Authors'),
                    #                 bad_data_dict)
            elif len(contributors_misplaced) > 0:
                newrec["metadata"].setdefault("creators", []).extend(
                    contributors_misplaced
                )
                # append_bad_data(row['id'], ('authors', row['authors'],
                #                             'contributor as only author'),
                #                 bad_data_dict)
        except (SyntaxError, ValueError):
            print(row["authors"])
            _append_bad_data(
                row["id"],
                ("authors:Syntax or ValueError", row["authors"]),
                bad_data_dict,
            )
    else:
        _append_bad_data(
            row["id"], ("authors:no value", row["authors"]), bad_data_dict
        )

    # TODO: Compare these fields?
    # if row['author_info']:
    #     try:
    #         # row['authors'] = row['authors'].replace('\\', '&quot;')
    #         authors = json.loads(row['authors'])

    #         for a in authors:
    #             new_person = {}
    #     except (SyntaxError, ValueError) as e:
    #         print(row['author_info'])
    #         append_bad_data(row['id'], ('author_info:Syntax or ValueError',
    #                                     row['author_info']), bad_data_dict)

    return newrec, bad_data_dict


def _get_subject_from_jsonl(subject: str) -> str:
    """
    Retrieve the full subject string corresponding to the provided label
    """
    # FIXME: Finish finding id numbers
    existing_subjects = {
        "Linguistics": "999202",
        "Digital humanities": "963599",
        "Arabic language": "812287",
        "Spanish language": "1128292",
        "American literature": "807113",
        "English literature": "911989",
        "Poetics": "1067682",
        "Comparative literature": "1734553",
        "Literature and science": "1000093",
        "German language": "941408",
        "Philosophy": "1060777",
        "Ethics": "915833",
        "Religion": "1093763",
        # 'Rhetoric': '',
        # 'Portuguese literature',
        # 'Biopolitics',
        # 'Irish literature',
        # 'Literature',
        # 'Church history',
        # 'British literature',
        # 'Animal rights',
        # 'Art criticism',
        # 'Sculpture',
        # 'Research libraries',
        # 'Writing',
        # 'Anthropology',
        # 'Environmental sociology',
        # 'Ethnomusicology',
        # 'Film criticism',
        # 'Continental philosophy',
        # 'Critical geography',
        # 'Earth sciences',
        # 'Arts',
        # 'Geography',
        # 'History',
        # 'Greek literature',
        # 'Jewish literature',
        # 'Spanish literature',
        # 'Ethnic studies',
        # 'Library science',
        # 'Music',
        # 'Psychiatry',
        # 'Aesthetics',
        # 'Ecocriticism',
        # 'Economics',
        # 'Intertextuality',
        # 'American poetry',
        # 'Beat literature',
        # 'Dutch literature',
        # 'Italian literature',
        # 'Feminism',
        # 'Music libraries',
        # 'Musicology',
        # 'Character',
        # 'Sustainability',
        # 'Cognitive science',
        # 'Polish language',
        # 'Postmodernism',
        # 'Neoliberalism',
        # 'Imperialism'
    }
    if subject in existing_subjects.keys():
        return f"{existing_subjects[subject]}:{subject}:topical"
    else:
        return ""


def add_chapter_label(
    newrec: dict, row: dict, bad_data_dict: dict
) -> tuple[dict, dict]:
    """Add chapter title information to the new record.

    This handles a chapter title or other label when that information is not
    the same as the title of the work. It is recorded using the custom field
    `kcr:chapter_label`.

    Args:
        newrec (_type_): The new record being prepared for serialization
        row (_type_): The CORE record being processed
        bad_data_dict (_type_): A dictionary of error messages recording
                                problems with the data in the CORE record

    Returns:
        dict: The new record dict with chapter title info added
    """
    if row["chapter"]:
        mychap = _normalize_string(row["chapter"])
        mytitle = _normalize_string(row["title"])

        # FIXME: Is book_journal_title ever appropriate for chapter label?
        # mybooktitle = _normalize_string(row["book_journal_title"])
        if mychap == mytitle:
            pass
        # FIXME: This needs work
        elif mychap in mytitle and len(mychap) > 18:
            _append_bad_data(
                row["id"],
                ("chapter in title", row["chapter"], row["title"]),
                bad_data_dict,
            )
        else:
            rn = r"^M{0,3}(CM|CD|D?C{0,3})?(XC|XL|L?X{0,3})?(IX|IV|V?I{0,3})?$"
            if re.search(
                r"^([Cc]hapter )?\d+[\.,;]?\d*$", row["chapter"]
            ) or re.search(rn, row["chapter"]):
                newrec["custom_fields"]["kcr:chapter_label"] = _clean_string(
                    row["chapter"]
                )
            # elif mytitle in mychap \
            #         and re.search(r'^([Cc]hapter )?\d+[\.,;]?\d*\s?',
            #                       mychap.replace(mytitle, '')):
            #     # print('~~~~', row['chapter'])
            #     # print('~~~~~~~', row['title'])
            #     shortchap = row['chapter'
            #                     ].replace(row['title'], '').strip()
            #     shortchap = re.sub(r'[Cc]hap(ter)\s?', '', shortchap)
            #     shortchap = re.sub(r'[\.,:]?\s?-?$', '', shortchap)
            # print('~~~~~~~', shortchap)
            # newrec['custom_fields']['kcr:chapter_label'] = shortchap
            # FIXME: label being truncated with \\\\\\\\\ in hc:27769
            elif re.search(r"^[Cc]hapter", row["chapter"]):
                shortchap = re.sub(r"^[Cc]hapter\s*", "", row["chapter"])
                newrec["custom_fields"]["kcr:chapter_label"] = _clean_string(
                    shortchap
                )
            elif row["chapter"] == "N/A":
                pass
            else:
                newrec["custom_fields"]["kcr:chapter_label"] = _clean_string(
                    row["chapter"]
                )
    return newrec, bad_data_dict


def add_legacy_commons_info(
    newrec: dict, row: dict, bad_data_dict: dict
) -> tuple[dict, dict]:
    """Add legacy commons information to the new record.

    Adds the following information about the legacy commons CORE record to the
    new record:
        - the commons pid (row `id`) as an `identifier` with scheme
        `hclegacy-pid`
        - the commons record id (row 'record_identifier'; like "1000361-385")
        as an `identifier` with scheme `hclegacy-record-id`
        - the commons domain (row `domain`; like "arlisna.hcommons.org") as a
        custom field `kcr:commons_domain`
        - the original submitter's email address (row `submitter_email`) as a
        custom field `kcr:submitter_email`
        - the original submitter's Commons username (row `submitter_login`) as
        a custom field `kcr:submitter_username`
        - the original submitter's Commons user id (row `submitter`) as a
        custom field `hclegacy:submitter_id`
        - the committee id for a committee deposit (row `committee_id`) as a
        custom field `hclegacy:committee_deposit` if the `committee_deposit`
        flag is "yes"
        - the legacy commons collection id (row `member_of`) as a custom field
        `hclegacy:collection`
        - the original submitter's HC society memberships (row `society_id`) as
        a custom field `hclegacy:submitter_org_memberships`
        - the original submitter's organization (row `organization`) as a
        custom field `hclegacy:submitter_affiliation`
        - the `published` flag (row `published`) as a custom field
        `hclegacy:previously_published`

    Args:
        newrec (_type_): The new record being prepared for serialization
        row (_type_): The CORE record being processed
        bad_data_dict (_type_): A dictionary of error messages recording
                                problems with the data in the CORE record

    Returns:
        dict: The new record dict with legacy commons info added
    """
    # HC legacy admin information
    newrec["metadata"]["identifiers"].append(
        {"identifier": row["id"], "scheme": "hclegacy-pid"}
    )
    assert row["id"] == row["pid"]
    newrec["metadata"]["identifiers"].append(
        {
            "identifier": str(row["record_identifier"]),
            "scheme": "hclegacy-record-id",
        }
    )
    newrec["custom_fields"]["kcr:commons_domain"] = row["domain"]

    # HC submitter info
    newrec["custom_fields"]["kcr:submitter_email"] = row["submitter_email"]
    newrec["custom_fields"]["kcr:submitter_username"] = row["submitter_login"]
    if row["submitter"]:
        try:
            row["submitter"] = str(row["submitter"])
            # Doesn't work because not Invenio user id
            newrec["parent"]["access"]["owned_by"].append(
                {"user": row["submitter"]}
            )
            newrec["custom_fields"]["hclegacy:submitter_id"] = row["submitter"]
        except ValueError:
            row["submitter"] = None
            _append_bad_data(
                row["id"], ("submitter", row["submitter"]), bad_data_dict
            )

    # Committee deposit
    if row["committee_deposit"] == "yes":
        try:
            cid = int(row["committee_id"])
            newrec["custom_fields"]["hclegacy:committee_deposit"] = cid
        except ValueError:
            _append_bad_data(
                row["id"], ("committee_id", row["committee_id"]), bad_data_dict
            )

    # HC legacy collection
    if row["member_of"]:
        newrec["custom_fields"]["hclegacy:collection"] = row["member_of"]

    # Original submitter's HC society memberships
    if row["society_id"]:
        row["society_id"] = (
            row["society_id"]
            if type(row["society_id"]) is list
            else [row["society_id"]]
        )
        newrec["custom_fields"]["hclegacy:submitter_org_memberships"] = row[
            "society_id"
        ]

    # Was CORE deposit previously published?
    if row["published"]:
        newrec["custom_fields"]["hclegacy:previously_published"] = row[
            "published"
        ]

    if row["organization"]:
        newrec["custom_fields"]["hclegacy:submitter_affiliation"] = row[
            "organization"
        ]

    return newrec, bad_data_dict


def add_embargo_info(
    newrec: dict, row: dict, bad_data_dict: dict
) -> tuple[dict, dict]:
    """Add access information to the new record.

    Adds any embargo dates based on the `embargoed` flag ("yes"/"no") and
    the `embargo_end_date` date string.

    Args:
        newrec (_type_): The new record being prepared for serialization
        row (_type_): The CORE record being processed
        bad_data_dict (_type_): A dictionary of error messages recording
                                problems with the data in the CORE record

    Returns:
        dict: The new record dict with access info added
    """
    # Access information
    if row["embargoed"] == "yes" and row["embargo_end_date"]:
        end_date_dt = datetime.strptime(
            row["embargo_end_date"].strip(), "%m/%d/%Y"
        ).date()
        end_date_iso = end_date_dt.isoformat()
        newrec.setdefault("access", {})["embargo"] = {
            "active": True,
            "until": end_date_iso,
            "reason": None,
        }
    return newrec, bad_data_dict


def add_titles(
    newrec: dict, row: dict, bad_data_dict: dict
) -> tuple[dict, dict]:
    """Add title information to the new record.

    The CORE record included two title fields: 'title_unchanged' with the raw
    title string entered by the user, and 'title' with the title string
    stripped of HTML tags. This function adds the unstripped 'title_unchanged'
    to the new record as its 'title'. If the two title fields are different,
    the stripped 'title' is added as an additional title (in
    'additional_titles') with type 'Primary title with HTML stripped'.

    args:
        newrec (_type_): The new record being prepared for serialization
        row (_type_): The CORE record being processed
        bad_data_dict (_type_): A dictionary of error messages recording
                                problems with the data in the CORE record

    Returns:
        dict: The new record dict with title info added
    """
    # Titles
    # FIXME: Filter out titles with punctuation from full biblio ref in
    #    field?
    # FIXME: Remove things like surrounding quotation marks
    mytitle = row["title_unchanged"]
    newrec["metadata"]["title"] = _clean_string(mytitle)
    if row["id"] == "hc:36367":
        newrec["metadata"]["title"] = (
            'Do "Creatures of the State" Have Constitutional Rights? Standing'
            " for Municipalities to Assert Procedural Due Process Claims"
            " against the State"
        )
    # FIXME: types here are CV, need to expand to accommodate stripped desc
    if row["title_unchanged"] != row["title"]:
        if row["id"] == "hc:36367":
            pass
        else:
            newrec["metadata"].setdefault("additional_titles", []).append(
                {
                    "title": _clean_string(row["title"]),
                    "type": {
                        "id": "other",
                        "title": {"en": "Primary title with HTML stripped"},
                    },
                }
            )
    return newrec, bad_data_dict


def add_descriptions(
    newrec: dict, row: dict, bad_data_dict: dict
) -> tuple[dict, dict]:
    """Add description information to the new record.

    The CORE record included two description fields: 'abstract_unchanged' with
    the raw description string entered by the user, and 'abstract' with the
    description string stripped of HTML tags. This function adds the unstripped
    'abstract_unchanged' to the new record as its 'description'. If the two
    description fields are different, the stripped 'abstract' is added as an
    additional description (in 'additional_descriptions') with type 'Other'.

    args:
        newrec (_type_): The new record being prepared for serialization
        row (_type_): The CORE record being processed
        bad_data_dict (_type_): A dictionary of error messages recording
                                problems with the data in the CORE record

    Returns:
        dict: The new record dict with description info added
    """

    # Descriptions/Abstracts
    # FIXME: handle double-escaped slashes?
    # FIXME: handle windows newlines?
    newrec["metadata"]["description"] = row["abstract_unchanged"].replace(
        "\r\n", "\n"
    )
    # FIXME: types here are CV, need to expand to accommodate stripped desc
    if row["abstract_unchanged"] != row["abstract"]:
        newrec["metadata"].setdefault("additional_descriptions", []).append(
            {
                "description": row["abstract"].replace("\r\n", "\n"),
                "type": {"id": "other", "title": {"en": "Other"}},
            }
        )
    return newrec, bad_data_dict


def add_notes(
    newrec: dict, row: dict, bad_data_dict: dict
) -> tuple[dict, dict]:
    """Add notes information to the new record.

    Uses the "notes_unchanged" field of the CORE record as the value for the
    custom field "kcr:notes" in the new record. If the "notes_unchanged" field
    is empty, no custom field is added.

    Args:
        newrec (_type_): The new record being prepared for serialization
        row (_type_): The CORE record being processed
        bad_data_dict (_type_): A dictionary of error messages recording
                                problems with the data in the CORE record

    Returns:
        dict: The new record dict with notes info added
    """
    # Notes
    if row["notes"]:
        newrec["custom_fields"]["kcr:notes"] = row["notes_unchanged"]
    return newrec, bad_data_dict


def add_identifiers(
    newrec: dict, row: dict, bad_data_dict: dict
) -> tuple[dict, dict]:
    """Add identifier information to the new record.

    Adds the following identifiers to the new record:
        - the CORE record's DOI as an `identifier` with scheme `doi`
        - the CORE record's URL as an `identifier` with scheme `url`
        - the CORE record's handle as an `identifier` with scheme `url`

    Args:
        newrec (_type_): The new record being prepared for serialization
        row (_type_): The CORE record being processed
        bad_data_dict (_type_): A dictionary of error messages recording
                                problems with the data in the CORE record

    Returns:
        dict: The new record dict with identifier info added
    """

    # Identifiers
    # FIXME: Is it right that these are all datacite dois?
    if row["deposit_doi"]:
        newrec.setdefault("pids", {})["doi"] = {
            "identifier": row["deposit_doi"].replace("doi:", ""),
            "provider": "datacite",
            "client": "datacite",
        }
        newrec["metadata"].setdefault("identifiers", []).append(
            {
                "identifier": row["deposit_doi"].replace("doi:", ""),
                "scheme": "datacite-doi",
            }
        )
    if row["doi"]:
        # FIXME: hc:24459 is getting description as doi value
        if len(row["doi"]) < 100:
            newrec["metadata"].setdefault("identifiers", []).append(
                {
                    "identifier": row["doi"].replace("https://doi.org/", ""),
                    "scheme": "doi",
                }
            )
        else:
            _append_bad_data(
                row["id"], ("doi too long", row["doi"]), bad_data_dict
            )
    if row["url"]:
        my_urls = re.split(r" and |;", row["url"])
        for url in my_urls:
            url = row["url"].replace(" ", "")
            if validators.url(url) or validators.url(f"https://{url}"):
                newrec["metadata"].setdefault("identifiers", []).append(
                    {
                        "identifier": row["url"].replace(
                            "http://dx.", "https://"
                        ),
                        "scheme": "url",
                    }
                )
            else:
                # print(row['id'], url)
                pass
    if row["handle"] and not any(
        n for n in newrec["metadata"]["identifiers"] if n["scheme"] == "url"
    ):
        newrec["metadata"].setdefault("identifiers", []).append(
            {
                "identifier": row["handle"].replace("http://dx.", "https://"),
                "scheme": "url",
            }
        )
    return newrec, bad_data_dict


def add_language_info(
    newrec: dict, row: dict, bad_data_dict: dict
) -> tuple[dict, dict]:
    """Add language information to the new record.

    Adds the language of the CORE record to the new record as a language
    identifier. If the CORE record does not have a language, the language is
    detected from the title and abstract fields using the langdetect library.

    Args:
        newrec (_type_): The new record being prepared for serialization
        row (_type_): The CORE record being processed
        bad_data_dict (_type_): A dictionary of error messages recording
                                problems with the data in the CORE record

    Returns:
        dict: The new record dict with language info added
    """

    # Language info
    # FIXME: Deal with all of these exceptions and the 'else' condition
    if row["language"]:
        if row["language"] == "Greek":
            row["language"] = "Greek, Modern (1453-)"
        mylang = iso639.Language.from_name(row["language"])
        newrec["metadata"]["languages"] = [
            {"id": mylang.part3, "title": {"en": mylang.name}}
        ]
    else:
        exceptions = [
            "hc:11565",
            "hc:48435",
            "hc:48455",
            "hc:11007",
            "hc:11263",
            "hc:11481",
            "hc:12907",
            "hc:13285",
            "hc:13321",
            "hc:13347",
            "hc:13351",
            "hc:13353",
            "hc:13377",
            "hc:13381",
            "hc:13461",
            "hc:13469",
            "hc:13477",
            "hc:13479",
            "hc:13503",
            "hc:13505",
            "hc:13507",
            "hc:13539",
            "hc:13569",
            "hc:13571",
            "hc:13577",
            "hc:13601",
            "hc:13643",
            "hc:13651",
            "hc:13673",
            "hc:13715",
            "hc:13785",
            "hc:13823",
            "hc:13841",
            "hc:13847",
            "hc:13939",
            "hc:13995",
            "hc:13997",
            "hc:14007",
            "hc:14065",
            "hc:14089",
            "hc:14093",
            "hc:14167",
            "hc:14169",
            "hc:14171",
            "hc:14173",
            "hc:14175",
            "hc:14179",
            "hc:14183",
            "hc:14187",
            "hc:14189",
            "hc:14193",
            "hc:14195",
            "hc:14207",
            "hc:14269",
            "hc:14271",
            "hc:14285",
            "hc:14331",
            "hc:14333",
            "hc:14343",
            "hc:14345",
            "hc:14393",
            "hc:14405",
            "hc:14407",
            "hc:14421",
            "hc:14425",
            "hc:14427",
            "hc:14433",
            "hc:14435",
            "hc:14437",
            "hc:14439",
            "hc:14461",
            "hc:14463",
            "hc:14465",
            "hc:14467",
            "hc:14469",
            "hc:14473",
            "hc:14477",
            "hc:14479",
            "hc:14481",
            "hc:14485",
            "hc:14517",
            "hc:14519",
            "hc:14523",
            "hc:14535",
            "hc:14537",
            "hc:14539",
            "hc:14615",
            "hc:14691",
            "hc:14695",
            "hc:14975",
            "hc:15237",
            "hc:15387",
            "hc:16197",
            "hc:16353",
            "hc:16473",
            "hc:16493",
            "hc:21289",
            "hc:29719",
            "hc:38161",
            "hc:40031",
            "hc:40185",
            "hc:41065",
            "hc:41659",
            "",
        ]
        lang1, lang2 = [], []
        if row["title"]:
            t = titlecase(row["title"])
            lang1 = [
                {"code": lang.lang, "prob": lang.prob}
                for lang in detect_langs(t)
            ]
        if row["abstract"]:
            try:
                lang2 = [
                    {"code": lang.lang, "prob": lang.prob}
                    for lang in detect_langs(row["abstract"])
                ]
            except Exception:
                pass
                # print('language exception with abstract!!!!')
                # print(row['abstract'])

        if lang1[0]["code"] == "en" and lang2 and lang2[0]["code"] == "en":
            newrec["metadata"]["languages"] = [
                {"id": "eng", "title": {"en": "English"}}
            ]
        elif lang1[0]["prob"] > 0.99 and row["id"] not in exceptions:
            newrec["metadata"]["languages"] = [{"id": lang1[0]["code"]}]
        elif (
            lang1[0]["prob"] < 0.9
            and lang2
            and lang2[0]["prob"] >= 0.9
            and row["id"] not in exceptions
        ):
            newrec["metadata"]["languages"] = [{"id": lang2[0]["code"]}]
        elif row["id"] in exceptions:
            pass
        else:
            # print(titlecase(row['title']))
            # print(row['id'], 'detected', lang1, lang2)
            pass

    return newrec, bad_data_dict


def add_edition_info(
    newrec: dict, row: dict, bad_data_dict: dict
) -> tuple[dict, dict]:
    """Add edition information to the new record.

    Adds the edition of the CORE record to the new record as a custom field
    `kcr:edition`.

    Args:
        newrec (_type_): The new record being prepared for serialization
        row (_type_): The CORE record being processed
        bad_data_dict (_type_): A dictionary of error messages recording
                                problems with the data in the CORE record

    Returns:
        dict: The new record dict with edition info added
    """

    # Edition
    # FIXME: There's some bad data here, like ISSNs
    if row["edition"]:
        newrec["custom_fields"]["kcr:edition"] = _clean_string(row["edition"])

    return newrec, bad_data_dict


def add_date_info(
    newrec: dict, row: dict, bad_data_dict: dict
) -> tuple[dict, dict]:
    """Add date information to the new record.

    Adds the following date information to the new record:
        - the CORE record's `date_issued` as a `publication_date`
        - the CORE record's `date` as an `issued` date
        - the CORE record's `record_change_date` as an `updated` date
        - the CORE record's `record_creation_date` as a `created` date

    Args:
        newrec (_type_): The new record being prepared for serialization
        row (_type_): The CORE record being processed
        bad_data_dict (_type_): A dictionary of error messages recording
                                problems with the data in the CORE record

    Returns:
        dict: The new record dict with date info added
    """

    def convert_date_words(date: str) -> str:
        """Convert a date string with words to a date string with numbers.

        Args:
            date (str): A date string with words

        Returns:
            str: The date string with words converted to numbers
        """
        date_parts = re.split(r"[, \.]", date)
        date_parts = [p for p in date_parts if p not in ["del", "de", " ", ""]]
        print(date_parts)
        month = ""
        day = ""
        year = ""
        months = {
            "january": "01",
            "enero": "01",
            "janvier": "01",
            "february": "02",
            "février": "02",
            "febrero": "02",
            "februar": "02",
            "march": "03",
            "marzo": "03",
            "marc": "03",
            "april": "04",
            "avril": "04",
            "abril": "04",
            "aprisl": "04",
            "апреля": "04",
            "may": "05",
            "mayo": "05",
            "mai": "05",
            "mei": "05",
            "june": "06",
            "junio": "06",
            "juin": "06",
            "july": "07",
            "julio": "07",
            "juillet": "07",
            "julho": "07",
            "august": "08",
            "agosto": "08",
            "août": "08",
            "september": "09",
            "septiembre": "09",
            "septembre": "09",
            "septmber": "09",
            "septemebr": "09",
            "settembre": "09",
            "october": "10",
            "octobre": "10",
            "octubre": "10",
            "november": "11",
            "novembre": "11",
            "noviembre": "11",
            "december": "12",
            "décembre": "12",
            "diciembre": "12",
            "dezembro": "12",
        }
        month_abbrevs = {
            "jan": "01",
            "janv": "01",
            "ja": "01",
            "feb": "02",
            "febr": "02",
            "fe": "02",
            "fev": "02",
            "mar": "03",
            "apr": "04",
            "ap": "04",
            "may": "05",
            "jun": "06",
            "jul": "07",
            "aug": "08",
            "au": "08",
            "sep": "09",
            "sept": "09",
            "se": "09",
            "oct": "10",
            "octo": "10",
            "oc": "10",
            "nov": "11",
            "no": "11",
            "dec": "12",
            "de": "12",
        }
        for d in date_parts:
            d_cand = d.lower().strip().replace(",", "").replace(".", "")
            if d_cand in months.keys():
                month = months[d_cand]
                date_parts = [p for p in date_parts if p != d]
            elif d_cand in month_abbrevs.keys():
                month = month_abbrevs[d_cand]
                date_parts = [p for p in date_parts if p != d]
        for d in date_parts:
            if len(d) == 4 and d.isdigit() and int(d) > 0 < 3000:
                year = d
                date_parts = [p for p in date_parts if p != d]
        for d in date_parts:
            suffixes = r"(th|st|nd|rd)"
            day_cand = re.sub(suffixes, "", d.lower())
            if day_cand.isdigit() and len(day_cand) <= 2:
                day = day_cand
                date_parts = [p for p in date_parts if p != d]
        if year and month and not day and len(date_parts) == 1:
            day = date_parts[0]
        if year and month and day:
            return reorder_date_parts("-".join([year, month, day]))
        elif year and month:
            return "-".join([year, month])
        else:
            return date

    def fill_missing_zeros(date: str) -> str:
        """Fill in missing zeros in a date string.

        Args:
            date (str): A date string with missing zeros

        Returns:
            str: The date string with missing zeros filled in
        """
        date_parts = list(filter(None, re.split(r"[\.\-:\/,]+", date)))
        for i, part in enumerate(date_parts):
            if len(part) < 2:
                date_parts[i] = "0" + part
            if part.isdigit() and len(part) == 2 and int(part) > 31:
                if int(part) <= 27:
                    date_parts[i] = "20" + part
                else:
                    date_parts[i] = "19" + part
        return "-".join(date_parts)

    def reorder_date_parts(date: str) -> str:
        """Reorder the parts of a date string.

        Args:
            date (str): A date string with parts in the order YYYY-DD-MM or
                        DD-MM-YYYY or MM-DD-YYYY

        Returns:
            str: The date string with parts in the order YYYY-MM-DD
        """
        date = fill_missing_zeros(date)
        date_parts = list(filter(None, re.split(r"[\.\-:\/ ]+", date)))
        print(date_parts)
        try:
            assert len(date_parts) >= 2 <= 3
            assert [int(p) for p in date_parts]
            year = [d for d in date_parts if len(d) == 4][0]
            others = [d for d in date_parts if len(d) != 4]
            if len(others) == 2:
                month_candidates = [d for d in date_parts if int(d) <= 12]
                if len(month_candidates) == 1:
                    month = month_candidates[0]
                    day = [d for d in others if d != month][0]
                else:
                    month, day = others
                return "-".join([year, month, day])
            else:
                return "-".join([year, others[0]])
        except (AssertionError, IndexError, ValueError):
            return date

    def parse_human_readable(date: str) -> str:
        """Parse a human readable date string.

        Args:
            date (str): A human readable date string

        Returns:
            str: The date string parsed into ISO format
        """
        try:
            return timefhuman(row["date"]).isoformat().split("T")[0]
        except (ValueError, TypeError, IndexError):
            return date

    def is_seasonal_date(date: str) -> bool:
        """Return True if the date is a human readable seasonal date."""
        seasons = [
            "spring",
            "summer",
            "fall",
            "winter",
            "autumn",
            "spr",
            "sum",
            "fal",
            "win",
            "aut",
            "intersession",
        ]
        date_parts = date.split(" ")
        valid = False
        if len(date_parts) == 2:
            years = [d for d in date_parts if len(d) in [2, 4] and d.isdigit()]
            if len(years) == 1:
                season_part = [d for d in date_parts if d != years[0]][0]
                season_parts = re.findall(r"\w+", season_part)
                if all(s for s in season_parts if s.lower() in seasons):
                    valid = True
        return valid

    def repair_date(date: str) -> tuple[bool, str]:
        invalid = True
        newdate = date
        for date_func in [
            reorder_date_parts,
            convert_date_words,
            parse_human_readable,
        ]:
            newdate = date_func(row["date"])
            print(date_func)
            print(newdate)
            if valid_date(newdate):
                print(valid_date(newdate))
                invalid = False
                break

        if invalid and is_seasonal_date(date):
            invalid = False

        return invalid, newdate

    def repair_range(date: str) -> tuple[bool, str]:
        print("repairing range")
        invalid = True
        range_parts = re.split(r"[\-–\/]", date)
        print(range_parts)
        if (
            len(range_parts) == 2
            and len(range_parts[0]) == 4
            and range_parts[0][:2] in ["19", "20"]
            and len(range_parts[1]) == 2
        ):
            if range_parts[1].isdigit() and int(range_parts[1]) <= 30:
                range_parts[1] = "20" + range_parts[1]
            elif range_parts[1].isdigit() and int(range_parts[1]) > 30:
                range_parts[1] = "19" + range_parts[1]
        for i, part in enumerate(range_parts):
            if not valid_date(part):
                invalid, range_parts[i] = repair_date(part)
            else:
                invalid = False
        print(range_parts)
        if not invalid:
            date = "/".join(range_parts)
        print(date)
        return invalid, date

    # Date info
    # FIXME: does "issued" work here?
    pprint(newrec["metadata"])
    pprint(row)
    newrec["metadata"]["publication_date"] = row["date_issued"].split("T")[0]
    if row["date_issued"] != row["date"] and row["date"] not in ["", " "]:
        row["date"] = row["date"].split("T")[0]
        date_description = "Publication date"
        date_to_insert = row["date"]
        if not valid_date(date_to_insert):
            print("invalid")
            invalid, date_to_insert = repair_date(date_to_insert)
            print(date_to_insert)
            if invalid:
                invalid, date_to_insert = repair_range(date_to_insert)
            if invalid and date_to_insert.lower() in [
                "undated",
                "forthcoming",
            ]:
                invalid = False
            if invalid:
                _append_bad_data(
                    row["id"],
                    ("bad date", row["date"], date_to_insert),
                    bad_data_dict,
                )
                date_description = "Human readable publication date"
        newrec["metadata"].setdefault("dates", []).append(
            {
                "date": date_to_insert,
                "type": {
                    "id": "issued",
                    "title": {"en": "Issued", "de": "Veröffentlicht"},
                },
                "description": date_description,
            }
        )

    if row["record_change_date"]:
        assert valid_date(row["record_change_date"])
        # except AssertionError:
        #     print(row['id'])
        #     print(row['record_change_date'])
        #     print(valid_date(row['record_change_date']))
        newrec["updated"] = row["record_change_date"]
        newrec["custom_fields"]["hclegacy:record_change_date"] = row[
            "record_change_date"
        ]
    if row["record_creation_date"]:
        assert valid_date(row["record_creation_date"])
        newrec["created"] = row["record_creation_date"]
        newrec["custom_fields"]["hclegacy:record_creation_date"] = row[
            "record_creation_date"
        ]

    return newrec, bad_data_dict


def add_groups_info(
    newrec: dict, row: dict, bad_data_dict: dict
) -> tuple[dict, dict]:
    """Add information about Commons groups to the new record.

    Adds the following group information to the new record:
        - for each group, combines the Commons group id (in the `group_ids`
        list) and group name (in the `group` list) as an item in the custom
        field `hclegacy:groups_for_deposit`

    Args:
        newrec (_type_): The new record being prepared for serialization
        row (_type_): The CORE record being processed
        bad_data_dict (_type_): A dictionary of error messages recording
                                problems with the data in the CORE record

    Returns:
        dict: The new record dict with group info added
    """

    # Group info for deposit
    try:
        # print(row['group'])
        # print(row['group_ids'])A. Pifferetti, A. & I. Dosztal (comps.i
        if row["group"] not in [None, [], ""]:
            row["group"] = row["group"]
        if row["group_ids"] not in [None, [], ""]:
            row["group_ids"] = row["group_ids"]
        assert len(row["group"]) == len(row["group_ids"])
        group_list = []
        if len(row["group"]) > 0:
            for i, n in enumerate(row["group_ids"]):
                group_list.append(
                    {"group_identifier": n, "group_name": row["group"][i]}
                )
            newrec["custom_fields"]["hclegacy:groups_for_deposit"] = group_list
    except AssertionError:
        row["hclegacy:groups_for_deposit"] = None
        _append_bad_data(
            row["id"],
            ("group or group_ids", row["group"], row["group_ids"]),
            bad_data_dict,
        )
    except json.decoder.JSONDecodeError:
        # print(e)
        # print(row['group'], row['group_ids'])
        row["hclegacy:groups_for_deposit"] = None
        _append_bad_data(
            row["id"],
            ("group or group_ids", row["group"], row["group_ids"]),
            bad_data_dict,
        )

    return newrec, bad_data_dict


def add_book_authors(
    newrec: dict, row: dict, bad_data_dict: dict
) -> tuple[dict, dict]:
    """Add book author information to the new record.

    Args:
        newrec (_type_): The new record being prepared for serialization
        row (_type_): The CORE record being processed
        bad_data_dict (_type_): A dictionary of error messages recording
                                problems with the data in the CORE record
    Returns:
        dict: The new record dict with book author info added
    """

    # book info
    # FIXME: Need to augment out-of-the-box imprint custom fields
    if row["book_author"]:
        book_names, bad_data_dict = _add_book_authors(
            row["book_author"], bad_data_dict, row["id"]
        )
        newrec["metadata"].setdefault("contributors", []).extend(book_names)

    return newrec, bad_data_dict


def add_volume_info(
    newrec: dict, row: dict, bad_data_dict: dict
) -> tuple[dict, dict]:
    """Add volume information to the new record.

    Adds the volume of the CORE record to the new record as a custom field
    `kcr:volumes`.

    Args:
        newrec (_type_): The new record being prepared for serialization
        row (_type_): The CORE record being processed
        bad_data_dict (_type_): A dictionary of error messages recording
                                problems with the data in the CORE record
    Returns:
        dict: The new record dict with volume info added
    """

    # volume info
    # FIXME: distinguish volume meaning for ambiguous resource types
    if row["volume"]:
        if newrec["metadata"]["resource_type"]["id"] in article_types:
            newrec["custom_fields"].setdefault("journal:journal", {})[
                "volume"
            ] = row["volume"]
        elif newrec["metadata"]["resource_type"]["id"] in book_types:
            newrec["custom_fields"].setdefault("kcr:volumes", {})["volume"] = (
                row["volume"]
            )
        else:
            # print(row['id'], newrec['metadata']['resource_type']['id'],
            # row['volume'])
            newrec["custom_fields"].setdefault("kcr:volumes", {})["volume"] = (
                row["volume"]
            )
    return newrec, bad_data_dict


def add_publication_details(
    newrec: dict, row: dict, bad_data_dict: dict
) -> tuple[dict, dict]:
    """Add publication information to the new record.

    Adds the ISBN of the CORE record to the new record as a custom field
    `imprint:imprint:isbn`. If the work has more than one isbn, additional
    numbers are added as identifiers with scheme `isbn`. If the ISBN is
    invalid, it is added to the `bad_data_dict` with the key `invalid isbn`.

    Also adds the publisher of the CORE record to the new record as a metadata
    field `publisher`. If the publisher is missing, the publisher is set to
    "unknown".

    Args:
        newrec (_type_): The new record being prepared for serialization
        row (_type_): The CORE record being processed
        bad_data_dict (_type_): A dictionary of error messages recording
                                problems with the data in the CORE record
    Returns:
        dict: The new record dict with ISBN info added
    """

    if row["isbn"]:
        row["isbn"] = row["isbn"].replace(r"\\0", "")
        isbn = get_isbnlike(row["isbn"])

        # FIXME: make isbn a list
        # FIXME: still record invalid isbns?
        isbn_list = []
        for i in isbn:
            checked_i = valid_isbn(i)
            if not checked_i:
                # print(isbn)
                # print('invalid isbn', ':', checked_i, ':', clean(i), ':',
                # row['isbn'])
                _append_bad_data(
                    row["id"], ("invalid isbn", row["isbn"]), bad_data_dict
                )
            else:
                isbn_list.append(checked_i)
        if len(isbn_list) > 0:
            newrec["custom_fields"].setdefault("imprint:imprint", {})[
                "isbn"
            ] = isbn_list[0]
            if len(isbn_list) > 1:
                for i in isbn_list[1:]:
                    newrec["metadata"].setdefault("identifiers", []).append(
                        {"identifier": i, "scheme": "isbn"}
                    )

    # FIXME: Handle missing publishers?
    if row["publisher"]:
        newrec["metadata"]["publisher"] = _clean_string(row["publisher"])
    else:
        newrec["metadata"]["publisher"] = "unknown"

    return newrec, bad_data_dict


def add_book_journal_title(
    newrec: dict, row: dict, bad_data_dict: dict
) -> tuple[dict, dict]:
    """Add book/journal title information to the new record.

    If the record resource type is a book, adds the CORE record's
    `book_journal_title` as a custom field `imprint:imprint:title`. If the
    record resource type is an article, adds the CORE record's
    `book_journal_title` as a custom field `journal:journal:title`. If the
    record resource type is neither a book nor an article, adds the CORE
    record's `book_journal_title` as a custom field `imprint:imprint:title` and
    adds the record resource type to the `bad_data_dict` with the key
    `resource_type for book_journal_title`.

    Args:
        newrec (_type_): The new record being prepared for serialization
        row (_type_): The CORE record being processed
        bad_data_dict (_type_): A dictionary of error messages recording
                                problems with the data in the CORE record

    Returns:
        dict: The new record dict with book/journal title info added
    """
    if row["book_journal_title"]:
        myfield = "imprint:imprint"
        if newrec["metadata"]["resource_type"]["id"] in article_types:
            myfield = "journal:journal"
        if newrec["metadata"]["resource_type"]["id"] not in [
            *book_types,
            *article_types,
        ] and publication_types[
            newrec["custom_fields"]["hclegacy:publication_type"]
        ] not in [
            *book_types,
            *article_types,
        ]:
            # print('****', newrec['metadata']['resource_type']['id'])
            _append_bad_data(
                row["id"],
                (
                    "resource_type for book_journal_title",
                    newrec["metadata"]["resource_type"]["id"],
                ),
                bad_data_dict,
            )
        # FIXME: check right field for legalComment, bibliography, lecture,
        # conferencePaper, legalResponse, other:other, other:essay,
        # translation, videoRecording, blogPost, interviewTranscript,
        # poeticWork,
        # fictionalWork, image:visualArt, image:map,
        # instructionalResource:syllabus, onlinePublication,
        # presentation:other,
        # instructionalResource:other, musicalRecording, catalog, dataset,
        # audiovisual:documentary, lecture
        if myfield not in newrec["custom_fields"].keys():
            newrec["custom_fields"][myfield] = {}
        # FIXME: in hc:24459 title replaced by just \\\\
        # FIXME: in hc:52887, hc:27377 title truncated with \\\\
        newrec["custom_fields"][myfield]["title"] = _clean_string(
            row["book_journal_title"]
        )
    return newrec, bad_data_dict


def add_pages(
    newrec: dict, row: dict, bad_data_dict: dict
) -> tuple[dict, dict]:
    """Add page information to the new record.

    Adds the following page information to the new record:
        - if the record resource type is an article, adds the CORE record's
        `start_page` and `end_page` as a custom field `journal:journal:pages`
        - if the record resource type is a chapter, adds the CORE record's
        `start_page` and `end_page` as a custom field `imprint:imprint:pages`

    Args:
        newrec (_type_): The new record being prepared for serialization
        row (_type_): The CORE record being processed
        bad_data_dict (_type_): A dictionary of error messages recording
        problems with the data in the CORE record

    Returns:
        dict: The new record dict with page info added
    """

    # article/chapter info

    if row["start_page"]:
        pages = row["start_page"]
        if row["end_page"]:
            pages = f'{pages}-{row["end_page"]}'
        if newrec["metadata"]["resource_type"]["id"] in article_types:
            newrec["custom_fields"].setdefault("journal:journal", {})[
                "pages"
            ] = pages
        else:
            newrec["custom_fields"].setdefault("imprint:imprint", {})[
                "pages"
            ] = pages
        if newrec["metadata"]["resource_type"]["id"] not in [
            *book_types,
            *article_types,
            *ambiguous_types,
        ] and publication_types[
            newrec["custom_fields"]["hclegacy:publication_type"]
        ] not in [
            *book_types,
            *article_types,
            *ambiguous_types,
        ]:
            _append_bad_data(
                row["id"],
                (
                    "resource_type for start_page/end_page",
                    newrec["metadata"]["resource_type"]["id"],
                ),
                bad_data_dict,
            )
    return newrec, bad_data_dict


def add_journal_info(
    newrec: dict, row: dict, bad_data_dict: dict
) -> tuple[dict, dict]:
    """Add journal information to the new record.

    Adds the following journal information to the new record:
        - If the record has an `issue` value, adds the CORE record's `issue` as
        a custom field `journal:journal:issue`
        - If the record has an `issn` value, adds the CORE record's `issn` as a
        custom field `journal:journal:issn`. Validates the ISSN and tries to
        repair malformed ISSNs. If the `issn` is invalid, it is added to the
        `bad_data_dict` with the key `invalid issn`. If the `issn` validates as
        an ISBN, adds it instead as a custom field `imprint:imprint:isbn` and
        adds the `issn` to the `bad_data_dict` with the key `isbn in issn
        field`.

    Args:
        newrec (_type_): The new record being prepared for serialization
        row (_type_): The CORE record being processed
        bad_data_dict (_type_): A dictionary of error messages
        recording problems with the data in the CORE record

    Returns:
        dict: The new record dict with journal info added
    """

    def sanitize_issn_string(mystring):
        assert type(mystring) is str
        mystring = mystring.replace("\u2013", "-")
        mystring = mystring.replace("\u2014", "-")
        mystring = re.sub(r"\s?-\s?", "-", mystring)
        mystring = mystring.replace("Х", "X")
        mystring = mystring.replace(".", "")
        return mystring

    if row["issue"]:
        issue = re.sub(r"([Ii]ssue|[nN][Oo]?\.?)\s?", "", row["issue"])
        issue = re.sub(r"\((.*)\)", r"\1", issue)
        issue = re.sub(r"[\.,]$", "", issue)
        newrec["custom_fields"].setdefault("journal:journal", {})[
            "issue"
        ] = issue

    # FIXME: make issn a list
    if row["issn"]:
        extra_issns = []
        myissn = row["issn"]
        if isinstance(row["issn"], list):
            myissn = row["issn"][0]
            for i in row["issn"][1:]:
                extra_issns.append(i)

        if valid_isbn(myissn):
            # print('isbn', row['issn'])
            newrec["custom_fields"].setdefault("imprint:imprint", {})[
                "isbn"
            ] = myissn
            _append_bad_data(
                row["id"],
                ("issn", "isbn in issn field", myissn),
                bad_data_dict,
            )
        else:
            # myissn = row['issn'].replace(b'\xe2\x80\x94'.decode('utf-8'),
            # '-')
            # myissn = myissn.replace('\x97', '-')
            myissn = sanitize_issn_string(myissn)
            myissnx = re.findall(r"\d{4}[-\s\.]?\d{3}[\dxX]", myissn)
            if isinstance(myissnx, list) and len(myissnx) >= 1:
                if len(myissnx) > 1:
                    for i in myissnx[1:]:
                        extra_issns.append(i)
                myissnx = myissnx[0]
            if len(myissnx) < 1:
                _append_bad_data(
                    row["id"],
                    ("issn", "malformed", row["issn"]),
                    bad_data_dict,
                )
            else:
                assert type(myissn) is str
                myissnx = re.sub(r"ISSN:? ?", "", myissnx)
                try:
                    if issn.validate(myissnx):
                        newrec["custom_fields"].setdefault(
                            "journal:journal", {}
                        )["issn"] = myissnx
                except Exception:
                    # print('exception', i, row['issn'])
                    _append_bad_data(
                        row["id"],
                        ("issn", "invalid last digit", row["issn"]),
                        bad_data_dict,
                    )

        if len(extra_issns) > 0:
            for i in extra_issns:
                if valid_isbn(i):
                    newrec["metadata"].setdefault("identifiers", []).append(
                        {"identifier": i, "scheme": "isbn"}
                    )
                    _append_bad_data(
                        row["id"],
                        ("issn", "isbn in issn field", i),
                        bad_data_dict,
                    )
                else:
                    i = sanitize_issn_string(i)
                    if issn.validate(i):
                        newrec["metadata"].setdefault(
                            "identifiers", []
                        ).append({"identifier": i, "scheme": "issn"})
                    else:
                        _append_bad_data(
                            row["id"], ("issn", "malformed", i), bad_data_dict
                        )

    return newrec, bad_data_dict


def add_institution(
    newrec: dict, row: dict, bad_data_dict: dict
) -> tuple[dict, dict]:
    """Add institution information to the new record.

    Args:
        newrec (_type_): The new record being prepared for serialization
        row (_type_): The CORE record being processed
        bad_data_dict (_type_): A dictionary of error messages recording
        problems with the data in the CORE record

    Returns:
        dict: The new record dict with institution info added
    """

    if row["institution"]:
        # print(row['id'])
        # print(newrec['metadata']['resource_type']['id'])
        newrec["custom_fields"]["kcr:sponsoring_institution"] = _clean_string(
            row["institution"]
        )
        if newrec["metadata"]["resource_type"]["id"] not in [
            "textDocument-thesis",
            "textDocument-report",
            "textDocument-whitePaper",
        ]:
            _append_bad_data(
                row["id"],
                (
                    "resource_type for institution",
                    newrec["metadata"]["resource_type"]["id"],
                ),
                bad_data_dict,
            )

    return newrec, bad_data_dict


def add_meeting_info(
    newrec: dict, row: dict, bad_data_dict: dict
) -> tuple[dict, dict]:
    """Add meeting information to the new record.

    Adds the following meeting information to the new record:

        - If the record has a `conference_date` or `meeting_date` value, adds
        the CORE record's `conference_date` or `meeting_date` as a `dates`
        subfield of the custom field `meeting:meeting`
        - If the record has a `conference_location` or `meeting_location`
        value, adds the CORE record's `conference_location` or
        `meeting_location` as a `place` subfield of the custom field
        `meeting:meeting`
        - If the record has a `conference_organization` or
        `meeting_organization` value, adds the CORE record's
        `conference_organization` or `meeting_organization` as a custom field
        `kcr:meeting_organization`
        - If the record has a `conference_title` or `meeting_title` value, adds
        the CORE record's `conference_title` or `meeting_title` as a `title`
        subfield of the custom field `meeting:meeting`

    Args:
        newrec (_type_): The new record being prepared for serialization
        row (_type_): The CORE record being processed
        bad_data_dict (_type_): A dictionary of error messages recording
        problems with the data in the CORE record

    Returns:
        dict: The new record dict with meeting info added
    """

    if row["conference_date"] or row["meeting_date"]:
        # if not newrec['custom_fields']['meeting:meeting']:
        #     newrec['custom_fields']['meeting:meeting'] = {}
        newrec["custom_fields"].setdefault("meeting:meeting", {})["dates"] = (
            row["conference_date"] or row["meeting_date"]
        )
    if row["conference_location"] or row["meeting_location"]:
        newrec["custom_fields"].setdefault("meeting:meeting", {})["place"] = (
            _clean_string(
                row["conference_location"] or row["meeting_location"]
            )
        )
    if row["conference_organization"] or row["meeting_organization"]:
        newrec["custom_fields"]["kcr:meeting_organization"] = _clean_string(
            row["conference_organization"] or row["meeting_organization"]
        )
    # FIXME: meeting_title being truncated with \\\\ in hc:46017, hc:19211
    if row["conference_title"] or row["meeting_title"]:
        newrec["custom_fields"].setdefault("meeting:meeting", {})["title"] = (
            _clean_string(row["conference_title"] or row["meeting_title"])
        )

    return newrec, bad_data_dict


def add_subjects_keywords(
    newrec: dict, row: dict, bad_data_dict: dict
) -> tuple[dict, dict]:
    """Add subject and keyword information to the new record.

    Adds the following subject and keyword information to the new record:
        - If the record has a `keyword` value, adds each item from the CORE
        record's `keyword` to a custom field `kcr:user_defined_tags`
        - If the record has a `subject` value, for each item in the `subject`
        list adds a dictionary with the following information to the `subjects`
        list of the new record's metadata:
            - `id`: the FAST id for the subject (a url string)
            - `subject`: the subject heading (a string)
            - `scheme`: the FAST facet label for the subject (a string)
        Attempts to fix malformed subject headings in the CORE record because
        Invenio will not accept invalid subject entries.

    Args:
        newrec (_type_): The new record being prepared for serialization
        row (_type_): The CORE record being processed
        bad_data_dict (_type_): A dictionary of error messages recording
        problems with the data in the CORE record

    Returns:
        dict: The new record dict with subject and keyword info added
    """

    # FIXME: keyword ids filled in and harmonized where possible
    #   with subject headings below
    # FIXME: use named entity recognition to regularize
    #   capitalization?
    if row["keyword"]:
        keywords = []
        if isinstance(row["keyword"], dict):
            row["keyword"] = row["keyword"].values()
            for k in row["keyword"]:
                # kid = None
                # if k.casefold() in keywords_global_dict.keys():
                #     kid = keywords_global_dict[k.casefold()][0]
                #     if k not in keywords_global_dict[k.casefold()][1]:
                #         keywords_global_dict[k.casefold()][1].append(k)
                # print('got id from global for keyword', k)
                # else:
                #     kid = current_keyword_id
                #     keywords_global_dict[k.casefold()] = (kid, [k])
                #     current_keyword_id += 1
                # print('missing id for keyword', k)
                # keywords.append({'tag_label': k,
                #                  'tag_identifier': kid})
                keywords.append(k)
        else:
            keywords = row["keyword"]

        if keywords:
            newrec["custom_fields"]["kcr:user_defined_tags"] = keywords

    if row["subject"]:
        missing_subjects = [
            "Public humanities",
            "Scholarly communication",
            "European history",
            "African American culture",
            "Literature and philosophy",
            "Asian history",
            "Modern history",
            "Postcolonial literature",
            "Ancient history",
            "Ancient Mediterranean religions",
            "Early Christianity",
            "Religions of late Antiquity",
            "Literature and economics",
            "Contemporary art",
            "Translation studies",
            "Classical studies",
            "Sociology of development",
            "African studies",
            "Data sharing",
            "Cultural anthropology",
            "Criticism of the arts",
            "Theory of the arts",
            "Music criticism",
            "African American studies",
            "Ancient literature",
            "Biblical studies",
            "Hebrew bible",
            "Literary criticism",
            "Pentateuchal studies",
            "Medieval studies",
            "Urban studies",
            "Comparative religious ethics",
            "American studies",
            "Asian-American studies",
            "Film studies",
            "17th century",
            "Migration studies",
            "Music analysis",
            "Ancient Greece",
            "Music information retrieval",
            "Archival studies",
            "Native American literature",
            "Coming-of-age literature",
            "Poesia",
            "American art",
            "Late Antiquity",
            "Music composition",
            "Accelerationism",
            "Behavioral anthropology",
            "20th century",
            "Immigration history",
            "Bibliography",
            "Biography",
            "Education",
            "English",
            "Poetry",
            "Romanticism",
            "19th-century German literature",
            "Polish culture",
            "Polish studies",
        ]
        bad_subjects = {
            "1411635:Criticism, interpretation, etc.:topical": (
                "1411635:Criticism, interpretation, etc.:form"
            ),
            "863509:Classsical literature:topical": (
                "863509:Classical literature:topical"
            ),
            "Art history": "815264:Art--History:topical",
            "Medieval literature": "1000151:Literature, Medieval:topical",
            "Literary theory": "1353577:Literature--Theory:topical",
            "Cultural studies": "885059:Culture:topical",
            "Political philosophy": (
                "1060799:Philosophy--Political aspects:topical"
            ),
            "History of religions": "1093783:Religion--History:topical",
            "Religious studies": "1093763:Religion:topical",
            "Translation": "1154795:Translating and interpreting:topical",
            "Australasian/Pacific literature": (
                "821406:Australasian literature:topical"
            ),
            "Comics": "1921613:Comics (Graphic works):form",
            "Graphic novels": "1726630:Graphic novels:form",
            "Cultural history": "885069:Culture--History:topical",
            "Epigraphy": "973837:Inscriptions:topical",
            "Latin American studies": "1245945:Latin America:geographic",
            "Sociology of agriculture": (
                "801646:Agriculture--Social aspects:topical"
            ),
            "Ancient law": "993683:Law--Antiquities:topical",
            "Digital communication": "893634:Digital communications:topical",
            "Internet sociology": "1766793:Internet--Social aspects:topical",
            "Library and information science": (
                "997916:Library science:topical"
            ),
            "Social anthropology": (
                "810233:Anthropology--Social aspects:topical"
            ),
            "History of the arts": "817758:Arts--History:topical",
            "Music history": "1030330:Music--History:topical",
            "Interdisciplinary studies": (
                "976131:Interdisciplinary research:topical"
            ),
            "Illuminated manuscripts": (
                "967235:Illumination of books and manuscripts:topical"
            ),
            "India": "1210276:India:geographic",
            "Apostle Paul": "288253:St. Paul:personal",
            "Academic librarianship": "794993:Academic librarians:topical",
            "Sociology of aging": "800348:Aging--Social aspects:topical",
            "Sociology of culture": "885083:Culture--Social aspects:topical",
            "Holocaust studies": "958866:Jewish Holocaust (1939-1945):topical",
            "Literature and psychology": (
                "1081551:Psychology and literature:topical"
            ),
            "Gender studies": "939598:Gender identity--Research:topical",
            "Historical musicology": "1030896:Musicology--History:topical",
            "Shakespeare": "314312:Shakespeare, William, 1849-1931:personal",
            "Sociology of finance": (
                "842573:Business enterprises--Finance--Social aspects:topical"
            ),
            "Central Europe": "1244544:Central Europe:geographic",
            "Contemporary history": (
                "1865054:History of contemporary events:topical"
            ),
            "Labor history": "989812:Labor--History:topical",
            "Epicurus": "44478:Epicurus:personal",
            "Stanley Cavell": "28565:Cavell, Stanley, 1926-2018:personal",
            "Translation of poetry": "1067745:Poetry--Translating:topical",
            "James Joyce": "370728:Joyce, James:personal",
            "Jack Kerouac": "52352:Kerouac, Jack, 1922-1969:personal",
            "Feminisms": "922671:Feminism:topical",
            "Feminist art history": "922756:Feminist art criticism:topical",
            "Gospels": "1766655:Bible stories, English--N.T. Gospels:topical",
            "Manuscript studies": "1008230:Manuscripts:topical",
            "Book history": "836420:Books--History:topical",
            "Harlem Renaissance": "951467:Harlem Renaissance:topical",
            "Music performance": "1030398:Music--Performance:topical",
            "Latin America": "1245945:Latin America:topical",
            "Portuguese culture": (
                "1072404:Portuguese--Ethnic identity:topical"
            ),
            "Venezuela": "1204166:Venezuela:geographic",
            "Aesthetic theory": "798702:Aesthetics:topical",
            "21st-century American literature": (
                "807113:American literature:topical"
            ),
            "Poetics and poetry": "1067682:Poetics:topical",
        }
        covered_subjects = []
        if isinstance(row["subject"], dict):
            row["subject"] = row["subject"].values()
        for s in row["subject"]:
            if s in missing_subjects:
                newrec["custom_fields"].setdefault(
                    "kcr:user_defined_tags", []
                ).append(s)
            else:
                if s in bad_subjects.keys():
                    s = bad_subjects[s]
                # normalize inconsistent facet labels
                pieces = list(filter(None, s.split(":")))
                if len(pieces) < 3:
                    try:
                        s = _get_subject_from_jsonl(s)
                        pieces = s.split(":")
                        assert s != ""
                    except AssertionError:
                        newrec["custom_fields"].setdefault(
                            "kcr:user_defined_tags", []
                        ).append(s)
                        _append_bad_data(
                            row["id"], ("invalid subject", s), bad_data_dict
                        )
                id_num = pieces[0]
                subject = ":".join(pieces[1:-1])
                facet_label = pieces[-1]
                subs = {
                    "Corporate Name": "corporate",
                    "Topic": "topical",
                    "Event": "event",
                    "Form\/Genre": "form",
                    "Geographic": "geographic",
                    "Meeting": "meeting",
                    "Personal Name": "personal",
                }
                if facet_label in subs.keys():
                    facet_label = subs[facet_label]
                if s not in covered_subjects:
                    newrec["metadata"].setdefault("subjects", []).append(
                        {
                            "id": f"http://id.worldcat.org/fast/{id_num}",
                            "subject": subject,
                            "scheme": f"FAST-{facet_label}",
                        }
                    )
                covered_subjects.append(s)

    return newrec, bad_data_dict


def add_rights_info(
    newrec: dict, row: dict, bad_data_dict: dict
) -> tuple[dict, dict]:
    """Add rights information to the new record.

    Adds the following rights information to the new record:
        - If the record has a `type_of_license` value, adds the CORE record's
        `type_of_license` as a `rights` subfield of the new record's metadata.
        The `rights` subfield is a list of dictionaries with the following
        information:
            - `id`: the id for the license (a string)
            - `props`: a dictionary with the following information:
                - `url`: the url for the license (a string)
                - `scheme`: the license scheme (a string) with a value of
                'spdx' (left out for 'arr' licenses)
            - `title`: the title of the license (a dictionary with a single
            key/value pair, where the key is the language code and the value
            is the license title in that language)
            - `description`: the description of the license (a dictionary with
            a single key/value pair, where the key is the language code and the
            value is the license description in that language)

    Args:
        newrec (_type_): The new record being prepared for serialization
        row (_type_): The CORE record being processed
        bad_data_dict (_type_): A dictionary of error messages recording
        problems with the data in the CORE record

    Returns:
        dict: The new record dict with rights info added
    """

    if row["type_of_license"]:
        license_id, license_name, license_url = licenses[
            row["type_of_license"]
        ]
        newrec["metadata"].setdefault("rights", []).append(
            {
                "id": license_id,
                # can't pass both id and title/description
                # "props": {"url": license_url},
                # "title": {"en": license_name},
                # "description": {"en": ""},
            }
        )
        # if license_id != "arr":
        #     newrec["metadata"]["rights"][0]["props"]["scheme"] = "spdx"

    return newrec, bad_data_dict


def add_file_info(
    newrec: dict, row: dict, bad_data_dict: dict
) -> tuple[dict, dict]:
    """Add file information to the new record.

    Args:
        newrec (_type_): The new record being prepared for serialization
        row (_type_): The CORE record being processed
        bad_data_dict (_type_): A dictionary of error messages recording
        problems with the data in the CORE record

    Returns:
        dict: The new record dict with file info added
    """

    if row["file_pid"] or row["fileloc"] or row["filename"]:
        newrec["custom_fields"]["hclegacy:file_location"] = row["fileloc"]
        newrec["custom_fields"]["hclegacy:file_pid"] = row["file_pid"]
        newrec["files"] = {
            "enabled": True,
            "entries": {
                f'{row["filename"]}': {
                    "key": row["filename"],
                    "mimetype": row["filetype"],
                    "size": row["filesize"],
                }
            },
            "default_preview": row["filename"],
        }
    return newrec, bad_data_dict


def serialize_json() -> tuple[list[dict], dict]:
    """
    Parse and serialize csv data into Invenio JSON format.
    """
    debug = GLOBAL_DEBUG or True

    baserec: dict = {
        "parent": {"access": {"owned_by": []}},
        "custom_fields": {},
        "metadata": {
            "resource_type": {},
            "title": "",
            "creators": [],
            "publication_date": [],
            "identifiers": [],
            "languages": [],
            "rights": [],
        },
        "files": {"entries": []},
    }

    newrec_list: list[dict] = []
    bad_data_dict: dict[str, list] = {}
    line_count: int = 0

    with open(Path(DATA_DIR, "core-export-may-15-23.json")) as json_file:
        top_object = json.loads(json_file.read())
        for row in top_object:
            newrec = deepcopy(baserec)

            # commons info
            newrec, bad_data_dict = add_legacy_commons_info(
                newrec, row, bad_data_dict
            )
            newrec, bad_data_dict = add_groups_info(newrec, row, bad_data_dict)
            newrec, bad_data_dict = add_embargo_info(
                newrec, row, bad_data_dict
            )

            # basic metadata
            newrec, bad_data_dict = add_titles(newrec, row, bad_data_dict)
            newrec, bad_data_dict = add_descriptions(
                newrec, row, bad_data_dict
            )
            newrec, bad_data_dict = add_notes(newrec, row, bad_data_dict)
            newrec, bad_data_dict = _add_resource_type(
                newrec, row, bad_data_dict
            )
            newrec, bad_data_dict = add_identifiers(newrec, row, bad_data_dict)
            newrec, bad_data_dict = add_language_info(
                newrec, row, bad_data_dict
            )
            newrec, bad_data_dict = add_edition_info(
                newrec, row, bad_data_dict
            )
            newrec, bad_data_dict = _add_author_data(
                newrec, row, bad_data_dict
            )
            newrec, bad_data_dict = add_date_info(newrec, row, bad_data_dict)
            newrec, bad_data_dict = add_subjects_keywords(
                newrec, row, bad_data_dict
            )
            newrec, bad_data_dict = add_rights_info(newrec, row, bad_data_dict)

            # Info for chapters and articles
            newrec, bad_data_dict = add_chapter_label(
                newrec, row, bad_data_dict
            )
            newrec, bad_data_dict = add_book_authors(
                newrec, row, bad_data_dict
            )
            newrec, bad_data_dict = add_volume_info(newrec, row, bad_data_dict)
            newrec, bad_data_dict = add_publication_details(
                newrec, row, bad_data_dict
            )
            newrec, bad_data_dict = add_book_journal_title(
                newrec, row, bad_data_dict
            )
            newrec, bad_data_dict = add_pages(newrec, row, bad_data_dict)
            newrec, bad_data_dict = add_journal_info(
                newrec, row, bad_data_dict
            )

            # Info for dissertations and reports
            newrec, bad_data_dict = add_institution(newrec, row, bad_data_dict)

            # conference/meeting info
            newrec, bad_data_dict = add_meeting_info(
                newrec, row, bad_data_dict
            )

            # Uploaded file details
            newrec, bad_data_dict = add_file_info(newrec, row, bad_data_dict)

            newrec_list.append(newrec)
            line_count += 1

        # pprint([r for r in newrec_list if r['metadata']['resource_type']
        # ['id'] == 'publication:journalArticle'])

        # pprint([r for r in newrec_list if r['metadata']['identifiers'][0]
        # ['identifier'] == 'hc:45177'])
        # pprint([r for r in top_object if r['id'] == 'hc:45177'])

        # auth_errors = {k:v for k, v in bad_data_dict.items() for i in v
        # if i[0][:8] == 'authors' and len(i) == 2}
        # pprint(auth_errors)
        if debug:
            pprint(bad_data_dict)
        # print(len(auth_errors))
    print(f"Processed {line_count} lines.")
    print(f"Found {len(bad_data_dict)} records with bad data.")
    # FIXME: make issn field multiple?

    with jsonlines.open(
        Path(__file__).parent / "data" / "serialized_core_data.jsonl", mode="w"
    ) as output_file:
        for rec in newrec_list:
            output_file.write(rec)

    return newrec_list, bad_data_dict
