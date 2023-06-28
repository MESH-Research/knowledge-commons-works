#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 MESH Research
#
# core-migrate is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""
Functions to re-serialize legacy CORE deposits exported as json files to a json schema consumable by InvenioRDM.

The main function `serialize_json` writes the output to a jsonl file, with
one json object per line, separated by newlines.
"""

from copy import deepcopy
from datetime import datetime
from timefhuman import timefhuman
from isbnlib import get_isbnlike
import iso639
import json
import jsonlines
from langdetect import detect_langs
from pathlib import Path
from stdnum import issn
from titlecase import titlecase
from pprint import pprint
import re
import validators

from core_migrate.config import (
    DATA_DIR,
    GLOBAL_DEBUG,
)
from core_migrate.utils import valid_date, valid_isbn, generate_random_string

book_types = [
    'textDocument-bookChapter',
    'textDocument-bookSection',
    'textDocument-book',
    'textDocument-monograph',
    'textDocument-dissertation',
    'textDocument-report',
    'textDocument-whitePaper',
    'other-bibliography',
    'presentation-conferencePaper',
    'textDocument-conferenceProceeding',
    'presentation-conferencePaper',
    'other-essay'
]

article_types = ['textDocument-journalArticle',
                    'textDocument-abstract',
                    'textDocument-review',
                    'textDocument-newspaperArticle',
                    'textDocument-editorial',
                    'textDocument-magazineArticle',
                    'textDocument-onlinetextDocument'
                    ]

ambiguous_types = [
    'textDocument-fictionalWork',
    'other-other',
    'textDocument-interviewTranscript',
    'textDocument-legalComment',
    'textDocument-legalResponse',
    'textDocument-poeticWork',
    'textDocument-translation'
    ]

licenses = {'All Rights Reserved': (
                'arr',
                'Proprietary. All rights reserved.',
                'https://en.wikipedia.org/wiki/All_rights_reserved'
            ),
            'Attribution-NonCommercial-NoDerivatives': (
                'cc-by-nc-nd-4.0',
                'Creative Commons Attribution Non Commercial No Derivatives '
                '4.0 International',
                'https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode'
            ),
            'Attribution-NonCommercial-ShareAlike': (
                'cc-by-nc-sa-4.0',
                'Creative Commons Attribution Non Commercial Share '
                'Alike 4.0 International',
                'https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode'
            ),
            'Attribution': (
                'cc-by-4.0',
                'Creative Commons Attribution 4.0 International',
                'https://creativecommons.org/licenses/by/4.0/legalcode'
            ),
            'Attribution-NonCommercial': (
                'cc-by-nc-4.0',
                'Creative Commons Attribution Non Commercial '
                '4.0 International',
                'https://creativecommons.org/licenses/by-nc/4.0/legalcode'
            ),
            'Attribution-NoDerivatives': (
                'cc-by-nd-4.0',
                'Creative Commons Attribution No Derivatives 4.0 International',
                'https://creativecommons.org/licenses/by-nd/4.0/legalcode'
                ),
            'Attribution-ShareAlike': (
                'cc-by-sa-4.0',
                'Creative Commons Attribution Share Alike 4.0 International',
                'https://creativecommons.org/licenses/by-sa/4.0/legalcode'
            ),
            'All-Rights-Granted': (
                '0bsd',
                'BSD Zero Clause License',
                'https://spdx.org/licenses/0BSD.html'
            ),
            'All Rights Granted': (
                '0bsd',
                'BSD Zero Clause License',
                'https://spdx.org/licenses/0BSD.html'
            )
            }


def _normalize_string(mystring:str) -> str:
    mystring = mystring.casefold()
    mystring = _clean_string(mystring)
    mystring = mystring.replace('’', "'")
    mystring = mystring.replace('“', "'")
    try:
        if mystring[0] in ['"', "'"]:
            mystring = mystring[1:]
        if mystring[-1] in ['"', "'"]:
            mystring = mystring[:-1]
    except IndexError:
        pass
    return mystring


def _clean_string(mystring:str) -> str:
    """
    Remove unwanted characters from a string and return it.
    """
    if re.search(r"[\'\"]", mystring):
        mystring = re.sub(r"\\+'", r"'", mystring)
        mystring = re.sub(r'\\+"', r'"', mystring)
    else:
        mystring = re.sub(r'\\+', r'\\', mystring)
    mystring = mystring.replace('  ', ' ')
    return mystring


def _append_bad_data(rowid:str, content:tuple, bad_data_dict:dict):
    """
    Add info on bad data to dictionary of bad data
    """
    bad_data_dict.setdefault(rowid, []).append(content)
    return bad_data_dict


def _add_resource_type(rec, pubtype, genre, filetype):
    """
    """
    bad_data = []
    kcr_resource_types = {"audiovisual": ["documentary", "interviewRecording",
                                "videoRecording", "audioRecording", "musicalRecording", "other", "performance", "podcastEpisode"
                           ],
                           "dataset": ["other"],
                           "image": ["chart", "diagram", "figure", "map",
                                     "visualArt", "photograph", "other"
                            ],
                            "instructionalResource": ["curriculum",
                                                      "lessonPlan", "syllabus",
                                                       "other"
                            ],
                            "presentation": ["slides",
                                             "conferencePaper", "conferencePoster", "presentationText", "other"],
                            "software": [
                                "3DModel", "computationalModel", "computationalNotebook", "service", "application"
                            ],
                            "textDocument": [
                                "abstract", "bibliography", "blogPost", "book", "bookSection", "conferenceProceeding", "dataManagementPlan",
                                "documentation", "editorial", "essay", "interviewTranscript", "journalArticle", "legalResponse", "legalComment", "magazineArticle", "monograph", "newspaperArticle", "onlinePublication",
                                "other", "poeticWork", "preprint", "report", "workingPaper", "review",
                                "technicalStandard", "thesis", "whitePaper"
                            ],
                            "other": [
                                "catalog", "collection", "event", "interactiveResource", "notes", "peerReview", "physicalObject", "workflow", "text"
                            ]
                            }
    types_of_resource = {"Audio": "audiovisual-audioRecording",
                         "Image": "image-other",
                         "Mixed material": "other-other",
                         "Software": "software-application",
                         "Text": "textDocument-other",
                         "Video": "audiovisual-videoRecording"}

    genres = {"Abstract": "textDocument-abstract",
              "Article": "textDocument-journalArticle",
              "Bibliography": "other-bibliography",
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
              "Data set": "dataset-other",
              "Dissertation": "textDocument-thesis",
              "Documentary": "audiovisual-documentary",
              "Editorial": "textDocument-editorial",
              "Essay": "other-essay",
              "Fictional work": "textDocument-bookSection",  # FIXME: indicate ficiontal???
              "Finding aid": "other-other",
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
              "Other": "other-other",
              "Performance": "audiovisual-performance",
              "Photograph": "image-other",
              "Podcast": "audiovisual-podcastEpisode",
              "Poetry": "textDocument-poeticWork",
              "Presentation": "presentation-other",
              "Report": "textDocument-report",
              "Review": "textDocument-review",
              "Sound recording-musical": "audiovisual-musicalRecording",
              "Sound recording-non musical": "audiovisual-audioRecording", "Syllabus": "instructionalResource-syllabus",
              "Technical report": "textDocument-report",
              "Thesis": "textDocument-thesis",
              "Translation": "textDocument-other",
              "Video": "audiovisual-videoRecording",
              "Video essay": "audiovisual-videoRecording",
              "Visual art": "image-visualArt",
              "White paper": "textDocument-whitePaper"}

    publication_types = {"book-chapter": "textDocument-bookSection",
                            "book-review": "textDocument-review",
                            "book-section": "textDocument-bookSection",
                            "journal-article": "textDocument-journalArticle",
                            "magazine-section": "textDocument-magazineArticle",
                            "monograph": "textDocument-monograph",
                            "newspaper-article": "textDocument-newspaperArticle",
                            "online-publication": "textDocument-onlinePublication",
                            "podcast": "audiovisual-podcastEpisode",
                            "proceedings-article": "textDocument-conferenceProceeding"}
    if genre in genres.keys():
        rec['metadata']['resource_type'] = {'id': genres[genre]}
        if (pubtype == "Interview") and (filetype in ['audio/mpeg', 'audio/ogg', 'audio/wav', 'video/mp4', 'video/quicktime']):
            rec['metadata']['resource_type'
                            ] = {"id": "audiovisual-interviewRecording"}
        if (pubtype in publication_types.keys() and
                genres[genre] != publication_types[pubtype]):
            rec['custom_fields']['hclegacy:publication_type'] = pubtype
    else:
        rec['metadata']['resource_type'] = {"id": ''}
        bad_data.append(('genre', genre))
        rec['custom_fields']['hclegacy:publication_type'] = pubtype
        if pubtype in publication_types.keys():
            rec['metadata']['resource_type'
                            ] = {"id": publication_types[pubtype]}
        else:
            bad_data.append(('publication-type', pubtype))

    return rec, bad_data


def _add_book_authors(author_string:str, bad_data_dict:dict,
                     row_id) -> tuple[list[dict], dict]:
    """
    Convert the "book_author" string to JSON objects for Invenio
    """
    author_list = []

    def invert_flipped_name(terms):
        return [terms[1], terms[0]]

    def find_comma_delineated_names(focus):
        # print('focus', focus)
        if focus[-1] == ',':
            focus = focus[:-1]
        focus = focus.strip()
        if ', ' in focus:
            level1parts = focus.split(', ')
            # print('level1parts', level1parts)
            first = level1parts[0]
            # print('first', first)
            if len(first.split(' ')) > 1:
                focus = [f.strip().split(' ') for f in level1parts]
                # print('a focus', focus)
            elif len(first.split(' ')) == 1:
                focus = invert_flipped_name(level1parts)
                # print('b focus', focus)
            if len(level1parts) > 2:
                focus = focus + find_comma_delineated_names(', '.join(level1parts[2:]))
        else:
            focus = focus.strip().split(' ')
            # print('space split', focus)
            if len(focus) > 2:
                focus = [' '.join(focus[:-1]), focus[-1]]
        if isinstance(focus[0], str):
            focus = [focus]
        for i, f in enumerate(focus):
            if len(f) > 2:
                focus[i] = [' '.join(f[:-1]), f[-1]]
        return focus

    is_editor = False
    if re.search(r'.*\(?([Hh]e?r(au)?sg(egeben)?|[Ee]d(it(or|ed( by)?)?)?s?)\.?.*', author_string):
        # print(row['book_author'])
        author_string = re.sub(
            r'(,? )?\(?([Hh]e?r(au)?sg(egeben)?|[Ee]d(itor)?s?\.?)\)?',
            '', author_string)
        author_string = re.sub(
            r'^([Hh]e?r(au)?sg(egeben|eber(in)?)?|[Ee]d(it)?(ed|or)?s?( [Bb]y)?)[\.,]? ',
            '', author_string)
        is_editor = True
    try:
        bas = author_string
        # print('***********', bas)
        if bas[-1] in ['.', ';']:
            bas = bas[:-1]
        if re.search(r'( and| y| &|;| \/) ', author_string):
            bas = re.split(r' and | y | & | \/ |;', bas)
            new_bas = []
            for focus in bas:
                new_bas = new_bas + find_comma_delineated_names(focus)
            bas = new_bas
        elif ', ' in author_string:
            bas = find_comma_delineated_names(bas)
        elif len(bas.split(' ')) < 4:
            bas = find_comma_delineated_names(bas)
        if isinstance(bas, str):
            bas = [bas]
        for b in bas:
            # print(b, type(b))
            if isinstance(b, str):
                fullname = b
                given, family = '', ''
            else:
                fullname = f'{b[1]}, {b[0]}' if len(b) > 1 else b[0]
                given = b[0] if len(b) > 1 else ''
                family = b[1] if len(b) > 1 else ''
            author_list.append(
                {
                    'person_or_org': {
                        'name': _clean_string(fullname),
                        "type": "personal",
                        "given_name": _clean_string(given),
                        "family_name": _clean_string(family)
                    },
                    'role': {
                        'id': ('editor' if is_editor else 'author')
                    }
                }
            )
    except TypeError as e:
        _append_bad_data(row_id,
                        ('book_author', author_string), bad_data_dict)
    # FIXME: handle simple spaced names with no delimiters
    # FIXME: last name repeated like "Kate Holland"?
    # FIXME: "Coarelli, F. Patterson, H."
    # FIXME: "Hamilton, Portnoy, Wacks"
    # FIXME: ['M. Antoni J. Üçerler', 'SJ']
    # FIXME: Edited by Koenraad Verboven, Ghent University and Christian Laes, University of Antwerp, University of Tampere
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

def _add_author_data(newrec:dict, row:dict, bad_data_dict:dict
                    ) -> tuple[dict, dict]:
    """
    Add information about authors to the supplied record from supplied row.

    Processes data from the 'authors' and 'author_info' csv export fields.
    """

    creators = []
    contributors_misplaced = []
    creators_misplaced = []
    # FIXME: "HC Admin" showing up with "submitter" role?
    allowed_roles = ['author', 'editor', 'contributor',
                     'translator', 'creator', 'other', 'project director']
    if row['authors']:
        # print(row['pid'])
        try:
            # row['authors'] = row['authors'].replace('\\', '&quot;')
            for a in row['authors']:
                # Some records have "hcadmin" in role of "submitter"
                if a['uni'] == "hcadmin":
                    continue
                a['family']= _clean_string(a['family'])
                a['given'] = _clean_string(a['given'])
                new_person = {}

                new_person['person_or_org'] = {
                    'type': "personal",  # FIXME: can't hard code
                    # 'name': a['fullname'],
                    'name': f'{a["family"]}, {a["given"]}',
                    'given_name': a['given'],
                    'family_name': a['family']
                }
                if a['role'] and a['role'] in allowed_roles or not a['role']:
                    # TODO: are null roles a problem?
                    if a['role'] == 'project director':
                        new_person['role'] = {'id': "projectLeader"}
                    else:
                        new_person['role'] = {'id': a['role']}
                else:
                    _append_bad_data(row['id'],
                                    (f'authors:{a["fullname"]}:role', a['role']),
                                    bad_data_dict)
                if a['affiliation']:
                    new_person['affiliations'] = [{'name': f} for f in a['affiliation'].split('|')]
                if a['uni']:  # uni is the hc username
                    new_person['person_or_org']['identifiers'] = [
                        {'identifier': a['uni'], 'scheme': 'hc_username'}]
                if a['role'] in allowed_roles:
                    if a['role'] == 'contributor':
                        new_person['role'] = {'id': 'other'}
                        contributors_misplaced.append(new_person)
                    else:
                        creators.append(new_person)
            if len(creators) > 0:
                newrec['metadata'].setdefault('creators', []).extend(
                    creators
                )
                if contributors_misplaced:
                    newrec['metadata'].setdefault('contributors', []).extend(
                        contributors_misplaced
                    )
                    # append_bad_data(row['id'], ('authors', row['authors'],
                    #                             'contributor moved from Authors'),
                    #                 bad_data_dict)
            elif len(contributors_misplaced) > 0:
                newrec['metadata'].setdefault('creators', []).extend(
                    contributors_misplaced
                )
                # append_bad_data(row['id'], ('authors', row['authors'],
                #                             'contributor as only author'),
                #                 bad_data_dict)
        except (SyntaxError, ValueError) as e:
            print(row['authors'])
            _append_bad_data(row['id'], ('authors:Syntax or ValueError',
                                        row['authors']), bad_data_dict)
    else:
        _append_bad_data(row['id'], ('authors:no value', row['authors']),
                        bad_data_dict)

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


def _get_subject_from_jsonl(subject:str) -> str:
    """
    Retrieve the full subject string corresponding to the subject label provided
    """
    # FIXME: Finish finding id numbers
    existing_subjects = {
        'Linguistics': '999202',
        'Digital humanities': "963599",
        'Arabic language': '812287',
        'Spanish language': '1128292',
        'American literature': '807113',
        'English literature': '911989',
        'Poetics': '1067682',
        'Comparative literature': '1734553',
        'Literature and science': '1000093',
        'German language': '941408',
        'Philosophy': '1060777',
        'Ethics': '915833',
        'Religion': '1093763',
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
        return f'{existing_subjects[subject]}:{subject}:topical'
    else:
        return ''


def serialize_json() -> tuple[list[dict], dict]:
    """
    Parse and serialize csv data into Invenio JSON format.
    """
    debug = GLOBAL_DEBUG or True
    multiple_issn_list = []

    baserec:dict = {'parent': {
                        'access': {
                            'owned_by': []
                        }
                    },
                    'custom_fields': {
                    },
                    'metadata': {
                        'resource_type': {},
                        'title': "",
                        'additional_titles': [],
                        'additional_descriptions': [],
                        'creators': [],
                        'publication_date': [],
                        'identifiers': [],
                        'languages': [],
                        'rights': [],
                    },
                    'files': {'entries': []},
    }

    newrec_list:list[dict] = []
    bad_data_dict:dict[str, list] = {}
    line_count:int = 0

    with open(Path(DATA_DIR, 'core-export-may-15-23.json')) as json_file:
        # top_object = json.loads('{"data": ' + json_file.read() + '}')
        top_object = json.loads(json_file.read())
        pprint([t for t in top_object if t['id'] == 'mla:583'][0])
        for row in top_object:
            newrec = deepcopy(baserec)

            if row['chapter']:
                mychap = _normalize_string(row['chapter'])
                mytitle = _normalize_string(row['title'])
                mybooktitle = _normalize_string(row['book_journal_title'])
                if mychap == mytitle:
                    pass
                # FIXME: This needs work
                elif mychap in mytitle and len(mychap) > 18:
                    _append_bad_data(row['id'],
                                    ('chapter in title', row['chapter'],
                                     row['title']), bad_data_dict)
                    # print('~~~~', row['chapter'])
                    # print('~~~~', row['title'])
                else:
                    rn = r'^M{0,3}(CM|CD|D?C{0,3})?(XC|XL|L?X{0,3})?(IX|IV|V?I{0,3})?$'
                    if re.search(r'^([Cc]hapter )?\d+[\.,;]?\d*$',
                                 row['chapter']) or \
                            re.search(rn, row['chapter']):
                        newrec['custom_fields'][
                            'kcr:chapter_label'] = _clean_string(row['chapter'])
                        # print('&&&&&', row['chapter'], row['title'])
                        # print('&&&&&', newrec['custom_fields']['kcr:chapter_label'])
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
                    #FIXME: label being truncated with \\\\\\\\\ in hc:27769
                    elif re.search(r'^[Cc]hapter', row['chapter']):
                        shortchap = re.sub(r'^[Cc]hapter\s*', '',
                                           row['chapter'])
                        newrec['custom_fields']['kcr:chapter_label'
                                                ] = _clean_string(shortchap)
                        # print('&&&&&', row['chapter'], row['title'])
                        # print('&&&&&', newrec['custom_fields']['kcr:chapter_label'])
                    # elif mytitle == mybooktitle:
                    #     print('----', row['chapter'])
                    #     row['title'] = row['chapter']
                    #     newrec['metadata']['title'] = row['chapter']
                    #     print('-------', newrec['metadata']['title'])
                    elif row['chapter'] == 'N/A':
                        pass
                    else:
                        # print(row['chapter'])
                        # print('**', row['title'])
                        # print('**', row['title_unchanged'])
                        newrec['custom_fields']['kcr:chapter_label'
                            ] = _clean_string(row['chapter'])

            # HC legacy admin information
            newrec['metadata']['identifiers'].append(
                {'identifier': row['id'], 'scheme': 'hclegacy-pid'}
            )
            assert row['id'] == row['pid']
            newrec['metadata']['identifiers'].append(
                {'identifier': row['record_identifier'], 'scheme': 'hclegacy-record-id'}
            )
            newrec['custom_fields']['kcr:commons_domain'] = row['domain']

            # HC submitter info
            newrec['custom_fields']['kcr:submitter_email'
                                    ] = row['submitter_email']
            newrec['custom_fields']['kcr:submitter_username'
                                    ] = row['submitter_login']

            # Access information
            if row['embargoed'] == 'yes' and row['embargo_end_date']:
                end_date_dt = datetime.strptime(row['embargo_end_date'].strip(),
                                                '%m/%d/%Y').date()
                end_date_iso = end_date_dt.isoformat()
                newrec.setdefault('access', {})['embargo'] = {
                    "active": True,
                    "until": end_date_iso,
                    "reason": None
                },

            # Titles
            # FIXME: Filter out titles with punctuation from full biblio ref in #   field?
            # FIXME: Remove things like surrounding quotation marks
            mytitle = row['title_unchanged']
            newrec['metadata']['title'] = _clean_string(mytitle)
            # FIXME: types here are CV, need to expand to accommodate stripped desc
            newrec['metadata']['additional_titles'].append(
                {"title": _clean_string(row['title']),
                    "type": {
                        "id": "other",
                        "title": {"en": "Primary title with HTML stripped"}
                    },
                }
            )
            # Descriptions/Abstracts
            # FIXME: handle double-escaped slashes?
            # FIXME: handle windows newlines?
            newrec['metadata']['description'] = row['abstract_unchanged'].replace('\r\n', '\n')
            # FIXME: types here are CV, need to expand to accommodate stripped desc
            newrec['metadata']['additional_descriptions'].append(
                {"description": row['abstract'].replace('\r\n', '\n'),
                 "type": {
                     "id": "other",
                     "title": {"en": "Primary description with HTML stripped"}
                 }
                }
            )

            # Notes
            if row['notes']:
                newrec['custom_fields'].setdefault('kcr:notes', []).append(
                    {'note_text': row['notes_unchanged'],
                     'note_text_sanitized': row['notes'],
                     'note_description': 'general'
                     }
                )

            # Resource type
            newrec, bad_data = _add_resource_type(newrec,
                                                 row['publication-type'],
                                                 row['genre'], row['filetype'])
            if bad_data:
                for i in bad_data:
                    _append_bad_data(row['id'], i, bad_data_dict)

            # Identifiers
            # FIXME: Is it right that these are all datacite dois?
            if row['deposit_doi']:
                newrec.setdefault('pids', {})[
                    'doi'] = {"identifier": row['deposit_doi'].replace('doi:', ''),
                              "provider": "datacite",
                              "client": "datacite"}
                newrec['metadata'].setdefault('identifiers', []).append(
                    {"identifier": row["deposit_doi"].replace('doi:', ''),
                     "scheme": "datacite-doi"}
                )
            if row['doi']:
                # FIXME: hc:24459 is getting description as doi value
                if len(row['doi']) < 40:
                    newrec['metadata'].setdefault('identifiers', []).append(
                        {"identifier": row['doi'],
                        "scheme": "doi"}
                    )
                else:
                    _append_bad_data(row['id'], ('doi too long', row['doi']), bad_data_dict)
            if row['handle']:
                newrec['metadata'].setdefault('identifiers', []).append(
                    {"identifier": row['handle'].replace('http://dx.', 'https://'),
                     "scheme": "url"}
                )
            if row['url']:
                my_urls = re.split(r' and |;', row['url'])
                for url in my_urls:
                    url = row['url'].replace(' ', '')
                    if validators.url(url) or validators.url(f'https://{url}'):
                        newrec['metadata'].setdefault('identifiers', []).append(
                            {"identifier": row['url'].replace('http://dx.', 'https://'),
                            "scheme": "url"}
                        )
                    else:
                        # print(row['id'], url)
                        pass

            # Language info
            # FIXME: Deal with all of these exceptions and the 'else' condition
            if row['language']:
                if row['language'] == 'Greek':
                    row['language'] = 'Greek, Modern (1453-)'
                mylang = iso639.Language.from_name(row['language']).part3
                newrec['metadata']['languages'] = [{"id": mylang}]
            else:
                exceptions = [
                    'hc:11565', 'hc:48435', 'hc:48455', 'hc:11007', 'hc:11263', 'hc:11481', 'hc:12907', 'hc:13285', 'hc:13321', 'hc:13347', 'hc:13351', 'hc:13353', 'hc:13377', 'hc:13381', 'hc:13461', 'hc:13469', 'hc:13477', 'hc:13479', 'hc:13503', 'hc:13505', 'hc:13507', 'hc:13539', 'hc:13569', 'hc:13571', 'hc:13577', 'hc:13601', 'hc:13643', 'hc:13651', 'hc:13673', 'hc:13715', 'hc:13785', 'hc:13823', 'hc:13841', 'hc:13847', 'hc:13939', 'hc:13995', 'hc:13997', 'hc:14007', 'hc:14065', 'hc:14089', 'hc:14093', 'hc:14167', 'hc:14169', 'hc:14171', 'hc:14173', 'hc:14175', 'hc:14179', 'hc:14183', 'hc:14187', 'hc:14189', 'hc:14193', 'hc:14195', 'hc:14207', 'hc:14269', 'hc:14271', 'hc:14285', 'hc:14331', 'hc:14333', 'hc:14343', 'hc:14345', 'hc:14393', 'hc:14405', 'hc:14407', 'hc:14421', 'hc:14425', 'hc:14427', 'hc:14433', 'hc:14435', 'hc:14437', 'hc:14439', 'hc:14461', 'hc:14463', 'hc:14465', 'hc:14467', 'hc:14469',
                    'hc:14473', 'hc:14477', 'hc:14479', 'hc:14481', 'hc:14485',
                    'hc:14517', 'hc:14519', 'hc:14523', 'hc:14535', 'hc:14537',
                    'hc:14539', 'hc:14615', 'hc:14691', 'hc:14695', 'hc:14975',
                    'hc:15237', 'hc:15387', 'hc:16197', 'hc:16353', 'hc:16473',
                    'hc:16493', 'hc:21289', 'hc:29719', 'hc:38161', 'hc:40031',
                    'hc:40185', 'hc:41065', 'hc:41659', ''
                ]
                lang1, lang2 = [], []
                if row['title']:
                    t = titlecase(row['title'])
                    lang1 = [{'code': lang.lang, 'prob': lang.prob}
                              for lang in detect_langs(t)]
                if row['abstract']:
                    try:
                        lang2 = [{'code': lang.lang, 'prob': lang.prob}
                                for lang in detect_langs(row['abstract'])]
                    except Exception:
                        pass
                        # print('language exception with abstract!!!!')
                        # print(row['abstract'])

                if (lang1[0]['code'] == 'en' and lang2 and
                        lang2[0]['code'] == 'en'):
                    newrec['metadata']['languages'] = [{"id": 'eng'}]
                elif lang1[0]['prob'] > 0.99 and row['id'] not in exceptions:
                    newrec['metadata']['languages'] = [{"id": lang1[0]['code']}]
                elif (lang1[0]['prob'] < 0.9 and lang2 and
                        lang2[0]['prob'] >= 0.9 and
                        row['id'] not in exceptions):
                    newrec['metadata']['languages'] = [{"id": lang2[0]['code']}]
                elif row['id'] in exceptions:
                    pass
                else:
                    # print(titlecase(row['title']))
                    # print(row['id'], 'detected', lang1, lang2)
                    pass

            # Edition
            # FIXME: There's some bad data here, like ISSNs
            if row['edition']:
                newrec['custom_fields']['kcr:edition'] = _clean_string(row['edition'])

            # Committee deposit
            if row['committee_deposit'] == "yes":
                try:
                    cid = int(row['committee_id'])
                    newrec['custom_fields'][
                           'hclegacy:committee_deposit'] = cid
                except ValueError:
                    _append_bad_data(row['id'],
                                    ('committee_id', row['committee_id']),
                                    bad_data_dict)

            # HC legacy collection
            if row['member_of']:
                newrec['custom_fields']['hclegacy:collection'
                                        ] = row['member_of']

            # Original submitter's HC society memberships
            if row['society_id']:
                row['society_id'] = row['society_id'] \
                    if type(row['society_id']) == list else [row['society_id']]
                newrec['custom_fields'][
                    'hclegacy:submitter_org_memberships'] = row['society_id']

            # Was CORE deposit previously published?
            if row['published']:
                newrec['custom_fields']['hclegacy:previously_published'
                                        ] = row['published']

            # ORiginal submitter
            if row['submitter']:
                try:
                    row['submitter'] = int(row['submitter'])
                    # Doesn't work because not Invenio user id
                    newrec['parent']['access']['owned_by'].append(
                        {'user': row['submitter']}
                    )
                    newrec['custom_fields'
                           ]['hclegacy:submitter_id'] = row['submitter']
                except ValueError:
                    row['submitter'] = None
                    _append_bad_data(row['id'],
                                    ('submitter', row['submitter']),
                                    bad_data_dict)

            # Author info
            newrec, bad_data_dict = _add_author_data(newrec, row, bad_data_dict)

            if row['organization']:
                newrec['custom_fields'
                       ]['hclegacy:submitter_affiliation'] = row['organization']

            newrec_list.append(newrec)
            line_count += 1

            # Date info
            # FIXME: does "issued" work here?
            newrec['metadata']['publication_date'] = row['date_issued'].split('T')[0]
            if row['date_issued'] != row['date'] and row['date'] != '':
                row['date'] = row['date'].split('T')[0]
                if valid_date(row['date']):
                    newrec['metadata'].setdefault('dates', []).append(
                        { "date": row['date'],
                            "type": { "id": "issued", "title": { "en": "Issued" } },
                            "description": "Human readable publication date" }
                    )
                else:
                    # FIXME: Handle these random dates better
                    mydate = row['date_issued'].split('T')[0]
                    try:
                        mydate = timefhuman(row['date']).isoformat().split('T')[0]
                    except (ValueError, TypeError, IndexError):
                        _append_bad_data(row['id'],
                                ('bad date', row['date']),
                                bad_data_dict)
                    newrec['metadata'].setdefault('dates', []).append(
                        { "date": mydate,
                            "type": { "id": "issued", "title": { "en": "Issued" } },
                            "description": "Human readable publication date" }
                    )

            if row['record_change_date']:
                assert valid_date(row['record_change_date'])
                # except AssertionError:
                #     print(row['id'])
                #     print(row['record_change_date'])
                #     print(valid_date(row['record_change_date']))
                newrec['updated'] = row['record_change_date']
                newrec['custom_fields']['hclegacy:record_change_date'] = row['record_change_date']
            if row['record_creation_date']:
                assert valid_date(row['record_creation_date'])
                newrec['created'] = row['record_creation_date']
                newrec['custom_fields']['hclegacy:record_creation_date'] = row['record_creation_date']

            # Group info for deposit
            try:
                # print(row['group'])
                # print(row['group_ids'])A. Pifferetti, A. & I. Dosztal (comps.i
                if row['group'] not in [None, [], ""]:
                    row['group'] = row['group']
                if row['group_ids'] not in [None, [], ""]:
                    row['group_ids'] = row['group_ids']
                assert len(row['group']) == len(row['group_ids'])
                group_list = []
                if len(row['group']) > 0:
                    for i, n in enumerate(row['group_ids']):
                        group_list.append({"group_identifier": n,
                                           "group_name": row['group'][i]})
                    newrec['custom_fields']['hclegacy:groups_for_deposit'
                                            ] = group_list
            except AssertionError:
                row['hclegacy:groups_for_deposit'] = None
                _append_bad_data(row['id'],
                                ('group or group_ids', row['group'], row['group_ids']),
                                bad_data_dict)
            except json.decoder.JSONDecodeError as e:
                # print(e)
                # print(row['group'], row['group_ids'])
                row['hclegacy:groups_for_deposit'] = None
                _append_bad_data(row['id'],
                                ('group or group_ids', row['group'], row['group_ids']),
                                bad_data_dict)

            # book info
            # FIXME: Need to augment out-of-the-box imprint custom fields
            if row['book_author']:
                newrec['custom_fields']['imprint:imprint'] = {}
                # print(row['book_author'])
                book_names, bad_data_dict = _add_book_authors(
                    row['book_author'], bad_data_dict, row['id'])
                newrec['custom_fields']['imprint:imprint'][
                    'creators'] = book_names

            # volume info
            # FIXME: distinguish volume meaning for ambiguous resource types
            if row['volume']:
                if newrec['metadata']['resource_type']['id'] in article_types:
                    newrec['custom_fields'].setdefault('journal:journal', {}
                        )['volume'] = row['volume']
                elif newrec['metadata']['resource_type']['id'] in book_types:
                    newrec['custom_fields'].setdefault('kcr:volumes', {}
                        )['volume'] = row['volume']
                else:
                    # print(row['id'], newrec['metadata']['resource_type']['id'], row['volume'])
                    newrec['custom_fields'].setdefault('kcr:volumes', {}
                        )['volume'] = row['volume']

            if row['isbn']:
                row['isbn'] = row['isbn'].replace(r'\\0', '')
                isbn = get_isbnlike(row['isbn'])

                # FIXME: make isbn a list
                # FIXME: still record invalid isbns?
                newrec['custom_fields'].setdefault('imprint:imprint', {}
                                                   )['isbn'] = []
                for i in isbn:
                    checked_i = valid_isbn(i)
                    if not checked_i:
                        # print(isbn)
                        # print('invalid isbn', ':', checked_i, ':', clean(i), ':', row['isbn'])
                        _append_bad_data(row['id'],
                                        ('invalid isbn', row['isbn']),
                                        bad_data_dict)
                    else:
                        newrec['custom_fields'][
                            'imprint:imprint']['isbn'].append(checked_i)

            # Handle missing publishers?
            if row['publisher']:
                newrec['metadata']['publisher'] = _clean_string(
                    row['publisher'])
            else:
                newrec['metadata']['publisher'] = "unknown"

            if row['book_journal_title']:
                myfield = 'imprint:imprint'
                if newrec['metadata']['resource_type'][
                        'id'] in article_types:
                    myfield = 'journal:journal'
                if newrec['metadata']['resource_type']['id'] not in [
                    *book_types, *article_types]:
                    # print('****', newrec['metadata']['resource_type']['id'])
                    _append_bad_data(row['id'],
                                    ('resource_type for book_journal_title',
                                     newrec['metadata']['resource_type']['id']),
                                     bad_data_dict)
                # FIXME: check right field for legalComment, bibliography, lecture, conferencePaper, legalResponse, other:other, other:essay, translation, videoRecording, blogPost, interviewTranscript, poeticWork, fictionalWork, image:visualArt, image:map, instructionalResource:syllabus, onlinePublication, presentation:other, instructionalResource:other, musicalRecording, catalog, dataset:other, audiovisual:documentary, lecture
                if myfield not in newrec['custom_fields'].keys():
                    newrec['custom_fields'][myfield] = {}
                # FIXME: in hc:24459 title replaced by just \\\\
                # FIXME: in hc:52887, hc:27377 title truncated with \\\\
                newrec['custom_fields'][myfield][
                    'title'] = _clean_string(row['book_journal_title'])

            # article/chapter info

            if row['id'] == 'hc:33383':
                print('pagess...')
                print(row['start_page'], row['end_page'])
                print(newrec['metadata']['resource_type']['id'])
            if row['start_page']:
                pages = row['start_page']
                if row['end_page']:
                    pages = f'{pages}-{row["end_page"]}'
                if newrec['metadata']['resource_type']['id'
                        ] in article_types:
                    newrec['custom_fields'].setdefault(
                        'journal:journal', {})['pages'] = pages
                else:
                    newrec['custom_fields'].setdefault(
                        'imprint:imprint', {})['pages'] = pages
                if newrec['metadata']['resource_type']['id'
                        ] not in [*book_types, *article_types,
                                    *ambiguous_types]:
                    _append_bad_data(row['id'],
                        ('resource_type for start_page/end_page',
                            newrec['metadata']['resource_type']['id']),
                        bad_data_dict)

            if row['issue']:
                issue = re.sub(r'([Ii]ssue|[nN][Oo]?\.?)\s?', '', row['issue'])
                issue = re.sub(r'\((.*)\)', r'\1', issue)
                issue = re.sub(r'[\.,]$', '', issue)
                newrec['custom_fields'].setdefault('journal:journal', {}
                                                    )['issue'] = issue

            # FIXME: make issn a list
            if row['issn']:
                myissn = row['issn']
                if isinstance(row['issn'], list):
                    multiple_issn_list.append((row['id'], row['issn']))
                    myissn = row['issn'][0]

                if valid_isbn(myissn):
                    # print('isbn', row['issn'])
                    newrec['custom_fields'].setdefault(
                        'imprint:imprint', {})['isbn'] = myissn
                    _append_bad_data(row['id'],
                        ('issn', 'isbn in issn field', myissn),
                        bad_data_dict)
                else:
                    # myissn = row['issn'].replace(b'\xe2\x80\x94'.decode('utf-8'), '-')
                    # myissn = myissn.replace('\x97', '-')
                    assert type(myissn) == str
                    myissn = myissn.replace(u'\u2013', '-')
                    myissn = myissn.replace(u'\u2014', '-')
                    myissn = re.sub(r'\s?-\s?', '-', myissn)
                    myissn = myissn.replace('Х', 'X')
                    myissn = myissn.replace('.', '')
                    myissnx = re.findall(r'\d{4}[-\s\.]?\d{3}[\dxX]', myissn)
                    if isinstance(myissnx, list) and len(myissnx) >= 1:
                        if len(myissnx) > 1:
                            multiple_issn_list.append((row['id'], row['issn']))
                        myissnx = myissnx[0]
                    if len(myissnx) < 1:
                        _append_bad_data(row['id'],
                            ('issn', 'malformed', row['issn']),
                            bad_data_dict)
                    else:
                        assert type(myissn) == str
                        myissnx = re.sub(r'ISSN:? ?', '', myissnx)
                        try:
                            if issn.validate(myissnx):
                                newrec['custom_fields'].setdefault(
                                    'journal:journal', {})['issn'] = myissnx
                        except Exception:
                            # print('exception', i, row['issn'])
                            _append_bad_data(row['id'],
                                ('issn', 'invalid last digit',
                                    row['issn']),
                                bad_data_dict)

            # extra for dissertations and reports
            if row['institution']:
                # print(row['id'])
                # print(newrec['metadata']['resource_type']['id'])
                newrec['custom_fields']['kcr:sponsoring_institution'
                                        ] = _clean_string(row['institution'])
                if newrec['metadata']['resource_type']['id'] not in [
                        'publication:dissertation', 'publication:report',
                        'publication:whitePaper']:
                    _append_bad_data(row['id'],
                        ('resource_type for institution',
                            newrec['metadata']['resource_type']['id']),
                        bad_data_dict)

            # conference/meeting info
            if row['conference_date'] or row['meeting_date']:
                # if not newrec['custom_fields']['meeting:meeting']:
                #     newrec['custom_fields']['meeting:meeting'] = {}
                newrec['custom_fields'].setdefault('meeting:meeting', {})[
                    'dates'] = row['conference_date'] or row['meeting_date']
            if row['conference_location'] or row['meeting_location']:
                newrec['custom_fields'].setdefault('meeting:meeting', {})[
                    'place'] = _clean_string(row['conference_location'
                                    ] or row['meeting_location'])
            if row['conference_organization'] or row['meeting_organization']:
                newrec['custom_fields'][
                    'kcr:meeting_organization'] = _clean_string(row[
                        'conference_organization'] or row[
                            'meeting_organization'])
            # FIXME: meeting_title being truncated with \\\\ in hc:46017, hc:19211
            if row['conference_title'] or row['meeting_title']:
                newrec['custom_fields'].setdefault('meeting:meeting', {})[
                    'title'] = _clean_string(row['conference_title'] or row['meeting_title'])

            # subjects and keywords
            # FIXME: keyword ids filled in and harmonized where possible
            #   with subject headings below
            # FIXME: use named entity recognition to regularize
            #   capitalization?
            if row['keyword']:
                keywords = []
                if isinstance(row['keyword'], dict):
                    row['keyword'] = row['keyword'].values()
                    for k in row['keyword']:
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
                    keywords = row['keyword']

                if keywords:
                    newrec['custom_fields'][
                        'kcr:user_defined_tags'] = keywords

            if row['subject']:
                missing_subjects = ['Public humanities',
                                    'Scholarly communication',
                                    'European history',
                                    'African American culture',
                                    'Literature and philosophy',
                                    'Asian history',
                                    'Modern history',
                                    'Postcolonial literature',
                                    'Ancient history',
                                    'Ancient Mediterranean religions',
                                    'Early Christianity',
                                    'Religions of late Antiquity',
                                    'Literature and economics',
                                    'Contemporary art',
                                    'Translation studies',
                                    'Classical studies',
                                    'Sociology of development',
                                    'African studies',
                                    'Data sharing',
                                    'Cultural anthropology',
                                    'Criticism of the arts',
                                    'Theory of the arts',
                                    'Music criticism',
                                    'African American studies',
                                    'Ancient literature',
                                    'Biblical studies',
                                    'Hebrew bible',
                                    'Literary criticism',
                                    'Pentateuchal studies',
                                    'Medieval studies',
                                    'Urban studies',
                                    'Comparative religious ethics',
                                    'American studies',
                                    'Asian-American studies',
                                    'Film studies',
                                    '17th century',
                                    'Migration studies',
                                    'Music analysis',
                                    'Ancient Greece',
                                    'Music information retrieval',
                                    'Archival studies',
                                    'Native American literature',
                                    'Coming-of-age literature',
                                    'Poesia',
                                    'American art',
                                    'Late Antiquity',
                                    'Music composition',
                                    'Accelerationism',
                                    'Behavioral anthropology',
                                    '20th century',
                                    'Immigration history',
                                    'Bibliography',
                                    'Biography',
                                    'Education',
                                    'English',
                                    'Poetry',
                                    'Romanticism',
                                    '19th-century German literature',
                                    'Polish culture',
                                    'Polish studies'
                                    ]
                bad_subjects = {
                    'Art history': "815264:Art--History:topical",
                    'Medieval literature': "1000151:Literature, Medieval:topical",
                    'Literary theory':
                        "1353577:Literature--Theory:topical",
                    'Cultural studies': "885059:Culture:topical",
                    'Political philosophy': "1060799:Philosophy--Political aspects:topical",
                    'History of religions': "1093783:Religion--History:topical",
                    'Religious studies': "1093763:Religion:topical",
                    'Translation': "1154795:Translating and interpreting:topical",
                    'Australasian/Pacific literature': "821406:Australasian literature:topical",
                    'Comics': "1921613:Comics (Graphic works):form",
                    'Graphic novels': "1726630:Graphic novels:form",
                    'Cultural history': "885069:Culture--History:topical",
                    'Epigraphy': "973837:Inscriptions:topical",
                    'Latin American studies': "1245945:Latin America:geographic",
                    'Sociology of agriculture': "801646:Agriculture--Social aspects:topical",
                    'Ancient law': "993683:Law--Antiquities:topical",
                    'Digital communication': "893634:Digital communications:topical",
                    'Internet sociology': "1766793:Internet--Social aspects:topical",
                    'Library and information science': "997916:Library science:topical",
                    'Social anthropology': "810233:Anthropology--Social aspects:topical",
                    'History of the arts': "817758:Arts--History:topical",
                    'Music history': "1030330:Music--History:topical",
                    'Interdisciplinary studies': "976131:Interdisciplinary research:topical",
                    'Illuminated manuscripts': "967235:Illumination of books and manuscripts:topical",
                    'India': "1210276:India:geographic",
                    'Apostle Paul': "288253:St. Paul:personal",
                    'Academic librarianship': "794993:Academic librarians:topical",
                    'Sociology of aging': "800348:Aging--Social aspects:topical",
                    'Sociology of culture': "885083:Culture--Social aspects:topical",
                    'Holocaust studies': "958866:Jewish Holocaust (1939-1945):topical",
                    'Literature and psychology': "1081551:Psychology and literature:topical",
                    'Gender studies': "939598:Gender identity--Research:topical",
                    'Historical musicology': "1030896:Musicology--History:topical",
                    'Shakespeare': "314312:Shakespeare, William, 1849-1931:personal",
                    'Sociology of finance': "842573:Business enterprises--Finance--Social aspects:topical",
                    'Central Europe': "1244544:Central Europe:geographic",
                    'Contemporary history': "1865054:History of contemporary events:topical",
                    'Labor history': "989812:Labor--History:topical",
                    'Epicurus': "44478:Epicurus:personal",
                    'Stanley Cavell': "28565:Cavell, Stanley, 1926-2018:personal",
                    'Translation of poetry': "1067745:Poetry--Translating:topical",
                    'James Joyce': "370728:Joyce, James:personal",
                    'Jack Kerouac': "52352:Kerouac, Jack, 1922-1969:personal",
                    'Feminisms': "922671:Feminism:topical",
                    'Feminist art history': "922756:Feminist art criticism:topical",
                    'Gospels': "1766655:Bible stories, English--N.T. Gospels:topical",
                    'Manuscript studies': "1008230:Manuscripts:topical",
                    'Book history': "836420:Books--History:topical",
                    'Harlem Renaissance': "951467:Harlem Renaissance:topical",
                    'Music performance': "1030398:Music--Performance:topical",
                    'Latin America': "1245945:Latin America:topical",
                    'Portuguese culture': "1072404:Portuguese--Ethnic identity:topical",
                    'Venezuela': "1204166:Venezuela:geographic",
                    'Aesthetic theory': "798702:Aesthetics:topical",
                    '21st-century American literature': "807113:American literature:topical",
                    'Poetics and poetry': "1067682:Poetics:topical"
                }
                covered_subjects = []
                if isinstance(row['subject'], dict):
                    row['subject'] = row['subject'].values()
                for s in row['subject']:
                    if s in missing_subjects:
                        newrec['custom_fields'].setdefault(
                            'kcr:user_defined_tags', []).append(s)
                    else:
                        if s in bad_subjects.keys():
                            s = bad_subjects[s]
                        # normalize inconsistent facet labels
                        pieces = s.split(':')
                        if len(pieces) < 3:
                            try:
                                s = _get_subject_from_jsonl(s)
                                pieces = s.split(':')
                                assert s != ''
                            except AssertionError:
                                # print('%%%%')
                                # print('record', row['id'])
                                # print(row['subject'])
                                # print(s.split(':'))
                                newrec['custom_fields'].setdefault(
                                    'kcr:user_defined_tags', []).append(s)
                                _append_bad_data(row['id'],
                                        ('invalid subject', s),
                                        bad_data_dict)
                        id_num = pieces[0]
                        subject = ':'.join(pieces[1:-1])
                        facet_label = pieces[-1]
                        subs = {'Corporate Name': 'corporate',
                                'Topic': 'topical',
                                'Event': 'event',
                                'Form\/Genre': 'form',
                                'Geographic': 'geographic',
                                'Meeting': 'meeting',
                                'Personal Name': 'personal'}
                        if facet_label in subs.keys():
                            facet_label = subs[facet_label]
                        if s not in covered_subjects:
                            newrec['metadata'].setdefault('subjects', []).append(
                                {
                                    "id": f'http://id.worldcat.org/fast/{id_num}',
                                    "subject": subject,
                                    "scheme": f"FAST-{facet_label}"
                                }
                            )
                        covered_subjects.append(s)

            if row['file_pid'] or row['fileloc'] or row['filename']:
                newrec['custom_fields']['hclegacy:file_location'
                                        ] = row['fileloc']
                newrec['custom_fields']['hclegacy:file_pid'
                                        ] = row['file_pid']
                newrec['files'] = {
                    "enabled": True,
                    "entries": {
                        f'{row["filename"]}': {
                            "key": row["filename"],
                            "mimetype": row["filetype"],
                            "size": row['filesize'],
                        }
                    },
                    "default_preview": row['filename']
                }

            if row['type_of_license']:
                license_id, license_name, license_url = licenses[row['type_of_license']]
                newrec['metadata'].setdefault('rights', []).append(
                    {
                    "id": license_id,
                    "props": {
                        "scheme": "spdx",
                        "url": license_url
                    },
                    "title": {"en": license_name},
                    "description": {"en": ""}
                    }
                )

        # pprint([r for r in newrec_list if r['metadata']['resource_type']['id'] == 'publication:journalArticle'])

        # pprint([r for r in newrec_list if r['metadata']['identifiers'][0]['identifier'] == 'hc:45177'])
        # pprint([r for r in top_object if r['id'] == 'hc:45177'])

        # auth_errors = {k:v for k, v in bad_data_dict.items() for i in v if i[0][:8] == 'authors' and len(i) == 2}
        # pprint(auth_errors)
        # pprint(bad_data_dict)
        # print(len(auth_errors))
    print(f'Processed {line_count} lines.')
    print(f'Found {len(bad_data_dict)} records with bad data.')
    # FIXME: make issn field multiple?
    print(len(multiple_issn_list), 'records with multiple issns')

    with jsonlines.open(Path(__file__).parent / 'data' /
                        'serialized_core_data.jsonl', mode="w") as output_file:
        for rec in newrec_list:
            output_file.write(rec)

    return newrec_list, bad_data_dict
