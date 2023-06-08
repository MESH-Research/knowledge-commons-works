from halo import Halo
from pathlib import Path
from pprint import pprint
import re
from tqdm import trange
import xml.etree.ElementTree as ET
"""

Escaping

In the converted yaml file double quotes (") are escaped with a backslash (\"). Single backslashes followed by a letter are also escaped (\\) so that the Invenio importer does not try to interpret the slash and following letter as a control character.
"""

def convert_to_yaml() -> bool:
    """
    Parse a FAST marcxml file and write to an Invenio yaml vocabulary file

    :param str source_folder: A string representing the path (absolute
                              or relative to this script file) for the
                              folder holding the marcxml files.
    :param str target_folder: A string representing the path (absolute
                              or relative to this script file) for the
                              folder where the subjects_fast.yaml file
                              exists (or will be created if it does not
                              exist).
    """
    mx = "{http://www.loc.gov/MARC21/slim}"
    slugs = ["Corporate",
             "Topical",
             "Chronological",
             "Event",
             "FormGenre",
             "Geographic",
             "Meeting",
             "Personal",
             "Title"]

    source_folder = Path(__file__).parent / 'downloads'
    source_paths = [f"{source_folder}/FAST{s}.marcxml" for s in slugs]
    target_folder = Path(__file__).parent / 'vocabularies'
    with open(f'{target_folder}/subjects_fast.yaml', "a"
              ) as target_file:
        for idx, source_path in enumerate(source_paths):
            print(f'\nConverting {slugs[idx]} vocabulary to Invenio yaml format')
            with open(source_path, "rb") as source_file:
                # print('\nParsing FAST marcxml file (This may take a while!)')
                spinner = Halo(text='    parsing FAST marcxml file (This may take a while!)', spinner='dots')
                spinner.start()
                parsed = ET.parse(source_file)
                spinner.stop()
                print(f'  done parsing {source_path.split("/")[-1]}')

                print(f'  converting contents to yaml')
                root = parsed.getroot()

                records = root.findall(f'./{mx}record')

                for r in trange(len(records)):
                    record = records[r]
                    # pprint([r for r in record])
                    id_num = record.find(f"./{mx}controlfield[@tag='001']")
                    id_num = id_num.text
                    id_num = re.sub(r'fst[0]*', '', id_num)

                    uri_field_parent = record.find(
                        f'./{mx}datafield[@tag="024"]'
                        )
                    # pprint(uri_field_parent)
                    # pprint([u for u in uri_field_parent])
                    uri_field = uri_field_parent.find(f'./{mx}subfield[@code="a"]')
                    # pprint(uri_field.text)
                    uri = uri_field.text

                    label_parent = [r for r in record
                                    if 'tag' in r.attrib.keys()
                                    and r.attrib['tag'] in ["148", "150", "110", "147", "155", "151", "111", "100", "130"]][0]

                    facets = {"110": "corporate",
                            "150": "topical",
                            "148": "chronological",
                            "147": "event",
                            "155": "form",
                            "151": "geographic",
                            "111": "meeting",
                            "100": "personal",
                            "130": "title"
                            }
                    # label_parent = record.find(
                    #     f'./{mx}datafield[@tag="150" or @tag="148" or @tag="110" or @tag="147" or @tag="155" or @tag="151" or @tag="111" or @tag="100" or @tag="130")]')
                    facet_num = label_parent.attrib['tag']
                    label_fields = [l for l in label_parent
                                    if 'code' in l.attrib.keys()
                                    and l.attrib['code'] in ["a", "b", "c", "d", "x", "z"]]
                    # label_fields = label_parent.findall(
                    #     f'./{mx}subfield[@code=("a", "b", "c", "d", "x", "z")]')
                    if len(label_fields) > 1:
                        code_letters = [f.get('code') for f in label_fields]
                        if any(c for c in code_letters if c in ["b", "c", "d", "p"]):
                            # ["a", "b"],
                            # ["a", "b", "b"],
                            # ["a", "b", "b", "b"],
                            # ["a", "b", "b", "b"],
                            # ["a", "c"],
                            # ["a", "d"],
                            # ["a", "b", "c"],
                            # ["a", "b", "d"],
                            # ["a", "b", "c", "d"],
                            # ["a", "c", "d"],
                            # ["a", "c", "d", "c"],
                            # ["a", "d", "c"],
                            # ["a", "p"]
                            label = ' '.join([f.text for f in label_fields])
                        elif any(c for c in code_letters if c in ["x", "z"]):
                            # ["a", "x"],
                            # ["a", "x", "x"],
                            # ["a", "x", "x", "x"],
                            # ["a", "z"],
                            # ["a", "z", "z"],
                            # ["a", "z", "z", "z"]
                            label = '--'.join([f.text for f in label_fields])
                        else:
                            pprint('BAD CODE COMBINATION')
                            pprint(facets[facet_num])
                            pprint(id_num)
                            pprint([f.get('code') for f in label_fields])
                    else:
                        label = label_fields[0].text
                    # escape quotation marks
                    label = label.replace('"', '\\"')
                    label = re.sub(r'\\([a-z A-Z])', r'\\\\1', label)
                    # Note: CORE facets were inconsistent, but have been normalized
                    # 110 corporate "Corporate Name"
                    # 150 topical "Topic"
                    # 148 chronological
                    # 147 event "Event"
                    # 155 form "Form\/Genre"
                    # 151 geographic "Geographic"
                    # 111 meeting "Meeting"
                    # 100 personal "Personal Name"
                    # 130 title
                    full_label = f'{id_num}:{label}:{facets[facet_num]}'
                    myline = f'- id: "{uri}"\n  scheme: FAST\n  subject: "{full_label}"\n'
                    target_file.write(myline)
                print('  finished writing this facet to yaml file')
    print(f'All done! All FAST facet terms have been converted to a single Invenio vocabulary file: {target_folder}/subjects_fast.yaml')
    return(True)