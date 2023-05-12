from click.testing import CliRunner
from core_migrate import parse_csv
import pytest

json22625 = {
    'custom_fields':
        {'hclegacy:submitter_id': 1017065,
         'hclegacy:submitter_org_memberships': ['University Of Toronto'],
         'kcr:commons_domain': 'ajs.hcommons.org'
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
                 'role': 'author'}
            ],
            'dates': [],
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
            'publication_date': [],
            'resource_type': 'publication:bookChapter',
            'rights': [],
            'subjects': [],
            'title': 'מגדר וזמן בכתבי ר׳ שניאור זלמן מלאדי'},
    'parent': {'access': {'owned_by': [{'user': 1017065}]}}
}

json45177 = {
    'custom_fields': {
        'hclegacy:submitter_id': 1006873,
        'hclegacy:submitter_org_memberships': ['New York University'],
        'kcr:commons_domain': 'arlisna.hcommons.org'},
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
             'role': 'contributor'},
            {'person_or_org': {'family_name': 'Blueher',
                               'given_name': 'William',
                               'name': 'William Blueher',
                               'type': 'personal'},
             'role': 'contributor'},
            {'person_or_org': {'family_name': 'Clarke',
                               'given_name': 'Sherman',
                               'name': 'Sherman Clarke',
                               'type': 'personal'},
             'role': 'contributor'},
            {'person_or_org': {'family_name': 'Fultz',
                              'given_name': 'Tamara',
                              'name': 'Tamara Fultz',
                              'type': 'personal'},
            'role': 'contributor'},
            {'person_or_org': {'family_name': "L\\'Ecuyer-Coelho",
                              'given_name': 'Marie-Chantal',
                              'name': "Marie-Chantal L\\'Ecuyer-Coelho",
                              'type': 'personal'},
            'role': 'contributor'},
            {'person_or_org': {'family_name': 'Maier',
                              'given_name': 'John',
                              'name': 'John Maier',
                              'type': 'personal'},
            'role': 'contributor'},
            {'person_or_org': {'family_name': 'Neumann',
                              'given_name': 'Calli',
                              'name': 'Calli Neumann',
                              'type': 'personal'},
            'role': 'contributor'},
            {'person_or_org': {'family_name': 'Oldal',
                              'given_name': 'Maria',
                              'name': 'Maria Oldal',
                              'type': 'personal'},
            'role': 'contributor'},
            {'person_or_org': {'family_name': 'Osborne Bender',
                                'given_name': 'Sarah',
                                'name': 'Sarah Osborne Bender',
                                'type': 'personal'},
            'role': 'contributor'},
            {'person_or_org': {'family_name': 'O’Keefe',
                                'given_name': 'Elizabeth',
                                'name': 'Elizabeth O’Keefe',
                                'type': 'personal'},
            'role': 'contributor'},
            {'affiliations': ['New York University'],
            'person_or_org': {'family_name': 'Provo',
                                'given_name': 'Alexandra',
                                'identifiers': [{'identifier': 'aprovo',
                                                'scheme': 'hc_username'}],
                                'name': 'Alexandra Provo',
                                'type': 'personal'},
            'role': 'contributor'},
            {'person_or_org': {'family_name': 'Puccio',
                                'given_name': 'Andrea',
                                'name': 'Andrea Puccio',
                                'type': 'personal'},
            'role': 'contributor'},
            {'person_or_org': {'family_name': 'Stafford',
                                'given_name': 'Karen',
                                'name': 'Karen Stafford',
                                'type': 'personal'},
            'role': 'contributor'},
            {'person_or_org': {'family_name': 'Wildenhaus',
                                'given_name': 'Karly',
                                'name': 'Karly Wildenhaus',
                                'type': 'personal'},
            'role': 'contributor'}],
              'dates': [],
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
              'publication_date': [],
              'resource_type': 'publication:bookSection',
              'rights': [],
              'subjects': [],
              'title': 'Notes'},
 'parent': {'access': {'owned_by': [{'user': 1006873}]}}}

json44881 = {
    'custom_fields': {'hclegacy:submitter_id': 1018587,
                      'kcr:commons_domain': 'arlisna.hcommons.org'},
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
                         'role': 'contributor'}],
        'creators': [{'person_or_org': {'family_name': 'Clarke',
                                        'given_name': 'Sherman',
                                        'name': 'Sherman Clarke',
                                        'type': 'personal'},
                      'role': 'author'},
                     {'person_or_org': {'family_name': 'Starr',
                                        'given_name': 'Daniel',
                                        'name': 'Daniel Starr',
                                        'type': 'personal'},
                      'role': 'author'}],
        'dates': [],
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
        'publication_date': [],
        'resource_type': 'publication:interviewTranscript',
        'rights': [],
        'subjects': [],
        'title': 'ARLIS/NA Oral History for Distinguished Service Award '
                 'Winners, Sherman Clarke and Daniel Starr'},
    'parent': {'access': {'owned_by': [{'user': 1018587}]}}
}

@pytest.mark.parametrize("expected_json", [(json22625), (json45177),
                                           (json44881)])
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