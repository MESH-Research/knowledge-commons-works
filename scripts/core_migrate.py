#! /usr/bin/env python
from ast import literal_eval
import click
from copy import deepcopy
import csv
from datetime import datetime
from fedoraapi import FedoraApi
from isbnlib import is_isbn10, is_isbn13, get_isbnlike, clean
import iso639
import json
from langdetect import detect_langs
from stdnum import issn
import requests
# import numpy as np
from titlecase import titlecase
from typing import Optional
import os
# import pandas as pd
from pprint import pprint
import re
import validators
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape, unescape

@click.group()
def cli():
    pass

book_types = [
    'publication:bookChapter',
    'publication:bookSection',
    'publication:book',
    'publication:monograph',
    'publication:dissertation',
    'publication:report',
    'publication:whitePaper',
    'other:bibliography',
    'presentation:conferencePaper',
    'publication:conferenceProceeding',
    'presentation:conferencePaper',
    'other:essay'
]

article_types = ['publication:journalArticle',
                    'publication:abstract',
                    'publication:review',
                    'publication:newspaperArticle',
                    'publication:editorial',
                    'publication:magazineArticle',
                    'publication:onlinePublication'
                    ]

ambiguous_types = [
    'publication:fictionalWork',
    'other:other',
    'publication:interviewTranscript',
    'publication:legalComment',
    'publication:legalResponse',
    'publication:poeticWork',
    'publication:translation'
    ]


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

licenses = {'All Rights Reserved': (
                'all-rights-reserved',
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

def append_bad_data(rowid:str, content:tuple, bad_data_dict:dict):
    """
    Add info on bad data to dictionary of bad data
    """
    bad_data_dict.setdefault(rowid, []).append(content)
    return bad_data_dict


def valid_isbn(isbn:str) -> bool:
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
        try:
            # TODO: This only handles single years, year-months,
            # or year-month-days. Do we need ranges?
            dtregex = r'^(?P<year>[0-9]{4})(-(?P<month>1[0-2]|0[1-9])(-(?P<day>3[0-1]|0[1-9]|[1-2][0-9]))?)?$'
            assert re.search(dtregex, datestring)
        except:
            return False
    return True


def add_resource_type(rec, pubtype, genre, filetype):
    """
    """
    bad_data = []
    kcr_resource_types = {"dataset": ["other"],
                            "image": ["chart", "diagram", "map", "visualArt", "other"],
                            "instructionalResource": ["curriculum", "syllabus", "other"],
                            "presentation": ["slides", "speech", "conferencePaper", "conferencePoster", "lecture", "other"],
                            "publication": [
                                "abstract", "blogPost", "book", "bookSection", "review",
                                "conferenceProceeding", "dataPaper",
                                "bookReview", "dissertation", "documentation", "fictionalWork", "interviewTranscript", "journal", "journalArticle", "legalResponse", "legalComment", "magazineArticle", "newspaperArticle", "onlinePublication",
                                "other", "preprint", "report",
                                "monograph", "proceedingsArticle", "translation", "whitePaper"
                            ],
                            "software": [
                                "3dModel", "computationalModel", "computationalNotebook", "outputManagementPlan", "service", "application"
                            ],
                            "audiovisual": ["documentary", "interviewRecording",
                                "video", "soundRecording", "musicalRecording", "other", "podcast"
                            ],
                            "other": [
                                "bibliography", "catalog", "collection", "essay", "event", "findingAid", "interactiveResource", "notes", "peerReview", "physicalObject", "standard", "workflow", "mixedMaterial", "text"
                            ]
                            }
    types_of_resource = {"Audio": "audiovisual:soundRecording",
                         "Image": "image:other",
                         "Mixed material": "other:mixedMaterial",
                         "Software": "software:application",
                         "Text": "other:text",
                         "Video": "audiovisual:video"}

    genres = {"Abstract": "publication:abstract",
              "Article": "publication:journalArticle",
              "Bibliography": "other:bibliography",
              "Blog Post": "publication:blogPost",
              "Book": "publication:book",
              "Book chapter": "publication:bookChapter",
              "Book review": "publication:review",
              "Book section": "publication:bookSection",
              "Catalog": "other:catalog",
              "Chart": "image:chart",
              "Code or software": "software: application",
              "Conference paper": "presentation:conferencePaper",
              "Conference poster": "presentation:conferencePoster",
              "Conference proceeding": "publication:conferenceProceeding",
              "Course material or learning objects": "instructionalResource:other",
              "Course Material or learning objects": "instructionalResource: other",
              "Data set": "dataset:other",
              "Dissertation": "publication:dissertation",
              "Documentary": "audiovisual:documentary",
              "Editorial": "publication:editorial",
              "Essay": "other:essay",
              "Fictional work": "publication:fictionalWork",
              "Finding aid": "other:other",
              "Image": "image:other",
              "Interview": "publication:interviewTranscript",
              "Lecture": "presentation:lecture",
              "Legal Comment": "publication:legalComment",
              "Legal response": "publication:legalResponse",
              "Magazine section": "publication:magazineArticle",
              "Map": "image:map",
              "Monograph": "publication:monograph",
              "Music": "audiovisual:musicalRecording",
              "Newspaper article": "publication:newspaperArticle",
              "Online publication": "publication:onlinePublication",
              "Online Publication": "publication:onlinePublication",
              "Other": "other:other",
              "Performance": "audioVisual:performance",
              "Photograph": "image:other",
              "Podcast": "audiovisual:podcast",
              "Poetry": "publication:poeticWork",
              "Presentation": "presentation:other",
              "Report": "publication:report",
              "Review": "publication:review",
              "Sound recording-musical": "audiovisual:musicalRecording",
              "Sound recording-non musical": "audiovisual:soundRecording", "Syllabus": "instructionalResource:syllabus",
              "Technical report": "publication:report",
              "Thesis": "publication:dissertation",
              "Translation": "publication:translation",
              "Video": "audiovisual:videoRecording",
              "Video essay": "audiovisual:videoRecording",
              "Visual art": "image:visualArt",
              "White paper": "publication:whitePaper"}

    publication_types = {"book-chapter": "publication:bookChapter",
                            "book-review": "publication:review",
                            "book-section": "publication:bookSection",
                            "journal-article": "publication:journalArticle",
                            "magazine-section": "publication:magazineArticle",
                            "monograph": "publication:monograph",
                            "newspaper-article": "publication:newspaperArticle",
                            "online-publication": "publication:onlinePublication",
                            "podcast": "audiovisual:podcast",
                            "proceedings-article": "publication:proceedingsArticle"}
    if genre in genres.keys():
        rec['metadata']['resource_type'] = {'id': genres[genre]}
        if (pubtype == "Interview") and (filetype in ['audio/mpeg', 'audio/ogg', 'audio/wav', 'video/mp4', 'video/quicktime']):
            rec['metadata']['resource_type'
                            ] = {"id": "audiovisual:interviewRecording"}
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


def add_book_authors(author_string:str, bad_data_dict:dict,
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
                fullname = f'{b[0]} {b[1]}' if len(b) > 1 else b[0]
                given = b[0] if len(b) > 1 else ''
                family = b[1] if len(b) > 1 else ''
            author_list.append(
                {
                    'person_or_org': {
                        'name': fullname,
                        "type": "personal",
                        "given_name": given,
                        "family_name": family
                    },
                    'role': {
                        'id': ('editor' if is_editor else 'author')
                    }
                }
            )
    except TypeError as e:
        append_bad_data(row_id,
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

def add_author_data(newrec:dict, row:dict, bad_data_dict:dict
                    ) -> tuple[dict, dict]:
    """
    Add information about authors to the supplied record from supplied row.

    Processes data from the 'authors' and 'author_info' csv export fields.
    """

    creators = []
    contributors_misplaced = []
    creators_misplaced = []
    # FIXME: What roles do we allow? Submitter?
    allowed_roles = ['author', 'editor', 'contributor', 'submitter',
                     'translator', 'creator', 'project director']
    if row['authors']:
        # print(row['pid'])
        try:
            # row['authors'] = row['authors'].replace('\\', '&quot;')
            for a in row['authors']:
                new_person = {}

                new_person['person_or_org'] = {
                    'type': "personal",  # FIXME: can't hard code
                    'name': a['fullname'],
                    'given_name': a['given'],
                    'family_name': a['family']
                }
                if a['role'] and a['role'] in allowed_roles or not a['role']:
                    # TODO: are null roles a problem?
                    new_person['role'] = {'id': a['role']}
                else:
                    append_bad_data(row['id'],
                                    (f'authors:{a["fullname"]}:role', a['role']),
                                    bad_data_dict)
                if a['affiliation']:
                    new_person['affiliations'] = a['affiliation'].split('|')
                if a['uni']:  # uni is the hc username
                    new_person['person_or_org']['identifiers'] = [
                        {'identifier': a['uni'], 'scheme': 'hc_username'}]
                if a['role'] in allowed_roles:
                    if a['role'] == 'contributor':
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
            append_bad_data(row['id'], ('authors:Syntax or ValueError',
                                        row['authors']), bad_data_dict)
    else:
        append_bad_data(row['id'], ('authors:no value', row['authors']),
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


@cli.command(name="serialize")
def serialize_command_wrapper():
    """
    Isolates click registration for ease of unit testing.
    """
    serialize_json()


def serialize_json() -> tuple[dict, dict]:
    """
    Parse and serialize csv data into Invenio JSON format.
    """
    keywords_global_dict = {}
    current_keyword_id = 0
    licenses_list = []

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
                        'dates': [],
                        'subjects': [],
                        'languages': [],
                        'rights': [],
                        'formats': []
                    },
                    'files': {'entries': []},
    }

    newrec_list:list[dict] = []
    bad_data_dict:dict[str: list] = {}
    line_count:int = 0

    with open('../../kcr-untracked-files/core-export-may-15-23.json') as json_file:
        # top_object = json.loads('{"data": ' + json_file.read() + '}')
        top_object = json.loads(json_file.read())
        pprint(top_object[0])
        for row in top_object:
            newrec = deepcopy(baserec)

            if row['chapter']:
                def normalize(mystring):
                    mystring = mystring.casefold()
                    mystring = re.sub(r'\\*"', '"', mystring)
                    mystring = re.sub(r"\\*'", "'", mystring)
                    mystring = mystring.replace('  ', ' ')
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
                mychap = normalize(row['chapter'])
                mytitle = normalize(row['title'])
                mybooktitle = normalize(row['book_journal_title'])
                if mychap == mytitle:
                    pass
                # FIXME: This needs work
                elif mychap in mytitle and len(mychap) > 18:
                    append_bad_data(row['id'],
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
                            'kcr:chapter_label'] = row['chapter']
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
                    elif re.search(r'^[Cc]hapter', row['chapter']):
                        shortchap = re.sub(r'^[Cc]hapter\s*', '',
                                           row['chapter'])
                        newrec['custom_fields']['kcr:chapter_label'] = shortchap
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
                                                ] = row['chapter']

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
            if row['organization']:
                newrec['custom_fields']['hclegacy:submitter_affiliation'
                                        ] = row['organization']

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
            newrec['metadata']['title'] = mytitle
            newrec['metadata']['additional_titles'].append(
                {"title": row['title'],
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
            newrec, bad_data = add_resource_type(newrec,
                                                 row['publication-type'],
                                                 row['genre'], row['filetype'])
            if bad_data:
                for i in bad_data:
                    append_bad_data(row['id'], i, bad_data_dict)

            # Identifiers
            # FIXME: Is it right that these are all datacite dois?
            if row['deposit_doi']:
                newrec.setdefault('pids', {})[
                    'doi'] = {"identifier": row['deposit_doi'],
                              "provider": "datacite",
                              "client": "datacite"}
            if row['doi']:
                newrec['metadata'].setdefault('identifiers', []).append(
                    {"identifier": row['doi'],
                     "scheme": "doi"}
                )
            if row['handle']:
                newrec['metadata'].setdefault('identifiers', []).append(
                    {"identifier": row['handle'],
                     "scheme": "handle"}
                )
            if row['url']:
                my_urls = re.split(r' and |;', row['url'])
                for url in my_urls:
                    url = row['url'].replace(' ', '')
                    if validators.url(url) or validators.url(f'https://{url}'):
                        newrec['metadata'].setdefault('identifiers', []).append(
                            {"identifier": row['url'],
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
                lang1, lang2 = None, None
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
                newrec['custom_fields']['kcr:edition'] = row['edition']

            # Committee deposit
            if row['committee_deposit'] == "yes":
                try:
                    cid = int(row['committee_id'])
                    newrec['custom_fields'][
                           'hclegacy:committee_deposit'] = cid
                except ValueError:
                    append_bad_data(row['id'],
                                    ('committee_id', row['committee_id']),
                                    bad_data_dict)

            # HC legacy collection
            if row['member_of']:
                newrec['custom_fields']['hclegacy:collection'
                                        ] = row['member_of']

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
                    append_bad_data(row['id'],
                                    ('submitter', row['submitter']),
                                    bad_data_dict)

            # Author info
            newrec, bad_data_dict = add_author_data(newrec, row, bad_data_dict)

            if row['organization']:
                newrec['custom_fields'
                       ].setdefault('hclegacy:submitter_org_memberships',
                                    []).append(row['organization'])

            newrec_list.append(newrec)
            line_count += 1

            # Date info
            # FIXME: does "issued" work here?
            newrec['metadata']['publication_date'] = row['date_issued']
            if row['date_issued'] != row['date']:
                newrec['metadata'].setdefault('dates', []).append(
                    {
                        "date": row['date'],
                        "type": {
                            "id": "issued",
                            "title": { "en": "Issued" }
                        },
                        "description": "Human readable publication date"
                    }
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
                append_bad_data(row['id'],
                                ('group or group_ids', row['group'], row['group_ids']),
                                bad_data_dict)
            except json.decoder.JSONDecodeError as e:
                # print(e)
                # print(row['group'], row['group_ids'])
                row['hclegacy:groups_for_deposit'] = None
                append_bad_data(row['id'],
                                ('group or group_ids', row['group'], row['group_ids']),
                                bad_data_dict)

            # book info
            # FIXME: Need to augment out-of-the-box imprint custom fields
            if row['book_author']:
                newrec['custom_fields']['imprint:imprint'] = {}
                # print(row['book_author'])
                book_names, bad_data_dict = add_book_authors(
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
                    newrec['custom_fields'].setdefault('kcr:volume', {}
                        )['volume'] = row['volume']
                else:
                    # print(row['id'], newrec['metadata']['resource_type']['id'], row['volume'])
                    newrec['custom_fields'].setdefault('kcr:volume', {}
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
                        append_bad_data(row['id'],
                                        ('invalid isbn', row['isbn']),
                                        bad_data_dict)
                    else:
                        newrec['custom_fields'][
                            'imprint:imprint']['isbn'].append(checked_i)

            if row['publisher']:
                newrec['metadata']['publisher'] = row['publisher']

            if row['book_journal_title']:
                myfield = 'imprint:imprint'
                if newrec['metadata']['resource_type'][
                        'id'] in article_types:
                    myfield = 'journal:journal'
                if newrec['metadata']['resource_type']['id'] not in [
                    *book_types, *article_types]:
                    # print('****', newrec['metadata']['resource_type']['id'])
                    append_bad_data(row['id'],
                                    ('resource_type for book_journal_title',
                                     newrec['metadata']['resource_type']['id']),
                                     bad_data_dict)
                # FIXME: check right field for legalComment, bibliography, lecture, conferencePaper, legalResponse, other:other, other:essay, translation, videoRecording, blogPost, interviewTranscript, poeticWork, fictionalWork, image:visualArt, image:map, instructionalResource:syllabus, onlinePublication, presentation:other, instructionalResource:other, musicalRecording, catalog, dataset:other, audiovisual:documentary, lecture
                if myfield not in newrec['custom_fields'].keys():
                    newrec['custom_fields'][myfield] = {}
                newrec['custom_fields'][myfield][
                    'title'] = row['book_journal_title']

                # article/chapter info
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
                        append_bad_data(row['id'],
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
                    if valid_isbn(row['issn']):
                        # print('isbn', row['issn'])
                        newrec['custom_fields'].setdefault(
                            'imprint:imprint', {})['isbn'] = [row['issn']]
                        append_bad_data(row['id'],
                            ('issn', 'isbn in issn field', row['issn']),
                            bad_data_dict)
                    else:
                        newrec['custom_fields'].setdefault(
                            'journal:journal', {})['issn'] = []

                        # myissn = row['issn'].replace(b'\xe2\x80\x94'.decode('utf-8'), '-')

                        # myissn = myissn.replace('\x97', '-')
                        myissn = row['issn'].replace(u'\u2013', '-')
                        myissn = myissn.replace(u'\u2014', '-')
                        myissn = re.sub(r'\s?-\s?', '-', myissn)
                        myissn = myissn.replace('Х', 'X')
                        myissn = myissn.replace('.', '')
                        myissnx = re.findall(r'\d{4}[-\s\.]?\d{3}[\dxX]', myissn)
                        if len(myissnx) < 1:
                            append_bad_data(row['id'],
                                ('issn', 'malformed', row['issn']),
                                bad_data_dict)
                        else:
                            for i in myissnx:
                                i = re.sub(r'ISSN:? ?', '', i)
                                try:
                                    if issn.validate(i):
                                        newrec['custom_fields'][
                                            'journal:journal']['issn'].append(i)
                                except Exception:
                                    # print('exception', i, row['issn'])
                                    append_bad_data(row['id'],
                                        ('issn', 'invalid last digit',
                                         row['issn']),
                                        bad_data_dict)


                # extra for dissertations and reports
                if row['institution']:
                    # print(row['id'])
                    # print(newrec['metadata']['resource_type']['id'])
                    newrec['custom_fields']['kcr:sponsoring_institution'
                                            ] = row['institution']
                    if newrec['metadata']['resource_type']['id'] not in [
                            'publication:dissertation', 'publication:report',
                            'publication:whitePaper']:
                        append_bad_data(row['id'],
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
                        'place'] = row['conference_location'
                                       ] or row['meeting_location']
                if row['conference_organization'] or row['meeting_organization']:
                    newrec['custom_fields'][
                        'kcr:meeting_organization'] = row[
                            'conference_organization'] or row[
                                'meeting_organization']
                if row['conference_title'] or row['meeting_title']:
                    newrec['custom_fields'].setdefault('meeting:meeting', {})[
                        'title'] = row['conference_title'] or row['meeting_title']

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
                        kid = None
                        if k.casefold() in keywords_global_dict.keys():
                            kid = keywords_global_dict[k.casefold()][0]
                            if k not in keywords_global_dict[k.casefold()][1]:
                                keywords_global_dict[k.casefold()][1].append(k)
                            # print('got id from global for keyword', k)
                        else:
                            kid = current_keyword_id
                            keywords_global_dict[k.casefold()] = (kid, [k])
                            current_keyword_id += 1
                            # print('missing id for keyword', k)
                        keywords.append({'tag_label': k,
                                         'tag_identifier': kid})
                    if keywords:
                        newrec['custom_fields'][
                            'kcr:user_defined_tags'] = keywords

            if row['subject']:
                covered_subjects = []
                for s in row['subject']:
                    if s not in covered_subjects:
                        newrec['metadata'].setdefault('subjects', []).append(
                            {
                                "id": s,
                                "scheme": "fast"
                            }
                        )
                    covered_subjects.append(s)

            # uploaded file info
            # FIXME: Is this right? How are we handling upload?
            if row['id'] == 'hc:45177':
                print('files...')
                print(row['file_pid'], row['fileloc'], row['filename'])
            if row['file_pid'] or row['fileloc'] or row['filename']:
                newrec['custom_fields']['hclegacy:file_location'
                                        ] = row['fileloc']
                newrec['custom_fields']['hclegacy:file_pid'
                                        ] = row['file_pid']
                newrec['files'] = {
                    "enabled": "true",
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

        pprint([r for r in newrec_list if r['metadata']['identifiers'][0]['identifier'] == 'hc:45177'])
        pprint([r for r in top_object if r['id'] == 'hc:45177'])

        # auth_errors = {k:v for k, v in bad_data_dict.items() for i in v if i[0][:8] == 'authors' and len(i) == 2}
        # pprint(auth_errors)
        # pprint(bad_data_dict)
        # print(len(auth_errors))
    print(f'Processed {line_count} lines.')
    print(f'Found {len(bad_data_dict)} records with bad data.')

    return newrec_list, bad_data_dict


fedora_fields = ["pid", "label", "state", "ownerId", "cDate", "mDate",
                 "dcmDate", "title", "creator", "subject", "description",
                 "publisher", "contributor", "date", "type", "format",
                 "identifier", "source", "language", "relation", "coverage",
                 "rights"]

@cli.command(name="fedora")
@click.option("--count", default=20, help="Maximum number of records to return")
@click.option("--query", default=None, help="A query string to limit the records")
@click.option("--protocol", default="fedora-xml", help="The api protocol to use for the request")
@click.option("--pid", default=None, help="A pid or regular expression to select records by pid")
@click.option("--terms", default=None, help="One or more subject terms to filter the records")
@click.option("--fields", default=None, help="A comma separated string list of "
              "fields to return for each record")
def fetch_fedora(query:Optional[str], protocol:str, pid:Optional[str],
                 terms:Optional[str], fields: Optional[str], count:int
                 ) -> list[dict]:
    """
    Fetch deposit records from the Fedora CORE datastream.
    """
    fields_list = fields.split(',') if fields is not None else fedora_fields
    FEDORA_USER = os.environ['FEDORA_USER']
    FEDORA_PASSWORD = os.environ['FEDORA_PASSWORD']

    f = FedoraApi(base_url="https://comcore.devel.lib.msu.edu/fedora",
                     username=os.environ['FEDORA_USER'],
                     password=os.environ['FEDORA_PASSWORD'])
    r = ""
    if protocol == "fedora-xml":
        fedora_url = f"https://comcore.devel.lib.msu.edu/fedora/objects/{pid}/objectXML" # whole datastream object
        r = requests.get(fedora_url, auth=(FEDORA_USER, FEDORA_PASSWORD))
        pprint(r.text)
    if protocol == "DC":
        fedora_url = f"https://comcore.devel.lib.msu.edu/fedora/objects/{pid}/datastreams/DC?format=xml" # dc metadata
        r = requests.get(fedora_url, auth=(FEDORA_USER, FEDORA_PASSWORD))
        pprint(r.text)
    elif protocol == "ext":
        fedora_url = f"https://comcore.devel.lib.msu.edu/fedora/objects/{pid}/datastreams/RELS-EXT?format=xml" # rdf
        r = requests.get(fedora_url, auth=(FEDORA_USER, FEDORA_PASSWORD))
        pprint(r.text)
    elif protocol == "content":
        fedora_url = f"https://comcore.devel.lib.msu.edu/fedora/objects/{pid}/datastreams/CONTENT?format=xml" # file size, etc.
        r = requests.get(fedora_url, auth=(FEDORA_USER, FEDORA_PASSWORD))
        pprint(r.text)
    # fedora_url = "https://comcore.devel.lib.msu.edu/fedora/objects/hc:23276/relationships?format=xml" # rdf
    # fedora_url = "https://comcore.devel.lib.msu.edu/fedora/objects/hc:23276/datastreams?format=xml" # rdf
    # fedora_url = "https://comcore.devel.lib.msu.edu/fedora/search"

    # query = urllib.quote('title:rome creator:staples')
    # fedora_url = f'https://comcore.devel.lib.msu.edu/fedora/objects?pid=true&label=true&state=true&ownerId=true&cDate=true&mDate=true&dcmDate=true&title=true&creator=true&subject=true&description=true&publisher=true&contributor=true&date=true&type=true&format=true&identifier=true&source=true&language=true&relation=true&coverage=true&rights=true&terms=&query=title~gothic&resultFormat=xml&query=title~Gothic creator~*K*&maxResults=3'
    elif protocol == "fedora-terms":
        r = f.find_all_objects(terms, fields=fields_list, query=f"identifier~{pid}")
        pprint(r)
    elif protocol == "fedora-pid":
        r = f.find_all_objects_by_id(f"{pid}", fields=fields_list)
        pprint(r)
    # all_objects = f.find_all_objects("", fields=fields_list,
    #                                  query="'title~Gothic'", maxResults=count)

    records = []
    aggregator_pid = 0
    main_pid = 0

    root = ET.fromstring(r[1])

    def _getnode(base, fieldname):
        # node = base.find(f'{dc}{fieldname}')
        node = base.findall(f'{prefix}{fieldname}')
        if len(node) > 0:
            return node[0].text
        else:
            return None
    def _getnodes(base, fieldname):
        # nodes = base.findall(f'{dc}{fieldname}')
        nodes = base.findall(f'{prefix}{fieldname}')
        return nodes

    prefix = "{http://www.fedora.info/definitions/1/0/types/}"
    # prefix = "{info:fedora/fedora-system:def/foxml#}"
    # oai_dc = "{http://www.openarchives.org/OAI/2.0/oai_dc/}"
    # dc = "{http://purl.org/dc/elements/1.1/}"
    # basepath = f'./{prefix}datastream/{prefix}datastreamVersion/{prefix}xmlContent/{oai_dc}dc'

    # rdf = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"
    # cc_rights = root.findall(f'./{prefix}datastream[@ID="RELS-EXT"]/{prefix}datastreamVersion/{prefix}xmlContent/{rdf}RDF/{rdf}Description/{{http://creativecommons.org/ns#}}license')

    versions = root.findall(f'./{prefix}resultList/{prefix}objectFields')
    for v in versions:
        newrec = {'metadata': {
                    'resource_type': {},
                    'title': "",
                    'creators': [],
                    'publication_date': [],
                    'identifiers': [],
                    'dates': [],
                    'subjects': [],
                    'languages': [],
                    'rights': [],
                    'formats': []
                    },
                  'files': {'entries': []},
        }

        # TODO: standardize type vocabulary?
        newrec['metadata']['resource_type'] = _getnode(v, 'type')
        newrec['metadata']['title'] = _getnode(v, 'title')

        for c in _getnodes(v, 'creator'):
            newrec['metadata']['creators'].append(
                {'person_or_org': {'type': "personal",
                                   'name': c.text,
                                   'identifiers': []},
                 'affiliations': []}
            )
        # TODO: given name and family name???
        # TODO: Affiliation???
        for o in _getnodes(v, 'contributor'):
            newrec['metadata']['contributors'].append(
                {'person_or_org': {'type': "personal",
                                   'name': o.text,
                                   'identifiers': []},
                 'affiliations': []}
            )

        newrec['metadata']['description'] = _getnode(v, 'description')
        for s in _getnodes(v, 'subject'):
            newrec['metadata']['subjects'].append(
                {'subject': s.text,
                 'scheme': "fast"}
            )
        # TODO: put this in pids?
        main_pid = _getnode(v, 'pid')
        newrec['metadata']['identifiers'].append(
            {'identifier': main_pid,
            'scheme': 'hc'}
        )
        # Checks to ensure EDTF Level 0 format
        pubDate = _getnode(v, 'date')
        newrec['metadata']['publication_date'] = pubDate
        try:
            assert(valid_date(pubDate))
        except AssertionError:
            print('could not validate pubDate:', pubDate, f'({main_pid})')

        for i in _getnodes(v, 'identifier'):
            if i.text != main_pid:
                aggregator_pid = i.text
                newrec['metadata']['identifiers'].append(
                    {'identifier': i.text,
                     'scheme': 'hc-aggregator'}
                )
        if _getnode(v, 'rights') == None:
            newrec['metadata']['rights'].append(
                {"id": "cc-by-4.0",
                 "description": {"en": "The Creative Commons Attribution "
                                 "license allows re-distribution and re-use of "
                                 "a licensed work on the condition that the "
                                 "creator is appropriately credited."},
                 "link": "https://creativecommons.org/licenses/by/4.0/"
                }
            )
        else:
            newrec['metadata']['rights'].append({"id": _getnode(v, 'rights')})

        if _getnode(v, 'publisher'):
            newrec['metadata']['publisher'] = _getnode(v, 'publisher')
        if _getnode(v, 'format'):
            newrec['metadata']['formats'] = [_getnode(v, 'format')]

        # TODO: format language???
        if _getnode(v, 'language'):
            newrec['metadata']['languages'].append(
                {'id': _getnode(v, 'language')}
            )

        # CORE uses w3cdtf and Invenio requires edtf level 0
        # Ensure EDTF
        cDate = _getnode(v, 'cDate')
        if cDate:
            newrec['metadata']['dates'].append(
                {'date': cDate, 'description': 'record created',
                'type': {'id': 'created', 'title': {'en': 'Record created'}}}
            )
        try:
            assert(valid_date(cDate))
        except AssertionError:
            print('could not validate cDate:', cDate, f'({main_pid})')

        # Ensure EDTF
        mDate = _getnode(v, 'mDate')
        if mDate:
            newrec['metadata']['dates'].append(
                {'date':  mDate,
                'description': 'record last updated',
                'type': {'id': 'updated', 'title': {'en': 'Record updated'}}}
            )
        try:
            assert(valid_date(mDate))
        except AssertionError:
            print('could not validate cDate:', mDate, f'({main_pid})')

        # TODO: do we keep this AND mdate?
        dcmDate = _getnode(v, 'dcmDate')
        if dcmDate:
            newrec['metadata']['dates'].append(
                {'date': dcmDate,
                 'description': 'record last updated (dc)',
                 'type': {'id': 'updated', 'title': {'en': 'Record updated (dc)'}}}
            )
            assert(valid_date(dcmDate))

        filename = _getnode(v, 'label')
        newrec['files']['entries'].append({
                f'{filename}':
                    {"key": filename,
                    "mimetype": _getnode(v, 'format')}
            }
        )

        # TODO: ownerId???
        # TODO: CORE tags?
        # TODO: CORE url?
        # TODO: CORE issn?
        # TODO: CORE notes?

        # TODO: CORE 'source', 'relation', 'coverage',

        # TODO: CORE 'state',

        # Retrieve data not available via Fedora api
        fedora_desc_url = f'https://comcore.devel.lib.msu.edu/fedora/objects/{aggregator_pid}/datastreams/descMetadata/content?format=xml'
        ag_result = requests.get(fedora_desc_url,
                                 auth=(FEDORA_USER, FEDORA_PASSWORD))

        # print(r.status_code)
        # print(r.headers)
        if ag_result.status_code != 200:
            print('Failed to retrieve descMetadata for', aggregator_pid)
        # print(r.encoding)
        # print(ag_result.text)
        # print(ag_result.content)
        mods_prefix = "{http://www.loc.gov/mods/v3}"
        ag_root = ET.fromstring(ag_result.text)

        # TODO: can <name> also be contributor?
        # FIXME: Some names given erroneous @type of "personal":
        # e.g., hc:38793-4
        for name in ag_root.findall(f'{mods_prefix}name'):
            gname = name.find(f'{mods_prefix}namePart[@type="given"]')
            fname = name.find(f'{mods_prefix}namePart[@type="family"]')
            if fname is not None:
                myName = gname.text + ' ' + fname.text
                print('myName', myName)
                n = [n for n in newrec['metadata']['creators'] if
                    n['person_or_org']['name'] == myName][0]
                n['person_or_org']['given_name'] = gname.text
                n['person_or_org']['family_name'] = fname.text
                # TODO: what is organizational type called?
                # assume everyone is personal otherwise?
                if name.get('type') not in ['personal', None]:
                    print('name type is:', name.get('type'))
                t = name.get('type') if name.get('type') else "personal"
                n['person_or_org']['type'] = t
                # TODO: get ORCID identifiers?
                # TODO: am I right that the ID here is the hc user id?
                if name.get('ID'):
                    n['person_or_org']['identifiers'].append(
                        {"scheme": "hc",
                         "identifier": name.get('ID')}
                    )
                if name.find(f'{mods_prefix}role/roleTerm') is not None:
                    n['role'] = name.find(f'{mods_prefix}role/roleTerm')
                # Invenio only allows affiliations for persons
                if (n['person_or_org']['type'] == "personal" and
                    name.find(f'{mods_prefix}affiliation') is not None):
                    n['affiliations'].append(
                        {'name': name.find(f'{mods_prefix}affiliation').text}
                    )
                    # should we try to add 'id' for org from ROR?
        lang = ag_root.find(f'{mods_prefix}language')
        if (newrec['metadata']['languages'] == [] and lang is not None):
            newrec['metadata']['languages'].append(
                {'id': lang.find(f'{mods_prefix}languageTerm').text}
            )

        records.append(newrec)

    pprint(records)
    # newrec['status'] =

    # pprint(records)

    return records

if __name__=="__main__":
    cli()