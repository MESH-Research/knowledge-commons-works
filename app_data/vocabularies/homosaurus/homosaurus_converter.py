"""Convert Homosaurus JSON-LD to Invenio subjects JSONL.

Homosaurus v5 ``skos:prefLabel`` values are JSON-LD language tags (a single
``{"@language", "@value"}`` object or a list of them). Invenio's subject
schema requires ``subject`` to be a plain string; optional ``title`` holds
the i18n map (``{"en": "...", "es": "...", ...}``).

Invenio ``i18n_strings`` only accept two-letter language keys
(``^[a-z]{2}$``). Regional tags (``en-gb``, ``en-us``) are folded to the
primary subtag when that key is not already set; other non-conforming codes
are dropped.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

_I18N_KEY = re.compile(r"^[a-z]{2}$")
_REGIONAL_LANG = re.compile(r"^([a-z]{2})-.+")


def _pref_labels_to_title(pref_label: Any) -> dict[str, str]:
    """Normalize a JSON-LD ``skos:prefLabel`` into an i18n title map.

    Args:
        pref_label: String, language-tagged object, or list of those.

    Returns:
        Language-code → label map with only two-letter keys. Bare strings
        are stored under ``en``. Exact two-letter tags win over folded
        regional tags (e.g. ``en`` over ``en-gb``).
    """
    if pref_label is None or pref_label == "":
        return {}

    if isinstance(pref_label, str):
        return {"en": pref_label}

    entries = pref_label if isinstance(pref_label, list) else [pref_label]
    exact: dict[str, str] = {}
    folded: dict[str, str] = {}
    for entry in entries:
        if isinstance(entry, str):
            exact.setdefault("en", entry)
            continue
        if not isinstance(entry, dict):
            continue
        value = entry.get("@value")
        if not isinstance(value, str) or not value:
            continue
        lang = entry.get("@language") or "en"
        if not isinstance(lang, str) or not lang:
            continue
        lang = lang.lower().strip()
        if _I18N_KEY.match(lang):
            exact[lang] = value
            continue
        match = _REGIONAL_LANG.match(lang)
        if match:
            folded.setdefault(match.group(1), value)
    # Exact two-letter labels win over regionally folded ones.
    return {**folded, **exact}


def _subject_from_title(title: dict[str, str]) -> str:
    """Pick the display subject string from an i18n title map.

    Prefers English; otherwise the first available label.
    """
    if "en" in title:
        return title["en"]
    if title:
        return next(iter(title.values()))
    return ""


def convert_json(input_file: str | Path, output_file: str | Path) -> int:
    """Convert Homosaurus ``@graph`` JSON-LD to subjects JSONL.

    Args:
        input_file: Path to Homosaurus JSON-LD (``@graph`` of concepts).
        output_file: Path for the subjects JSONL output.

    Returns:
        Number of subject rows written.
    """
    input_path = Path(input_file)
    output_path = Path(output_file)

    with input_path.open(encoding="utf-8") as f:
        data = json.load(f)

    count = 0
    with output_path.open("w", encoding="utf-8") as f:
        for item in data["@graph"]:
            title = _pref_labels_to_title(item.get("skos:prefLabel"))
            subject = _subject_from_title(title)
            if not subject:
                continue
            new_item: dict[str, Any] = {
                "id": item.get("@id", ""),
                "scheme": "Homosaurus",
                "subject": subject,
                "title": title,
            }
            f.write(json.dumps(new_item, ensure_ascii=False) + "\n")
            count += 1
    return count


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    n = convert_json(here / "homosaurus.v5.jsonld", here / "subjects_homosaurus.jsonl")
    print(f"Wrote {n} subjects to {here / 'subjects_homosaurus.jsonl'}")
