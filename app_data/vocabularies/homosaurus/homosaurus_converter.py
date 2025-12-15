import json


def convert_json(input_file, output_file):
    with open(input_file) as f:
        data = json.load(f)

    with open(output_file, "w") as f:
        for item in data["@graph"]:
            new_item = {
                "id": item.get("@id", ""),
                "scheme": "Homosaurus",
                "subject": item.get("skos:prefLabel", ""),
            }
            f.write(json.dumps(new_item) + "\n")


if __name__ == "__main__":
    convert_json("homosaurus.v3.jsonld", "subjects_homosaurus.jsonl")
