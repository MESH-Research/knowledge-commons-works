import pytest
from core_migrate.core_crawler import get_metadata


@pytest.mark.parametrize(
    "record_id, expected_metadata",
    [
        (
            "hc:62925",
            {
                "visible_metadata": {
                    "title": (
                        "Flyer for The Spanish Baroque and latin "
                        "American Literary Modernity: writing in Constellation"
                    ),
                    "abstract:": (
                        "This contains a table of contents and description for"
                        " the book, The Spanish Baroque and Latin American"
                        " Literary Modernity: Writing in Constellation, as a"
                        " follow up to my paper for the 2024 MLA. Chapter One"
                        ' formed the basis for "Góngora, Inca Garcilaso, and'
                        " the Meeting of Humanist and Indigenous Modes of"
                        ' Knowledge."'
                    ),
                    "author": "Crystal Anne Chemris (see profile)",
                    "date": "2024",
                    "group": (
                        "CLCS Mediterranean, CLCS Renaissance and Early"
                        " Modern, LLC 16th- and 17th-Century Spanish and"
                        " Iberian Poetry and Prose, LLC 20th- and 21st-Century"
                        " Latin American, LLC Colonial Latin American"
                    ),
                    "item type": "Other",
                    "last updated": "7 hours ago",
                    "license": "Attribution",
                    "permanent url": "https://doi.org/10.17613/ds9j-my39",
                    "status": "Provisional",
                    "filename": "spanish-baroque-latam-lit-mla-24.pdf",
                },
                "page_xml_data": {
                    "title": (
                        "Flyer for The Spanish Baroque and latin American"
                        " Literary Modernity: writing in Constellation"
                    ),
                    "abstract:": (
                        "This contains a table of contents and description for"
                        " the book, The Spanish Baroque and Latin American"
                        " Literary Modernity: Writing in Constellation, as a"
                        " follow up to my paper for the 2024 MLA. Chapter One"
                        ' formed the basis for "Góngora, Inca Garcilaso, and'
                        " the Meeting of Humanist and Indigenous Modes of"
                        ' Knowledge."'
                    ),
                    "name": {
                        "type": "personal",
                        "first_name": "Crystal",
                        "last_name": "Chemris",
                        "role": "author",
                        "affiliation": (
                            "University of California, Santa Barbara"
                        ),
                    },
                    "item type": "Other",
                    "date": "2024",
                },
            },
        ),
        (
            "hc:62919",
            {
                "visible_metadata": {
                    "title": (
                        "Experiences of Security Guards Serving in Diocesan"
                        " Schools During the COVID-19 Pandemic: A Case Study"
                        .upper()
                    ),
                    "author": (
                        "Victor Brian L. Catalbas, Ana Glenda S. Lactuan"
                        " Frederick Fabella"
                    ),
                    "date": "2024",
                    "item type": "Article",
                    "permanent url": "https://doi.org/10.17613/pqzr-ah83",
                    "abstract": (
                        "This study explores the life of the school security"
                        " guard in the context of “new normal” brought about"
                        " by the global pandemic. As educational institutions"
                        " adapt to the challenges of this unprecedented era,"
                        " the role of school security guard has become"
                        " increasingly vital in maintaining a safe and secure"
                        " environment for students, staff, and visitors. The"
                        " purpose of this study is to shed light on the unique"
                        " challenges, responsibilities, and experiences faced"
                        " by school security guards during the COVID-19"
                        " pandemic. This research utilizes a qualitative"
                        " approach, employing in-depth interview to gather"
                        " data from school security guards rendering duties in"
                        " the diocesan school. The findings of this study"
                        " highlight the multifaceted role played by school"
                        " security guards during the pandemic. They serve as"
                        " frontline workers, responsible for implementing and"
                        " enforcing safety protocols, managing access control,"
                        " and ensuring the well-being of students, staff, and"
                        " visitors. The findings also reveal that school"
                        " security guards have demonstrated remarkable"
                        " adaptability and resilience in the face of the new"
                        " normal. They have embraced their expanded"
                        " responsibilities and successfully implemented health"
                        " and safety protocols within their schools. It"
                        " emphasizes the importance of collaboration and"
                        " effective communication among all stakeholders"
                        " involved in school security including school"
                        " administrators, policy makers and local security"
                        " agencies in developing comprehensive strategies to"
                        " address the evolving security needs. The findings"
                        " further underscore the significance of fostering a"
                        " supportive and inclusive environment that"
                        " prioritizes the well-being of school security guards"
                        " and the entire school community."
                    ),
                    "editor": "Frederick Fabella (see profile)",
                    "filename": (
                        "experiences-security-guards-diocesan-"
                        "schools-covid-19-pandemic-case-study.pdf"
                    ),
                    "group": (
                        "Ignatian International Journal for Multidisciplinary"
                        " Research"
                    ),
                    "last updated:": "7 hours ago",
                    "license:": "Attribution-NonCommercial",
                    "notes": "",
                    "published_as": "Journal article",
                    "tag": (
                        "school security guards, COVID-19 pandemic,"
                        " experiences and challenges, qualitative research"
                    ),
                },
                "page_xml_data": {
                    "title": (
                        "Experiences of Security Guards Serving in Diocesan"
                        " Schools During the COVID-19 Pandemic: A Case Study"
                        .upper()
                    ),
                    "date": "2024",
                    "name": [
                        {
                            "type": "personal",
                            "first_name": "Victor Brian L.",
                            "last_name": "Catalbas",
                            "role": "author",
                            "affiliation": "University of San Carlos",
                        },
                        {
                            "type": "personal",
                            "first_name": "Ana Glenda S.",
                            "last_name": "Lactuan",
                            "role": "author",
                            "affiliation": "University of San Carlos",
                        },
                        {
                            "type": "personal",
                            "first_name": "Frederick",
                            "last_name": "Fabella",
                            "role": "author",
                            "affiliation": "University of San Carlos",
                        },
                    ],
                    "item type": "Article",
                    "typeOfResource": "Text",
                    "language": "eng",
                    "journal": (
                        "Ignatian International Journal for Multidisciplinary"
                        " Research"
                    ),
                    "publisher": "ICCE",
                    "volume": "2",
                    "issue": "1",
                    "page start": "30",
                    "page end": "61",
                    "long date": "January, 2024",
                    "doi": "https://doi.org/10.5281/zenodo.10476927",
                    "issn": "2984 9942",
                    "abstract": (
                        "This study explores the life of the school security"
                        " guard in the context of “new normal” brought about"
                        " by the global pandemic. As educational institutions"
                        " adapt to the challenges of this unprecedented era,"
                        " the role of school security guard has become"
                        " increasingly vital in maintaining a safe and secure"
                        " environment for students, staff, and visitors. The"
                        " purpose of this study is to shed light on the unique"
                        " challenges, responsibilities, and experiences faced"
                        " by school security guards during the COVID-19"
                        " pandemic. This research utilizes a qualitative"
                        " approach, employing in-depth interview to gather"
                        " data from school security guards rendering duties in"
                        " the diocesan school. The findings of this study"
                        " highlight the multifaceted role played by school"
                        " security guards during the pandemic. They serve as"
                        " frontline workers, responsible for implementing and"
                        " enforcing safety protocols, managing access control,"
                        " and ensuring the well-being of students, staff, and"
                        " visitors. The findings also reveal that school"
                        " security guards have demonstrated remarkable"
                        " adaptability and resilience in the face of the new"
                        " normal. They have embraced their expanded"
                        " responsibilities and successfully implemented health"
                        " and safety protocols within their schools. It"
                        " emphasizes the importance of collaboration and"
                        " effective communication among all stakeholders"
                        " involved in school security including school"
                        " administrators, policy makers and local security"
                        " agencies in developing comprehensive strategies to"
                        " address the evolving security needs. The findings"
                        " further underscore the significance of fostering a"
                        " supportive and inclusive environment that"
                        " prioritizes the well-being of school security guards"
                        " and the entire school community."
                    ),
                },
            },
        ),
    ],
)
def test_get_metadata(record_id, expected_metadata):
    actual_metadata = get_metadata(record_id)

    assert isinstance(actual_metadata, dict)
    assert actual_metadata
    assert (
        actual_metadata["visible_metadata"]
        == expected_metadata["visible_metadata"]
    )
    assert (
        actual_metadata["page_xml_data"] == expected_metadata["page_xml_data"]
    )
