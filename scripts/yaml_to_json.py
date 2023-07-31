#! /usr/bin/python

import json
from pathlib import Path
import yaml

def main():
    with open(Path(__file__).parent / "field_config.yaml", 'rb') as configfile:
        myconfig =  yaml.safe_load(configfile)

    with open(Path(__file__).parent / "field_config.json", 'w') as outputfile:
        config_json = json.dumps(myconfig, indent=2)
        outputfile.write(config_json)

    return myconfig

if __name__ == "__main__":
    main()