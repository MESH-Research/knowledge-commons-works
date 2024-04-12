#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 MESH Research
#
# core-migrate is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

from click.testing import CliRunner
from copy import deepcopy
from core_migrate.main import cli
from core_migrate.utils import valid_date, generate_random_string
from core_migrate.serializer import add_date_info, serialize_json
from core_migrate.record_loader import (
    api_request,
    create_invenio_record,
    create_invenio_user,
    delete_invenio_draft_record,
    create_invenio_community,
    create_full_invenio_record,
    upload_draft_files,
)
from core_migrate.utils import _clean_string, _normalize_punctuation
import datetime
import json
import re
import os
from pprint import pprint
import pytest
import pytz
from dateutil.parser import isoparse

TESTING_SERVER_DOMAIN = os.environ["TESTING_SERVER_DOMAIN"]

json28491 = {
    "created": "2020-01-30T16:46:54Z",
    "custom_fields": {
        "hclegacy:collection": "hccollection:1",
        "hclegacy:file_location": (
            "/srv/www/commons/current/web/app/uploads"
            "/humcore/2020/01/o_1dvrj3578"
            "b4822agim1fh81efg7.pdf.tratamiento-de-los-re"
            "siduos-de-la-industria-del-pro"
            "cesado-de-alimentos.pdf"
        ),
        "hclegacy:file_pid": "hc:28492",
        "hclegacy:groups_for_deposit": [
            {
                "group_identifier": "1000807",
                "group_name": "Environmental Humanities",
            },
            {
                "group_identifier": "1003089",
                "group_name": "Foreign Language Teaching and the Environment",
            },
            {"group_identifier": "1003408", "group_name": "Sustainability"},
            {
                "group_identifier": "1002912",
                "group_name": "World-Ecology Research Network",
            },
        ],
        "hclegacy:previously_published": "published",
        "hclegacy:submitter_id": "1020225",
        "hclegacy:record_change_date": "2020-01-30T16:46:54Z",
        "hclegacy:record_creation_date": "2020-01-30T16:46:54Z",
        "imprint:imprint": {"isbn": "978-84-200-1103-5"},
        "kcr:commons_domain": "hcommons.org",
        "kcr:edition": "Spanish",
        "kcr:submitter_email": "lenox.institute@gmail.com",
        "hclegacy:submitter_org_memberships": ["hc"],
        "kcr:submitter_username": "lenoxinstitute100",
        "kcr:notes": (
            "An  English version of the same book is published by "
            "CRC Press in 2006:       Wang, Lawrence K, Hung, "
            "Yung-Tse, Lo, Howard H, and Yapijakis, "
            "Constantine (2006).   Waste Treatment in the Food "
            "Processing Industry.   CRC Press, Boca Raton, "
            "Florida, USA.   333 pages.  ISBN  0-8493-7236-4."
        ),
        "kcr:user_defined_tags": [
            "Steam",
            "STEM",
            "Science and technology studies (STS)",
        ],
    },
    "files": {
        "default_preview": (
            "tratamiento-de-los-residuos-de-la-"
            "industria-del-procesado-de-alimentos.pdf"
        ),
        "enabled": True,
        "entries": {
            "tratamiento-de-los-residuos-de-la-industria-del-procesado-de-alimentos.pdf": {
                "key": "tratamiento-de-los-residuos-de-la-industria-del-procesado-de-alimentos.pdf",
                "mimetype": "application/pdf",
                "size": "21928738",
            }
        },
    },
    "metadata": {
        "additional_descriptions": [
            {
                "description": (
                    "Wang, Lawrence K, Hung, Yung-Tse, Lo, Howard H, "
                    "Yapijakis, Constantine  and  Ribas, Alberto "
                    "lbarz (2008).  TRATAMIENTO de los RESIDUOS de la "
                    "INDUSTRIA del PROCESADO de ALIMENTOS  "
                    "(Spanish).  Waste Treatment in the Food Processing "
                    "Industry.   Editorial ACRIBIA, S. A.,, Apartado "
                    "466, 50080, Zaragoza, Espana. 398 pages. ISBN  "
                    "978-84-200-1103-5  ---------------ABSTRACT:  This book "
                    "emphasizes in-depth presentation of "
                    "environmental pollution sources, waste "
                    "characteristics, control technologies, "
                    "management strategies, facility "
                    "innovations, process alternatives, "
                    "costs, case histories, effluent "
                    "standards, and future trends for the food "
                    "industry, and in-depth presentation of methodologies, "
                    "technologies, alternatives, regional effects, "
                    "and global effects of important pollution control "
                    "practice that may be applied to the industry.  "
                    "Important waste treatment topics covered in this "
                    "book include: dairies, seafood processing plants, "
                    "olive oil manufacturing factories, potato "
                    "processing installations, soft drink "
                    "production plants, bakeries and various other food "
                    "processing facilities."
                ),
                "type": {"id": "other", "title": {"en": "Other"}},
            }
        ],
        "creators": [
            {
                "person_or_org": {
                    "family_name": "Hung",
                    "given_name": "Yung-Tse",
                    "name": "Hung, Yung-Tse",
                    "type": "personal",
                },
                "role": {"id": "editor", "title": {"en": "Editor"}},
            },
            {
                "person_or_org": {
                    "family_name": "Lo",
                    "given_name": "Howard H",
                    "name": "Lo, Howard H",
                    "type": "personal",
                },
                "role": {"id": "editor", "title": {"en": "Editor"}},
            },
            {
                "person_or_org": {
                    "family_name": "Ribas",
                    "given_name": "Alberto lbarz",
                    "name": "Ribas, Alberto lbarz",
                    "type": "personal",
                },
                "role": {"id": "translator", "title": {"en": "Translator"}},
            },
            {
                "person_or_org": {
                    "family_name": "Wang",
                    "given_name": "Lawrence K",
                    "identifiers": [
                        {
                            "identifier": "lenoxinstitute100",
                            "scheme": "hc_username",
                        }
                    ],
                    "name": "Wang, Lawrence K",
                    "type": "personal",
                },
                "role": {"id": "editor", "title": {"en": "Editor"}},
            },
            {
                "person_or_org": {
                    "family_name": "Yapijakis",
                    "given_name": "Constantine",
                    "name": "Yapijakis, Constantine",
                    "type": "personal",
                },
                "role": {"id": "editor", "title": {"en": "Editor"}},
            },
        ],
        "description": (
            "Wang, Lawrence K, Hung, Yung-Tse, Lo, Howard H, "
            "Yapijakis, Constantine  and  Ribas, Alberto "
            "lbarz (2008).  TRATAMIENTO de los RESIDUOS de "
            "la INDUSTRIA del PROCESADO de ALIMENTOS  "
            "(Spanish).  Waste Treatment in the Food "
            "Processing Industry.   Editorial ACRIBIA, S. "
            "A.,, Apartado 466, 50080, Zaragoza, Espana. 398 "
            "pages. ISBN  978-84-200-1103-5  "
            "---------------ABSTRACT:  This book emphasizes "
            "in-depth presentation of environmental "
            "pollution sources, waste characteristics, "
            "control technologies, management strategies, "
            "facility innovations, process alternatives, "
            "costs, case histories, effluent standards, and "
            "future trends for the food industry, and "
            "in-depth presentation of methodologies, "
            "technologies, alternatives, regional effects, "
            "and global effects of important pollution "
            "control practice that may be applied to the "
            "industry.  Important waste treatment topics "
            "covered in this book include: dairies, seafood "
            "processing plants, olive oil manufacturing "
            "factories, potato processing installations, "
            "soft drink production plants, bakeries and "
            "various other food processing facilities."
        ),
        "identifiers": [
            {"identifier": "hc:28491", "scheme": "hclegacy-pid"},
            {"identifier": "1000360-28455", "scheme": "hclegacy-record-id"},
            {"identifier": "10.17613/g0rz-0930", "scheme": "datacite-doi"},
            {
                "identifier": "https://doi.org/10.17613/g0rz-0930",
                "scheme": "url",
            },
        ],
        "languages": [{"id": "spa", "title": {"en": "Spanish"}}],
        "publication_date": "2008",
        "resource_type": {"id": "textDocument-book"},
        "publisher": (
            "Editorial ACRIBIA, S. A., Apartado 466, 50080, Zaragoza, Espana."
        ),
        "rights": [
            {
                "description": {
                    "en": (
                        "Proprietary material. No permissions are "
                        "granted for any kind of copyring or "
                        "re-use. All rights reserved"
                    )
                },
                "id": "arr",
                "icon": "copyright",
                "props": {
                    "url": "https://en.wikipedia.org/wiki/All_rights_reserved"
                },
                "title": {"en": "All Rights Reserved"},
            }
        ],
        "subjects": [
            {
                "id": "http://id.worldcat.org/fast/1108387",
                "subject": "Science--Study and teaching",
                "scheme": "FAST-topical",
            },
            {
                "id": "http://id.worldcat.org/fast/1145221",
                "subject": "Technology--Study and teaching",
                "scheme": "FAST-topical",
            },
        ],
        "title": (
            "TRATAMIENTO de los RESIDUOS de la INDUSTRIA del "
            "PROCESADO de ALIMENTOS"
        ),
    },
    "updated": "2020-01-30T16:46:54Z",
    "parent": {"access": {"owned_by": [{"user": "1020225"}]}},
    "pids": {
        "doi": {
            "client": "datacite",
            "identifier": "10.17613/g0rz-0930",
            "provider": "datacite",
        }
    },
}

json583 = {
    "created": "2016-02-29T13:11:39Z",
    "custom_fields": {
        "hclegacy:collection": "mlacollection:1",
        "hclegacy:file_location": "/srv/www/commons/current/web/app/uploads/humcore/o_1acmi0cu8sf62q1m9jhmp154q7.pdf.the-new-open-access-environment-innovation-in-research-editing-publishing.pdf",
        "hclegacy:file_pid": "mla:584",
        "hclegacy:groups_for_deposit": [
            {
                "group_identifier": "69",
                "group_name": "HEP Part-Time and Contingent Faculty Issues",
            },
            {
                "group_identifier": "47",
                "group_name": "HEP Teaching as a Profession",
            },
            {"group_identifier": "51", "group_name": "TC Digital Humanities"},
            {
                "group_identifier": "66",
                "group_name": "TM Bibliography and Scholarly Editing",
            },
            {
                "group_identifier": "71",
                "group_name": "TM Libraries and Research",
            },
        ],
        "hclegacy:publication_type": "proceedings-article",
        "hclegacy:previously_published": "published",
        "hclegacy:record_change_date": "2017-11-21T19:18:37Z",
        "hclegacy:record_creation_date": "2016-02-29T13:11:39Z",
        "hclegacy:submitter_affiliation": "U of London, Birkbeck C",
        "hclegacy:submitter_id": "3365",
        "hclegacy:submitter_org_memberships": ["hc", "mla"],
        "imprint:imprint": {
            "title": (
                "The New Open Access "
                "Environment: Innovation in "
                "Research, Editing and "
                "Publishing"
            )
        },
        "kcr:commons_domain": "mla.hcommons.org",
        "kcr:meeting_organization": "Modern Languages Association",
        "kcr:submitter_email": "caroline.edwards@bbk.ac.uk",
        "kcr:submitter_username": "cai247",
        "kcr:user_defined_tags": [
            "digital humanities",
            "editing",
            "open access",
            "scholarly communication",
            "the profession",
            "Academe",
            "Public humanities",
            "Scholarly communication",
        ],
        "meeting:meeting": {
            "dates": "10 January 2016",
            "place": "Marriott Hotel, Austin, Texas",
            "title": (
                "131st Annual Convention of the Modern Languages Association"
            ),
        },
    },
    "files": {
        "default_preview": "the-new-open-access-environment-innovation-in-research-editing-publishing.pdf",
        "enabled": True,
        "entries": {
            "the-new-open-access-environment-innovation-in-research-editing-publishing.pdf": {
                "key": "the-new-open-access-environment-innovation-in-research-editing-publishing.pdf",
                "mimetype": "application/pdf",
                "size": "4004498",
            }
        },
    },
    "metadata": {
        "additional_descriptions": [
            {
                "description": (
                    "This panel was designed to address the "
                    "convention's featured issues of the academic "
                    "profession, publishing &amp; editing, open "
                    "access, and new technologies. Using a roundtable "
                    "format, the panel discussed how open access "
                    "publications are transforming the kind of research "
                    "that is possible and necessitating new editorial "
                    "practices. The session hosted an informed "
                    "discussion with the audience about the current "
                    "changes in scholarly publishing and the "
                    "opportunities, as well as challenges, that "
                    "open access brings to literary scholarship in the "
                    "21st century."
                ),
                "type": {"id": "other", "title": {"en": "Other"}},
            }
        ],
        "creators": [
            {
                "person_or_org": {
                    "family_name": "Eaglestone",
                    "given_name": "Robert",
                    "identifiers": [
                        {
                            "identifier": "roberteaglestone",
                            "scheme": "hc_username",
                        }
                    ],
                    "name": "Eaglestone, Robert",
                    "type": "personal",
                },
                "role": {"id": "author", "title": {"en": "Author"}},
            },
            {
                "affiliations": [{"name": "U of London, Birkbeck C"}],
                "person_or_org": {
                    "family_name": "Edwards",
                    "given_name": "Caroline",
                    "identifiers": [
                        {"identifier": "cai247", "scheme": "hc_username"}
                    ],
                    "name": "Edwards, Caroline",
                    "type": "personal",
                },
                "role": {"id": "author", "title": {"en": "Author"}},
            },
            {
                "person_or_org": {
                    "family_name": "Gundry",
                    "given_name": "Jenifer",
                    "name": "Gundry, Jenifer",
                    "type": "personal",
                },
                "role": {"id": "author", "title": {"en": "Author"}},
            },
            {
                "person_or_org": {
                    "family_name": "Mueller",
                    "given_name": "Alex",
                    "identifiers": [
                        {"identifier": "alexmueller", "scheme": "hc_username"}
                    ],
                    "name": "Mueller, Alex",
                    "type": "personal",
                },
                "role": {"id": "author", "title": {"en": "Author"}},
            },
            {
                "person_or_org": {
                    "family_name": "Zellinger",
                    "given_name": "Elissa",
                    "identifiers": [
                        {"identifier": "ezell", "scheme": "hc_username"}
                    ],
                    "name": "Zellinger, Elissa",
                    "type": "personal",
                },
                "role": {"id": "author", "title": {"en": "Author"}},
            },
        ],
        "description": (
            "This panel was designed to address the "
            "convention's featured issues of the academic "
            "profession, publishing &amp; editing, open "
            "access, and new technologies. Using a "
            "roundtable format, the panel discussed how open "
            "access publications are transforming the kind "
            "of research that is possible and necessitating "
            "new editorial practices. The session hosted an "
            "informed discussion with the audience about the "
            "current changes in scholarly publishing and the "
            "opportunities, as well as challenges, that open "
            "access brings to literary scholarship in the "
            "21st century."
        ),
        "identifiers": [
            {"identifier": "mla:583", "scheme": "hclegacy-pid"},
            {"identifier": "10664", "scheme": "hclegacy-record-id"},
            {"identifier": "10.17613/M6930Z", "scheme": "datacite-doi"},
            {"identifier": "https://doi.org/10.17613/M6930Z", "scheme": "url"},
        ],
        "languages": [{"id": "eng", "title": {"en": "English"}}],
        "publication_date": "2016",
        "resource_type": {"id": "presentation-other"},
        "rights": [
            {
                "description": {
                    "en": (
                        "Proprietary material. No permissions are "
                        "granted for any kind of copyring or "
                        "re-use. All rights reserved"
                    )
                },
                "id": "arr",
                "icon": "copyright",
                "props": {
                    "url": "https://en.wikipedia.org/wiki/All_rights_reserved"
                },
                "title": {"en": "All Rights Reserved"},
            }
        ],
        "subjects": [
            {
                "id": "http://id.worldcat.org/fast/903005",
                "subject": "Education, Higher",
                "scheme": "FAST-topical",
            },
            {
                "id": "http://id.worldcat.org/fast/963599",
                "subject": "Digital humanities",
                "scheme": "FAST-topical",
            },
            {
                "id": "http://id.worldcat.org/fast/911989",
                "subject": "English literature",
                "scheme": "FAST-topical",
            },
        ],
        "publisher": "Open Library of Humanities",
        "title": (
            "The New Open Access Environment: Innovation in "
            "Research, Editing and Publishing"
        ),
    },
    "parent": {"access": {"owned_by": [{"user": "3365"}]}},
    "pids": {
        "doi": {
            "client": "datacite",
            "identifier": "10.17613/M6930Z",
            "provider": "datacite",
        }
    },
    "updated": "2017-11-21T19:18:37Z",
}

json38367 = {
    "created": "2021-04-26T05:57:56Z",
    "custom_fields": {
        "hclegacy:collection": "hccollection:1",
        "hclegacy:file_location": (
            "/srv/www/commons/current/web/app/uploads/"
            "humcore/2021/04/o_1f46c249h11hjav61sv"
            "d1l318047.pdf.system-dynamics-growt"
            "h-distribution-and-financialization.pdf"
        ),
        "hclegacy:file_pid": "hc:38368",
        "hclegacy:groups_for_deposit": [
            {
                "group_identifier": "1002960",
                "group_name": "Literature and Economics",
            }
        ],
        "hclegacy:previously_published": "published",
        "hclegacy:publication_type": "online-publication",
        "hclegacy:record_change_date": "2021-04-27T16:36:31Z",
        "hclegacy:record_creation_date": "2021-04-26T05:57:56Z",
        "hclegacy:submitter_affiliation": "Université Sorbonne Paris Nord",
        "hclegacy:submitter_id": "1028135",
        "hclegacy:submitter_org_memberships": ["hc"],
        "imprint:imprint": {
            "title": "https://tesiunam.dgb.unam.mx/F/KVS7IYBX26S3PMEDX1SXFF6XRKP48FV5JRD21J7UNV85V8U82E-42627?func=full-set-set&set_number=198105&set_entry=000001&format=999"
        },
        "kcr:commons_domain": "hcommons.org",
        "kcr:sponsoring_institution": (
            "Universidad Nacional Autónoma de México (UNAM)"
        ),
        "kcr:submitter_email": "eduardoalo1234@gmail.com",
        "kcr:submitter_username": "gabogabito123",
        "kcr:user_defined_tags": [
            "Computer Simulation",
            "financialization",
            "macroeconomics",
            "modelling",
        ],
    },
    "files": {
        "default_preview": (
            "system-dynamics-growth-distribution-and-financialization.pdf"
        ),
        "enabled": True,
        "entries": {
            "system-dynamics-growth-distribution-and-financialization.pdf": {
                "key": (
                    "system-dynamics-growth-distribution-and-financ"
                    "ialization.pdf"
                ),
                "mimetype": "application/pdf",
                "size": "2185244",
            }
        },
    },
    "metadata": {
        "additional_descriptions": [
            {
                "description": (
                    "These models are a representation of "
                    "the macroeconomic evolution of the "
                    "US economy from 1970 to 2010. The main variables "
                    "addressed are economic growth, income "
                    "distribution and private debt. The "
                    "theoretical basis of the model "
                    "relies on what Bhaduri labeled as "
                    'the "Marx-Keynes-Kalecki" '
                    "tradition that has four distinctive "
                    "assumptions: 1) The price of this "
                    "one-commidty model is determined by a "
                    "mark-up over the production costs. "
                    "2) Aggregate demand determines "
                    "(AD) the level of production (Y). 3) "
                    "Investment (I) is the key variable "
                    "within aggregate demand. 4) The "
                    "level of aggregate supply (Yt) is "
                    "equal to aggregate demand (ADt). "
                    "There are other features of the "
                    "model that are also worth to "
                    "pinpoint. The baseline model has "
                    "three sectors: workers, "
                    "industrial capital and private "
                    "banking. The first two sectors are "
                    "clearly differentiated by "
                    "the marginal propensities of "
                    "their members to consume and their "
                    "access to credit. Workers have a "
                    "marginal propensity to "
                    "consume that goes from 0.5 to 1.3. "
                    "The propensity of consumption of "
                    "this sector varies with respect to "
                    'two macro-level "shaping '
                    'structures" that determine this '
                    "sector's microeconomic "
                    "behavior. Workers' propensity to "
                    "consume varies non-linearly "
                    "regarding inflation, and it "
                    "exhibits a positive and "
                    "linear relationship with "
                    "respect to the industrial "
                    "capital's share on total income. On "
                    "the other hand, capitalists can "
                    "save or become indebted depending "
                    "on the saving-investment gap. Any investment "
                    "decision over savings is always financed by the "
                    "acquisition of private debt "
                    "provided by private banks, and "
                    "the excess of savings is used to "
                    "pay the debt contracted by the "
                    "capitalists. Whilst the "
                    "activity of private banking is "
                    "limited only to the granting of "
                    "credit, the accumulation of "
                    "private debt represents its "
                    "source of profits. A subsidiary "
                    "assumption that is maintained "
                    "throughout this model is that it "
                    "is a closed economy without "
                    "government."
                ),
                "type": {"id": "other", "title": {"en": "Other"}},
            }
        ],
        "creators": [
            {
                "affiliations": [{"name": "Université Sorbonne Paris Nord"}],
                "person_or_org": {
                    "family_name": "Martínez Hernández",
                    "given_name": "Alberto-Gabino",
                    "identifiers": [
                        {
                            "identifier": "gabogabito123",
                            "scheme": "hc_username",
                        }
                    ],
                    "name": "Martínez Hernández, Alberto-Gabino",
                    "type": "personal",
                },
                "role": {"id": "author", "title": {"en": "Author"}},
            }
        ],
        "description": (
            "These models are a representation of the "
            "macroeconomic evolution of the US economy from "
            "1970 to 2010. The main variables addressed are "
            "economic growth, income distribution and "
            "private debt. The theoretical basis of the "
            "model relies on what Bhaduri labeled as the "
            '"Marx-Keynes-Kalecki" tradition that has four '
            "distinctive assumptions: \n"
            "\n"
            "1) The price of this one-commidty model is "
            "determined by a mark-up over the production "
            "costs. \n"
            "2) Aggregate demand determines (AD) the level "
            "of production (Y).\n"
            "3) Investment (I) is the key variable within "
            "aggregate demand. \n"
            "4) The level of aggregate supply (Yt) is equal "
            "to aggregate demand (ADt). \n"
            "\n"
            "There are other features of the model that are "
            "also worth to pinpoint. The baseline model has "
            "three sectors: workers, industrial capital and "
            "private banking. The first two sectors are "
            "clearly differentiated by the marginal "
            "propensities of their members to consume and "
            "their access to credit. Workers have a marginal "
            "propensity to consume that goes from 0.5 to "
            "1.3. The propensity of consumption of this "
            "sector varies with respect to two macro-level "
            '"shaping structures" that determine this '
            "sector's microeconomic behavior. Workers' "
            "propensity to consume varies non-linearly "
            "regarding inflation, and it exhibits a positive "
            "and linear relationship with respect to the "
            "industrial capital's share on total income. On "
            "the other hand, capitalists can save or become "
            "indebted depending on the saving-investment "
            "gap. Any investment decision over savings is "
            "always financed by the acquisition of private "
            "debt provided by private banks, and the excess "
            "of savings is used to pay the debt contracted "
            "by the capitalists. Whilst the activity of "
            "private banking is limited only to the granting "
            "of credit, the accumulation of private debt "
            "represents its source of profits. A subsidiary "
            "assumption that is maintained throughout this "
            "model is that it is a closed economy without "
            "government."
        ),
        "identifiers": [
            {"identifier": "hc:38367", "scheme": "hclegacy-pid"},
            {"identifier": "1000360-44555", "scheme": "hclegacy-record-id"},
            {"identifier": "10.17613/5ehz-cb19", "scheme": "datacite-doi"},
            {
                "identifier": (
                    "http://132.248.9.195/ptd2018/mayo/0774053/Index.html"
                ),
                "scheme": "url",
            },
        ],
        "languages": [{"id": "spa", "title": {"en": "Spanish"}}],
        "publication_date": "2018",
        "resource_type": {"id": "textDocument-thesis"},
        "rights": [
            {
                "description": {
                    "en": (
                        "Proprietary material. No permissions are "
                        "granted for any kind of copyring or "
                        "re-use. All rights reserved"
                    )
                },
                "id": "arr",
                "icon": "copyright",
                "props": {
                    "url": "https://en.wikipedia.org/wiki/All_rights_reserved"
                },
                "title": {"en": "All Rights Reserved"},
            }
        ],
        "subjects": [
            {
                "id": "http://id.worldcat.org/fast/902116",
                "subject": "Economics",
                "scheme": "FAST-topical",
            },
            {
                "id": "http://id.worldcat.org/fast/958235",
                "subject": "History",
                "scheme": "FAST-topical",
            },
            {
                "id": "http://id.worldcat.org/fast/1012163",
                "subject": "Mathematics",
                "scheme": "FAST-topical",
            },
        ],
        "publisher": "Universidad Nacional Autónoma de Mexico (UNAM)",
        "title": (
            "The macroeconomic evolution of the USA, 1970 - 2010. "
            "A heterodox mathematical modelling approach with "
            "System Dynamics."
        ),
    },
    "parent": {"access": {"owned_by": [{"user": "1028135"}]}},
    "pids": {
        "doi": {
            "client": "datacite",
            "identifier": "10.17613/5ehz-cb19",
            "provider": "datacite",
        }
    },
    "updated": "2021-04-27T16:36:31Z",
}

json48799 = {
    "created": "2022-09-29T14:34:36Z",
    "custom_fields": {
        "hclegacy:collection": "hccollection:1",
        "hclegacy:file_location": (
            "/srv/www/commons/current/web/app/uploads/"
            "humcore/2022/09/o_1ge4qi6ga1aqnfqk12h"
            "h1sei18377.pdf.super-apps_final.pdf"
        ),
        "hclegacy:file_pid": "hc:48800",
        "hclegacy:previously_published": "published",
        "hclegacy:publication_type": "online-publication",
        "hclegacy:record_change_date": "2022-09-29T14:34:36Z",
        "hclegacy:record_creation_date": "2022-09-29T14:34:36Z",
        "hclegacy:submitter_affiliation": "Concordia University",
        "hclegacy:submitter_id": "1011375",
        "hclegacy:submitter_org_memberships": ["hc"],
        "imprint:imprint": {"title": "theplatformlab.com"},
        "kcr:commons_domain": "hcommons.org",
        "kcr:sponsoring_institution": "The Platform Lab",
        "kcr:submitter_email": "jacqueline.ristola@mail.concordia.ca",
        "kcr:user_defined_tags": ["platform studies"],
        "kcr:submitter_username": "jristola009",
    },
    "files": {
        "default_preview": "super-apps_final.pdf",
        "enabled": True,
        "entries": {
            "super-apps_final.pdf": {
                "key": "super-apps_final.pdf",
                "mimetype": "application/pdf",
                "size": "1523200",
            }
        },
    },
    "metadata": {
        "description": (
            "This whitepaper report gives an overview of a "
            'variety of "superapps," apps designed to bring '
            "together a vast number of services within a "
            "single interface. The purpose of this "
            "report is to provide a general "
            "understanding of the super app form "
            "as it becomes a dominant global "
            "framework, and to consider platform "
            "capitalism's transformational shape."
        ),
        "contributors": [
            {
                "person_or_org": {
                    "family_name": "Altheman",
                    "given_name": "Elena",
                    "name": "Altheman, Elena",
                    "type": "personal",
                },
                "role": {"id": "other", "title": {"en": "Other"}},
            },
            {
                "person_or_org": {
                    "family_name": "Chai",
                    "given_name": "Roslina",
                    "name": "Chai, Roslina",
                    "type": "personal",
                },
                "role": {"id": "other", "title": {"en": "Other"}},
            },
            {
                "person_or_org": {
                    "family_name": "Ciarma",
                    "given_name": "Santino",
                    "name": "Ciarma, Santino",
                    "type": "personal",
                },
                "role": {"id": "other", "title": {"en": "Other"}},
            },
            {
                "person_or_org": {
                    "family_name": "Crawford",
                    "given_name": "Colin",
                    "name": "Crawford, Colin",
                    "type": "personal",
                },
                "role": {"id": "other", "title": {"en": "Other"}},
            },
            {
                "person_or_org": {
                    "family_name": "Kumar",
                    "given_name": "Sneha",
                    "name": "Kumar, Sneha",
                    "type": "personal",
                },
                "role": {"id": "other", "title": {"en": "Other"}},
            },
            {
                "person_or_org": {
                    "family_name": "Petit",
                    "given_name": "Aurélie",
                    "name": "Petit, Aurélie",
                    "type": "personal",
                },
                "role": {"id": "other", "title": {"en": "Other"}},
            },
            {
                "affiliations": [{"name": "Concordia University"}],
                "person_or_org": {
                    "family_name": "Ristola",
                    "given_name": "Jacqueline",
                    "identifiers": [
                        {"identifier": "jristola009", "scheme": "hc_username"}
                    ],
                    "name": "Ristola, Jacqueline",
                    "type": "personal",
                },
                "role": {"id": "other", "title": {"en": "Other"}},
            },
            {
                "person_or_org": {
                    "family_name": "Steinberg",
                    "given_name": "Marc",
                    "name": "Steinberg, Marc",
                    "type": "personal",
                },
                "role": {"id": "other", "title": {"en": "Other"}},
            },
            {
                "person_or_org": {
                    "family_name": "Zhou",
                    "given_name": "Xin",
                    "name": "Zhou, Xin",
                    "type": "personal",
                },
                "role": {"id": "other", "title": {"en": "Other"}},
            },
        ],
        "creators": [
            {
                "person_or_org": {
                    "family_name": "Pitre",
                    "given_name": "Jake",
                    "name": "Pitre, Jake",
                    "type": "personal",
                },
                "role": {"id": "editor", "title": {"en": "Editor"}},
            }
        ],
        "dates": [
            {
                "date": "2022",
                "description": "Human readable publication date",
                "type": {
                    "id": "issued",
                    "title": {"en": "Issued", "de": "Veröffentlicht"},
                },
            }
        ],
        "identifiers": [
            {"identifier": "hc:48799", "scheme": "hclegacy-pid"},
            {"identifier": "1000360-61936", "scheme": "hclegacy-record-id"},
            {"identifier": "10.17613/y30x-r594", "scheme": "datacite-doi"},
            {
                "identifier": "https://www.theplatformlab.com/super-apps",
                "scheme": "url",
            },
        ],
        "languages": [{"id": "eng", "title": {"en": "English"}}],
        "publication_date": "2022",
        "publisher": "The Platform Lab",
        "resource_type": {"id": "textDocument-whitePaper"},
        "rights": [
            {
                "description": {
                    "en": (
                        "The Creative Commons Attribution license "
                        "allows re-distribution and re-use of a "
                        "licensed work on the condition that the "
                        "creator is appropriately credited."
                    )
                },
                "id": "cc-by-4.0",
                "icon": "cc-by-icon",
                "props": {
                    "scheme": "spdx",
                    "url": (
                        "https://creativecommons.org/licenses/by/4.0/legalcode"
                    ),
                },
                "title": {
                    "en": "Creative Commons Attribution 4.0 International"
                },
            }
        ],
        "title": "Super Apps: A Platform Lab Report",
    },
    "parent": {"access": {"owned_by": [{"user": "1011375"}]}},
    "pids": {
        "doi": {
            "client": "datacite",
            "identifier": "10.17613/y30x-r594",
            "provider": "datacite",
        }
    },
    "updated": "2022-09-29T14:34:36Z",
}

json33383 = {
    "access": {
        "embargo": {"active": True, "reason": None, "until": "2021-11-25"}
    },
    "created": "2020-11-25T12:35:10Z",
    "custom_fields": {
        "hclegacy:collection": "hccollection:1",
        "hclegacy:file_location": (
            "/srv/www/commons/current/web/app/uploads/"
            "humcore/2020/11/o_1envm12vp11cmvs61ic"
            "r7g3oqk7.pdf.24519197_005_03-04_s004_text."
            "pdf"
        ),
        "hclegacy:file_pid": "hc:33384",
        "hclegacy:groups_for_deposit": [
            {
                "group_identifier": "1004129",
                "group_name": "Arabic script manuscripts",
            },
            {
                "group_identifier": "1001234",
                "group_name": "Islamicate Studies",
            },
            {"group_identifier": "1000753", "group_name": "Medieval Studies"},
            {
                "group_identifier": "1000830",
                "group_name": "Science Studies and the History of Science",
            },
        ],
        "hclegacy:previously_published": "published",
        "hclegacy:record_change_date": "2023-01-23T14:20:48Z",
        "hclegacy:record_creation_date": "2020-11-25T12:35:10Z",
        "hclegacy:submitter_affiliation": "University of Southern California",
        "hclegacy:submitter_id": "1008812",
        "hclegacy:submitter_org_memberships": ["hc"],
        "journal:journal": {
            "title": "Philological Encounters",
            "issue": "3",
            "pages": "308-352",
            "issn": "2451-9189",
            "volume": "5",
        },
        "kcr:commons_domain": "hcommons.org",
        "kcr:submitter_email": "alexandre.roberts@gmail.com",
        "kcr:submitter_username": "amroberts",
        "kcr:user_defined_tags": [
            "History of science",
            "History and philosophy of mathematics",
        ],
    },
    "files": {
        "default_preview": "24519197_005_03-04_s004_text.pdf",
        "enabled": True,
        "entries": {
            "24519197_005_03-04_s004_text.pdf": {
                "key": "24519197_005_03-04_s004_text.pdf",
                "mimetype": "application/pdf",
                "size": "1278745",
            }
        },
    },
    "metadata": {
        # 'additional_descriptions': [
        #     {'description': 'This article examines an Arabic mathematical '
        #                     'manuscript at Columbia University’s Rare '
        #                     'Book and Manuscript Library (or. 45), focusing '
        #                     'on a previously unpublished set of texts: the '
        #                     'treatise on the mathematical method known as '
        #                     'Double False Position, as supplemented by '
        #                     'Jābir ibn Ibrāhīm al-Ṣābī (tenth century?), and the '
        #                     'commentaries by Aḥmad ibn al-Sarī (d. 548/1153–4) '
        #                     'and Saʿd al-Dīn Asʿad ibn Saʿīd al-Hamadhānī '
        #                     '(12th/13th century?), the latter previously '
        #                     'unnoticed. The article sketches the contents of '
        #                     'the manuscript, then offers an editio princeps, '
        #                     'translation, and analysis of the treatise. It then '
        #                     'considers how the Swiss historian of mathematics '
        #                     'Heinrich Suter (1848–1922) read Jābir’s treatise '
        #                     '(as contained in a different manuscript) before '
        #                     'concluding with my own proposal for how to go about '
        #                     'reading this mathematical text: as a witness of '
        #                     'multiple stages of a complex textual tradition of '
        #                     'teaching, extending, and rethinking '
        #                     'mathematics—that is, we should read it philologically.',
        #      'type': {'id': 'other',
        #               'title': {'en': 'Other'}
        #               }
        #      }
        # ],
        "creators": [
            {
                "affiliations": [
                    {"name": "University of Southern California"}
                ],
                "person_or_org": {
                    "family_name": "Roberts",
                    "given_name": "Alexandre",
                    "identifiers": [
                        {"identifier": "amroberts", "scheme": "hc_username"}
                    ],
                    "name": "Roberts, Alexandre",
                    "type": "personal",
                },
                "role": {"id": "author", "title": {"en": "Author"}},
            }
        ],
        "dates": [
            {
                "date": "2020-10-13",
                "description": "Human readable publication date",
                "type": {
                    "id": "issued",
                    "title": {"en": "Issued", "de": "Veröffentlicht"},
                },
            }
        ],
        "description": (
            "This article examines an Arabic mathematical "
            "manuscript at Columbia University’s Rare Book "
            "and Manuscript Library (or. 45), focusing on a "
            "previously unpublished set of texts: the "
            "treatise on the mathematical method known as "
            "Double False Position, as supplemented by Jābir "
            "ibn Ibrāhīm al-Ṣābī (tenth century?), and the "
            "commentaries by Aḥmad ibn al-Sarī (d. "
            "548/1153–4) and Saʿd al-Dīn Asʿad ibn Saʿīd "
            "al-Hamadhānī (12th/13th century?), the latter "
            "previously unnoticed. The article sketches the "
            "contents of the manuscript, then offers an "
            "editio princeps, translation, and analysis of "
            "the treatise. It then considers how the Swiss "
            "historian of mathematics Heinrich Suter "
            "(1848–1922) read Jābir’s treatise (as contained "
            "in a different manuscript) before concluding "
            "with my own proposal for how to go about "
            "reading this mathematical text: as a witness of "
            "multiple stages of a complex textual tradition "
            "of teaching, extending, and rethinking "
            "mathematics—that is, we should read it "
            "philologically."
        ),
        "identifiers": [
            {"identifier": "hc:33383", "scheme": "hclegacy-pid"},
            {"identifier": "1000360-40298", "scheme": "hclegacy-record-id"},
            {"identifier": "10.17613/xxxj-e936", "scheme": "datacite-doi"},
            {"identifier": "10.1163/24519197-BJA10007", "scheme": "doi"},
            {
                "identifier": "https://doi.org/10.17613/xxxj-e936",
                "scheme": "url",
            },
            {"identifier": "2451-9197", "scheme": "issn"},
        ],
        "languages": [{"id": "eng", "title": {"en": "English"}}],
        "publication_date": "2020",
        "resource_type": {"id": "textDocument-journalArticle"},
        "rights": [
            {
                "description": {
                    "en": (
                        "Proprietary material. No permissions are "
                        "granted for any kind of copyring or "
                        "re-use. All rights reserved"
                    )
                },
                "id": "arr",
                "icon": "copyright",
                "props": {
                    "url": "https://en.wikipedia.org/wiki/All_rights_reserved"
                },
                "title": {"en": "All Rights Reserved"},
            }
        ],
        "subjects": [
            {
                "id": "http://id.worldcat.org/fast/1108176",
                "subject": "Science",
                "scheme": "FAST-topical",
            },
            {
                "id": "http://id.worldcat.org/fast/958235",
                "subject": "History",
                "scheme": "FAST-topical",
            },
            {
                "id": "http://id.worldcat.org/fast/1012213",
                "subject": "Mathematics--Philosophy",
                "scheme": "FAST-topical",
            },
            {
                "id": "http://id.worldcat.org/fast/1012163",
                "subject": "Mathematics",
                "scheme": "FAST-topical",
            },
        ],
        "publisher": "Brill",
        "title": (
            "Mathematical Philology in the Treatise on Double "
            "False Position in an Arabic Manuscript at Columbia "
            "University"
        ),
    },
    "parent": {"access": {"owned_by": [{"user": "1008812"}]}},
    "pids": {
        "doi": {
            "client": "datacite",
            "identifier": "10.17613/xxxj-e936",
            "provider": "datacite",
        }
    },
    "updated": "2023-01-23T14:20:48Z",
}

json16079 = {
    "created": "2017-10-26T12:31:39Z",
    "pids": {
        "doi": {
            "client": "datacite",
            "identifier": "10.17613/M6M225",
            "provider": "datacite",
        }
    },
    "custom_fields": {
        "hclegacy:collection": "hccollection:1",
        "hclegacy:file_location": (
            "/srv/www/commons/current/web/app/uploads/"
            "humcore/2017/10/o_1btcal4jbimf52817p91"
            "1ojlp57.pdf.dhbenelux-digitization"
            "-and-exogenesis.pdf"
        ),
        "hclegacy:file_pid": "hc:16080",
        "hclegacy:groups_for_deposit": [
            {"group_identifier": "1000551", "group_name": "Digital Humanists"},
            {
                "group_identifier": "1000697",
                "group_name": "Textual Scholarship",
            },
        ],
        "hclegacy:previously_published": "published",
        "hclegacy:submitter_org_memberships": ["hc"],
        "hclegacy:record_change_date": "2017-10-27T14:27:17Z",
        "hclegacy:record_creation_date": "2017-10-26T12:31:39Z",
        "hclegacy:submitter_id": "1010997",
        "imprint:imprint": {
            "pages": "28-29",
            "title": (
                "DHBenelux 2. Book of "
                "Abstracts for the Second "
                "Digital Humanities Benelux "
                "Conference"
            ),
        },
        "kcr:commons_domain": "hcommons.org",
        "kcr:meeting_organization": "University of Antwerp",
        "kcr:submitter_email": "wout.dillen@uantwerpen.be",
        "kcr:submitter_username": "woutdillen",
        "kcr:user_defined_tags": ["20th century", "Textual criticism"],
        "meeting:meeting": {
            "dates": "8-9 June 2015",
            "place": "Antwerp, Belgium",
            "title": "DH Benelux 2015",
        },
    },
    "files": {
        "default_preview": "dhbenelux-digitization-and-exogenesis.pdf",
        "enabled": True,
        "entries": {
            "dhbenelux-digitization-and-exogenesis.pdf": {
                "key": "dhbenelux-digitization-and-exogenesis.pdf",
                "mimetype": "application/pdf",
                "size": "205462",
            }
        },
    },
    "metadata": {
        # 'additional_descriptions': [
        #     {'description': 'Within the field of genetic criticism, '
        #                     'Raymonde Debray Genette coined the terms ‘en- '
        #                     'dogenesis’ and ‘exogenesis’ to denote '
        #                     'respectively the writing of drafts and the '
        #                     'interaction with external source texts during the '
        #                     'writing process. The proposed panel focuses on the '
        #                     'ways in which exogenesis and its relationship with '
        #                     'endogenesis can be given shape in a digital '
        #                     'infrastructure. The case studies are the works, '
        #                     'reading notes and personal libraries '
        #                     'of James Joyce and Samuel Beckett.',
        #      'type': {'id': 'other',
        #               'title': {'en': 'Other'}
        #               }
        #     }
        # ],
        "creators": [
            {
                "person_or_org": {
                    "family_name": "Crowley",
                    "given_name": "Ronan",
                    "name": "Crowley, Ronan",
                    "type": "personal",
                },
                "role": {"id": "author", "title": {"en": "Author"}},
            },
            {
                "person_or_org": {
                    "family_name": "De Keyser",
                    "given_name": "Tom",
                    "name": "De Keyser, Tom",
                    "type": "personal",
                },
                "role": {"id": "author", "title": {"en": "Author"}},
            },
            {
                "person_or_org": {
                    "family_name": "Dillen",
                    "given_name": "Wout",
                    "identifiers": [
                        {"identifier": "woutdillen", "scheme": "hc_username"}
                    ],
                    "name": "Dillen, Wout",
                    "type": "personal",
                },
                "role": {"id": "author", "title": {"en": "Author"}},
            },
            {
                "person_or_org": {
                    "family_name": "Neyt",
                    "given_name": "Vincent",
                    "name": "Neyt, Vincent",
                    "type": "personal",
                },
                "role": {"id": "author", "title": {"en": "Author"}},
            },
            {
                "person_or_org": {
                    "family_name": "Van Hulle",
                    "given_name": "Dirk",
                    "name": "Van Hulle, Dirk",
                    "type": "personal",
                },
                "role": {"id": "author", "title": {"en": "Author"}},
            },
        ],
        "description": (
            "Within the field of genetic criticism, Raymonde "
            "Debray Genette coined the terms ‘en- dogenesis’ "
            "and ‘exogenesis’ to denote respectively the "
            "writing of drafts and the interaction with "
            "external source texts during the writing "
            "process. The proposed panel focuses on the ways "
            "in which exogenesis and its relationship with "
            "endogenesis can be given shape in a digital "
            "infrastructure. The case studies are the works, "
            "reading notes and personal libraries of James "
            "Joyce and Samuel Beckett."
        ),
        "identifiers": [
            {"identifier": "hc:16079", "scheme": "hclegacy-pid"},
            {"identifier": "1000360-8725", "scheme": "hclegacy-record-id"},
            {"identifier": "10.17613/M6M225", "scheme": "datacite-doi"},
            {"identifier": "10.5281/zenodo.1009526", "scheme": "doi"},
            {"identifier": "https://doi.org/10.17613/M6M225", "scheme": "url"},
        ],
        "languages": [{"id": "eng", "title": {"en": "English"}}],
        "publisher": "unknown",
        "resource_type": {"id": "textDocument-conferenceProceeding"},
        "rights": [
            {
                "description": {
                    "en": (
                        "The Creative Commons Attribution license "
                        "allows re-distribution and re-use of a "
                        "licensed work on the condition that the "
                        "creator is appropriately credited."
                    )
                },
                "id": "cc-by-4.0",
                "icon": "cc-by-icon",
                "props": {
                    "scheme": "spdx",
                    "url": (
                        "https://creativecommons.org/licenses/by/4.0/legalcode"
                    ),
                },
                "title": {
                    "en": "Creative Commons Attribution 4.0 International"
                },
            }
        ],
        "subjects": [
            {
                "id": "http://id.worldcat.org/fast/1159810",
                "subject": "Twentieth century",
                "scheme": "FAST-topical",
            },
            {
                "id": "http://id.worldcat.org/fast/963599",
                "subject": "Digital humanities",
                "scheme": "FAST-topical",
            },
            {
                "id": "http://id.worldcat.org/fast/979030",
                "subject": "Irish literature",
                "scheme": "FAST-topical",
            },
            {
                "id": "http://id.worldcat.org/fast/883762",
                "subject": "Criticism, Textual",
                "scheme": "FAST-topical",
            },
        ],
        "publication_date": "2015",
        "dates": [
            {
                "date": "2015-06-01",  # '8 June 2015',
                "description": "Human readable publication date",
                "type": {
                    "id": "issued",
                    "title": {"en": "Issued", "de": "Veröffentlicht"},
                },
            }
        ],
        "title": "Digitization and Exogenesis",
    },
    "parent": {"access": {"owned_by": [{"user": "1010997"}]}},
    "updated": "2017-10-27T14:27:17Z",
}

json34031 = {
    "created": "2021-01-11T23:48:41Z",
    "pids": {
        "doi": {
            "client": "datacite",
            "identifier": "10.17613/0qxh-ed23",
            "provider": "datacite",
        }
    },
    "custom_fields": {
        "hclegacy:collection": "hccollection:1",
        "hclegacy:file_location": (
            "/srv/www/commons/current/web/app/uploads/"
            "humcore/2021/01/o_1erptio851p4e9e41ep"
            "f1p4o15eq7.pdf.gnosticism-theorized-"
            "major-trends-and-approaches-dillon.pdf"
        ),
        "hclegacy:file_pid": "hc:34032",
        "hclegacy:previously_published": "published",
        "hclegacy:record_change_date": "2021-01-11T23:48:41Z",
        "hclegacy:record_creation_date": "2021-01-11T23:48:41Z",
        "hclegacy:submitter_affiliation": "Rice University",
        "hclegacy:submitter_id": "1025015",
        "hclegacy:submitter_org_memberships": ["hc"],
        "imprint:imprint": {
            "pages": "23-38",
            "isbn": "9780028663500",
            "title": "Secret Religion:",
        },
        "kcr:commons_domain": "hcommons.org",
        "kcr:submitter_email": "mjdillon@alumni.rice.edu",
        "kcr:submitter_username": "matthewjdillon",
        "kcr:user_defined_tags": ["Western esotericism", "Early Christianity"],
    },
    "files": {
        "default_preview": (
            "gnosticism-theorized-major-trends-and-approaches-dillon.pdf"
        ),
        "enabled": True,
        "entries": {
            "gnosticism-theorized-major-trends-and-approaches-dillon.pdf": {
                "key": (
                    "gnosticism-theorized-major-trends-and-approaches-"
                    "dillon.pdf"
                ),
                "mimetype": "application/pdf",
                "size": "322864",
            }
        },
    },
    "metadata": {
        # 'additional_descriptions': [
        #     {'description': 'Overview of the major trends and approaches to '
        #                     "the study of 'Gnosticism' after the discovery of "
        #                     'the Nag Hammadi Codices.',
        #      'type': {'id': 'other',
        #               'title': {'en': 'Other'}
        #               }
        #      }
        # ],
        "publication_date": "2016",
        "publisher": "MacMillan Reference USA",
        "creators": [
            {
                "affiliations": [{"name": "Rice University"}],
                "person_or_org": {
                    "family_name": "Dillon",
                    "given_name": "M.",
                    "identifiers": [
                        {
                            "identifier": "matthewjdillon",
                            "scheme": "hc_username",
                        }
                    ],
                    "name": "Dillon, M.",
                    "type": "personal",
                },
                "role": {"id": "author", "title": {"en": "Author"}},
            }
        ],
        "contributors": [
            {
                "person_or_org": {
                    "family_name": "DeConick",
                    "given_name": "April",
                    "name": "DeConick, April",
                    "type": "personal",
                },
                "role": {"id": "other", "title": {"en": "Other"}},
            }
        ],
        "description": (
            "Overview of the major trends and approaches to "
            "the study of 'Gnosticism' after the discovery "
            "of the Nag Hammadi Codices."
        ),
        "identifiers": [
            {"identifier": "hc:34031", "scheme": "hclegacy-pid"},
            {"identifier": "1000360-41326", "scheme": "hclegacy-record-id"},
            {"identifier": "10.17613/0qxh-ed23", "scheme": "datacite-doi"},
            {
                "identifier": "https://doi.org/10.17613/0qxh-ed23",
                "scheme": "url",
            },
        ],
        "languages": [{"id": "eng", "title": {"en": "English"}}],
        "resource_type": {"id": "textDocument-bookSection"},
        "rights": [
            {
                "description": {
                    "en": (
                        "Proprietary material. No permissions are "
                        "granted for any kind of copyring or "
                        "re-use. All rights reserved"
                    )
                },
                "id": "arr",
                "icon": "copyright",
                "props": {
                    "url": "https://en.wikipedia.org/wiki/All_rights_reserved"
                },
                "title": {"en": "All Rights Reserved"},
            }
        ],
        "subjects": [
            {
                "id": "http://id.worldcat.org/fast/943906",
                "subject": "Gnosticism",
                "scheme": "FAST-topical",
            },
            {
                "id": "http://id.worldcat.org/fast/1043123",
                "subject": "Occultism",
                "scheme": "FAST-topical",
            },
            {
                "id": "http://id.worldcat.org/fast/1245064",
                "subject": "Europe",
                "scheme": "FAST-geographic",
            },
            {
                "id": "http://id.worldcat.org/fast/1710945",
                "subject": "Church history--Primitive and early church",
                "scheme": "FAST-topical",
            },
        ],
        "title": (
            "Gnosticism Theorized: Major Trends and Approaches to "
            "the Study of Gnosticism"
        ),
    },
    "parent": {"access": {"owned_by": [{"user": "1025015"}]}},
    "updated": "2021-01-11T23:48:41Z",
}


json11451 = {
    "created": "2017-03-08T05:01:44Z",
    "pids": {
        "doi": {
            "client": "datacite",
            "identifier": "10.17613/M6733G",
            "provider": "datacite",
        }
    },
    "custom_fields": {
        "hclegacy:collection": "hccollection:1",
        "hclegacy:file_location": (
            "/srv/www/commons/current/web/app/uploads/"
            "humcore/o_1bam4ggaprbg1t5b1jb9ck83hh7.pdf."
            "female_agency_ophelia.pdf"
        ),
        "hclegacy:file_pid": "hc:11452",
        "hclegacy:groups_for_deposit": [
            {
                "group_identifier": "174",
                "group_name": (
                    "East Asian Languages and Literatures after 1900"
                ),
            },
            {"group_identifier": "246", "group_name": "Global Shakespeares"},
            {
                "group_identifier": "97",
                "group_name": "GS Drama and Performance",
            },
            {"group_identifier": "25", "group_name": "LLC Shakespeare"},
            {"group_identifier": "91", "group_name": "TC Translation Studies"},
        ],
        "hclegacy:submitter_id": "49",
        "hclegacy:previously_published": "published",
        "hclegacy:record_change_date": "2017-09-16T16:41:52Z",
        "hclegacy:record_creation_date": "2017-03-08T05:01:44Z",
        "hclegacy:submitter_affiliation": "George Washington U",
        "hclegacy:submitter_org_memberships": ["hc", "mla"],
        "imprint:imprint": {
            "isbn": "978-1-349-29760-3",
            "pages": "79-100",
            "title": "The Afterlife of Ophelia",
        },
        "kcr:chapter_label": "5",
        "kcr:commons_domain": "mla.hcommons.org",
        "kcr:submitter_email": "ajoubin@gwu.edu",
        "kcr:submitter_username": "joubin",
        "kcr:user_defined_tags": [
            "Adaptation",
            "East Asian literatures",
            "Film history",
            "Gender studies",
            "Shakespeare",
        ],
    },
    "files": {
        "default_preview": "female_agency_ophelia.pdf",
        "enabled": True,
        "entries": {
            "female_agency_ophelia.pdf": {
                "key": "female_agency_ophelia.pdf",
                "mimetype": "application/pdf",
                "size": "48666405",
            }
        },
    },
    "metadata": {
        "additional_descriptions": [
            {
                "description": (
                    "There are three "
                    "main East Asian "
                    "approaches to "
                    "interpreting "
                    "Ophelia. The first "
                    "is informed by the "
                    "fascination with "
                    "and reaction "
                    "against the "
                    "Victorian "
                    "pictorialization "
                    "of Ophelia, "
                    "especially John "
                    "Everett Millais’s "
                    "famous Ophelia "
                    "(1851), that "
                    "emphasized, as "
                    "Kimberly Rhodes "
                    "describes, her "
                    "“pathos, "
                    "innocence, and "
                    "beauty rather than "
                    "the unseemly "
                    "detail of her "
                    "death.” Despite "
                    "having lived "
                    "through negative "
                    "experiences, "
                    "Ophelia retains a "
                    "childlike "
                    "innocence in these "
                    "rewritings. For "
                    "example, New "
                    "Hamlet by Lao She "
                    "(penname of Shu "
                    "Qingchun, "
                    "1899-1966) "
                    "parodies China’s "
                    "“Hamlet complex” "
                    "(the inability to "
                    "act at a time of "
                    "national crisis) "
                    "and the "
                    "fascination with "
                    "an Ophelia "
                    "submerged in "
                    "water. Both "
                    "Ophelia and "
                    "Millais’s painting "
                    "are featured in "
                    "two of Japanese "
                    "writer Natsume "
                    "Sōseki’s early "
                    "twentieth-century "
                    "novels. A second "
                    "approach "
                    "emphasizes the "
                    "local context. "
                    "Adapters used "
                    "local values to "
                    "engage with and "
                    "even critique the "
                    "Victorian "
                    "narrative "
                    "tradition of "
                    "moralization. Late "
                    "nineteenth-century "
                    "translator Lin Shu "
                    "(1852-1924), for "
                    "example, tones "
                    "down the "
                    "sentimentalization "
                    "of Ophelia in his "
                    "classical Chinese "
                    "rewriting of "
                    "Charles and Mary "
                    "Lamb’s Tales from "
                    "Shakespeare, "
                    "showcasing the "
                    "conflict between "
                    "Victorian and "
                    "Confucian moral "
                    "codes. The third "
                    "approach focuses "
                    "upon an "
                    "objectified and "
                    "sexualized "
                    "Ophelia. As other "
                    "chapters in this "
                    "volume "
                    "demonstrate, this "
                    "is not exclusively "
                    "an Asian "
                    "phenomenon. "
                    "However, the "
                    "eroticism "
                    "associated with "
                    "the Ophelia figure "
                    "in a number of "
                    "Asian stage and "
                    "screen versions of "
                    "Hamlet, such as "
                    "Sherwood Hu’s film "
                    "Prince of the "
                    "Himalayas (2006), "
                    "aligns Ophelia "
                    "with East Asian "
                    "ideals of "
                    "femininity, but "
                    "also brings out "
                    "the sexuality that "
                    "is latent or "
                    "suppressed in "
                    "Victorian "
                    "interpretations. "
                    "They do so by "
                    "aligning Ophelia "
                    "with East Asian "
                    "ideals of "
                    "femininity."
                ),
                "type": {"id": "other", "title": {"en": "Other"}},
            }
        ],
        "creators": [
            {
                "affiliations": [{"name": "George Washington U"}],
                "person_or_org": {
                    "family_name": "Alice Joubin",
                    "given_name": "Alexa",
                    "identifiers": [
                        {"identifier": "joubin", "scheme": "hc_username"}
                    ],
                    "name": "Alice Joubin, Alexa",
                    "type": "personal",
                },
                "role": {"id": "author", "title": {"en": "Author"}},
            }
        ],
        "contributors": [
            {
                "person_or_org": {
                    "family_name": "Peterson",
                    "given_name": "Kaara",
                    "name": "Peterson, Kaara",
                    "type": "personal",
                },
                "role": {"id": "other", "title": {"en": "Other"}},
            },
            {
                "person_or_org": {
                    "family_name": "Williams",
                    "given_name": "Deanne",
                    "name": "Williams, Deanne",
                    "type": "personal",
                },
                "role": {"id": "other", "title": {"en": "Other"}},
            },
        ],
        "publication_date": "2012",
        "description": (
            "There are three main East Asian approaches to "
            "interpreting Ophelia. The first is informed by "
            "the fascination with and reaction against the "
            "Victorian pictorialization of Ophelia, "
            "especially John Everett Millais’s famous "
            "Ophelia (1851), that emphasized, as Kimberly "
            "Rhodes describes, her “pathos, innocence, and "
            "beauty rather than the unseemly detail of her "
            "death.”  Despite having lived through negative "
            "experiences, Ophelia retains a childlike "
            "innocence in these rewritings. For example, New "
            "Hamlet by Lao She (penname of Shu Qingchun, "
            '1899-1966) parodies China’\'“"""mlet comple””"'
            "(the inability to act at a time of national "
            "crisis) and the fascination with an Ophelia "
            "submerged in water. Both Ophelia and Millais’s "
            "painting are featured in two of Japanese writer "
            "Natsume Sōseki’s early twentieth-century "
            "novels. A second approach emphasizes the local "
            "context. Adapters used local values to engage "
            "with and even critique the Victorian narrative "
            "tradition of moralization. Late "
            "nineteenth-century translator Lin Shu "
            "(1852-1924), for example, tones down the "
            "sentimentalization of Ophelia in his classical "
            "Chinese rewriting of Charles and Mary Lamb’s "
            "Tales from Shakespeare, showcasing the conflict "
            "between Victorian and Confucian moral codes. "
            "The third approach focuses upon an objectified "
            "and sexualized Ophelia. As other chapters in "
            "this volume demonstrate, this is not "
            "exclusively an Asian phenomenon. However, the "
            "eroticism associated with the Ophelia figure in "
            "a number of Asian stage and screen versions of "
            "Hamlet, such as Sherwood Hu’s film Prince of "
            "the Himalayas (2006), aligns Ophelia with East "
            "Asian ideals of femininity, but also brings out "
            "the sexuality that is latent or suppressed in "
            "Victorian interpretations. They do so by "
            "aligning Ophelia with East Asian ideals of "
            "femininity."
        ),
        "identifiers": [
            {"identifier": "hc:11451", "scheme": "hclegacy-pid"},
            {"identifier": "1-1013793", "scheme": "hclegacy-record-id"},
            {"identifier": "10.17613/M6733G", "scheme": "datacite-doi"},
            {"identifier": "10.1057/9781137016461", "scheme": "doi"},
            {"identifier": "https://doi.org/10.17613/M6733G", "scheme": "url"},
        ],
        "languages": [{"id": "eng", "title": {"en": "English"}}],
        "resource_type": {"id": "textDocument-bookSection"},
        "rights": [
            {
                "description": {"en": ""},
                "id": "cc-by-nc-4.0",
                "icon": "cc-by-nc-icon",
                "props": {
                    "scheme": "spdx",
                    "url": "https://creativecommons.org/licenses/by-nc/4.0/legalcode",
                },
                "title": {
                    "en": (
                        "Creative Commons Attribution Non "
                        "Commercial 4.0 International"
                    )
                },
            }
        ],
        "subjects": [
            {
                "id": "http://id.worldcat.org/fast/900999",
                "subject": "East Asian literature",
                "scheme": "FAST-topical",
            },
            {
                "id": "http://id.worldcat.org/fast/1027285",
                "subject": "Motion pictures",
                "scheme": "FAST-topical",
            },
            {
                "id": "http://id.worldcat.org/fast/958235",
                "subject": "History",
                "scheme": "FAST-topical",
            },
            {
                "id": "http://id.worldcat.org/fast/29048",
                "subject": "Shakespeare, William, 1564-1616",
                "scheme": "FAST-personal",
            },
        ],
        "publisher": "Palgrave",
        "title": (
            "The Paradox of Female Agency: Ophelia and East Asian "
            "Sensibilities"
        ),
    },
    "parent": {"access": {"owned_by": [{"user": "49"}]}},
    "updated": "2017-09-16T16:41:52Z",
}

json22647 = {
    "created": "2019-02-01T19:30:52Z",
    "pids": {
        "doi": {
            "client": "datacite",
            "identifier": "10.17613/1d2d-2y15",
            "provider": "datacite",
        }
    },
    "custom_fields": {
        "hclegacy:collection": "hccollection:1",
        "hclegacy:file_location": (
            "/srv/www/commons/current/web/app/uploads/"
            "humcore/2019/02/o_1d2l8l61vl7ouij402qpl35p7."
            "pdf.sh-unfixing-epic-2018.pdf"
        ),
        "hclegacy:file_pid": "hc:22648",
        "hclegacy:groups_for_deposit": [
            {
                "group_identifier": "1000636",
                "group_name": "Ancient Greece & Rome",
            },
            {
                "group_identifier": "1000816",
                "group_name": "Classical Tradition",
            },
            {
                "group_identifier": "1000630",
                "group_name": "Poetics and Poetry",
            },
        ],
        "hclegacy:previously_published": "published",
        "hclegacy:record_change_date": "2019-02-01T19:30:52Z",
        "hclegacy:record_creation_date": "2019-02-01T19:30:52Z",
        "hclegacy:submitter_affiliation": "Liverpool Hope University",
        "hclegacy:submitter_id": "1012453",
        "hclegacy:submitter_org_memberships": ["hc"],
        "imprint:imprint": {
            "isbn": "9780198804215",
            "pages": "262-274",
            "title": (
                "Epic Performances from the Middle Ages into the "
                "Twenty-First Century"
            ),
        },
        "kcr:commons_domain": "hcommons.org",
        "kcr:chapter_label": (
            "18 - Unfixing Epic: Homeric Orality and Contemporary Performance"
        ),
        "kcr:submitter_email": "stephe_harrop@hotmail.co.uk",
        "kcr:submitter_username": "stepheharrop",
        "kcr:user_defined_tags": [
            "Classical reception",
            "Theater and film",
            "Performance",
        ],
    },
    "files": {
        "default_preview": "sh-unfixing-epic-2018.pdf",
        "enabled": True,
        "entries": {
            "sh-unfixing-epic-2018.pdf": {
                "key": "sh-unfixing-epic-2018.pdf",
                "mimetype": "application/pdf",
                "size": "599103",
            }
        },
    },
    "metadata": {
        # 'additional_descriptions': [
        #     {'description': 'This chapter examines the '
        #                     'impact of a putative oral '
        #                     'Homer upon the work of recent '
        #                     'performance-makers. The influence of '
        #                     'oral-poetic theories is (as '
        #                     'yet) an under-explored '
        #                     'area of study, neglected by '
        #                     'scholars whose literary expertise '
        #                     'leads them to focus on dramatic '
        #                     'texts and production '
        #                     'histories, with each revisionary '
        #                     'text or production regarded as a '
        #                     'single, stable, and repeatable '
        #                     'entity. The field of classical '
        #                     'reception studies at present lacks '
        #                     'the conceptual and theoretical means '
        #                     'to engage effectively with '
        #                     'works which deliberately '
        #                     'exploit elements of ‘in-performance’ '
        #                     'composition, and which positively '
        #                     'value the qualities of '
        #                     'fluidity and flexibility evoked '
        #                     'by oral-poetic interpretations of '
        #                     'ancient epic. However, the '
        #                     'present work contends that a '
        #                     'notional oral Homer informs a '
        #                     'diverse array of contemporary '
        #                     'theatre texts and performance '
        #                     'practices,  and that a full '
        #                     'appreciation of the different ways '
        #                     'in which oral-poetic theory '
        #                     'can influence the creation of these '
        #                     'depends upon an ability to '
        #                     'identify and interpret the '
        #                     'interplay between ‘fixed’ and '
        #                     '‘unfixed’ elements both within particular '
        #                     'performances, and within different '
        #                     'iterations of the same production or '
        #                     'event. Kate Tempest’s '
        #                     'performance-poem Brand New Ancients '
        #                     'is analysed as a striking recent '
        #                     'example of creative interplay '
        #                     'between such ‘fixed’ and '
        #                     '‘unfixed’ elements.',
        #     'type': {'id': 'other',
        #              'title': {'en': 'Other'}
        #              }
        #     }
        # ],
        "creators": [
            {
                "affiliations": [{"name": "Liverpool Hope University"}],
                "person_or_org": {
                    "family_name": "Harrop",
                    "given_name": "Stephe",
                    "identifiers": [
                        {"identifier": "stepheharrop", "scheme": "hc_username"}
                    ],
                    "name": "Harrop, Stephe",
                    "type": "personal",
                },
                "role": {"id": "author", "title": {"en": "Author"}},
            }
        ],
        "contributors": [
            {
                "person_or_org": {
                    "family_name": "Macintosh",
                    "given_name": "Fiona",
                    "name": "Macintosh, Fiona",
                    "type": "personal",
                },
                "role": {"id": "other", "title": {"en": "Other"}},
            },
            {
                "person_or_org": {
                    "family_name": "McConnell",
                    "given_name": "Justine",
                    "name": "McConnell, Justine",
                    "type": "personal",
                },
                "role": {"id": "other", "title": {"en": "Other"}},
            },
            {
                "person_or_org": {
                    "family_name": "Harrison",
                    "given_name": "Stephen",
                    "name": "Harrison, Stephen",
                    "type": "personal",
                },
                "role": {"id": "other", "title": {"en": "Other"}},
            },
            {
                "person_or_org": {
                    "family_name": "Harrison",
                    "given_name": "Stephen",
                    "name": "Harrison, Stephen",
                    "type": "personal",
                },
                "role": {"id": "other", "title": {"en": "Other"}},
            },
            {
                "person_or_org": {
                    "family_name": "Kenward",
                    "given_name": "Claire",
                    "name": "Kenward, Claire",
                    "type": "personal",
                },
                "role": {"id": "other", "title": {"en": "Other"}},
            },
        ],
        "publication_date": "2018",
        "description": (
            "This chapter examines the impact of a putative "
            "oral Homer upon the work of recent "
            "performance-makers. The influence of "
            "oral-poetic theories is (as yet) an "
            "under-explored area of study, neglected by "
            "scholars whose literary expertise leads them to "
            "focus on dramatic texts and production "
            "histories, with each revisionary text or "
            "production regarded as a single, stable, and "
            "repeatable entity. The field of classical "
            "reception studies at present lacks the "
            "conceptual and theoretical means to engage "
            "effectively with works which deliberately "
            "exploit elements of ‘in-performance’ "
            "composition, and which positively value the "
            "qualities of fluidity and flexibility evoked by "
            "oral-poetic interpretations of ancient epic. "
            "However, the present work contends that a "
            "notional oral Homer informs a diverse array of "
            "contemporary theatre texts and performance "
            "practices, and that a full appreciation of the "
            "different ways in which oral-poetic theory can "
            "influence the creation of these depends upon an "
            "ability to identify and interpret the interplay "
            "between ‘fixed’ and ‘unfixed’ elements both "
            "within particular performances, and within "
            "different iterations of the same production or "
            "event. Kate Tempest’s performance-poem Brand "
            "New Ancients is analysed as a striking recent "
            "example of creative interplay between such "
            "‘fixed’ and ‘unfixed’ elements."
        ),
        "identifiers": [
            {"identifier": "hc:22647", "scheme": "hclegacy-pid"},
            {"identifier": "1000360-19934", "scheme": "hclegacy-record-id"},
            {"identifier": "10.17613/1d2d-2y15", "scheme": "datacite-doi"},
            {
                "identifier": "https://doi.org/10.17613/1d2d-2y15",
                "scheme": "url",
            },
        ],
        "languages": [{"id": "eng", "title": {"en": "English"}}],
        "resource_type": {"id": "textDocument-bookSection"},
        "rights": [
            {
                "description": {
                    "en": (
                        "Proprietary material. No permissions are "
                        "granted for any kind of copyring or "
                        "re-use. All rights reserved"
                    )
                },
                "id": "arr",
                "icon": "copyright",
                "props": {
                    "url": "https://en.wikipedia.org/wiki/All_rights_reserved"
                },
                "title": {"en": "All Rights Reserved"},
            }
        ],
        "subjects": [
            {
                "id": "http://id.worldcat.org/fast/863509",
                "subject": "Classical literature",
                "scheme": "FAST-topical",
            },
            {
                "id": "http://id.worldcat.org/fast/1411635",
                "subject": "Criticism, interpretation, etc.",
                "scheme": "FAST-form",
            },
            {
                "id": "http://id.worldcat.org/fast/1149217",
                "subject": "Theater",
                "scheme": "FAST-topical",
            },
            {
                "id": "http://id.worldcat.org/fast/1027285",
                "subject": "Motion pictures",
                "scheme": "FAST-topical",
            },
            {
                "id": "http://id.worldcat.org/fast/29137",
                "subject": "Homer",
                "scheme": "FAST-personal",
            },
            {
                "id": "http://id.worldcat.org/fast/913799",
                "subject": "Epic poetry",
                "scheme": "FAST-topical",
            },
        ],
        "publisher": "Oxford University Press",
        "title": "Unfixing Epic: Homeric Orality and Contemporary Performance",
    },
    "parent": {"access": {"owned_by": [{"user": "1012453"}]}},
    "updated": "2019-02-01T19:30:52Z",
}

json42615 = {
    "created": "2021-11-10T15:06:20Z",
    "pids": {
        "doi": {
            "client": "datacite",
            "identifier": "10.17613/6v9q-8878",
            "provider": "datacite",
        }
    },
    "custom_fields": {
        "hclegacy:collection": "hccollection:1",
        "hclegacy:file_location": (
            "/srv/www/commons/current/web/app/uploads"
            "/humcore/2021/11/o_1fk563qmpqgs1on0ue"
            "g6mfcf7.pdf.palazzo-vernacular_pa"
            "tterns_in_portugal_and_brazil-2021.pdf"
        ),
        "hclegacy:file_pid": "hc:42616",
        "hclegacy:previously_published": "published",
        "hclegacy:record_change_date": "2021-11-10T15:06:20Z",
        "hclegacy:record_creation_date": "2021-11-10T15:06:20Z",
        "hclegacy:submitter_affiliation": (
            "University of Brasilia School of Architecture and Urbanism"
        ),
        "hclegacy:submitter_id": "1011841",
        "hclegacy:submitter_org_memberships": ["hc", "sah"],
        "journal:journal": {
            "issn": "2660-583X",
            "issue": "2",
            "pages": "359-370",
            "title": (
                "Journal of Traditional Building, Architecture and Urbanism"
            ),
        },
        "kcr:commons_domain": "sah.hcommons.org",
        "kcr:submitter_email": "pedro.palazzo@gmail.com",
        "kcr:submitter_username": "palazzo",
        "kcr:user_defined_tags": [
            "renaisance",
            "lot sizes",
            "building types",
            "Urbanism/urban planning",
            "Portuguese empire",
            "Luso-Brazilian studies",
            "Architectural history",
            "Urban history",
            "18th century",
            "19th century",
        ],
    },
    "files": {
        "default_preview": (
            "palazzo-vernacular_patterns_in_portugal_and_brazil-2021.pdf"
        ),
        "enabled": True,
        "entries": {
            "palazzo-vernacular_patterns_in_portugal_and_brazil-2021.pdf": {
                "key": (
                    "palazzo-vernacular_patterns_in_portugal_and_b"
                    "razil-2021.pdf"
                ),
                "mimetype": "application/pdf",
                "size": "498676",
            }
        },
    },
    "metadata": {
        "creators": [
            {
                "affiliations": [
                    {
                        "name": (
                            "University of Brasilia School "
                            "of Architecture and Urbanism"
                        )
                    }
                ],
                "person_or_org": {
                    "family_name": (
                        "P. Palazzo"
                    ),  # FIXME: why is initial with family name?
                    "given_name": "Pedro",
                    "identifiers": [
                        {"identifier": "palazzo", "scheme": "hc_username"}
                    ],
                    "name": (
                        "P. Palazzo, Pedro"
                    ),  # Why is name switched to family, given?
                    "type": "personal",
                },
                "role": {"id": "author", "title": {"en": "Author"}},
            }
        ],
        "dates": [
            {
                "date": "2021-11-10",
                "description": "Human readable publication date",
                "type": {
                    "id": "issued",
                    "title": {"en": "Issued", "de": "Veröffentlicht"},
                },
            }
        ],
        "publication_date": "2021",
        "description": (
            "Traditional towns in Portugal and Brazil have "
            "evolved a finely tuned coordination between, on "
            "the one hand, modular dimensions for street "
            "widths and lot sizes, and on the other, a "
            "typology of room shapes and layouts within "
            "houses. Despite being well documented in urban "
            "history, this coordination was in the last "
            "century often interpreted as contingent, a "
            "result of the limited material means of "
            "pre-industrial societies. But the continued "
            "application and gradual adaptation of these "
            "urban and architectural patterns through "
            "periods of industrialization and economic "
            "development suggests that they respond both to "
            "enduring housing requirements and to piecemeal "
            "urban growth. This article surveys the "
            "persistence of urban and architectural patterns "
            "up to the early 20th century, showing their "
            "resilience in addressing modern housing and "
            "urbanization requirements."
        ),
        "identifiers": [
            {"identifier": "hc:42615", "scheme": "hclegacy-pid"},
            {"identifier": "1001712-776", "scheme": "hclegacy-record-id"},
            {"identifier": "10.17613/6v9q-8878", "scheme": "datacite-doi"},
            {
                "identifier": "https://doi.org/10.17613/6v9q-8878",
                "scheme": "url",
            },
        ],
        "languages": [{"id": "eng", "title": {"en": "English"}}],
        "resource_type": {"id": "textDocument-journalArticle"},
        "rights": [
            {
                "description": {"en": ""},
                "id": "cc-by-nc-nd-4.0",
                "icon": "cc-by-nc-nd-icon",
                "props": {
                    "scheme": "spdx",
                    "url": "https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode",
                },
                "title": {
                    "en": (
                        "Creative Commons Attribution Non "
                        "Commercial No Derivatives 4.0 "
                        "International"
                    )
                },
            }
        ],
        "subjects": [
            {
                "id": "http://id.worldcat.org/fast/862177",
                "subject": "City planning",
                "scheme": "FAST-topical",
            },
            {
                "id": "http://id.worldcat.org/fast/861853",
                "subject": "Cities and towns--Study and teaching",
                "scheme": "FAST-topical",
            },
            {
                "id": "http://id.worldcat.org/fast/1208476",
                "subject": "Portugal",
                "scheme": "FAST-geographic",
            },
            {
                "id": "http://id.worldcat.org/fast/1930859",
                "subject": "Portuguese colonies",
                "scheme": "FAST-topical",
            },
            {
                "id": "http://id.worldcat.org/fast/813346",
                "subject": "Architecture",
                "scheme": "FAST-topical",
            },
            {
                "id": "http://id.worldcat.org/fast/958235",
                "subject": "History",
                "scheme": "FAST-topical",
            },
            {
                "id": "http://id.worldcat.org/fast/904058",
                "subject": "Eighteenth century",
                "scheme": "FAST-topical",
            },
            {
                "id": "http://id.worldcat.org/fast/1037841",
                "subject": "Nineteenth century",
                "scheme": "FAST-topical",
            },
        ],
        "publisher": "Toledo: INTBAU Spain",
        "title": (
            "Vernacular Patterns in Portugal and Brazil: Evolution "
            "and Adaptations"
        ),
    },
    "parent": {"access": {"owned_by": [{"user": "1011841"}]}},
    "updated": "2021-11-10T15:06:20Z",
}

json22625 = {
    "created": "2019-01-29T03:57:00Z",
    "pids": {
        "doi": {
            "client": "datacite",
            "identifier": "10.17613/hrhn-3k43",
            "provider": "datacite",
        }
    },
    "custom_fields": {
        "hclegacy:collection": "hccollection:1",
        "hclegacy:file_location": (
            "/srv/www/commons/current/web/app/uploads/"
            "humcore/2019/01/o_1d2bs18df1fnlt45186"
            "1gk91rer7.pdf.55710426.pdf"
        ),
        "hclegacy:file_pid": "hc:22626",
        "kcr:submitter_email": "wojciech.tworek.09@ucl.ac.uk",
        "kcr:submitter_username": "wtworek",
        "kcr:commons_domain": "ajs.hcommons.org",
        "kcr:user_defined_tags": [
            "Hasidism",
            "Chabad",
            "Jewish studies",
            "Jewish mysticism",
            "Jewish thought",
        ],
        "hclegacy:previously_published": "published",
        "hclegacy:submitter_affiliation": "University Of Toronto",
        "hclegacy:submitter_id": "1017065",
        "hclegacy:submitter_org_memberships": ["ajs", "hc"],
        "imprint:imprint": {
            "pages": "57-74",
            "title": "Habad Hasidism: History, Thought, Image",
        },
        "hclegacy:groups_for_deposit": [
            {"group_identifier": "1000610", "group_name": "Jewish Mysticism"},
            {
                "group_identifier": "1000611",
                "group_name": "Modern Jewish Thought and Theology",
            },
        ],
        "hclegacy:record_change_date": "2019-01-29T03:57:00Z",
        "hclegacy:record_creation_date": "2019-01-29T03:57:00Z",
    },
    "files": {
        "default_preview": "55710426.pdf",
        "enabled": True,
        "entries": {
            "55710426.pdf": {
                "key": "55710426.pdf",
                "mimetype": "application/pdf",
                "size": "266856",
            }
        },
    },
    "metadata": {
        # {'additional_descriptions':
        #     [{'description': ('The issue of gender has been a topic of '
        #                      'discussion in the research of Hasidism since S. '
        #                      'A. Horodecky’s book (1923), in which he '
        #                      'claimed that Hasidism brought about full ' 'equality of Jewish men and women in the field '
        #                      'of spirituality. Although his claims have been '
        #                      'by and large rejected, most\nscholars agree that '
        #                      'the twentieth century Chabad movement has '
        #                      'indeed created space for women in the hasidic '
        #                      'model of spirituality. This article sets out to '
        #                      'explore whether the particular interest of '
        #                      'contemporary Chabad in the role of women is a '
        #                      'new phenomenon or has existed from the '
        #                      'movement’s inception. Rather than looking at the '
        #                      'issue from a social-historical perspective, the '
        #                      'article examines the gender discourse conveyed '
        #                      'in the homilies of the founder of Chabad, Rabbi '
        #                      'Shneur Zalman of Liadi (1745–1812). It explores '
        #                      'the role of the feminine aspect of divinity in '
        #                      'the process of creation, and its envisioned '
        #                      'elevation in the future-to-come, in an attempt '
        #                      'to establish the relation between the gender '
        #                      'category of “female” and flesh-and-blood '
        #                      'women in the teachings of Shneur Zalman of '
        #                      'Liadi. This, in turn, leads to determine '
        #                      'whether the concept of the transfigurations of '
        #                      'genders in the future-to-come, a Chabad '
        #                      'tradition that originates in the teachings of '
        #                      'Shneur Zalman of Liadi and serves as '
        #                      'the ideological ground for the empowerment of '
        #                      'Chabad women in the writings of the late '
        #                      'Lubavitcher Rebbe in the twentieth century, '
        #                      'could have any relevance to the daily life of '
        #                      'wives and daughters of Shneur Zalman’s '
        #                      'followers.'),
        #       'type': {'id': 'other',
        #                'title': {'en': 'Other'}
        #                }
        #     }],
        "creators": [
            {
                "affiliations": [{"name": "University Of Toronto"}],
                "person_or_org": {
                    "family_name": "Tworek",
                    "given_name": "Wojciech",
                    "identifiers": [
                        {"identifier": "wtworek", "scheme": "hc_username"}
                    ],
                    "name": "Tworek, Wojciech",
                    "type": "personal",
                },
                "role": {"id": "author", "title": {"en": "Author"}},
            }
        ],
        "contributors": [
            {
                "person_or_org": {
                    "family_name": "Sagiv",
                    "given_name": "Gadi",
                    "name": "Sagiv, Gadi",
                    "type": "personal",
                },
                "role": {"id": "other", "title": {"en": "Other"}},
            },
            {
                "person_or_org": {
                    "family_name": "Meir",
                    "given_name": "Jonatan",
                    "name": "Meir, Jonatan",
                    "type": "personal",
                },
                "role": {"id": "other", "title": {"en": "Other"}},
            },
        ],
        "publication_date": "2016",
        "description": (
            "The issue of gender has been a topic of "
            "discussion in the research of Hasidism since S. "
            "A. Horodecky’s book (1923), in which he claimed "
            "that Hasidism brought about full equality of "
            "Jewish men and women in the field of "
            "spirituality. Although his claims have been by "
            "and large rejected, most\n"
            "scholars agree that the twentieth century Chabad "
            "movement has indeed created space for women in "
            "the hasidic model of spirituality. This article "
            "sets out to explore whether the particular "
            "interest of contemporary Chabad in the role of "
            "women is a new phenomenon or has existed from "
            "the movement’s inception. Rather than looking at "
            "the issue from a social-historical perspective, "
            "the article examines the gender discourse "
            "conveyed in the homilies of the founder of "
            "Chabad, Rabbi Shneur Zalman of Liadi "
            "(1745–1812). It explores the role of the "
            "feminine aspect of divinity in the process of "
            "creation, and its envisioned elevation in the "
            "future-to-come, in an attempt to establish the "
            "relation between the gender category of “female” "
            "and flesh-and-blood women in the teachings of "
            "Shneur Zalman of Liadi. This, in turn, leads to "
            "determine whether the concept of the "
            "transfigurations of genders in the "
            "future-to-come, a Chabad tradition that "
            "originates in the teachings of Shneur Zalman of "
            "Liadi and serves as the ideological ground for "
            "the empowerment of Chabad women in the writings "
            "of the late Lubavitcher Rebbe in the twentieth "
            "century, could have any relevance to the daily "
            "life of wives and daughters of Shneur Zalman’s "
            "followers."
        ),
        "identifiers": [
            {"identifier": "hc:22625", "scheme": "hclegacy-pid"},
            {"identifier": "1000361-383", "scheme": "hclegacy-record-id"},
            {"identifier": "10.17613/hrhn-3k43", "scheme": "datacite-doi"},
            {
                "identifier": "https://doi.org/10.17613/hrhn-3k43",
                "scheme": "url",
            },
        ],
        "languages": [{"id": "heb", "title": {"en": "Hebrew"}}],
        "resource_type": {"id": "textDocument-bookSection"},
        "rights": [
            {
                "description": {
                    "en": (
                        "Proprietary material. No permissions are "
                        "granted for any kind of copyring or "
                        "re-use. All rights reserved"
                    )
                },
                "id": "arr",
                "icon": "copyright",
                "props": {
                    "url": "https://en.wikipedia.org/wiki/All_rights_reserved"
                },
                "title": {"en": "All Rights Reserved"},
            }
        ],
        "subjects": [
            {
                "id": "http://id.worldcat.org/fast/983377",
                "subject": "Jews--Study and teaching",
                "scheme": "FAST-topical",
            },
            {
                "id": "http://id.worldcat.org/fast/1031646",
                "subject": "Mysticism--Judaism",
                "scheme": "FAST-topical",
            },
            {
                "id": "http://id.worldcat.org/fast/1730516",
                "subject": "Jewish philosophy",
                "scheme": "FAST-topical",
            },
        ],
        "publisher": "Zalman Shazar Center",
        "title": "מגדר וזמן בכתבי ר׳ שניאור זלמן מלאדי",
    },
    "parent": {"access": {"owned_by": [{"user": "1017065"}]}},
    "updated": "2019-01-29T03:57:00Z",
}

json45177 = {
    "created": "2022-03-31T13:53:16Z",
    "pids": {
        "doi": {
            "client": "datacite",
            "identifier": "10.17613/zhmh-c741",
            "provider": "datacite",
        }
    },
    "custom_fields": {
        "hclegacy:collection": "hccollection:1",
        "hclegacy:file_location": (
            "/srv/www/commons/current/web/app/uploads/"
            "humcore/2022/03/o_1fvg3cpqe1hv61shk1"
            "sqs1uqplep7.pdf.cep_notes_revised_2022-03-30"
            ".pdf"
        ),
        "hclegacy:file_pid": "hc:45178",
        "hclegacy:record_change_date": "2022-03-31T13:55:13Z",
        "hclegacy:record_creation_date": "2022-03-31T13:53:16Z",
        "imprint:imprint": {
            "title": "Cataloging Exhibition Publications: Best Practices"
        },
        "kcr:edition": "2",
        "kcr:submitter_email": "aprovo@gmail.com",
        "kcr:submitter_username": "aprovo",
        "kcr:commons_domain": "arlisna.hcommons.org",
        "kcr:user_defined_tags": [
            "Cataloging",
            "Cataloging standards",
            "Cataloging Exhibition Publications: Best Practices",
            "Notes",
            "Exhibition publications",
            "Art librarianship",
        ],
        "hclegacy:previously_published": "published",
        "hclegacy:submitter_affiliation": "New York University",
        "hclegacy:submitter_id": "1006873",
        "hclegacy:submitter_org_memberships": ["arlisna", "hc"],
        "hclegacy:groups_for_deposit": [
            {
                "group_identifier": "1003999",
                "group_name": "ARLIS/NA Cataloging Advisory Committee",
            }
        ],
    },
    "files": {
        "default_preview": "cep_notes_revised_2022-03-30.pdf",
        "enabled": True,
        "entries": {
            "cep_notes_revised_2022-03-30.pdf": {
                "key": "cep_notes_revised_2022-03-30.pdf",
                "mimetype": "application/pdf",
                "size": "251202",
            }
        },
    },
    "metadata": {
        # 'additional_descriptions': [
        #     {'description': 'The ARLIS/NA Cataloging Advisory Committee has '
        #                     'drafted these best practices to provide practical '
        #                     'guidance to catalogers working with art exhibition '
        #                     'publications. The guidelines are confined to '
        #                     'cataloging issues and situations characteristic of '
        #                     'this type of material; they are intended to be '
        #                     'used with and are compatible with other '
        #                     'cataloging documentation including Resource '
        #                     'Description and Access (RDA) and LC-PCC Policy '
        #                     'Statements and Metadata Guidance Documents. '
        #                     'Examples have been given using the MARC21 '
        #                     'format for consistency and familiarity, but '
        #                     'MARC21 is not a prescribed or preferred schema. '
        #                     'The order of notes in this document generally '
        #                     'follows the WEMI framework but can be adjusted '
        #                     'for local practice or when it has been '
        #                     'decided that a particular note is of primary '
        #                     'importance.',
        #      'type': {'id': 'other',
        #               'title': {'en': 'Other'}}
        #     }
        # ],
        "creators": [
            {
                "person_or_org": {
                    "family_name": "Bitetti",
                    "given_name": "Bronwen",
                    "name": "Bitetti, Bronwen",
                    "type": "personal",
                },
                "role": {"id": "other", "title": {"en": "Other"}},
            },
            {
                "person_or_org": {
                    "family_name": "Blueher",
                    "given_name": "William",
                    "name": "Blueher, William",
                    "type": "personal",
                },
                "role": {"id": "other", "title": {"en": "Other"}},
            },
            {
                "person_or_org": {
                    "family_name": "Clarke",
                    "given_name": "Sherman",
                    "name": "Clarke, Sherman",
                    "type": "personal",
                },
                "role": {"id": "other", "title": {"en": "Other"}},
            },
            {
                "person_or_org": {
                    "family_name": "Fultz",
                    "given_name": "Tamara",
                    "name": "Fultz, Tamara",
                    "type": "personal",
                },
                "role": {"id": "other", "title": {"en": "Other"}},
            },
            {
                "person_or_org": {
                    "family_name": "L'Ecuyer-Coelho",
                    "given_name": "Marie-Chantal",
                    "name": "L'Ecuyer-Coelho, Marie-Chantal",
                    "type": "personal",
                },
                "role": {"id": "other", "title": {"en": "Other"}},
            },
            {
                "person_or_org": {
                    "family_name": "Maier",
                    "given_name": "John",
                    "name": "Maier, John",
                    "type": "personal",
                },
                "role": {"id": "other", "title": {"en": "Other"}},
            },
            {
                "person_or_org": {
                    "family_name": "Neumann",
                    "given_name": "Calli",
                    "name": "Neumann, Calli",
                    "type": "personal",
                },
                "role": {"id": "other", "title": {"en": "Other"}},
            },
            {
                "person_or_org": {
                    "family_name": "Oldal",
                    "given_name": "Maria",
                    "name": "Oldal, Maria",
                    "type": "personal",
                },
                "role": {"id": "other", "title": {"en": "Other"}},
            },
            {
                "person_or_org": {
                    "family_name": "Osborne Bender",
                    "given_name": "Sarah",
                    "name": "Osborne Bender, Sarah",
                    "type": "personal",
                },
                "role": {"id": "other", "title": {"en": "Other"}},
            },
            {
                "person_or_org": {
                    "family_name": "O'Keefe",
                    "given_name": "Elizabeth",
                    "name": "O'Keefe, Elizabeth",
                    "type": "personal",
                },
                "role": {"id": "other", "title": {"en": "Other"}},
            },
            {
                "affiliations": [{"name": "New York University"}],
                "person_or_org": {
                    "family_name": "Provo",
                    "given_name": "Alexandra",
                    "identifiers": [
                        {"identifier": "aprovo", "scheme": "hc_username"}
                    ],
                    "name": "Provo, Alexandra",
                    "type": "personal",
                },
                "role": {"id": "other", "title": {"en": "Other"}},
            },
            {
                "person_or_org": {
                    "family_name": "Puccio",
                    "given_name": "Andrea",
                    "name": "Puccio, Andrea",
                    "type": "personal",
                },
                "role": {"id": "other", "title": {"en": "Other"}},
            },
            {
                "person_or_org": {
                    "family_name": "Stafford",
                    "given_name": "Karen",
                    "name": "Stafford, Karen",
                    "type": "personal",
                },
                "role": {"id": "other", "title": {"en": "Other"}},
            },
            {
                "person_or_org": {
                    "family_name": "Wildenhaus",
                    "given_name": "Karly",
                    "name": "Wildenhaus, Karly",
                    "type": "personal",
                },
                "role": {"id": "other", "title": {"en": "Other"}},
            },
        ],
        "contributors": [
            {
                "person_or_org": {
                    "family_name": "ARLIS/NA Cataloging Advisory Committee",
                    "given_name": "",
                    "name": "ARLIS/NA Cataloging Advisory Committee",
                    "type": "personal",
                },
                "role": {"id": "other", "title": {"en": "Other"}},
            }
        ],
        "publication_date": "2022",
        "description": (
            "The ARLIS/NA Cataloging Advisory Committee has "
            "drafted these best practices to provide "
            "practical guidance to catalogers working with "
            "art exhibition publications. The guidelines are "
            "confined to cataloging issues and situations "
            "characteristic of this type of material; they "
            "are intended to be used with and are compatible "
            "with other cataloging documentation including "
            "Resource Description and Access (RDA) and LC-PCC "
            "Policy Statements and Metadata Guidance "
            "Documents. Examples have been given using the "
            "MARC21 format for consistency and familiarity, "
            "but MARC21 is not a prescribed or preferred "
            "schema. The order of notes in this document "
            "generally follows the WEMI framework but can be "
            "adjusted for local practice or when it has been "
            "decided that a particular note is of primary "
            "importance."
        ),
        "identifiers": [
            {"identifier": "hc:45177", "scheme": "hclegacy-pid"},
            {"identifier": "1001634-246", "scheme": "hclegacy-record-id"},
            {"identifier": "10.17613/zhmh-c741", "scheme": "datacite-doi"},
            {
                "identifier": "https://doi.org/10.17613/zhmh-c741",
                "scheme": "url",
            },
        ],
        "languages": [{"id": "eng", "title": {"en": "English"}}],
        "resource_type": {"id": "textDocument-bookSection"},
        "rights": [
            {
                "description": {"en": ""},
                "id": "cc-by-nc-nd-4.0",
                "icon": "cc-by-nc-nd-icon",
                "props": {
                    "scheme": "spdx",
                    "url": "https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode",
                },
                "title": {
                    "en": (
                        "Creative Commons Attribution Non "
                        "Commercial No Derivatives 4.0 "
                        "International"
                    )
                },
            }
        ],
        "publisher": "Art Libraries Society of North America",
        "title": "Notes",
    },
    "parent": {"access": {"owned_by": [{"user": "1006873"}]}},
    "updated": "2022-03-31T13:55:13Z",
}

json44881 = {
    "pids": {
        "doi": {
            "client": "datacite",
            "identifier": "10.17613/82yy-vj44",
            "provider": "datacite",
        }
    },
    "created": "2022-03-08T21:57:49Z",
    "custom_fields": {
        "hclegacy:file_location": (
            "/srv/www/commons/current/web/app/"
            "uploads/humcore/2022/03/"
            "o_1ftlo8pia8cm1ptgmrh1l1s10607.pdf"
            ".clarkestarr-transcript.pdf"
        ),
        "hclegacy:file_pid": "hc:44882",
        "hclegacy:previously_published": "not-published",
        "hclegacy:record_change_date": "2022-03-08T21:57:49Z",
        "hclegacy:record_creation_date": "2022-03-08T21:57:49Z",
        "hclegacy:collection": "hccollection:1",
        "kcr:submitter_email": "runmerd@gmail.com",
        "hclegacy:submitter_org_memberships": ["arlisna", "hc"],
        "kcr:submitter_username": "mlhale7",
        "kcr:user_defined_tags": [
            "Society history",
            "Art Libraries Society of North America",
            "Anniversary",
            "Gay librarians",
            "Vietnam War",
            "Art librarianship",
        ],
        "kcr:commons_domain": "arlisna.hcommons.org",
        "hclegacy:submitter_id": "1018587",
    },
    "files": {
        "default_preview": "clarkestarr-transcript.pdf",
        "enabled": True,
        "entries": {
            "clarkestarr-transcript.pdf": {
                "key": "clarkestarr-transcript.pdf",
                "mimetype": "application/pdf",
                "size": "183968",
            }
        },
    },
    "metadata": {
        # 'additional_descriptions': [
        #     {'description': 'Emily Walz interviews Distinguished '
        #                     'Service Award winners Sherman Clarke (2005) and '
        #                     'Daniel Starr (2014) on June 6, 2017, at the '
        #                     'New York Public Library. Both librarians are '
        #                     'career catalogers who joined ARLIS in its '
        #                     'earliest years; Clarke is best known as the '
        #                     'founder of Art NACO. Clarke and Starr both share '
        #                     'their experiences during the Vietnam War, when '
        #                     'each was classified as a conscientious objector. '
        #                     'The interview covers the challenges of the '
        #                     'Society, including working with management '
        #                     'companies and volunteer participation. The '
        #                     'interviewees also discuss the culture '
        #                     'of ARLIS/NA, in particular its inclusion of gay '
        #                     'and lesbian members. Clarke and Starr are '
        #                     'long-standing roommates at annual conferences.',
        #      'type': {'id': 'other',
        #               'title': {'en': 'Other'}
        #               }
        #      }
        # ],
        "contributors": [
            {
                "person_or_org": {
                    "family_name": "Walz",
                    "given_name": "Emily",
                    "name": "Walz, Emily",
                    "type": "personal",
                },
                "role": {"id": "other", "title": {"en": "Other"}},
            },
        ],
        "creators": [
            {
                "person_or_org": {
                    "family_name": "Clarke",
                    "given_name": "Sherman",
                    "name": "Clarke, Sherman",
                    "type": "personal",
                },
                "role": {"id": "author", "title": {"en": "Author"}},
            },
            {
                "person_or_org": {
                    "family_name": "Starr",
                    "given_name": "Daniel",
                    "name": "Starr, Daniel",
                    "type": "personal",
                },
                "role": {"id": "author", "title": {"en": "Author"}},
            },
        ],
        "dates": [
            {
                "date": "2017-06-06",
                "description": "Human readable publication date",
                "type": {
                    "id": "issued",
                    "title": {"en": "Issued", "de": "Veröffentlicht"},
                },
            }
        ],
        "publication_date": "2017",
        "description": (
            "Emily Walz interviews Distinguished Service "
            "Award winners Sherman Clarke (2005) and Daniel "
            "Starr (2014) on June 6, 2017, at the New York "
            "Public Library. Both librarians are career "
            "catalogers who joined ARLIS in its earliest "
            "years; Clarke is best known as the founder of "
            "Art NACO. Clarke and Starr both share their "
            "experiences during the Vietnam War, when each "
            "was classified as a conscientious objector. The "
            "interview covers the challenges of the Society, "
            "including working with management companies and "
            "volunteer participation. The interviewees also "
            "discuss the culture of ARLIS/NA, in particular "
            "its inclusion of gay and lesbian members. Clarke "
            "and Starr are long-standing roommates at annual "
            "conferences."
        ),
        "identifiers": [
            {"identifier": "hc:44881", "scheme": "hclegacy-pid"},
            {"identifier": "1001634-235", "scheme": "hclegacy-record-id"},
            {"identifier": "10.17613/82yy-vj44", "scheme": "datacite-doi"},
            {
                "identifier": "https://doi.org/10.17613/82yy-vj44",
                "scheme": "url",
            },
        ],
        "languages": [{"id": "eng", "title": {"en": "English"}}],
        "resource_type": {"id": "textDocument-interviewTranscript"},
        "publisher": "unknown",
        "rights": [
            {
                "description": {"en": ""},
                "id": "cc-by-nc-nd-4.0",
                "icon": "cc-by-nc-nd-icon",
                "props": {
                    "scheme": "spdx",
                    "url": "https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode",
                },
                "title": {
                    "en": (
                        "Creative Commons Attribution Non "
                        "Commercial No Derivatives 4.0 "
                        "International"
                    )
                },
            }
        ],
        "subjects": [
            {
                "id": "http://id.worldcat.org/fast/815177",
                "subject": "Art",
                "scheme": "FAST-topical",
            },
            {
                "id": "http://id.worldcat.org/fast/1047055",
                "subject": "Oral history",
                "scheme": "FAST-topical",
            },
            {
                "id": "http://id.worldcat.org/fast/997341",
                "subject": "Libraries",
                "scheme": "FAST-topical",
            },
        ],
        "title": (
            "ARLIS/NA Oral History for Distinguished Service Award "
            "Winners, Sherman Clarke and Daniel Starr"
        ),
    },
    "parent": {"access": {"owned_by": [{"user": "1018587"}]}},
    "updated": "2022-03-08T21:57:49Z",
}


@pytest.fixture(scope="module")
def serialized_records():
    actual_serialized_json, actual_bad_data = serialize_json()
    return {
        "actual_serialized_json": actual_serialized_json,
        "actual_bad_data": actual_bad_data,
    }


@pytest.mark.parametrize(
    "expected,row,bad_data_dict",
    [
        (
            {
                "publication_date": "2023",
                "issued": "2023-01-01",
                "description": "Publication date",
            },
            {
                "date_issued": "2023",
                "date": "2023-01-01",
            },
            {},
        ),
        (
            {
                "publication_date": "2015",
                "issued": "2015-02",
                "description": "Publication date",
            },
            {
                "date_issued": "2015",
                "date": "02.2015",
            },
            {},
        ),
        (
            {
                "publication_date": "2010",
                "issued": "2010-11-01",
                "description": "Publication date",
            },
            {
                "date_issued": "2010",
                "date": "Nov. 1, 2010",
            },
            {},
        ),
        (
            {
                "publication_date": "2023",
                "issued": "2023-04-22",
                "description": "Publication date",
            },
            {
                "date_issued": "2023",
                "date": "22ND APRIL,2023",
            },
            {},
        ),
        (
            {
                "publication_date": "2021",
                "issued": "2021/2022",
                "description": "Publication date",
            },
            {
                "date_issued": "2021",
                "date": "2021-2022",
            },
            {},
        ),
        (
            {
                "publication_date": "2019",
                "issued": "2019-02",
                "description": "Publication date",
            },
            {
                "date_issued": "2019",
                "date": "02/2019",
            },
            {},
        ),
        (
            {
                "publication_date": "2023",
                "issued": "2023-02-04",
                "description": "Publication date",
            },
            {
                "date_issued": "2023",
                "date": "4 de febrero 2023",
            },
            {},
        ),
        (
            {
                "publication_date": "2015",
                "issued": "2015-03",
                "description": "Publication date",
            },
            {
                "date_issued": "2015",
                "date": "March, 2015.",
            },
            {},
        ),
        (
            {
                "publication_date": "2021",
                "issued": "2021-10",
                "description": "Publication date",
            },
            {
                "date_issued": "2021",
                "date": "October, 2021.",
            },
            {},
        ),
        (
            {
                "publication_date": "2002",
                "issued": "2002/2015",
                "description": "Publication date",
            },
            {
                "date_issued": "2002",
                "date": "2002/2015",
            },
            {},
        ),
        (
            {
                "publication_date": "2022",
                "issued": "1991-04-22",
                "description": "Publication date",
            },
            {
                "date_issued": "2022",
                "date": "04/91/22",
            },
            {},
        ),
        (
            {
                "publication_date": "2022",
                "issued": "2017-06-30",
                "description": "Publication date",
            },
            {
                "date_issued": "2022",
                "date": "2017 06 30",
            },
            {},
        ),
        (
            {
                "publication_date": "2022",
                "issued": "2022/2023",
                "description": "Publication date",
            },
            {
                "date_issued": "2022",
                "date": "2022/23",
            },
            {},
        ),
    ],
)
def test_add_date_info(expected, row, bad_data_dict):
    actual_dict, actual_bad_data = add_date_info(
        {"metadata": {}},
        {
            **row,
            "id": "1001634-235",
            "record_change_date": "",
            "record_creation_date": "",
        },
        bad_data_dict,
    )
    assert actual_dict == {
        "metadata": {
            "publication_date": expected["publication_date"],
            "dates": [
                {
                    "date": expected["issued"],
                    "type": {
                        "id": "issued",
                        "title": {
                            "en": "Issued",
                            "de": "Veröffentlicht",
                        },
                    },
                    "description": expected["description"],
                }
            ],
        }
    }


@pytest.mark.parametrize(
    "expected_json",
    [
        (json42615),
        (json22625),
        (json45177),
        (json44881),
        (json22647),
        (json11451),
        (json34031),
        (json16079),
        (json33383),
        (json38367),
        (json48799),
        (json583),
        (json28491),
    ],
)
def test_serialize_json(expected_json, serialized_records):
    """ """
    # runner = CliRunner()
    # result = runner.invoke(parse_csv, [])
    # assert result.exit_code == 0
    # assert result.output[0] == json1

    actual_json = serialized_records["actual_serialized_json"]
    expected_json = deepcopy(expected_json)

    expected_pid = expected_json["metadata"]["identifiers"][0]["identifier"]
    actual_json_item = [
        j
        for j in actual_json
        for i in j["metadata"]["identifiers"]
        if i["identifier"] == expected_pid
    ][0]

    # to avoid having to insert German titles in serialization
    if "title" in expected_json["metadata"]["resource_type"].keys():
        del expected_json["metadata"]["resource_type"]["title"]
    # FAST vocab bug
    if "subjects" in expected_json["metadata"].keys():
        ports = [
            s
            for s in expected_json["metadata"]["subjects"]
            if s["subject"] == "Portuguese colonies"
        ]
        if ports:
            ports[0]["scheme"] = "FAST-geographic"
    if "rights" in expected_json["metadata"].keys():
        if "icon" in expected_json["metadata"]["rights"][0].keys():
            del expected_json["metadata"]["rights"][0]["icon"]
        if "description" in expected_json["metadata"]["rights"][0].keys():
            expected_json["metadata"]["rights"][0]["description"] = {"en": ""}
    if "description" in expected_json["metadata"].keys():
        for item in [expected_json, actual_json_item]:
            item["metadata"]["description"] = _normalize_punctuation(
                _clean_string(item["metadata"]["description"])
            )
    if "additional_descriptions" in expected_json["metadata"].keys():
        for item in [expected_json, actual_json_item]:
            item["metadata"]["additional_descriptions"][0]["description"] = (
                _normalize_punctuation(
                    _clean_string(
                        item["metadata"]["additional_descriptions"][0][
                            "description"
                        ]
                    )
                )
            )
    if "hclegacy:groups_for_deposit" in expected_json["custom_fields"].keys():
        for item in [expected_json, actual_json_item]:
            for g in item["custom_fields"]["hclegacy:groups_for_deposit"]:
                g["group_name"] = _normalize_punctuation(
                    _clean_string(g["group_name"])
                )
    for idx, myname in enumerate(expected_json["metadata"]["creators"]):
        for item in [expected_json, actual_json_item]:
            item["metadata"]["creators"][idx]["person_or_org"]["name"] = (
                _normalize_punctuation(
                    _clean_string(myname["person_or_org"]["name"])
                )
            )
            item["metadata"]["creators"][idx]["person_or_org"][
                "family_name"
            ] = _normalize_punctuation(
                _clean_string(myname["person_or_org"]["family_name"])
            )
    if "contributors" in expected_json["metadata"].keys():
        for item in [expected_json, actual_json_item]:
            for idx, myname in enumerate(item["metadata"]["contributors"]):
                item["metadata"]["contributors"][idx]["person_or_org"][
                    "name"
                ] = _normalize_punctuation(
                    _clean_string(myname["person_or_org"]["name"])
                )
                item["metadata"]["contributors"][idx]["person_or_org"][
                    "family_name"
                ] = _normalize_punctuation(
                    _clean_string(myname["person_or_org"]["family_name"])
                )
    # for idx, d in enumerate(expected_json['metadata']['dates']):
    #     if 'de' in d['type']['title'].keys():
    #         del expected_json['metadata']['dates'][idx]['type']['title']['de']

    for k in expected_json.keys():
        if k in ["custom_fields", "metadata"]:
            for i in expected_json[k].keys():
                assert actual_json_item[k][i] == expected_json[k][i]
        else:
            assert actual_json_item[k] == expected_json[k]

    assert expected_json.keys() == actual_json_item.keys()
    assert not any(
        [k for k in actual_json_item.keys() if k not in expected_json.keys()]
    )
    # assert actual_json_item['created'] == expected_json['created']
    # assert actual_json_item['custom_fields']['hclegacy:file_location'] == expected_json['custom_fields']['hclegacy:file_location']
    # assert actual_json_item['custom_fields']['hclegacy:file_pid'] == expected_json['custom_fields']['hclegacy:file_pid']
    # assert actual_json_item['custom_fields']['hclegacy:record_change_date'] == expected_json['custom_fields']['hclegacy:record_change_date']
    # assert actual_json_item['custom_fields']['hclegacy:record_creation_date'] == expected_json['custom_fields']['hclegacy:record_creation_date']
    # assert actual_json_item['custom_fields']['hclegacy:collection'] == expected_json['custom_fields']['hclegacy:collection']
    # assert actual_json_item['custom_fields']['hclegacy:submitter_id'] == expected_json['custom_fields']['hclegacy:submitter_id']
    # assert actual_json_item['custom_fields']['kcr:submitter_email'] == expected_json['custom_fields']['kcr:submitter_email']
    # assert actual_json_item['custom_fields']['kcr:submitter_username'] == expected_json['custom_fields']['kcr:submitter_username']
    # assert actual_json_item['custom_fields']['kcr:commons_domain'] == expected_json['custom_fields']['kcr:commons_domain']
    # assert actual_json_item['files'] == expected_json['files']
    # assert actual_json_item['metadata']['additional_descriptions'] == expected_json['metadata']['additional_descriptions']
    # assert actual_json_item['metadata']['additional_titles'] == expected_json['metadata']['additional_titles']
    # assert actual_json_item['metadata']['contributors'] == expected_json['metadata']['contributors']
    # assert actual_json_item['metadata']['creators'] == expected_json['metadata']['creators']
    # assert actual_json_item['metadata']['dates'] == expected_json['metadata']['dates']
    # assert actual_json_item['metadata']['publication_date'] == expected_json['metadata']['publication_date']
    # assert actual_json_item['metadata']['description'] == expected_json['metadata']['description']
    # assert actual_json_item['metadata']['formats'] == expected_json['metadata']['formats']
    # assert actual_json_item['metadata']['identifiers'] == expected_json['metadata']['identifiers']
    # assert actual_json_item['metadata']['identifiers'] == expected_json['metadata']['identifiers']
    # assert actual_json_item['metadata']['resource_type'] == expected_json['metadata']['resource_type']
    # assert actual_json_item['metadata']['rights'] == expected_json['metadata']['rights']
    # assert actual_json_item['metadata']['subjects'] == expected_json['metadata']['subjects']
    # assert actual_json_item['metadata']['keywords'] == expected_json['metadata']['keywords']
    # assert actual_json_item['metadata']['title'] == expected_json['metadata']['title']
    # assert actual_json_item['parent'] == expected_json['parent']
    # assert actual_json_item['updated'] == expected_json['updated']

    assert actual_json_item == expected_json


top_level_record_keys = [
    "links",
    "updated",
    "parent",
    "revision_id",
    "is_draft",
    "custom_fields",
    "pids",
    "is_published",
    "metadata",
    "stats",
    "status",
    "id",
    "created",
    "files",
    "versions",
    "access",
]

request_header_keys = [
    "Server",
    "Date",
    "Content-Type",
    "Transfer-Encoding",
    "Connection",
    "Vary",
    "X-RateLimit-Limit",
    "X-RateLimit-Remaining",
    "X-RateLimit-Reset",
    "Retry-After",
    "Permissions-Policy",
    "X-Frame-Options",
    "X-XSS-Protection",
    "X-Content-Type-Options",
    "Content-Security-Policy",
    "Strict-Transport-Security",
    "Referrer-Policy",
    "X-Request-ID",
    "Content-Encoding",
]


@pytest.mark.parametrize(
    "method,server,endpoint,args,json_dict,expected_response",
    [
        (
            "GET",
            TESTING_SERVER_DOMAIN,
            "records",
            "p6qjf-y6074",
            "",
            {"text": "", "headers": ""},
        )
    ],
)
def test_api_request(
    method, server, endpoint, args, json_dict, expected_response
):
    """ """
    other_args = {}
    if json_dict:
        other_args["json_dict"] = json_dict
    actual = api_request(
        method=method,
        endpoint=endpoint,
        server=server,
        args=args,
        **other_args,
    )
    assert actual["status_code"] == 200
    assert all(
        k in top_level_record_keys
        for k in list(json.loads(actual["text"]).keys())
    )
    assert all(k in top_level_record_keys for k in list(actual["json"].keys()))
    assert all(
        k in request_header_keys for k in list(actual["headers"].keys())
    )


@pytest.mark.parametrize(
    "json_payload,expected_status_code,expected_json",
    [
        (
            {
                "access": {"record": "public", "files": "public"},
                "custom_fields": {},
                "pids": {},
                "files": {"enabled": True},
                "metadata": {
                    "creators": [
                        {
                            "person_or_org": {
                                "family_name": "Brown",
                                "given_name": "Troy",
                                "type": "personal",
                            },
                            "role": {
                                "id": "author",
                                "title": {"en": "Author"},
                            },
                        },
                        {
                            "person_or_org": {
                                "family_name": "Collins",
                                "given_name": "Thomas",
                                "identifiers": [
                                    {
                                        "scheme": "orcid",
                                        "identifier": "0000-0002-1825-0097",
                                    }
                                ],
                                "name": "Collins, Thomas",
                                "type": "personal",
                            },
                            "affiliations": [
                                {"id": "01ggx4157", "name": "Entity One"}
                            ],
                            "role": {
                                "id": "author",
                                "title": {"en": "Author"},
                            },
                        },
                        {
                            "person_or_org": {
                                "name": "Troy Inc.",
                                "type": "organizational",
                            }
                        },
                    ],
                    "publication_date": "2020-06-01",
                    "publisher": "MESH Research",
                    "resource_type": {"id": "image-photograph"},
                    "title": "A Romans story",
                },
            },
            201,
            {
                "updated": "2023-05-30T18:57:05.296257+00:00",
                "parent": {
                    "communities": {},
                    "id": "###",
                    "access": {"links": [], "owned_by": [{"user": "3"}]},
                },
                "revision_id": 4,
                "is_draft": True,
                "custom_fields": {},
                "pids": {},
                "is_published": False,
                "metadata": {
                    "title": "A Romans story",
                    "creators": [
                        {
                            "person_or_org": {
                                "name": "Brown, Troy",
                                "given_name": "Troy",
                                "family_name": "Brown",
                                "type": "personal",
                            },
                            "role": {
                                "id": "author",
                                "title": {"en": "Author"},
                            },
                        },
                        {
                            "person_or_org": {
                                "family_name": "Collins",
                                "given_name": "Thomas",
                                "identifiers": [
                                    {
                                        "scheme": "orcid",
                                        "identifier": "0000-0002-1825-0097",
                                    }
                                ],
                                "name": "Collins, Thomas",
                                "type": "personal",
                            },
                            "role": {
                                "id": "author",
                                "title": {"en": "Author"},
                            },
                            "affiliations": [
                                {
                                    "id": "01ggx4157",
                                    "name": (
                                        "European Organization for Nuclear "
                                        "Research"
                                    ),
                                }
                            ],
                        },
                        {
                            "person_or_org": {
                                "name": "Troy Inc.",
                                "type": "organizational",
                            }
                        },
                    ],
                    "publication_date": "2020-06-01",
                    "publisher": "MESH Research",
                    "resource_type": {"id": "image-photograph"},
                },
                "status": "draft",
                "id": "4gqj3-d0z12",
                "created": "2023-05-30T18:57:05.271354+00:00",
                "expires_at": "2023-05-30 18:57:05.271380",
                "files": {
                    "enabled": True,
                    "order": [],
                    "count": 0,
                    "entries": {},
                    "total_bytes": 0,
                },
                "versions": {
                    "is_latest_draft": True,
                    "index": 1,
                    "is_latest": False,
                },
                "access": {
                    "files": "public",
                    "embargo": {"active": False, "reason": None},
                    "record": "public",
                    "status": "metadata-only",
                },
            },
        ),
        (json42615, 201, json42615),
        (json22625, 201, json22625),
        (json45177, 201, json45177),
        (json44881, 201, json44881),
        (json22647, 201, json22647),
        (json11451, 201, json11451),
        (json34031, 201, json34031),
        (json16079, 201, json16079),
        (json33383, 201, json33383),
        (json38367, 201, json38367),
        (json48799, 201, json48799),
        (json583, 201, json583),
        (json28491, 201, json28491),
    ],
)
def test_create_invenio_record(
    json_payload, expected_status_code, expected_json
):
    """ """
    # Send everything from test JSON fixtures except
    #  - created
    #  - updated
    #  - parent
    #  - pids
    #  -
    print("Starting")

    expected_headers = {
        "Server": "nginx/1.23.4",
        "Date": "Tue, 30 May 2023 19:07:31 GMT",
        "Content-Type": "application/json",
        "Content-Length": "182",
        "Connection": "keep-alive",
        "Set-Cookie": (
            "csrftoken=eyJhbGciOiJIUzUxMiIsImlhdCI6MTY4NTQ3MzY1MSwiZXhwIjoxNjg1NTYwMDUxfQ.IkZIODNHR0h2bThxZHdmRVMwaE9JRzgzaE9OaHJhaDFzIg.Te5wJA-7cO-jc29ydK-b2NvEkF17jZNclMIhpGfBou77Ib-I50Qiy4XCBxgttNGGBhkcbeYBRWOm_-2K7YsEBg;"
            " Expires=Tue, 06 Jun 2023 19:07:31 GMT; Max-Age=604800; Secure;"
            " Path=/; SameSite=Lax"
        ),
        "X-RateLimit-Limit": "500",
        "X-RateLimit-Remaining": "499",
        "X-RateLimit-Reset": "1685473712",
        "Retry-After": "60",
        "Permissions-Policy": "interest-cohort=()",
        "X-Frame-Options": "sameorigin",
        "X-XSS-Protection": "1; mode=block",
        "X-Content-Type-Options": "nosniff",
        "Content-Security-Policy": (
            "default-src 'self' data: 'unsafe-inline' blob:"
        ),
        "Strict-Transport-Security": "max-age=31556926; includeSubDomains",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }
    # fix because can't create duplicate dois
    if "doi" in json_payload["pids"].keys():
        random_doi = json_payload["pids"]["doi"]["identifier"].split("-")[0]
        random_doi = f"{random_doi}-{generate_random_string(5)}"
        json_payload["pids"]["doi"]["identifier"] = random_doi
        expected_json["pids"]["doi"]["identifier"] = random_doi

    # prepare json to use for record creation
    json_payload = {
        "custom_fields": deepcopy(json_payload["custom_fields"]),
        "metadata": deepcopy(json_payload["metadata"]),
        "pids": json_payload["pids"],
    }
    json_payload["access"] = {"record": "public", "files": "public"}
    json_payload["files"] = {"enabled": True}
    if "rights" in json_payload["metadata"].keys():
        json_payload["metadata"]["rights"] = [
            {"id": json_payload["metadata"]["rights"][0]["id"]}
        ]

    # prepare expected json for output (some differences from input)
    # REMEMBER: normalized here to simulate normalized output with
    # odd input
    expected_json = deepcopy(expected_json)
    if "description" in expected_json["metadata"].keys():
        expected_json["metadata"]["description"] = _normalize_punctuation(
            _clean_string(expected_json["metadata"]["description"])
        )
    if "additional_descriptions" in expected_json["metadata"].keys():
        expected_json["metadata"]["additional_descriptions"][0][
            "description"
        ] = _normalize_punctuation(
            _clean_string(
                expected_json["metadata"]["additional_descriptions"][0][
                    "description"
                ]
            )
        )

    # Create record and sanitize the result to ease comparison
    actual = create_invenio_record(json_payload)
    actual_id = actual["json"]["id"]
    actual_parent = actual["json"]["parent"]["id"]
    actual["json"]["metadata"]["resource_type"] = {
        "id": actual["json"]["metadata"]["resource_type"]["id"]
    }
    for idx, c in enumerate(actual["json"]["metadata"]["creators"]):
        if "role" in c.keys() and "de" in c["role"]["title"].keys():
            del actual["json"]["metadata"]["creators"][idx]["role"]["title"][
                "de"
            ]
    if "contributors" in actual["json"]["metadata"].keys():
        for idx, c in enumerate(actual["json"]["metadata"]["contributors"]):
            if "role" in c.keys() and "de" in c["role"]["title"].keys():
                del actual["json"]["metadata"]["contributors"][idx]["role"][
                    "title"
                ]["de"]
    if "description" in actual["json"]["metadata"].keys():
        actual["json"]["metadata"]["description"] = _normalize_punctuation(
            _clean_string(actual["json"]["metadata"]["description"])
        )
    if "additional_descriptions" in actual["json"]["metadata"].keys():
        for idx, d in enumerate(
            actual["json"]["metadata"]["additional_descriptions"]
        ):
            if "de" in d["type"]["title"].keys():
                del actual["json"]["metadata"]["additional_descriptions"][idx][
                    "type"
                ]["title"]["de"]
            actual["json"]["metadata"]["additional_descriptions"][idx][
                "description"
            ] = _normalize_punctuation(
                _clean_string(
                    actual["json"]["metadata"]["additional_descriptions"][idx][
                        "description"
                    ]
                )
            )
    # Test response content
    simple_fields = [
        f
        for f in actual["json"].keys()
        if f
        not in [
            "links",
            "parent",
            "id",
            "created",
            "updated",
            "versions",
            "expires_at",
            "is_draft",
            "access",
            "files",
            "status",
            "revision_id",
            "is_published",
        ]
    ]
    for s in simple_fields:
        print(actual["json"][s])
        if s == "errors":
            print("*****")
            pprint(actual["json"]["errors"])
        assert actual["json"][s] == expected_json[s]
    assert actual["json"]["versions"] == {
        "is_latest_draft": True,
        "index": 1,
        "is_latest": False,
    }
    assert actual["json"]["is_draft"] == True
    assert actual["json"]["access"] == {
        "files": "public",
        "embargo": {"active": False, "reason": None},
        "record": "public",
        "status": "metadata-only",
    }
    assert actual["json"]["status"] == "draft"
    assert type(actual["json"]["revision_id"]) == int
    assert actual["json"]["is_published"] == False

    links = {
        "self": f"https://{TESTING_SERVER_DOMAIN}/api/records/###/draft",
        "self_html": f"https://{TESTING_SERVER_DOMAIN}/uploads/###",
        "self_iiif_manifest": (
            f"https://{TESTING_SERVER_DOMAIN}/api/iiif/draft:###/manifest"
        ),
        "self_iiif_sequence": f"https://{TESTING_SERVER_DOMAIN}/api/iiif/draft:###/sequence/default",
        "files": (
            f"https://{TESTING_SERVER_DOMAIN}/api/records/###/draft/files"
        ),
        "archive": f"https://{TESTING_SERVER_DOMAIN}/api/records/###/draft/files-archive",
        "record": f"https://{TESTING_SERVER_DOMAIN}/api/records/###",
        "record_html": f"https://{TESTING_SERVER_DOMAIN}/records/###",
        "publish": f"https://{TESTING_SERVER_DOMAIN}/api/records/###/draft/actions/publish",
        "review": (
            f"https://{TESTING_SERVER_DOMAIN}/api/records/###/draft/review"
        ),
        "versions": (
            f"https://{TESTING_SERVER_DOMAIN}/api/records/###/versions"
        ),
        "access_links": (
            f"https://{TESTING_SERVER_DOMAIN}/api/records/###/access/links"
        ),
        "reserve_doi": (
            f"https://{TESTING_SERVER_DOMAIN}/api/records/###/draft/pids/doi"
        ),
        "communities": (
            f"https://{TESTING_SERVER_DOMAIN}/api/records/###/communities"
        ),
        "communities-suggestions": f"https://{TESTING_SERVER_DOMAIN}/api/records/###/communities-suggestions",
        "requests": (
            f"https://{TESTING_SERVER_DOMAIN}/api/records/###/requests"
        ),
    }
    actual_doi = ""
    if "doi" in actual["json"]["links"].keys():
        actual_doi = actual["json"]["pids"]["doi"]["identifier"]
        links["doi"] = "https://handle.stage.datacite.org/$$$"
    for label, link in actual["json"]["links"].items():
        assert link == links[label].replace("###", actual_id).replace(
            "$$$", actual_doi
        )

    assert actual["json"]["files"] == {
        "enabled": True,
        "entries": {},
        "count": 0,
        "order": [],
        "total_bytes": 0,
    }
    assert valid_date(actual["json"]["created"])
    assert isoparse(actual["json"]["created"]) - pytz.utc.localize(
        datetime.datetime.utcnow()
    ) <= datetime.timedelta(seconds=60)
    assert valid_date(actual["json"]["updated"])
    assert isoparse(actual["json"]["updated"]) - pytz.utc.localize(
        datetime.datetime.utcnow()
    ) <= datetime.timedelta(seconds=60)
    print("ACTUAL &&&&")
    pprint(actual)

    # Confirm the record is retrievable
    confirm_created = api_request(
        "GET", endpoint="records", args=f"{actual_id}/draft"
    )
    pprint(actual_id)
    pprint(confirm_created)
    print("Confirming record was created...")
    assert confirm_created["status_code"] == 200

    # Clean up created record from live db
    deleted = delete_invenio_draft_record(actual_id)
    assert deleted["status_code"] == 204

    # # Confirm it no longer exists
    confirm_deleted = api_request(
        "GET", endpoint="records", args=f"{actual_id}"
    )
    assert confirm_deleted["status_code"] == 404


def test_upload_draft_files():
    my_record = json42615

    json_payload = {
        "custom_fields": my_record["custom_fields"],
        "metadata": my_record["metadata"],
        "pids": my_record["pids"],
    }
    json_payload["access"] = {"record": "public", "files": "public"}
    json_payload["files"] = {"enabled": True}

    actual_draft = create_invenio_record(json_payload)
    actual_draft_id = actual_draft["json"]["id"]

    files_in = {
        "palazzo-vernacular_patterns_in_portugal_and_brazil-2021.pdf": (
            "/srv/www/commons/current/web/app/uploads"
            "/humcore/2021/11/o_1fk563qmpqgs1on0ue"
            "g6mfcf7.pdf.palazzo-vernacular_pa"
            "tterns_in_portugal_and_brazil-2021.pdf"
        )
    }

    actual_upload = upload_draft_files(
        draft_id=actual_draft_id, files_dict=files_in
    )
    pprint(actual_upload)
    for k, v in actual_upload["file_transactions"].items():
        assert k in files_in.keys()
        assert valid_date(v["upload_commit"]["json"]["created"])
        assert valid_date(v["upload_commit"]["json"]["updated"])
        assert v["upload_commit"]["json"]["status"] == "completed"
        assert v["upload_commit"]["json"]["metadata"] == None
    assert actual_upload["confirmation"]["status_code"] == 200


def test_create_invenio_community():
    slug = "mla"
    actual_community = create_invenio_community(slug)
    actual_community_id = actual_community["json"]["id"]
    assert actual_community["status_code"] == 201
    assert actual_community["json"]["metadata"]["slug"] == slug

    # Clean up created record from live db
    deleted = api_request(
        "DELETE", endpoint="communities", args=actual_community_id
    )
    assert deleted["status_code"] == 204

    # Confirm it no longer exists
    confirm_deleted = api_request(
        "GET", endpoint="communities", args=actual_community_id
    )
    assert confirm_deleted["status_code"] == 404


@pytest.mark.parametrize("json_in", [(json42615)])
def test_create_full_invenio_record(json_in):
    # random doi necessary because repeat tests with same data
    # can't re-use record's doi
    random_doi = json_in["pids"]["doi"]["identifier"].split("-")[0]
    random_doi = f"{random_doi}-{generate_random_string(5)}"
    json_in["pids"]["doi"]["identifier"] = random_doi
    actual_full_record = create_full_invenio_record(json_in)
    assert (
        actual_full_record["community"]["json"]["metadata"]["website"]
        == f'https://{json_in["custom_fields"]["kcr:commons_domain"]}'
    )
    assert actual_full_record["community"]["status_code"] == 200
    assert (
        actual_full_record["community"]["json"]["access"]["record_policy"]
        == "open"
    )
    assert (
        actual_full_record["community"]["json"]["access"]["review_policy"]
        == "open"
    )

    assert (
        actual_full_record["metadata_record_created"]["json"]["access"][
            "files"
        ]
        == "public"
    )
    assert (
        actual_full_record["metadata_record_created"]["json"]["access"][
            "record"
        ]
        == "public"
    )
    assert (
        actual_full_record["metadata_record_created"]["json"]["access"][
            "status"
        ]
        == "metadata-only"
    )
    assert (
        actual_full_record["metadata_record_created"]["json"]["is_draft"]
        == True
    )
    assert (
        actual_full_record["metadata_record_created"]["json"]["is_published"]
        == False
    )

    afu = actual_full_record["uploaded_files"]
    for k, v in json_in["files"]["entries"].items():
        actual_trans = afu["file_transactions"][k]
        assert actual_trans["content_upload"]["json"]["key"] == k
        assert actual_trans["content_upload"]["status_code"] == 200
        assert actual_trans["upload_commit"]["status_code"] == 200
        assert actual_trans["upload_commit"]["json"]["key"] == k
        assert actual_trans["upload_commit"]["json"]["size"] > 1000
        assert actual_trans["upload_commit"]["json"]["status"] == "completed"
        assert valid_date(actual_trans["upload_commit"]["json"]["created"])
        assert valid_date(actual_trans["upload_commit"]["json"]["updated"])
        assert afu["confirmation"]["status_code"] == 200

    assert type(actual_full_record["created_user"]["new_user"]) == bool
    assert int(actual_full_record["created_user"]["user_id"]) > 2 < 10000

    assert actual_full_record["request_to_community"]["status_code"] == 200
    assert valid_date(
        actual_full_record["request_to_community"]["json"]["created"]
    )
    assert actual_full_record["request_to_community"]["json"][
        "created_by"
    ] == {"user": "3"}
    assert (
        actual_full_record["request_to_community"]["json"]["is_closed"]
        == False
    )
    assert (
        actual_full_record["request_to_community"]["json"]["is_expired"]
        == False
    )
    assert (
        actual_full_record["request_to_community"]["json"]["is_open"] == False
    )
    assert (
        actual_full_record["request_to_community"]["json"]["receiver"][
            "community"
        ]
        == actual_full_record["community"]["json"]["id"]
    )
    assert (
        actual_full_record["request_to_community"]["json"]["status"]
        == "created"
    )
    assert (
        actual_full_record["request_to_community"]["json"]["type"]
        == "community-submission"
    )
    assert actual_full_record["request_to_community"]["json"]["topic"] == {
        "record": actual_full_record["metadata_record_created"]["json"]["id"]
    }

    assert valid_date(
        actual_full_record["review_submitted"]["json"]["created"]
    )
    assert (
        actual_full_record["review_submitted"]["json"]["created_by"]["user"]
        == "3"
    )
    assert actual_full_record["review_submitted"]["json"]["is_closed"] == False
    assert actual_full_record["review_submitted"]["json"]["is_open"] == True
    assert (
        actual_full_record["review_submitted"]["json"]["receiver"]["community"]
        == actual_full_record["community"]["json"]["id"]
    )
    assert (
        actual_full_record["review_submitted"]["json"]["status"] == "submitted"
    )
    assert (
        actual_full_record["review_submitted"]["json"]["topic"]["record"]
        == actual_full_record["metadata_record_created"]["json"]["id"]
    )
    assert (
        actual_full_record["review_submitted"]["json"]["title"]
        == actual_full_record["metadata_record_created"]["json"]["metadata"][
            "title"
        ]
    )
    assert (
        actual_full_record["review_submitted"]["json"]["type"]
        == "community-submission"
    )
    assert actual_full_record["review_submitted"]["status_code"] == 200

    assert actual_full_record["review_accepted"]["json"]["is_closed"] == True
    assert actual_full_record["review_accepted"]["json"]["is_open"] == False
    assert (
        actual_full_record["review_accepted"]["json"]["receiver"]["community"]
        == actual_full_record["community"]["json"]["id"]
    )
    assert (
        actual_full_record["review_accepted"]["json"]["status"] == "accepted"
    )
    assert (
        actual_full_record["review_accepted"]["json"]["topic"]["record"]
        == actual_full_record["metadata_record_created"]["json"]["id"]
    )
    assert (
        actual_full_record["review_accepted"]["json"]["title"]
        == actual_full_record["metadata_record_created"]["json"]["metadata"][
            "title"
        ]
    )
    assert (
        actual_full_record["review_accepted"]["json"]["type"]
        == "community-submission"
    )
    assert actual_full_record["review_accepted"]["status_code"] == 200

    assert actual_full_record["changed_ownership"]["return_code"] == 0
    print(actual_full_record)


@pytest.mark.parametrize(
    "email_in,new_user_flag",
    [("myaddress3@somedomain.edu", True), ("scottia4@msu.edu", False)],
)
def test_create_invenio_user(email_in, new_user_flag):
    actual_user = create_invenio_user(email_in)
    print(actual_user)
    assert re.match(r"\d+", actual_user["user_id"])
    assert actual_user["new_user"] == new_user_flag


def test_record_loader():
    runner = CliRunner()
    result = runner.invoke(cli, ["load", "0", "1"])
    assert result.exit_code == 0
    assert "Finished!" in result.output
    assert "Created 1 records in InvenioRDM" in result.output
