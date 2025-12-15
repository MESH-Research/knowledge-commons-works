import jsonlines

# Path to the input TSV file and the output JSONL file
input_file_path = "Joseph Ikhenoba Deposits - Sheet1.tsv"
output_file_path = "record-importer-overrides_knowledgeCommons.jsonl"


def add_to_skip_overrides(input_file_path, output_file_path):
    # Load existing records from the JSONL file into a dictionary
    existing_records = {}
    with jsonlines.open(output_file_path) as reader:
        for obj in reader:
            existing_records[obj["source_id"]] = obj

    # Open the input TSV file
    with open(input_file_path) as input_file:
        # Skip the header line
        next(input_file)
        # Iterate over each line in the input file
        for line in input_file:
            # Split the line by tabs
            fields = line.strip().split("\t")
            # Extract the ID field, which is the fourth field (index 3)
            id_value = fields[3]
            # Update or add the record with "skip": True
            existing_records[id_value] = existing_records.get(
                id_value, {"source_id": id_value}
            )
            existing_records[id_value]["skip"] = True
            existing_records[id_value]["notes"] = "Removed from CORE"

    # Write the updated records back to the JSONL file
    with jsonlines.open(output_file_path, mode="w") as writer:
        for record in existing_records.values():
            writer.write(record)


if __name__ == "__main__":
    add_to_skip_overrides(input_file_path, output_file_path)
