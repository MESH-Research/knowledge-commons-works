# Record search

This page covers how record search works in KCWorks for users and operators:
query syntax topics (such as quotes) and field aliases, plus how to customize
search configuration.

The in-app Search guide at [https://works.hcommons.org/help/search] covers
Lucene-style query syntax and lists the same field aliases for end users.

## What do quotes do around a search term?

Quotes around a search (like `"climate"`) tell OpenSearch to perform a *phrase*
search instead of a *term* search. But what's the difference? That can be
especially confusing for a single word, because quotes still mark the query as
a phrase search even when there is only one word inside them—yet in practice
`draw` and `"draw"` (or `title:draw` and `title:"draw"`) usually return the
**same set of hits**.

Unquoted (*term*) searches behave the way we expect a flexible **best match**
search to work. They look for analyzed terms across the default fields (or the
field you name), and results are ranked by relevance. Quoted (*phrase*)
searches use phrase-query semantics instead. For a single word, that usually
ends up requiring the same analyzed token to appear, so the hit list matches
the unquoted form. The real difference shows up with **more than one word**:
`"open science"` requires those words in order and next to each other, while
unquoted `open science` is looser about how the terms can match.

Phrase searches are still *not* quite "exact" searches. A word in quotes is
still analyzed by the search engine (tokenization, stemming, and so on). So a
phrase search for `"climate"` can still include hits with *climates* or other
forms of the same root word.

For multi-word phrases with a field alias, for example, `title:"open science"`
is sent as a phrase query against each path behind the `title` alias (main
title and additional titles).

For identifier-style precision, use aliases that target keyword-oriented fields
(for example `doi:`, `issn:`, `id:`) rather than relying on quotes on free-text
fields.

## Record search field aliases

KCWorks supports short field names in the search box (for example `title:climate`
instead of `metadata.title:climate`). This section describes the aliases for
**search users**, then how **operators** customize them.

### For search users

#### Field search with aliases

Type `alias:term` in the main search box or collection records search. Use
quotes around the search term for multi-word phrases (see
[What do quotes do around a search term?](#what-do-quotes-do-around-a-search-term)
for how quotes behave with single words):

| Example | Meaning |
| ------- | ------- |
| `title:climate` | Title fields contain the term `climate` (`metadata.title`, `metadata.additional_titles.title`) |
| `title:"open science"` | Phrase `open science` in those same title fields (in order, adjacent) |
| `author:smith` | Creator or contributor name or person/org identifier matches (`metadata.creators…` / `metadata.contributors…`) |
| `keyword:methodology` | User-defined keyword/tag (`custom_fields.kcr:user_defined_tags`) |
| `subject:history` | Controlled subject vocabulary term (`metadata.subjects.subject`) |
| `doi:10.1234/example` | DOI identifier (`pids.doi.identifier`) |
| `ror:01ggx4157` | Identifier value on affiliation, funder, or person/org identifier fields |

You can still use full OpenSearch paths when you need them
(`metadata.title:climate`). Aliases and full paths can be mixed with `AND` /
`OR` / `NOT` like any other advanced query.

#### Multi-field aliases

Some aliases search **more than one** indexed path and match if **any** path
hits. Notable examples:

| Alias | Searches across |
| ----- | --------------- |
| `title` | Main title and additional titles (`metadata.title`, `metadata.additional_titles.title`) |
| `description` / `abstract` | Main description and additional descriptions (`metadata.description`, `metadata.additional_descriptions.description`) |
| `author` / `contributor` / `creator` | Creators and contributors: names and person/org identifiers (`metadata.creators.person_or_org.name`, `metadata.contributors.person_or_org.name`, and the corresponding `….identifiers.identifier` paths) |
| `affiliation` | Creator and contributor affiliation names and identifiers (`metadata.creators.affiliations.name`, `metadata.contributors.affiliations.name`, and the corresponding `….identifiers.identifier` paths) |
| `funder` | Funder name and funder identifiers (`metadata.funding.funder.name`, `metadata.funding.funder.identifiers.identifier`) |
| `award` | Award title (all languages) and award number (`metadata.funding.award.title.*`, `metadata.funding.award.number`) |
| `organization` / `institution` | Affiliations, funders, publisher, thesis university, sponsoring institution, meeting organization (`metadata.publisher`, `custom_fields.thesis:thesis.university`, `custom_fields.kcr:sponsoring_institution`, `custom_fields.kcr:meeting_organization`, plus the affiliation and funder paths above) |
| `university` | Creator/contributor affiliations, thesis university, and sponsoring institution (`custom_fields.thesis:thesis.university`, `custom_fields.kcr:sponsoring_institution`, plus affiliation paths) |
| `degree` / `thesis_type` | `custom_fields.kcr:degree` and `custom_fields.thesis:thesis.type` |
| `department` / `discipline` | `custom_fields.thesis:thesis.department`, `custom_fields.kcr:institution_department`, and `custom_fields.kcr:discipline` |
| `thesis_department` | `custom_fields.thesis:thesis.department` and `custom_fields.kcr:institution_department` only |
| `place` | `metadata.locations.features.place`, `custom_fields.meeting:meeting.place`, `custom_fields.imprint:imprint.place` |
| `url` | `metadata.identifiers.identifier`, `metadata.related_identifiers.identifier`, `custom_fields.kcr:publication_url`, `custom_fields.meeting:meeting.url`, `custom_fields.code:codeRepository` |
| `ror` | Affiliation, funder, and person/org identifier values (`….affiliations.identifiers.identifier`, `metadata.funding.funder.identifiers.identifier`, `….person_or_org.identifiers.identifier`) |
| `collection` / `collections` | `parent.communities.ids`, `parent.communities.entries.slug`, `parent.communities.entries.metadata.title` |

#### Subjects vs keywords

- `subject` / `subjects` → controlled subjects (`metadata.subjects.subject`)
- `keyword` / `keywords` → depositor tags (`custom_fields.kcr:user_defined_tags`)

#### Software and AI

| Alias | Field |
| ----- | ----- |
| `programming_language` | `custom_fields.code:programmingLanguage` |
| `development_status` | `custom_fields.code:developmentStatus.id` |
| `code_repository` / `repository_url` / `repository` | `custom_fields.code:codeRepository` |
| `ai` / `ai_used` | `custom_fields.kcr:ai_usage.ai_used` (`true` / `false`) |
| `ai_description` | `custom_fields.kcr:ai_usage.ai_description` |

#### Complete alias list

Aliases are defined in `site/kcworks/config/search.py` as
`RECORD_SEARCH_FIELD_ALIASES`. Synonyms that share a target are grouped.

**Identifiers:** `id` (`id`); `recid` (`id`); `doi` (`pids.doi.identifier`);
`identifier` / `identifiers` (`metadata.identifiers.identifier`)

**Access:** `owner` (`parent.access.owned_by.user`); `access` /
`access_status` (`access.status`); `published` / `is_published`
(`is_published`)

**Bibliographic:** `title` (see multi-field table); `description` / `abstract`
(see multi-field table); `additional_description` /
`additional_descriptions` (`metadata.additional_descriptions.description`);
`publisher` (`metadata.publisher`); `publication_date` / `date`
(`metadata.publication_date`); `version` (`metadata.version`); `language` /
`languages` (`metadata.languages.id`); `format` / `formats`
(`metadata.formats`); `size` / `sizes` (`metadata.sizes`); `reference` /
`references` (`metadata.references.reference`); `place` (see multi-field table)

**Type:** `type` / `resource_type` (`metadata.resource_type.id`)

**URLs:** `url` (see multi-field table); `alternate_url` / `identifier_url`
(`metadata.identifiers.identifier`); `related_url`
(`metadata.related_identifiers.identifier`); `publication_url`
(`custom_fields.kcr:publication_url`); `meeting_url`
(`custom_fields.meeting:meeting.url`); `repository_url` / `repository`
(`custom_fields.code:codeRepository`)

**People / orgs:** `contributor` / `contributors` / `creator` / `creators` /
`author` / `authors` (see multi-field table under author); `affiliation` /
`affiliations` (see multi-field table); `funder` / `funding` (see multi-field
table); `award` (see multi-field table); `ror` (see multi-field table);
`organization` / `institution` (see multi-field table); `university` (see
multi-field table); `sponsoring_institution` / `sponsor`
(`custom_fields.kcr:sponsoring_institution`)

**Subjects / tags:** `subject` / `subjects` (`metadata.subjects.subject`);
`keyword` / `keywords` (`custom_fields.kcr:user_defined_tags`)

**Thesis / degree:** `degree` / `thesis_type` (see multi-field table);
`department` / `discipline` (see multi-field table); `thesis_department` (see
multi-field table); `thesis_university` (`custom_fields.thesis:thesis.university`)

**Files:** `file` / `filename` (`files.entries.key`); `file_type`
(`files.types`)

**Collections:** `collection` / `collections` (see multi-field table)

**Journal:** `journal` / `journal_title` (`custom_fields.journal:journal.title`);
`journal_volume` (`custom_fields.journal:journal.volume`); `journal_issue`
(`custom_fields.journal:journal.issue`); `issn`
(`custom_fields.journal:journal.issn`)

**Meeting / conference:** `meeting` / `meeting_title` / `conference`
(`custom_fields.meeting:meeting.title`); `meeting_acronym`
(`custom_fields.meeting:meeting.acronym`); `meeting_dates`
(`custom_fields.meeting:meeting.dates`)

**Imprint / book:** `imprint` / `book_title` / `book`
(`custom_fields.imprint:imprint.title`); `isbn`
(`custom_fields.imprint:imprint.isbn`); `edition`
(`custom_fields.imprint:imprint.edition`, `custom_fields.kcr:edition`);
`chapter` (`custom_fields.kcr:chapter_label`); `series`
(`custom_fields.kcr:book_series.series_title`)

**CodeMeta:** `code_repository` / `repository` (`custom_fields.code:codeRepository`);
`programming_language` (`custom_fields.code:programmingLanguage`);
`development_status` (`custom_fields.code:developmentStatus.id`)

**Other:** `note` / `notes`
(`custom_fields.kcr:notes.note_text`); `course` (`custom_fields.kcr:course_title`);
`project` (`custom_fields.kcr:project_title`); `ai` / `ai_used`
(`custom_fields.kcr:ai_usage.ai_used`); `ai_description`
(`custom_fields.kcr:ai_usage.ai_description`)

```{note}
There is no one-word `thesis` alias. Use `thesis_university`, `thesis_type`,
`thesis_department`, or `degree` as appropriate.
```

### For operators (customization)

#### Where aliases live

| Piece | Role |
| ----- | ---- |
| `site/kcworks/config/search.py` | `RECORD_SEARCH_FIELD_ALIASES` and `RECORD_SEARCH_QUERY_PARSER` |
| `site/kcworks/services/search/queryparser/transformer.py` | `MultiFieldSearchTransformer` (expands multi-path aliases to OR) |
| `invenio.cfg` → `RDM_SEARCH["query_parser_cls"]` | Wires the parser into record and community-records **API** search |
| `invenio.cfg` → `RDM_SEARCH_DRAFTS["query_parser_cls"]` | Same parser for user uploads / drafts **API** search |

Community/collection **UI** facet and sort lists use
`COMMUNITIES_RECORDS_SEARCH` (facets/sort only). Alias rewriting goes through
`RDM_SEARCH` (published/community) and `RDM_SEARCH_DRAFTS` (uploads).

#### Mapping value shapes

```python
RECORD_SEARCH_FIELD_ALIASES = {
    # Single OpenSearch path
    "publisher": "metadata.publisher",

    # Several paths → (path1:value OR path2:value OR ...)
    "title": (
        "metadata.title",
        "metadata.additional_titles.title",
    ),

    # Permission-gated fields (upstream pattern; whole mapping value)
    "internal_notes.note": RestrictedTerm(system_permission),
}
```

- Prefer **tuples of path strings** for multi-field aliases.
- Do not put `RestrictedTerm` / `FieldValueMapper` *inside* a tuple; those
  wrappers apply only when they are the entire mapping value.
- `FieldValueMapper(term_name, word=..., phrase=...)` can rewrite the search
  *value* (for example normalize a label to a stored id). `term_name` may be a
  string or a tuple of paths; the same rewritten value is applied to each OR
  arm.

After changing aliases, restart the web application so Flask reloads
`invenio.cfg` / imported config.

#### Updating end-user help

The public syntax guide is the template override:

`templates/semantic-ui/invenio_app_rdm/help/search.en.html`

Keep the alias list there in sync when you add or remove user-facing aliases.

#### Related config

- `RDM_FACETS` — facet definitions (including CodeMeta facets when merged)
- `RDM_SEARCH` / `COMMUNITIES_RECORDS_SEARCH` — which facets and sort options
  each surface exposes (keep lists aligned where the UX should match)
