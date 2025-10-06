#!/usr/bin/env python3
"""Create just the languages vocabulary type and load its data."""

import sys
import os
from pathlib import Path

# Add the project to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'site/kcworks'))

try:
    from flask import current_app
    from invenio_access.permissions import system_identity
    from invenio_vocabularies.proxies import current_service as vocabulary_service
    from invenio_vocabularies.records.api import Vocabulary
    from invenio_rdm_records.fixtures.vocabularies import GenericVocabularyEntry
    import yaml
    
    with current_app.app_context():
        # Check if languages vocabulary type already exists
        try:
            vocab_type = vocabulary_service.read_type(system_identity, "languages")
            print("Languages vocabulary type already exists")
        except Exception:
            print("Creating languages vocabulary type...")
            vocab_type = vocabulary_service.create_type(system_identity, "languages", "lng")
            print("Created languages vocabulary type")
        
        # Load the languages vocabulary entries
        print("Loading languages vocabulary entries...")
        languages_entry = GenericVocabularyEntry(
            Path("/opt/invenio/src/site/kcworks/dependencies/invenio-rdm-records/invenio_rdm_records/fixtures/data"),
            "languages",
            {"pid-type": "lng", "data-file": "vocabularies/languages.yaml"},
        )
        
        languages_entry.load(system_identity, ignore=set(), delay=False)
        Vocabulary.index.refresh()
        
        print("Languages vocabulary loaded successfully!")
        
        # Test that 'eng' is available
        try:
            eng_vocab = vocabulary_service.read(system_identity, ("languages", "eng"))
            print(f"✓ 'eng' language is available: {eng_vocab['title']['en']}")
        except Exception as e:
            print(f"✗ 'eng' language not found: {e}")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
