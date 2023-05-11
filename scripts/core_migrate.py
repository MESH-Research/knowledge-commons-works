#! /usr/bin/env python
import click
from copy import deepcopy
import csv
from datetime import datetime
from fedoraapi import FedoraApi
from itertools import zip_longest
import requests
# import numpy as np
from typing import Optional
import os
# import pandas as pd
from pprint import pprint
import re
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape, unescape


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
              "Performance": "other:other",
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

    publication_types = {"book-chapter": "publication:bookSection",
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
        rec['metadata']['resource_type'] = genres[genre]
        if (pubtype == "Interview") and (filetype in ['audio/mpeg', 'audio/ogg', 'audio/wav', 'video/mp4', 'video/quicktime']):
            rec['metadata']['resource_type'] = "audiovisual:interviewRecording"
        if (pubtype in publication_types.keys() and
                genres[genre] != publication_types[pubtype]):
            rec['custom_fields']['hclegacy:publication_type'] = pubtype
    else:
        rec['metadata']['resource_type'] = None
        bad_data.append(('genre', genre))
        rec['custom_fields']['hclegacy:publication_type'] = pubtype
        if pubtype in publication_types.keys():
            rec['metadata']['resource_type'] = publication_types[pubtype]
        else:
            bad_data.append(('publication-type', pubtype))

    return rec, bad_data


def parse_csv():
    """
    """

    roles_list = []
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

    with open('../kcr-untracked-files/core-may-4-2023.csv') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count:int = 0
        for row in csv_reader:
            newrec = deepcopy(baserec)
            newrec['custom_fields']['kcr:commons_domain'] = row['domain']

            newrec['metadata']['title'] = row['title_unchanged']
            newrec['metadata']['additional_titles'].append(
                {"title": row['title'],
                    "type": {
                        "id": "other",
                        "title": {"en": "Primary title with HTML stripped"}
                    },
                }
            )
            newrec['metadata']['description'] = row['abstract_unchanged']
            newrec['metadata']['additional_descriptions'].append(
                {"description": row['abstract'],
                 "type": {
                     "id": "other",
                     "title": {"en": "Primary description with HTML stripped"}
                 }
                }
            )

            newrec, bad_data = add_resource_type(newrec,
                                                 row['publication-type'],
                                                 row['genre'], row['filetype'])
            if bad_data:
                for i in bad_data:
                    bad_data_dict.setdefault(row['id'], []).append(i)



            newrec['metadata']['identifiers'].append(
                {'identifier': row['id'], 'scheme': 'hclegacy'}
            )

            if row['committee_deposit'] == "yes":
                try:
                    cid = int(row['committee_id'])
                    newrec['custom_fields'][
                           'hclegacy:committee_deposit'] = cid
                except ValueError:
                    bad_data_dict.setdefault(row['id'], []).append(
                        ('committee_id', row['committee_id'])
                    )

            if row['submitter']:
                try:
                    row['submitter'] = int(row['submitter'])
                    # Doesn't work because not Invenio user id
                    newrec['parent']['access']['owned_by'].append(
                        {'user': row['submitter']}
                    )
                except ValueError:


            if row['authors']:
                # Escaping/unescaping necessary to avoid splitting string on
                # escaped html entities
                row['authors'] = unescape(row['authors'])
                # Replace necessary because some affiliation values are
                # semicolon separated internally
                row['authors'] = row['authors'].replace('; ', '~~')
                for a in row['authors'].split(';'):
                    a_fields = ['name', 'given', 'family', 'username',
                                'role', 'affiliation']
                    # Replace necessary because some affiliation values are bar
                    # separated internally
                    a = a.replace(' |', '~~')
                    a_values = a.split('|')
                    if len(a_values) == 6:
                        a_dict = dict(zip_longest(a_fields, a_values))
                        newrec['metadata']['creators'].append(
                            {'person_or_org':
                                {'type': "personal",  # FIXME: can't hard code
                                 'name': escape(a_dict['name']),
                                 'given_name': escape(a_dict['given']),
                                 'family_name': escape(a_dict['family']),
                                 'identifiers': {
                                    'identifiers': escape(a_dict['username']),
                                    'scheme': 'hc_username'
                                  }
                                 },
                            'role': escape(a_dict['role']),
                            'affiliations': [
                                escape(a_dict['affiliation']).split('~~')]
                            }
                        )
                        if a_dict['role'] not in roles_list:
                            roles_list.append(a_dict['role'])
                    else:
                        bad_data_dict.setdefault(row['id'], []).append(
                            ('authors', row['authors'], len(a_values))
                        )
            else:
                bad_data_dict.setdefault(row['id'], []).append(
                    ('authors', row['authors'])
                )

            newrec_list.append(newrec)
            line_count += 1

        pprint(newrec_list[0])

        pprint(bad_data_dict)
        print(f'Processed {line_count} lines.')
        print(f'Found {len(bad_data_dict)} records with bad data.')
    return newrec_list, bad_data_dict


fedora_fields = ["pid", "label", "state", "ownerId", "cDate", "mDate",
                 "dcmDate", "title", "creator", "subject", "description",
                 "publisher", "contributor", "date", "type", "format",
                 "identifier", "source", "language", "relation", "coverage",
                 "rights"]

@click.command()
@click.option("--count", default=20, help="Maximum number of records to return")
@click.option("--query", default=None, help="A query string to limit the records")
@click.option("--pid", default=None, help="A pid or regular expression to select records by pid")
@click.option("--terms", default=None, help="One or more subject terms to filter the records")
@click.option("--fields", default=None, help="A comma separated string list of "
              "fields to return for each record")
def fetch_records(query:Optional[str], pid:Optional[str], terms:Optional[str],
                  fields: Optional[str], count:int) -> list[dict]:
    """
    Fetch deposit records from the Fedora CORE datastream.
    """
    fields_list = fields.split(',') if fields is not None else fedora_fields
    pprint(os.environ)
    FEDORA_USER = os.environ['FEDORA_USER']
    FEDORA_PASSWORD = os.environ['FEDORA_PASSWORD']
    fedora_url = "https://comcore.devel.lib.msu.edu/fedora/objects/hc:44598/objectXML" # whole datastream object
    # fedora_url = "https://comcore.devel.lib.msu.edu/fedora/objects/hc:23276/datastreams/DC?format=xml" # dc metadata
    # fedora_url = "https://comcore.devel.lib.msu.edu/fedora/objects/hc:23276/datastreams/RELS-EXT?format=xml" # rdf
    # fedora_url = "https://comcore.devel.lib.msu.edu/fedora/objects/hc:23276/datastreams/CONTENT?format=xml" # file size, etc.
    # fedora_url = "https://comcore.devel.lib.msu.edu/fedora/objects/hc:23276/relationships?format=xml" # rdf
    # fedora_url = "https://comcore.devel.lib.msu.edu/fedora/objects/hc:23276/datastreams?format=xml" # rdf
    # fedora_url = "https://comcore.devel.lib.msu.edu/fedora/search"

    # query = urllib.quote('title:rome creator:staples')
    # fedora_url = f'https://comcore.devel.lib.msu.edu/fedora/objects?pid=true&label=true&state=true&ownerId=true&cDate=true&mDate=true&dcmDate=true&title=true&creator=true&subject=true&description=true&publisher=true&contributor=true&date=true&type=true&format=true&identifier=true&source=true&language=true&relation=true&coverage=true&rights=true&terms=&query=title~gothic&resultFormat=xml&query=title~Gothic creator~*K*&maxResults=3'
    r = requests.get(fedora_url, auth=(FEDORA_USER, FEDORA_PASSWORD))
    pprint(r.text)

    f = FedoraApi(base_url="https://comcore.devel.lib.msu.edu/fedora",
                     username=os.environ['FEDORA_USER'],
                     password=os.environ['FEDORA_PASSWORD'])
    # all_objects = f.find_all_objects_by_id("hc:4477*", fields_list,
    #                                        maxResults=str(count))
    # all_objects = f.find_all_objects("", fields=fields_list,
    #                                  query="'title~Gothic'", maxResults=count)
    all_objects = f.find_objects(terms, fields=fields_list)
    print(all_objects)

    records = []
    aggregator_pid = 0
    main_pid = 0

    root = ET.fromstring(all_objects[1])

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
    parse_csv()
    # fetch_records()