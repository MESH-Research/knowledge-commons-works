#! /usr/bin/env python
import csv
import requests
import xml.etree.ElementTree as ET
# import numpy as np
import os
# import pandas as pd

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
        {"id": "dan"},
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
    fedora_url = "https://comcore.devel.lib.msu.edu/fedora/objects/hc:12780/objectXML"

    r = requests.get(fedora_url, auth=(FEDORA_USER, FEDORA_PASSWORD))
    print(r.status_code)
    print(r.headers)
    print(r.encoding)
    print(r.content)

    root = ET.fromstring(r.content)
    prefix = "{info:fedora/fedora-system:def/foxml#}"
    oai_dc = "{http://www.openarchives.org/OAI/2.0/oai_dc/}"
    contents = root.findall(f'./{prefix}datastream/{prefix}datastreamVersion/{prefix}xmlContent/{oai_dc}dc')
    print('contents')
    for c in contents:
        print(c)

    return []

def write_to_csv(rows:list[list[str]]) -> None:
    with open('csv_file', 'w', encoding='UTF8') as f:
        # create the csv writer
        writer = csv.writer(f)
        for row in rows:
            writer.writerow(row)

if __name__=="__main__":
    fetch_records()