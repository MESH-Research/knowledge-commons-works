#!/usr/bin/env python3
"""Script to count subjects by scheme in the database."""

from invenio_access.permissions import system_identity
from invenio_records_resources.proxies import current_service_registry
from invenio_vocabularies.records.models import SubjectMetadata
from sqlalchemy import func

# Count subjects by scheme from the subject_metadata table
schemes = SubjectMetadata.query.with_entities(
    SubjectMetadata.json['scheme'], 
    func.count(SubjectMetadata.id)
).group_by(SubjectMetadata.json['scheme']).all()

total = 0
for scheme, count in schemes:
    print(f'{scheme}: {count}')
    total += count
print(f'Total subjects in database: {total}')

# Also compare with search index
service = current_service_registry.get('subjects')
search_result = service.search(system_identity, size=1)
print(f'Search index count: {search_result.total}')
print(f'Difference: {total - search_result.total}')
