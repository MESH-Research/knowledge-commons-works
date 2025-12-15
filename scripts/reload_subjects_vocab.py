#!/usr/bin/env python3
"""Script to reload subjects vocabulary schemes individually."""

from pathlib import Path

from invenio_access.permissions import system_identity
from invenio_pidstore.errors import PIDAlreadyExists
from invenio_rdm_records.fixtures.tasks import create_vocabulary_record
from invenio_rdm_records.fixtures.vocabularies import VocabularyEntryWithSchemes
from marshmallow import ValidationError
from sqlalchemy.orm.exc import NoResultFound


def reload_subjects_vocabulary():
    """Reload missing subjects schemes individually."""
    print("Reloading missing subjects schemes...")
    
    # Only reload the missing schemes based on database count
    # FAST-personal: 647K loaded, 194K missing (skip first 647K)
    # FAST-title: 0 loaded, 69K missing (start from beginning)  
    # FAST-topical: 0 loaded, 485K missing (start from beginning)
    subjects_config = {
        "pid-type": "sub",
        "schemes": [
            {"id": "FAST-title", "name": "Faceted Application of Subject Terminology", "uri": "https://www.loc.gov/catworkshop/FAST/index.html", "data-file": "subjects_fast_title.jsonl"},
            {"id": "FAST-topical", "name": "Faceted Application of Subject Terminology", "uri": "https://www.loc.gov/catworkshop/FAST/index.html", "data-file": "subjects_fast_topical.jsonl"},
        ]
    }
    
    # FAST-personal needs special handling due to partial loading
    fast_personal_config = {
        "pid-type": "sub", 
        "schemes": [
            {"id": "FAST-personal", "name": "Faceted Application of Subject Terminology", "uri": "https://www.loc.gov/catworkshop/FAST/index.html", "data-file": "subjects_fast_personal.jsonl"}
        ]
    }
    
    # Directory where invenio-subjects-fast data files are located (container path)
    subjects_dir = Path("/opt/invenio/src/.venv/lib/python3.12/site-packages/invenio_subjects_fast/vocabularies")
    
    # Create subjects vocabulary entry
    subjects_entry = VocabularyEntryWithSchemes("subjects", subjects_dir, "subjects", subjects_config)
    
    print("Loading subjects vocabulary using VocabularyEntryWithSchemes...")
    
    # Use the same pattern as the vocabulary service
    # First, pre_load to create vocabulary type and schemes
    print("Pre-loading vocabulary type and schemes...")
    subjects_entry.pre_load(system_identity, ignore=set())
    
    # Process each scheme individually
    total_processed = 0
    total_created = 0
    total_skipped = 0
    
    # First handle FAST-personal with offset (partially loaded)
    print("\n=== Processing FAST-personal (offset: 647,000) ===")
    fast_personal_entry = VocabularyEntryWithSchemes("subjects", subjects_dir, "subjects", fast_personal_config)
    fast_personal_entry.pre_load(system_identity, ignore=set())
    
    scheme_processed = 0
    scheme_created = 0
    scheme_skipped = 0
    iteration_count = 0
    
    try:
        for data in fast_personal_entry.iterate(ignore=set()):
            iteration_count += 1
            
            # Skip first 647,000 records (already loaded)
            if iteration_count <= 647000:
                continue
            
            try:
                create_vocabulary_record("subjects", data)
                scheme_created += 1
            except (PIDAlreadyExists, NoResultFound, ValidationError):
                scheme_skipped += 1
            except Exception as e:
                print(f"  Error processing record: {e}")
                print(f"  Data: {data}")
                raise
            
            scheme_processed += 1
            if scheme_processed % 1000 == 0:
                print(f"  Processed {scheme_processed:,} records... (created: {scheme_created}, skipped: {scheme_skipped})")
                
    except Exception as e:
        print(f"Error processing FAST-personal: {e}")
        print(f"Total processed for FAST-personal before error: {scheme_processed}")
        raise
    
    print(f"Completed FAST-personal: {scheme_processed:,} processed, {scheme_created:,} created, {scheme_skipped:,} skipped")
    
    total_processed += scheme_processed
    total_created += scheme_created
    total_skipped += scheme_skipped
    
    # Then handle the other schemes (no offset needed)
    for scheme in subjects_config["schemes"]:
        scheme_id = scheme["id"]
        
        print(f"\n=== Processing {scheme_id} ===")
        
        # Create a single-scheme config for this iteration
        single_scheme_config = {
            "pid-type": "sub",
            "schemes": [scheme]
        }
        
        single_scheme_entry = VocabularyEntryWithSchemes("subjects", subjects_dir, "subjects", single_scheme_config)
        
        # Pre-load the scheme
        single_scheme_entry.pre_load(system_identity, ignore=set())
        
        scheme_processed = 0
        scheme_created = 0
        scheme_skipped = 0
        
        try:
            for data in single_scheme_entry.iterate(ignore=set()):
                try:
                    create_vocabulary_record("subjects", data)
                    scheme_created += 1
                except (PIDAlreadyExists, NoResultFound, ValidationError):
                    scheme_skipped += 1
                except Exception as e:
                    print(f"  Error processing record: {e}")
                    print(f"  Data: {data}")
                    raise
                
                scheme_processed += 1
                if scheme_processed % 1000 == 0:
                    print(f"  Processed {scheme_processed:,} records... (created: {scheme_created}, skipped: {scheme_skipped})")
                    
        except Exception as e:
            print(f"Error processing {scheme_id}: {e}")
            print(f"Total processed for {scheme_id} before error: {scheme_processed}")
            raise
        
        print(f"Completed {scheme_id}: {scheme_processed:,} processed, {scheme_created:,} created, {scheme_skipped:,} skipped")
        
        total_processed += scheme_processed
        total_created += scheme_created
        total_skipped += scheme_skipped
    
    print("\n=== FINAL SUMMARY ===")
    print(f"Total processed: {total_processed:,} records")
    print(f"Total created: {total_created:,} new records")
    print(f"Total skipped: {total_skipped:,} existing records")


if __name__ == '__main__':
    reload_subjects_vocabulary()
