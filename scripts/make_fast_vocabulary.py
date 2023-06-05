from pprint import pprint
import re
import xml.etree.ElementTree as ET

def process_fast():
    """
    Parse a FAST marcxml file and write to an Invenio yaml vocabulary file
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
    source_paths = [f"../../kcr-untracked-files/FASTAll/FAST{s}.marcxml" for s in slugs]

    with open("../app_data/vocabularies/subjects_fast.yaml", "a"
              ) as target_file:
        for source_path in source_paths:
            with open(source_path, "rb") as source_file:
                print('Parsing FAST marcxml file (This may take a while!)')
                parsed = ET.parse(source_file)
                root = parsed.getroot()
                print(root)

                records = root.findall(f'./{mx}record')

                for record in records[:100]:

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
                        if code_letters in (["a", "d"], ["a", "c", "d"], ["a", "p"]):
                            label = ' '.join([f.text for f in label_fields])
                        elif code_letters in (["a", "x"], ["a", "z"]):
                            label = '--'.join([f.text for f in label_fields])
                        else:
                            pprint('BAD CODE COMBINATION')
                            pprint(facets[facet_num])
                            pprint(id_num)
                            pprint([f.get('code') for f in label_fields])
                    else:
                        label = label_fields[0].text
                    # FIXME: CORE are missing padding 0s to make 8 digits (at start)
                    # FIXME: CORE facets are inconsistent
                    # 110 corporate "Corporate Name"
                    # 150 topical "Topic"
                    # 148 chronological
                    # 147 event "Event"
                    # 155 form "Form\/Genre"
                    # 151 geographic "Geographic"
                    # 111 meeting "Meeting"
                    # 100 personal "Personal Name"
                    # 130 title
                    label = f'{id_num}:{label}:{facets[facet_num]}'
                    myline = f'- id: "{uri}"\n  scheme: FAST\n  subject: "{label}"\n'
                    target_file.write(myline)
                    print('.', '')

if __name__ == "__main__":
    process_fast()