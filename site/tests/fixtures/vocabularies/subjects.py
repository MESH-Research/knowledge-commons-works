import pytest

from invenio_access.permissions import system_identity
from invenio_pidstore.errors import PIDAlreadyExists
from invenio_vocabularies.contrib.subjects.api import Subject
from invenio_records_resources.proxies import current_service_registry


@pytest.fixture(scope="module")
def subjects_service(app):
    return current_service_registry.get("subjects")


subject_data = [
    {
        "id": "http://id.worldcat.org/fast/963599",
        "scheme": "FAST-topical",
        "subject": "Digital humanities",
    },
    {
        "id": "http://id.worldcat.org/fast/863509",
        "scheme": "FAST-topical",
        "subject": "Human-machine systems--Planning",
    },
    {
        "id": "http://id.worldcat.org/fast/983377",
        "scheme": "FAST-topical",
        "subject": "Jews--Study and teaching",
    },
    {
        "id": "http://id.worldcat.org/fast/1208476",
        "scheme": "FAST-geographic",
        "subject": "Portugal",
    },
    {
        "id": "http://id.worldcat.org/fast/1012213",
        "scheme": "FAST-topical",
        "subject": "Mathematics--Philosophy",
    },
    {
        "id": "http://id.worldcat.org/fast/1012163",
        "scheme": "FAST-topical",
        "subject": "Mathematics",
    },
    {
        "id": "http://id.worldcat.org/fast/1930859",
        "scheme": "FAST-topical",
        "subject": "Portuguese colonies",
    },
    {
        "id": "http://id.worldcat.org/fast/813346",
        "scheme": "FAST-topical",
        "subject": "Architecture",
    },
    {
        "id": "http://id.worldcat.org/fast/1108387",
        "scheme": "FAST-topical",
        "subject": "Science--Study and teaching",
    },
    {
        "id": "http://id.worldcat.org/fast/863509",
        "scheme": "FAST-topical",
        "subject": "Eighteenth century",
    },
    {
        "id": "http://id.worldcat.org/fast/1037841",
        "scheme": "FAST-topical",
        "subject": "Nineteenth century",
    },
    {
        "id": "http://id.worldcat.org/fast/1145221",
        "scheme": "FAST-topical",
        "subject": "Technology--Study and teaching",
    },
    {
        "id": "http://id.worldcat.org/fast/903005",
        "scheme": "FAST-topical",
        "subject": "Education, Higher",
    },
    {
        "id": "http://id.worldcat.org/fast/861853",
        "scheme": "FAST-topical",
        "subject": "Cities and towns--Study and teaching",
    },
    {
        "id": "http://id.worldcat.org/fast/958235",
        "scheme": "FAST-topical",
        "subject": "History",
    },
    {
        "id": "http://id.worldcat.org/fast/911989",
        "scheme": "FAST-topical",
        "subject": "English literature",
    },
    {
        "id": "http://id.worldcat.org/fast/902116",
        "scheme": "FAST-topical",
        "subject": "Economics",
    },
    {
        "id": "http://id.worldcat.org/fast/862178",
        "scheme": "FAST-topical",
        "subject": "Abdominal Injuries",
    },
    {
        "id": "http://id.worldcat.org/fast/862177",
        "scheme": "FAST-topical",
        "subject": "City planning",
    },
    {
        "id": "http://id.worldcat.org/fast/1108176",
        "scheme": "FAST-topical",
        "subject": "Science",
    },
    {
        "id": "http://id.worldcat.org/fast/1159810",
        "scheme": "FAST-topical",
        "subject": "Twentieth century",
    },
    {
        "id": "http://id.worldcat.org/fast/943906",
        "scheme": "FAST-topical",
        "subject": "Gnosticism",
    },
    {
        "id": "http://id.worldcat.org/fast/863509",
        "scheme": "FAST-topical",
        "subject": "Classical literature",
    },
    {
        "id": "http://id.worldcat.org/fast/904058",
        "scheme": "FAST-topical",
        "subject": "Eighteenth century",
    },
    {
        "id": "http://id.worldcat.org/fast/1031646",
        "scheme": "FAST-topical",
        "subject": "Mysticism--Judaism",
    },
    {
        "id": "http://id.worldcat.org/fast/979030",
        "scheme": "FAST-topical",
        "subject": "Irish literature",
    },
    {
        "id": "http://id.worldcat.org/fast/815177",
        "scheme": "FAST-topical",
        "subject": "Art",
    },
    {
        "id": "http://id.worldcat.org/fast/1043123",
        "scheme": "FAST-topical",
        "subject": "Occultism",
    },
    {
        "id": "http://id.worldcat.org/fast/1411635",
        "scheme": "FAST-topical",
        "subject": "Criticism, interpretation, etc.",
    },
    {
        "id": "http://id.worldcat.org/fast/1730516",
        "scheme": "FAST-topical",
        "subject": "Jewish philosophy",
    },
    {
        "id": "http://id.worldcat.org/fast/883762",
        "scheme": "FAST-topical",
        "subject": "Criticism, textual",
    },
    {
        "id": "http://id.worldcat.org/fast/1245064",
        "scheme": "FAST-geographic",
        "subject": "Europe",
    },
    {
        "id": "http://id.worldcat.org/fast/1149217",
        "scheme": "FAST-topical",
        "subject": "Theater",
    },
    {
        "id": "http://id.worldcat.org/fast/1047055",
        "scheme": "FAST-topical",
        "subject": "Oral history",
    },
    {
        "id": "http://id.worldcat.org/fast/900999",
        "scheme": "FAST-topical",
        "subject": "East Asian literature",
    },
    {
        "id": "http://id.worldcat.org/fast/1047055",
        "scheme": "FAST-topical",
        "subject": "Oral history",
    },
    {
        "id": "http://id.worldcat.org/fast/1710945",
        "scheme": "FAST-topical",
        "subject": "Church history--Primitive and early church",
    },
    {
        "id": "http://id.worldcat.org/fast/1027285",
        "scheme": "FAST-topical",
        "subject": "Motion pictures",
    },
    {
        "id": "http://id.worldcat.org/fast/997341",
        "scheme": "FAST-topical",
        "subject": "Libraries",
    },
    {
        "id": "http://id.worldcat.org/fast/29048",
        "scheme": "FAST-personal",
        "subject": "Shakespeare, William, 1564-1616",
    },
    {
        "id": "http://id.worldcat.org/fast/29130",
        "scheme": "FAST-personal",
        "subject": "Shawn, Ted, 1891-1972",
    },
    {
        "id": "http://id.worldcat.org/fast/29137",
        "scheme": "FAST-personal",
        "subject": "Homer",
    },
    {
        "id": "http://id.worldcat.org/fast/913799",
        "scheme": "FAST-topical",
        "subject": "Epic poetry",
    },
]


@pytest.fixture(scope="module")
def subject_v(app, subjects_service):
    """Subject vocabulary record."""

    for subject in subject_data:
        try:
            subjects_service.create(
                system_identity,
                subject,
            )
        except PIDAlreadyExists:
            pass
    Subject.index.refresh()
