#! /usr/bin/env python
from copy import copy
import csv
import requests
import xml.etree.ElementTree as ET
# import numpy as np
import os
# import pandas as pd
from pprint import pprint

"""
Required fields:
- id (CV)
- creators:
    - person_or_org
        - type
        - given_name (if personal)
        - family_name (if personal)
        - name (if organizational)
    - role??? (CV)

Other top-level internal fields:

"$schema": "local://records/record-v1.0.0.json",
"id": "q5jr8-hny72",
"pid": { ... },  # info about internal id
"parent": { ... },
"access" : { ... },
"custom_fields": {},
"is_draft": true,
"is_published": false,
"links": {},
"revision_id: 1,
"status": "published",
"versions": {
    "index": 2,
    "is_latest": true,
    "is_latest_draft": true
},
"files" : {
  "enabled": "true",
  "entries": {
    "path/paper.pdf": {
      "bucket_id": "",
      "checksum": "",
      "created": "",
      "file_id": "",
      "key": "path/paper.pdf",
      "links": {
        "self": "",
        "content": "",
        "iiif_canvas": "",
        "iiif_base": "",
        "iiif_info": "",
        "iiif_api": ""
      },
      "metadata": {
        "width": 0,
        "height": 0
      },
      "mimetype": "",
      "size": 0,
      "status": "",
      "storage_class": "",
      "updated": "",
      "version_id": "",
    },
  },
  "default_preview": "path/paper.pdf"
},
"tombstone" : {
    "reason": "",
    "category": "",
    "removed_by": {"user": 1},
    "timestamp": ""
},
"""



invenio_json = {
"pids" : {
    "oai": {
      "identifier": "",
      "provider": ""
    },
    "doi": {
      "identifier": "",
      "provider": "",
      "client": ""
    },
    "concept-doi": {
      "identifier": "",
      "provider": "",
      "client": ""
    },
},
"files": {"entries": []},
"metadata" : {
    "resource_type": {
        "id": "",
        "title": {"en": ""}
        },
    "creators": [
        {"person_or_org": {
            "type": "personal|organizational",
            "given_name": "",
            "family_name":  "",
            "name": "",
            "identifiers": [
                {"scheme": "",
                "identifier": ""}
            ],
        },
        "role": "",
        "affiliations": [
            {"id": "",
            "name": ""}
            ]  # if person_or_org type is personal
        }
    ],
    "title": "",
    "additional_titles": [
        {"title": "",
        "type": {
            "id": "",
            "title": ""
        },
        "lang": {"id": ""}
        }
    ],
    "description": "",
    "additional_descriptions": [
        {"description": "",
        "type": {
            "id": "",
            "title": {
                "en": ""
            }
        },
        "lang": {"id": ""}}
    ],
    "rights": [
        {
        "id": "",
        "icon": "",
        "props": {
            "scheme": "spdx",
            "url": ""
        },
        "title": {"en": ""},
        "description": {"en": ""}
        }
    ],
    "contributors": [{
        "person_or_org": {
        "name": "",
        "type": "personal",
        "given_name": "",
        "family_name": "",
        "identifiers": [{
            "scheme": "",
            "identifier": ""
        }],
        },
        "role": {"id": ""},
        "affiliations": [{
        "id": "",
        "name": "",
        }]
    }],
    "subjects": [{
        "id": "",
        "subject": "",
        "scheme": ""
    }],
    "languages": [
        {"id": "eng"}
    ],
    "dates": [{
        "date": "",
        "type": {
        "id": "",
        "title": { "en": "" }
        },
        "description": ""
    }],
    "version": "",
    "publisher": "",
    "identifiers": [{
        "identifier": "",
        "scheme": ""
    }],
    "related_identifiers": [{
        "identifier": "",
        "scheme": "",
        "relation_type": {
            "id": "",
            "title": { "en": "" }
        },
        "resource_type": {
            "id": "",
            "title": { "en": "" }
        }
    }],
    "locations": {
        "features": [{
            "geometry": {
                "type": "",
                "coordinates": [46.23333, 6.05]
            },
            "identifiers": [{
                "scheme": "",
                "identifier": ""
            }],
            "place": "",
            "description": ""
        }],
    },
    "funding": [
        {
            "funder": {
                "id": ""
            },
            "award": {
                "id": ""
            }
        },
        {
            "funder": {
                "id": ""
            },
            "award": {
                "title": { "en": "" },
                "number": "",
                "identifiers": [{
                    "scheme": "",
                    "identifier": ""
                }]
            }
        }
    ],
    "references": [{
        "reference": "",
        "identifier": "",
        "scheme": ""
    }]
}
}

datacite_json = {
    "id": "",
    "doi": "",
    "url": "",
    "types": {
        "ris": "",
        "bibtex": "",
        "citeproc": "",
        "schemaOrg": "",
        "resourceType": "",
        "resourceTypeGeneral": ""
    },
    "identifiers": [
        {"identifierType": "",
         "identifier": ""}
    ],
    "creators": [
        {"name": "",
         "nameType": "",
        "givenName": "",
        "familyName": "",
        "nameIdentifiers": [
            {"schemeUri": "",
             "nameIdentifier": "",
             "nameIdentifierScheme": ""
             }
        ],
        "affiliation": ""
        }
    ],
    "titles": [{
        "title": "",
        "titleType": ""
        }
    ],
    "container": {
        "type": "Series",
        "identifier": "",
        "identifierType": ""
    },
    "publisher": "",
    "publicationYear": "",
    "Resource Type":
        {"Type Description"},
    "subjects": [
        {"subject": "",
         "schemeUri": "",
         "subjectScheme": ""
         }
    ],
    "contributors": [
        {"name": "",
         "nameType": "",
         "affiliation": [],
         "contributorType": "",
         "nameIdentifiers": [
            {"schemeUri": "",
             "nameIdentifier": "",
             "nameIdentifierScheme": ""
            }
         ]
        }
    ],
    "publication_date": "",
    "dates": [
        {"date": "",
         "dateType": "",
         "dateInformation": ""}
    ],
    "sizes": [],
    "formats": [],
    "descriptions": [
        {"lang": "",
         "description": "",
         "descriptionType": ""}
    ],
    "geolocations": [],
    "fundingReferences": [
    ],
    "relatedIdentifiers": [
        {"relatedIdentifier": "",
         "relationType": "",
         "resourceTypeGeneral": "",
         "relatedIdentifierType": ""
        },
    ],
    "relatedItems": [],
    "language": "",
    "version": "",
    "schemaVersion": "",
    "providerId": "",
    "clientId": "",
    "rightsList": [
        {"rightsURI": "",
         "rightsIdentifier": "",
         "rightsIdentifierScheme": "",
         "schemeURI": "",
        }
    ]
}

def fetch_records(records:list=[], count:int=20) -> list:
    """
    Fetch deposit records from the Fedora CORE datastream.
    """
    FEDORA_USER = os.environ['FEDORA_USER']
    FEDORA_PASSWORD = os.environ['FEDORA_PASSWORD']
    fedora_url = "https://comcore.devel.lib.msu.edu/fedora/objects/hc:23276/objectXML"
    # fedora_url = "https://comcore.devel.lib.msu.edu/fedora/search"

    # query = urllib.quote('title:rome creator:staples')
    # fedora_url = f'https://comcore.devel.lib.msu.edu/fedora/objects?pid=true&label=true&state=true&ownerId=true&cDate=true&mDate=true&dcmDate=true&title=true&creator=true&subject=true&description=true&publisher=true&contributor=true&date=true&type=true&format=true&identifier=true&source=true&language=true&relation=true&coverage=true&rights=true&terms=book&query=&resultFormat=xml&query={query}&maxResults={count}'

    r = requests.get(fedora_url, auth=(FEDORA_USER, FEDORA_PASSWORD))
    # print(r.status_code)
    # print(r.headers)
    # print(r.encoding)
    print(r.text)
    print(r.content)

    records = []

    root = ET.fromstring(r.text)
    print(root)

    def _getnode(base, fieldname):
        # node = base.find(f'{dc}{fieldname}')
        node = base.findall(f'{prefix}{fieldname}')
        if len(node) > 0:
            print('printing', node[0].text)
            return node[0].text
        else:
            print('returning')
            return None
    def _getnodes(base, fieldname):
        # nodes = base.findall(f'{dc}{fieldname}')
        nodes = base.findall(f'{prefix}{fieldname}')
        print('FOUND', len(nodes), fieldname)
        return nodes

    prefix = "{http://www.fedora.info/definitions/1/0/types/}"
    # prefix = "{info:fedora/fedora-system:def/foxml#}"
    # oai_dc = "{http://www.openarchives.org/OAI/2.0/oai_dc/}"
    # dc = "{http://purl.org/dc/elements/1.1/}"
    # basepath = f'./{prefix}datastream/{prefix}datastreamVersion/{prefix}xmlContent/{oai_dc}dc'

    # rdf = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"
    # cc_rights = root.findall(f'./{prefix}datastream[@ID="RELS-EXT"]/{prefix}datastreamVersion/{prefix}xmlContent/{rdf}RDF/{rdf}Description/{{http://creativecommons.org/ns#}}license')

    versions = root.findall(f'./{prefix}resultList/{prefix}objectFields')
    print(versions)
    for v in versions:
        newrec = {'metadata': {
                    'resource_type': {},
                    'title': "",
                    'creators': [],
                    'publication_date': [],
                    'identifiers': [],
                    'dates': [],
                    'subjects': [],
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
                                'name': c.text}}
            )
        # TODO: given name and family name???
        # TODO: Affiliation???
        for o in _getnodes(v, 'contributor'):
            newrec['metadata']['contributors'].append(
                {'person_or_org': {'type': "personal",
                                   'name': o.text}}
            )
        # TODO: given name and family name???
        # TODO: Affiliation???

        newrec['metadata']['description'] = _getnode(v, 'description')
        for s in _getnodes(v, 'subject'):
            newrec['metadata']['subjects'].append(
                {'subject': s.text,
                'scheme': "fast"}
            )
        newrec['metadata']['publication_date'] = _getnode(v, 'date')
        newrec['metadata']['identifiers'].append(
            {'identifier': _getnode(v, 'pid'),
            'scheme': 'hc'}
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
            newrec['metadata']['language'] = _getnode(v, 'language')

        newrec['metadata']['dates'].append(
            {'date': _getnode(v, 'cdate'), 'description': 'record created',
            'type': {'id': 'created', 'title': {'en': 'Record created'}}})
        newrec['metadata']['dates'].append(
            {'date':  _getnode(v, 'mdate'),
            'description': 'record last updated',
            'type': {'id': 'updated', 'title': {'en': 'Record updated'}}})

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

        records.append(newrec)

    # newrec['status'] =

    pprint(records)

    return records

def write_to_csv(rows:list[list[str]]) -> None:
    with open('csv_file', 'w', encoding='UTF8') as f:
        # create the csv writer
        writer = csv.writer(f)
        for row in rows:
            writer.writerow(row)

if __name__=="__main__":
    fetch_records()