from click.testing import CliRunner
from core_migrate import parse_csv
import pytest

json16079 = {
    'pids': {'doi': {'client': 'datacite',
                     'identifier': 'doi:10.17613/M6M225',
                     'provider': 'datacite'}
             },
    'custom_fields': {'hclegacy:groups_for_deposit': [{'group_identifier': '1000551',
                                                     'group_name': 'Digital '
                                                                   'Humanists'},
                                                    {'group_identifier': '1000697',
                                                     'group_name': 'Textual '
                                                                   'Scholarship'}],
                    'hclegacy:publication_type': 'proceedings-article',
                    'hclegacy:submitter_id': 1010997,
                    'imprint:imprint': {'title': 'DHBenelux 2. Book of '
                                                 'Abstracts for the Second '
                                                 'Digital Humanities Benelux '
                                                 'Conference'},
                    'kcr:commons_domain': 'hcommons.org',
                    'kcr:meeting_organization': 'University of Antwerp',
                    'kcr:submitter_email': 'wout.dillen@uantwerpen.be',
                    'kcr:submitter_username': 'woutdillen',
                    'meeting:meeting': {'dates': '8-9 June 2015',
                                        'place': 'Antwerp, Belgium',
                                        'title': 'DH Benelux 2015'}},
  'files': {'entries': []},
  'metadata': {'additional_descriptions': [{'description': 'Within the field '
                                                           'of genetic '
                                                           'criticism, '
                                                           'Raymonde Debray '
                                                           'Genette coined the '
                                                           'terms ‘en- '
                                                           'dogenesis’ and '
                                                           '‘exogenesis’ to '
                                                           'denote '
                                                           'respectively the '
                                                           'writing of drafts '
                                                           'and the '
                                                           'interaction with '
                                                           'external source '
                                                           'texts during the '
                                                           'writing process. '
                                                           'The proposed panel '
                                                           'focuses on the '
                                                           'ways in which '
                                                           'exogenesis and its '
                                                           'relationship with '
                                                           'endogenesis can be '
                                                           'given shape in a '
                                                           'digital '
                                                           'infrastructure. '
                                                           'The case studies '
                                                           'are the works, '
                                                           'reading notes and '
                                                           'personal libraries '
                                                           'of James Joyce and '
                                                           'Samuel Beckett.',
                                            'type': {'id': 'other',
                                                     'title': {'en': 'Primary '
                                                                     'description '
                                                                     'with '
                                                                     'HTML '
                                                                     'stripped'}}}],
               'additional_titles': [{'title': 'Digitization and Exogenesis',
                                      'type': {'id': 'other',
                                               'title': {'en': 'Primary title '
                                                               'with HTML '
                                                               'stripped'}}}],
               'creators': [{'person_or_org': {'family_name': 'Crowley',
                                               'given_name': 'Ronan',
                                               'name': 'Ronan Crowley',
                                               'type': 'personal'},
                             'role': {'id': 'author'}},
                            {'person_or_org': {'family_name': 'De Keyser',
                                               'given_name': 'Tom',
                                               'name': 'Tom De Keyser',
                                               'type': 'personal'},
                             'role': {'id': 'author'}},
                            {'person_or_org': {'family_name': 'Dillen',
                                               'given_name': 'Wout',
                                               'identifiers': [{'identifier': 'woutdillen',
                                                                'scheme': 'hc_username'}],
                                               'name': 'Wout Dillen',
                                               'type': 'personal'},
                             'role': {'id': 'author'}},
                            {'person_or_org': {'family_name': 'Neyt',
                                               'given_name': 'Vincent',
                                               'name': 'Vincent Neyt',
                                               'type': 'personal'},
                             'role': {'id': 'author'}},
                            {'person_or_org': {'family_name': 'Van Hulle',
                                               'given_name': 'Dirk',
                                               'name': 'Dirk Van Hulle',
                                               'type': 'personal'},
                             'role': {'id': 'author'}}],
               'description': 'Within the field of genetic criticism, Raymonde '
                              'Debray Genette coined the terms ‘en- dogenesis’ '
                              'and ‘exogenesis’ to denote respectively the '
                              'writing of drafts and the interaction with '
                              'external source texts during the writing '
                              'process. The proposed panel focuses on the ways '
                              'in which exogenesis and its relationship with '
                              'endogenesis can be given shape in a digital '
                              'infrastructure. The case studies are the works, '
                              'reading notes and personal libraries of James '
                              'Joyce and Samuel Beckett.',
               'formats': [],
               'identifiers': [{'identifier': 'hc:16079',
                                'scheme': 'hclegacy'},
                               {'identifier': 'https://doi.org/10.5281/zenodo.1009526',
                                'scheme': 'doi'}],
               'languages': [],
               'resource_type': {'id': 'publication:conferenceProceeding'},
               'rights': [],
               'subjects': [],
               'publication_date': '2015',
               'dates': [{'date': '8 June 2015',
                          'description': 'Human readable publication date',
                          'type': {'id': 'issued',
                          'title': {'en': 'Issued'}}}
                         ],
               'title': 'Digitization and Exogenesis'},
  'parent': {'access': {'owned_by': [{'user': 1010997}]}}}

json34031 = {
    'pids': {'doi': {'client': 'datacite',
                            'identifier': 'doi:10.17613/0qxh-ed23',
                            'provider': 'datacite'}},
'custom_fields': {'hclegacy:submitter_id': 1025015,
                    'hclegacy:submitter_org_memberships': ['Rice University'],
                    'imprint:imprint': {'creators': [{'person_or_org': {'family_name': 'DeConick',
                                                                        'given_name': 'April',
                                                                        'name': 'April '
                                                                                'DeConick',
                                                                        'type': 'personal'},
                                                      'role': {'id': 'author'}}],
                                        'title': 'Secret Religion:'},
                    'kcr:commons_domain': 'hcommons.org',
                    'kcr:submitter_email': 'mjdillon@alumni.rice.edu',
                    'kcr:submitter_username': 'matthewjdillon'},
  'files': {'entries': []},
  'metadata': {'additional_descriptions': [{'description': 'Overview of the '
                                                           'major trends and '
                                                           'approaches to the '
                                                           'study of '
                                                           "'Gnosticism' after "
                                                           'the discovery of '
                                                           'the Nag Hammadi '
                                                           'Codices.',
                                            'type': {'id': 'other',
                                                     'title': {'en': 'Primary '
                                                                     'description '
                                                                     'with '
                                                                     'HTML '
                                                                     'stripped'}}}],
               'publication_date': '2016',
               'additional_titles': [{'title': 'Gnosticism Theorized: Major '
                                               'Trends and Approaches to the '
                                               'Study of Gnosticism',
                                      'type': {'id': 'other',
                                               'title': {'en': 'Primary title '
                                                               'with HTML '
                                                               'stripped'}}}],
               'creators': [{'affiliations': ['Rice University'],
                             'person_or_org': {'family_name': 'Dillon',
                                               'given_name': 'M.',
                                               'identifiers': [{'identifier': 'matthewjdillon',
                                                                'scheme': 'hc_username'}],
                                               'name': 'M. Dillon',
                                               'type': 'personal'},
                             'role': {'id': 'author'}}],
               'dates': [],
               'description': 'Overview of the major trends and approaches to '
                              "the study of 'Gnosticism' after the discovery "
                              'of the Nag Hammadi Codices.',
               'formats': [],
               'identifiers': [{'identifier': 'hc:34031',
                                'scheme': 'hclegacy'}],
               'languages': [],
               'resource_type': {'id': 'publication:bookChapter'},
               'rights': [],
               'subjects': [],
               'title': 'Gnosticism Theorized: Major Trends and Approaches to '
                        'the Study of Gnosticism'},
  'parent': {'access': {'owned_by': [{'user': 1025015}]}}
  }


json11451 = {
    'pids': {'doi': {'client': 'datacite',
                               'identifier': 'doi:10.17613/M6733G',
                               'provider': 'datacite'}},
    'custom_fields': {'hclegacy:groups_for_deposit': [{'group_identifier': '174',
                                                     'group_name': 'East Asian '
                                                                   'Languages '
                                                                   'and '
                                                                   'Literatures '
                                                                   'after '
                                                                   '1900'},
                                                    {'group_identifier': '246',
                                                     'group_name': 'Global '
                                                                   'Shakespeares'},
                                                    {'group_identifier': '97',
                                                     'group_name': 'GS Drama '
                                                                   'and '
                                                                   'Performance'},
                                                    {'group_identifier': '25',
                                                     'group_name': 'LLC '
                                                                   'Shakespeare'},
                                                    {'group_identifier': '91',
                                                     'group_name': 'TC '
                                                                   'Translation '
                                                                   'Studies'}],
                    'hclegacy:submitter_id': 49,
                    'hclegacy:submitter_org_memberships': ['George Washington '
                                                           'U'],
                    'imprint:imprint': {'creators': [{'person_or_org': {'family_name': 'Peterson',
                                                                        'given_name': 'Kaara',
                                                                        'name': 'Kaara '
                                                                                'Peterson',
                                                                        'type': 'personal'},
                                                      'role': {'id': 'author'}},
                                                     {'person_or_org': {'family_name': 'Williams',
                                                                        'given_name': 'Deanne',
                                                                        'name': 'Deanne '
                                                                                'Williams',
                                                                        'type': 'personal'},
                                                      'role': {'id': 'author'}}],
                                        'title': 'The Afterlife of Ophelia'},
                    'kcr:chapter_label': '5',
                    'kcr:commons_domain': 'mla.hcommons.org',
                    'kcr:submitter_email': 'ajoubin@gwu.edu',
                    'kcr:submitter_username': 'joubin'},
  'files': {'entries': []},
  'metadata': {'additional_descriptions': [{'description': 'There are three '
                                                           'main East Asian '
                                                           'approaches to '
                                                           'interpreting '
                                                           'Ophelia. The first '
                                                           'is informed by the '
                                                           'fascination with '
                                                           'and reaction '
                                                           'against the '
                                                           'Victorian '
                                                           'pictorialization '
                                                           'of Ophelia, '
                                                           'especially John '
                                                           'Everett Millais’s '
                                                           'famous Ophelia '
                                                           '(1851), that '
                                                           'emphasized, as '
                                                           'Kimberly Rhodes '
                                                           'describes, her '
                                                           '“pathos, '
                                                           'innocence, and '
                                                           'beauty rather than '
                                                           'the unseemly '
                                                           'detail of her '
                                                           'death.” Despite '
                                                           'having lived '
                                                           'through negative '
                                                           'experiences, '
                                                           'Ophelia retains a '
                                                           'childlike '
                                                           'innocence in these '
                                                           'rewritings. For '
                                                           'example, New '
                                                           'Hamlet by Lao She '
                                                           '(penname of Shu '
                                                           'Qingchun, '
                                                           '1899-1966) '
                                                           'parodies China’s '
                                                           '“Hamlet complex” '
                                                           '(the inability to '
                                                           'act at a time of '
                                                           'national crisis) '
                                                           'and the '
                                                           'fascination with '
                                                           'an Ophelia '
                                                           'submerged in '
                                                           'water. Both '
                                                           'Ophelia and '
                                                           'Millais’s painting '
                                                           'are featured in '
                                                           'two of Japanese '
                                                           'writer Natsume '
                                                           'Sōseki’s early '
                                                           'twentieth-century '
                                                           'novels. A second '
                                                           'approach '
                                                           'emphasizes the '
                                                           'local context. '
                                                           'Adapters used '
                                                           'local values to '
                                                           'engage with and '
                                                           'even critique the '
                                                           'Victorian '
                                                           'narrative '
                                                           'tradition of '
                                                           'moralization. Late '
                                                           'nineteenth-century '
                                                           'translator Lin Shu '
                                                           '(1852-1924), for '
                                                           'example, tones '
                                                           'down the '
                                                           'sentimentalization '
                                                           'of Ophelia in his '
                                                           'classical Chinese '
                                                           'rewriting of '
                                                           'Charles and Mary '
                                                           'Lamb’s Tales from '
                                                           'Shakespeare, '
                                                           'showcasing the '
                                                           'conflict between '
                                                           'Victorian and '
                                                           'Confucian moral '
                                                           'codes. The third '
                                                           'approach focuses '
                                                           'upon an '
                                                           'objectified and '
                                                           'sexualized '
                                                           'Ophelia. As other '
                                                           'chapters in this '
                                                           'volume '
                                                           'demonstrate, this '
                                                           'is not exclusively '
                                                           'an Asian '
                                                           'phenomenon. '
                                                           'However, the '
                                                           'eroticism '
                                                           'associated with '
                                                           'the Ophelia figure '
                                                           'in a number of '
                                                           'Asian stage and '
                                                           'screen versions of '
                                                           'Hamlet, such as '
                                                           'Sherwood Hu’s film '
                                                           'Prince of the '
                                                           'Himalayas (2006), '
                                                           'aligns Ophelia '
                                                           'with East Asian '
                                                           'ideals of '
                                                           'femininity, but '
                                                           'also brings out '
                                                           'the sexuality that '
                                                           'is latent or '
                                                           'suppressed in '
                                                           'Victorian '
                                                           'interpretations. '
                                                           'They do so by '
                                                           'aligning Ophelia '
                                                           'with East Asian '
                                                           'ideals of '
                                                           'femininity.',
                                            'type': {'id': 'other',
                                                     'title': {'en': 'Primary '
                                                                     'description '
                                                                     'with '
                                                                     'HTML '
                                                                     'stripped'}}}],
               'additional_titles': [{'title': 'The Paradox of Female Agency: '
                                               'Ophelia and East Asian '
                                               'Sensibilities',
                                      'type': {'id': 'other',
                                               'title': {'en': 'Primary title '
                                                               'with HTML '
                                                               'stripped'}}}],
               'creators': [{'affiliations': ['George Washington U'],
                             'person_or_org': {'family_name': 'Alice Joubin',
                                               'given_name': 'Alexa',
                                               'identifiers': [{'identifier': 'joubin',
                                                                'scheme': 'hc_username'}],
                                               'name': 'Alexa Alice Joubin',
                                               'type': 'personal'},
                             'role': {'id': 'author'}}],
               'dates': [],
               'publication_date': '2012',
               'description': 'There are three main East Asian approaches to '
                              'interpreting Ophelia. The first is informed by '
                              'the fascination with and reaction against the '
                              'Victorian pictorialization of Ophelia, '
                              'especially John Everett Millais’s famous '
                              'Ophelia (1851), that emphasized, as Kimberly '
                              'Rhodes describes, her “pathos, innocence, and '
                              'beauty rather than the unseemly detail of her '
                              'death.”  Despite having lived through negative '
                              'experiences, Ophelia retains a childlike '
                              'innocence in these rewritings. For example, New '
                              'Hamlet by Lao She (penname of Shu Qingchun, '
                              '1899-1966) parodies China’s “Hamlet complex” '
                              '(the inability to act at a time of national '
                              'crisis) and the fascination with an Ophelia '
                              'submerged in water. Both Ophelia and Millais’s '
                              'painting are featured in two of Japanese writer '
                              'Natsume Sōseki’s early twentieth-century '
                              'novels. A second approach emphasizes the local '
                              'context. Adapters used local values to engage '
                              'with and even critique the Victorian narrative '
                              'tradition of moralization. Late '
                              'nineteenth-century translator Lin Shu '
                              '(1852-1924), for example, tones down the '
                              'sentimentalization of Ophelia in his classical '
                              'Chinese rewriting of Charles and Mary Lamb’s '
                              'Tales from Shakespeare, showcasing the conflict '
                              'between Victorian and Confucian moral codes. '
                              'The third approach focuses upon an objectified '
                              'and sexualized Ophelia. As other chapters in '
                              'this volume demonstrate, this is not '
                              'exclusively an Asian phenomenon. However, the '
                              'eroticism associated with the Ophelia figure in '
                              'a number of Asian stage and screen versions of '
                              'Hamlet, such as Sherwood Hu’s film Prince of '
                              'the Himalayas (2006), aligns Ophelia with East '
                              'Asian ideals of femininity, but also brings out '
                              'the sexuality that is latent or suppressed in '
                              'Victorian interpretations. They do so by '
                              'aligning Ophelia with East Asian ideals of '
                              'femininity.',
               'formats': [],
               'identifiers': [{'identifier': 'hc:11451',
                                'scheme': 'hclegacy'},
                               {'identifier': '10.1057/9781137016461',
                                'scheme': 'doi'}],
               'languages': [],
               'resource_type': {'id': 'publication:bookChapter'},
               'rights': [],
               'subjects': [],
               'title': 'The Paradox of Female Agency: Ophelia and East Asian '
                        'Sensibilities'},
  'parent': {'access': {'owned_by': [{'user': 49}]}}}

json22647 = {
    'pids': {'doi': {'client': 'datacite',
                               'identifier': 'doi:10.17613/1d2d-2y15',
                               'provider': 'datacite'}},
    'custom_fields': {
        'hclegacy:groups_for_deposit': [{'group_identifier': '1000636',
                                                     'group_name': 'Ancient '
                                                                   'Greece '
                                                                   '&amp; '
                                                                   'Rome'},
                                                    {'group_identifier': '1000816',
                                                     'group_name': 'Classical '
                                                                   'Tradition'},
                                                    {'group_identifier': '1000630',
                                                     'group_name': 'Poetics '
                                                                   'and '
                                                                   'Poetry'}],
        'hclegacy:submitter_id': 1012453,
        'hclegacy:submitter_org_memberships': ['Liverpool Hope University'],
        'imprint:imprint': {
            'creators': [
                {'person_or_org': {'family_name': 'Macintosh',
                                  'given_name': 'Fiona',
                                  'name': 'Fiona Macintosh',
                                  'type': 'personal'},
                'role': {'id': 'author'}
                },
                {'person_or_org': {'family_name': 'McConnell',
                                   'given_name': 'Justine',
                                   'name': 'Justine McConnell',
                                   'type': 'personal'},
                 'role': {'id': 'author'}
                 },
                {'person_or_org': {'family_name': 'Harrison',
                                   'given_name': 'Stephen',
                                   'name': 'Stephen Harrison',
                                   'type': 'personal'},
                 'role': {'id': 'author'}
                 },
                {'person_or_org': {'family_name': 'Harrison',
                                   'given_name': 'Stephen',
                                   'name': 'Stephen Harrison',
                                   'type': 'personal'},
                 'role': {'id': 'author'}
                 },
                {'person_or_org': {'family_name': 'Kenward',
                                   'given_name': 'Claire',
                                   'name': 'Claire Kenward',
                                   'type': 'personal'},
                 'role': {'id': 'author'}
                 }
            ],
            'title': 'Epic Performances from the Middle Ages into the '
                     'Twenty-First Century'},
        'kcr:commons_domain': 'hcommons.org',
        'kcr:chapter_label': '18 - Unfixing Epic: Homeric Orality '
                             'and Contemporary Performance',
        'kcr:submitter_email': 'stephe_harrop@hotmail.co.uk',
        'kcr:submitter_username': 'stepheharrop'},
    'files': {'entries': []},
    'metadata': {
        'additional_descriptions': [
            {'description': 'This chapter examines the '
                            'impact of a putative oral '
                            'Homer upon the work of recent '
                            'performance-makers. The influence of '
                            'oral-poetic theories is (as '
                            'yet) an under-explored '
                            'area of study, neglected by '
                            'scholars whose literary expertise '
                            'leads them to focus on dramatic '
                            'texts and production '
                            'histories, with each revisionary '
                            'text or production regarded as a '
                            'single, stable, and repeatable '
                            'entity. The field of classical '
                            'reception studies at present lacks '
                            'the conceptual and theoretical means '
                            'to engage effectively with '
                            'works which deliberately '
                            'exploit elements of ‘in-performance’ '
                            'composition, and which positively '
                            'value the qualities of '
                            'fluidity and flexibility evoked '
                            'by oral-poetic interpretations of '
                            'ancient epic. However, the '
                            'present work contends that a '
                            'notional oral Homer informs a '
                            'diverse array of contemporary '
                            'theatre texts and performance '
                            'practices,  and that a full '
                            'appreciation of the different ways '
                            'in which oral-poetic theory '
                            'can influence the creation of these '
                            'depends upon an ability to '
                            'identify and interpret the '
                            'interplay between ‘fixed’ and '
                            '‘unfixed’ elements both within particular '
                            'performances, and within different '
                            'iterations of the same production or '
                            'event. Kate Tempest’s '
                            'performance-poem Brand New Ancients '
                            'is analysed as a striking recent '
                            'example of creative interplay '
                            'between such ‘fixed’ and '
                            '‘unfixed’ elements.',
            'type': {'id': 'other',
                     'title': {'en': 'Primary description with '
                                     'HTML stripped'}
                     }
            }
        ],
        'additional_titles': [
            {'title': 'Unfixing Epic: Homeric Orality '
                      'and Contemporary Performance',
             'type': {'id': 'other',
                      'title': {'en': 'Primary title with HTML stripped'}}
             }
        ],
        'creators': [
            {'affiliations': ['Liverpool Hope University'],
             'person_or_org': {'family_name': 'Harrop',
                               'given_name': 'Stephe',
                               'identifiers': [{'identifier': 'stepheharrop',
                                                'scheme': 'hc_username'}],
                               'name': 'Stephe Harrop',
                               'type': 'personal'
                               },
             'role': {'id': 'author'}}],
        'publication_date': '2018',
        'dates': [],
        'description': 'This chapter examines the impact of a putative '
                        'oral Homer upon the work of recent '
                        'performance-makers. The influence of '
                        'oral-poetic theories is (as yet) an '
                        'under-explored area of study, neglected by '
                        'scholars whose literary expertise leads them to '
                        'focus on dramatic texts and production '
                        'histories, with each revisionary text or '
                        'production regarded as a single, stable, and '
                        'repeatable entity. The field of classical '
                        'reception studies at present lacks the '
                        'conceptual and theoretical means to engage '
                        'effectively with works which deliberately '
                        'exploit elements of ‘in-performance’ '
                        'composition, and which positively value the '
                        'qualities of fluidity and flexibility evoked by '
                        'oral-poetic interpretations of ancient epic. '
                        'However, the present work contends that a '
                        'notional oral Homer informs a diverse array of '
                        'contemporary theatre texts and performance '
                        'practices,  and that a full appreciation of the '
                        'different ways in which oral-poetic theory can '
                        'influence the creation of these depends upon an '
                        'ability to identify and interpret the interplay '
                        'between ‘fixed’ and ‘unfixed’ elements both '
                        'within particular performances, and within '
                        'different iterations of the same production or '
                        'event. Kate Tempest’s performance-poem Brand '
                        'New Ancients is analysed as a striking recent '
                        'example of creative interplay between such '
                        '‘fixed’ and ‘unfixed’ elements.',
        'formats': [],
        'identifiers': [{'identifier': 'hc:22647',
                         'scheme': 'hclegacy'}],
        'languages': [],
        'resource_type': {'id': 'publication:bookChapter'},
        'rights': [],
        'subjects': [],
        'title': 'Unfixing Epic: Homeric Orality and Contemporary '
                 'Performance'},
        'parent': {'access': {'owned_by': [{'user': 1012453}]}}}

json42615 = {
    'pids': {'doi': {'client': 'datacite',
                               'identifier': 'doi:10.17613/6v9q-8878',
                               'provider': 'datacite'}},
    'custom_fields': {
            'hclegacy:submitter_id': 1011841,
            'hclegacy:submitter_org_memberships': ['University of '
                                                   'Brasilia School of '
                                                   'Architecture and '
                                                   'Urbanism'],
            'journal:journal': {'title': 'Journal of Traditional '
                                         'Building, Architecture and '
                                         'Urbanism'},
            'kcr:commons_domain': 'sah.hcommons.org',
            'kcr:submitter_email': 'pedro.palazzo@gmail.com',
            'kcr:submitter_username': 'palazzo'},
    'files': {'entries': []},
    'metadata': {
        'additional_descriptions': [
            {'description':
                'Traditional towns in Portugal and Brazil have evolved a '
                'finely tuned coordination between, on the one hand, modular '
                'dimensions for street widths and lot sizes, and on '
                'the other, a typology of room shapes and layouts within '
                'houses. Despite being well documented in urban history, '
                'this coordination was in the last century often interpreted '
                'as contingent, a result of the limited material means of '
                'pre-industrial societies. But the continued application and '
                'gradual adaptation of these urban and architectural '
                'patterns through periods of industrialization and economic '
                'development suggests that they respond both to '
                'enduring housing requirements and to piecemeal urban '
                'growth. This article surveys the persistence of urban and '
                'architectural patterns up to the early 20th century, showing '
                'their resilience in addressing modern housing and '
                'urbanization requirements.',
             'type': {'id': 'other',
                      'title': {'en': 'Primary description with '
                                      'HTML stripped'}
                      }
             }
        ],
        'additional_titles': [
            {'title': 'Vernacular Patterns in Portugal and Brazil: Evolution '
                      'and Adaptations',
             'type': {'id': 'other',
                      'title': {'en': 'Primary title with HTML stripped'}}
             }
        ],
        'creators': [{'affiliations': ['University of Brasilia School '
                                       'of Architecture and Urbanism'],
                      'person_or_org': {'family_name': 'P. Palazzo',
                                        'given_name': 'Pedro',
                                        'identifiers': [{
                                            'identifier': 'palazzo',
                                            'scheme': 'hc_username'}],
                                        'name': 'Pedro P. Palazzo',
                                        'type': 'personal'},
                      'role': {'id': 'author'}}
                    ],
        'dates': [{'date': '2021-11-10',
                   'description': 'Human readable publication date',
                   'type': {'id': 'issued',
                   'title': {'en': 'Issued'}}}
                  ],
        'publication_date': '2021',
        'description': 'Traditional towns in Portugal and Brazil have '
                        'evolved a finely tuned coordination between, on '
                        'the one hand, modular dimensions for street '
                        'widths and lot sizes, and on the other, a '
                        'typology of room shapes and layouts within '
                        'houses. Despite being well documented in urban '
                        'history, this coordination was in the last '
                        'century often interpreted as contingent, a '
                        'result of the limited material means of '
                        'pre-industrial societies. But the continued '
                        'application and gradual adaptation of these '
                        'urban and architectural patterns through '
                        'periods of industrialization and economic '
                        'development suggests that they respond both to '
                        'enduring housing requirements and to piecemeal '
                        'urban growth. This article surveys the '
                        'persistence of urban and architectural patterns '
                        'up to the early 20th century, showing their '
                        'resilience in addressing modern housing and '
                        'urbanization requirements.',
        'formats': [],
        'identifiers': [{'identifier': 'hc:42615',
                         'scheme': 'hclegacy'}],
        'languages': [],
        'resource_type': {'id': 'publication:journalArticle'},
        'rights': [],
        'subjects': [],
        'title': 'Vernacular Patterns in Portugal and Brazil: Evolution '
                 'and Adaptations'},
    'parent': {
        'access': {'owned_by': [{'user': 1011841}]}
    }
}

json22625 = {
    'pids': {'doi': {'client': 'datacite',
                               'identifier': 'doi:10.17613/hrhn-3k43',
                               'provider': 'datacite'}},
    'custom_fields':
        {'kcr:submitter_email': "wojciech.tworek.09@ucl.ac.uk",
         'kcr:submitter_username': "wtworek",
         'kcr:commons_domain': 'ajs.hcommons.org',
         'hclegacy:submitter_id': 1017065,
         'hclegacy:submitter_org_memberships': ['University Of Toronto'],
         'imprint:imprint': {
             'creators': [
                 {'person_or_org': {'family_name': 'Sagiv',
                  'given_name': 'Gadi',
                  'name': 'Gadi Sagiv',
                  'type': 'personal'},
                  'role': {'id': 'author'}},
                 {'person_or_org': {'family_name': 'Meir',
                  'given_name': 'Jonatan',
                  'name': 'Jonatan Meir',
                  'type': 'personal'},
                  'role': {'id': 'author'}}],
             'title': 'Habad Hasidism: History, Thought, Image'
         },
         'hclegacy:groups_for_deposit': [
             {'group_identifier': '1000610',
              'group_name': 'Jewish Mysticism'},
             {'group_identifier': '1000611',
              'group_name': 'Modern Jewish Thought and Theology'}
         ]
         },
    'files':
        {'entries': []},
    'metadata':
        {'additional_descriptions':
            [{'description': ('The issue of gender has been a topic of '
                             'discussion in the research of Hasidism since S. '
                             'A. Horodecky’s book (1923), in which he '
                             'claimed that Hasidism brought about full ' 'equality of Jewish men and women in the field '
                             'of spirituality. Although his claims have been '
                             'by and large rejected, most\nscholars agree that '
                             'the twentieth century Chabad movement has '
                             'indeed created space for women in the hasidic '
                             'model of spirituality. This article sets out to '
                             'explore whether the particular interest of '
                             'contemporary Chabad in the role of women is a '
                             'new phenomenon or has existed from the '
                             'movement’s inception. Rather than looking at the '
                             'issue from a social-historical perspective, the '
                             'article examines the gender discourse conveyed '
                             'in the homilies of the founder of Chabad, Rabbi '
                             'Shneur Zalman of Liadi (1745–1812). It explores '
                             'the role of the feminine aspect of divinity in '
                             'the process of creation, and its envisioned '
                             'elevation in the future-to-come, in an attempt '
                             'to establish the relation between the gender '
                             'category of “female” and flesh-and-blood '
                             'women in the teachings of Shneur Zalman of '
                             'Liadi. This, in turn, leads to determine '
                             'whether the concept of the transfigurations of '
                             'genders in the future-to-come, a Chabad '
                             'tradition that originates in the teachings of '
                             'Shneur Zalman of Liadi and serves as '
                             'the ideological ground for the empowerment of '
                             'Chabad women in the writings of the late '
                             'Lubavitcher Rebbe in the twentieth century, '
                             'could have any relevance to the daily life of '
                             'wives and daughters of Shneur Zalman’s '
                             'followers.'),
              'type': {'id': 'other',
                       'title': {'en': 'Primary description with HTML '
                                       'stripped'}
                       }
            }],
            'additional_titles': [
                {'title': 'מגדר וזמן בכתבי ר׳ שניאור זלמן מלאדי',
                 'type': {'id': 'other',
                          'title': {'en': 'Primary title with HTML '
                                          'stripped'}}
                }
            ],
            'creators': [
                {'affiliations': ['University Of Toronto'],
                 'person_or_org': {'family_name': 'Tworek',
                                   'given_name': 'Wojciech',
                                   'identifiers': [{'identifier': 'wtworek',
                                                   'scheme': 'hc_username'}],
                                   'name': 'Wojciech Tworek',
                                   'type': 'personal'},
                 'role': {'id': 'author'}
                 }
            ],
            'dates': [],
            'publication_date': '2016',
            'description': 'The issue of gender has been a topic of '
                             'discussion in the research of Hasidism since S. '
                             'A. Horodecky’s book (1923), in which he claimed '
                             'that Hasidism brought about full equality of '
                             'Jewish men and women in the field of '
                             'spirituality. Although his claims have been by '
                             'and large rejected, most\n'
                             'scholars agree that the twentieth century Chabad '
                             'movement has indeed created space for women in '
                             'the hasidic model of spirituality. This article '
                             'sets out to explore whether the particular '
                             'interest of contemporary Chabad in the role of '
                             'women is a new phenomenon or has existed from '
                             'the movement’s inception. Rather than looking at '
                             'the issue from a social-historical perspective, '
                             'the article examines the gender discourse '
                             'conveyed in the homilies of the founder of '
                             'Chabad, Rabbi Shneur Zalman of Liadi '
                             '(1745–1812). It explores the role of the '
                             'feminine aspect of divinity in the process of '
                             'creation, and its envisioned elevation in the '
                             'future-to-come, in an attempt to establish the '
                             'relation between the gender category of “female” '
                             'and flesh-and-blood women in the teachings of '
                             'Shneur Zalman of Liadi. This, in turn, leads to '
                             'determine whether the concept of the '
                             'transfigurations of genders in the '
                             'future-to-come, a Chabad tradition that '
                             'originates in the teachings of Shneur Zalman of '
                             'Liadi and serves as the ideological ground for '
                             'the empowerment of Chabad women in the writings '
                             'of the late Lubavitcher Rebbe in the twentieth '
                             'century, could have any relevance to the daily '
                             'life of wives and daughters of Shneur Zalman’s '
                             'followers.',
            'formats': [],
            'identifiers': [{'identifier': 'hc:22625', 'scheme': 'hclegacy'}],
            'languages': [],
            'resource_type': {'id': 'publication:bookChapter'},
            'rights': [],
            'subjects': [],
            'title': 'מגדר וזמן בכתבי ר׳ שניאור זלמן מלאדי'},
    'parent': {'access': {'owned_by': [{'user': 1017065}]}}
}

json45177 = {
    'pids': {'doi': {'client': 'datacite',
                               'identifier': '10.17613/zhmh-c741',
                               'provider': 'datacite'}},
    'custom_fields': {
        'imprint:imprint': {
            'creators': [
                {'person_or_org':
                    {'family_name': '',
                     'given_name': '',
                     'name': 'ARLIS/NA Cataloging Advisory Committee',
                     'type': 'personal'},
                 'role': {'id': 'author'}
                 }
                ],
            'title': 'Cataloging Exhibition Publications: Best Practices'
         },
        'kcr:edition': '2',
        'kcr:submitter_email': "aprovo@gmail.com",
        'kcr:submitter_username': "aprovo",
        'kcr:commons_domain': 'arlisna.hcommons.org',
        'hclegacy:submitter_id': 1006873,
        'hclegacy:submitter_org_memberships': ['New York University'],
        'hclegacy:groups_for_deposit': [{'group_identifier': '1003999',
                                         'group_name': 'ARLIS/NA '
                                                       'Cataloging Advisory '
                                                       'Committee'}],
        },
    'files': {'entries': []},
    'metadata': {
        'additional_descriptions': [
            {'description': 'The ARLIS/NA Cataloging Advisory Committee has '
                            'drafted these best practices to provide practical '
                            'guidance to catalogers working with art exhibition '
                            'publications. The guidelines are confined to '
                            'cataloging issues and situations characteristic of '
                            'this type of material; they are intended to be '
                            'used with and are compatible with other '
                            'cataloging documentation including Resource '
                            'Description and Access (RDA) and LC-PCC Policy '
                            'Statements and Metadata Guidance Documents. '
                            'Examples have been given using the MARC21 '
                            'format for consistency and familiarity, but '
                            'MARC21 is not a prescribed or preferred schema. '
                            'The order of notes in this document generally '
                            'follows the WEMI framework but can be adjusted '
                            'for local practice or when it has been '
                            'decided that a particular note is of primary '
                            'importance.',
             'type': {'id': 'other',
                      'title': {'en': 'Primary description with HTML '
                                      'stripped'}}
            }
        ],
        'additional_titles': [
            {'title': 'Notes',
             'type': {'id': 'other',
                      'title': {'en': 'Primary title with HTML stripped'}}
             }
        ],
        'creators': [
            {'person_or_org': {'family_name': 'Bitetti',
                               'given_name': 'Bronwen',
                               'name': 'Bronwen Bitetti',
                               'type': 'personal'},
             'role': {'id': 'contributor'}},
            {'person_or_org': {'family_name': 'Blueher',
                               'given_name': 'William',
                               'name': 'William Blueher',
                               'type': 'personal'},
             'role': {'id': 'contributor'}},
            {'person_or_org': {'family_name': 'Clarke',
                               'given_name': 'Sherman',
                               'name': 'Sherman Clarke',
                               'type': 'personal'},
             'role': {'id': 'contributor'}},
            {'person_or_org': {'family_name': 'Fultz',
                              'given_name': 'Tamara',
                              'name': 'Tamara Fultz',
                              'type': 'personal'},
            'role': {'id': 'contributor'}},
            {'person_or_org': {'family_name': "L\\'Ecuyer-Coelho",
                              'given_name': 'Marie-Chantal',
                              'name': "Marie-Chantal L\\'Ecuyer-Coelho",
                              'type': 'personal'},
            'role': {'id': 'contributor'}},
            {'person_or_org': {'family_name': 'Maier',
                              'given_name': 'John',
                              'name': 'John Maier',
                              'type': 'personal'},
            'role': {'id': 'contributor'}},
            {'person_or_org': {'family_name': 'Neumann',
                              'given_name': 'Calli',
                              'name': 'Calli Neumann',
                              'type': 'personal'},
            'role': {'id': 'contributor'}},
            {'person_or_org': {'family_name': 'Oldal',
                              'given_name': 'Maria',
                              'name': 'Maria Oldal',
                              'type': 'personal'},
            'role': {'id': 'contributor'}},
            {'person_or_org': {'family_name': 'Osborne Bender',
                                'given_name': 'Sarah',
                                'name': 'Sarah Osborne Bender',
                                'type': 'personal'},
            'role': {'id': 'contributor'}},
            {'person_or_org': {'family_name': 'O’Keefe',
                                'given_name': 'Elizabeth',
                                'name': 'Elizabeth O’Keefe',
                                'type': 'personal'},
            'role': {'id': 'contributor'}},
            {'affiliations': ['New York University'],
            'person_or_org': {'family_name': 'Provo',
                                'given_name': 'Alexandra',
                                'identifiers': [{'identifier': 'aprovo',
                                                'scheme': 'hc_username'}],
                                'name': 'Alexandra Provo',
                                'type': 'personal'},
            'role': {'id': 'contributor'}},
            {'person_or_org': {'family_name': 'Puccio',
                                'given_name': 'Andrea',
                                'name': 'Andrea Puccio',
                                'type': 'personal'},
            'role': {'id': 'contributor'}},
            {'person_or_org': {'family_name': 'Stafford',
                                'given_name': 'Karen',
                                'name': 'Karen Stafford',
                                'type': 'personal'},
            'role': {'id': 'contributor'}},
            {'person_or_org': {'family_name': 'Wildenhaus',
                                'given_name': 'Karly',
                                'name': 'Karly Wildenhaus',
                                'type': 'personal'},
            'role': {'id': 'contributor'}}
            ],
              'dates': [],
              'publication_date': '2022',
              'description': 'The ARLIS/NA Cataloging Advisory Committee has '
                             'drafted these best practices to provide '
                             'practical guidance to catalogers working with '
                             'art exhibition publications. The guidelines are '
                             'confined to cataloging issues and situations '
                             'characteristic of this type of material; they '
                             'are intended to be used with and are compatible '
                             'with other cataloging documentation including '
                             'Resource Description and Access (RDA) and LC-PCC '
                             'Policy Statements and Metadata Guidance '
                             'Documents. Examples have been given using the '
                             'MARC21 format for consistency and familiarity, '
                             'but MARC21 is not a prescribed or preferred '
                             'schema. The order of notes in this document '
                             'generally follows the WEMI framework but can be '
                             'adjusted for local practice or when it has been '
                             'decided that a particular note is of primary '
                             'importance.',
              'formats': [],
              'identifiers': [{'identifier': 'hc:45177', 'scheme': 'hclegacy'}],
              'languages': [],
              'resource_type': {'id': 'publication:bookSection'},
              'rights': [],
              'subjects': [],
              'title': 'Notes'},
 'parent': {'access': {'owned_by': [{'user': 1006873}]}}}

json44881 = {
    'pids': {'doi': {'client': 'datacite',
                               'identifier': '10.17613/82yy-vj44',
                               'provider': 'datacite'}},
    'custom_fields': {
        'kcr:submitter_email': "runmerd@gmail.com",
        'kcr:submitter_username': "mlhale7",
        'kcr:commons_domain': 'arlisna.hcommons.org',
        'hclegacy:submitter_id': 1018587
        },
    'files': {'entries': []},
    'metadata': {
        'additional_descriptions': [
            {'description': 'Emily Walz interviews Distinguished '
                            'Service Award winners Sherman Clarke (2005) and '
                            'Daniel Starr (2014) on June 6, 2017, at the '
                            'New York Public Library. Both librarians are '
                            'career catalogers who joined ARLIS in its '
                            'earliest years; Clarke is best known as the '
                            'founder of Art NACO. Clarke and Starr both share '
                            'their experiences during the Vietnam War, when '
                            'each was classified as a conscientious objector. '
                            'The interview covers the challenges of the '
                            'Society, including working with management '
                            'companies and volunteer participation. The '
                            'interviewees also discuss the culture '
                            'of ARLIS/NA, in particular its inclusion of gay '
                            'and lesbian members. Clarke and Starr are '
                            'long-standing roommates at annual conferences.',
             'type': {'id': 'other',
                      'title': {'en': 'Primary description with HTML '
                                      'stripped'}
                      }
             }
        ],
        'additional_titles': [
            {'title': 'ARLIS/NA Oral History for Distinguished Service Award '
                      'Winners, Sherman Clarke and Daniel Starr',
             'type': {'id': 'other',
                      'title': {'en': 'Primary title with HTML stripped'}
                      }
             }
        ],
        'contributors': [{'person_or_org': {'family_name': 'Walz',
                                            'given_name': 'Emily',
                                            'name': 'Emily Walz',
                                            'type': 'personal'},
                         'role': {'id': 'contributor'}}
                         ],
        'creators': [{'person_or_org': {'family_name': 'Clarke',
                                        'given_name': 'Sherman',
                                        'name': 'Sherman Clarke',
                                        'type': 'personal'},
                      'role': {'id': 'author'}},
                     {'person_or_org': {'family_name': 'Starr',
                                        'given_name': 'Daniel',
                                        'name': 'Daniel Starr',
                                        'type': 'personal'},
                      'role': {'id': 'author'}}
                      ],
        'dates': [{'date': '2017-06-06',
                   'description': 'Human readable publication date',
                   'type': {'id': 'issued',
                   'title': {'en': 'Issued'}}}
                  ],
        'publication_date': '2017',
        'description': 'Emily Walz interviews Distinguished Service '
                        'Award winners Sherman Clarke (2005) and Daniel '
                        'Starr (2014) on June 6, 2017, at the New York '
                        'Public Library. Both librarians are career '
                        'catalogers who joined ARLIS in its earliest '
                        'years; Clarke is best known as the founder of '
                        'Art NACO. Clarke and Starr both share their '
                        'experiences during the Vietnam War, when each '
                        'was classified as a conscientious objector. The '
                        'interview covers the challenges of the Society, '
                        'including working with management companies and '
                        'volunteer participation. The interviewees also '
                        'discuss the culture of ARLIS/NA, in particular '
                        'its inclusion of gay and lesbian members. Clarke '
                        'and Starr are long-standing roommates at annual '
                        'conferences.',
        'formats': [],
        'identifiers': [{'identifier': 'hc:44881', 'scheme': 'hclegacy'}],
        'languages': [],
        'resource_type': {'id': 'publication:interviewTranscript'},
        'rights': [],
        'subjects': [],
        'title': 'ARLIS/NA Oral History for Distinguished Service Award '
                 'Winners, Sherman Clarke and Daniel Starr'},
    'parent': {'access': {'owned_by': [{'user': 1018587}]}}
}

@pytest.mark.parametrize("expected_json", [(json42615), (json22625),
    (json45177), (json44881), (json22647), (json11451), (json34031),
    (json16079)])
def test_parse_csv(expected_json):
    """
    """
    # runner = CliRunner()
    # result = runner.invoke(parse_csv, [])
    # assert result.exit_code == 0
    # assert result.output[0] == json1

    actual_json, actual_bad_data = parse_csv()
    expected_pid = expected_json['metadata']['identifiers'][0]['identifier']
    actual_json_item = [j for j in actual_json
                        for i in j['metadata']['identifiers']
                        if i['identifier'] == expected_pid][0]
    assert actual_json_item == expected_json