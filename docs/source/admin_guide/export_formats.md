# Export formats

KCWorks customizes how published records are serialized for download and
content negotiation (for example BibTeX). Citation display that goes through
CSL is separate: resource-type vocabulary props such as `props.csl` drive that
path, while some export serializers use their own resource-type maps.

## BibTeX serialization

Upstream InvenioRDM maps stock resource-type IDs (for example
`publication-conferencepaper`) to BibTeX entry types in
`BibTexSchema.entry_mapper`. KCWorks uses different vocabulary IDs (for example
`textDocument-proceedingsPaper`), so without a customization those records
always fall through to `@misc`.

KCWorks replaces BibTeX serialization in two places via
`kcworks.config.serializers` (imported from `invenio.cfg`):

- `RDM_RECORDS_SERIALIZERS` — API content negotiation
  (`Accept: application/x-bibtex` on `/api/records/<id>`)
- `APP_RDM_RECORD_EXPORTERS` — record-page export dropdown
  (`/records/<id>/export/bibtex`)

Both use `KCWorksBibtexSerializer` / `KCWorksBibTexSchema`, which keep the stock
map and add mappings for KC resource types.

| Code | Role |
| ---- | ---- |
| `site/kcworks/config/serializers.py` | `RDM_RECORDS_SERIALIZERS` and `APP_RDM_RECORD_EXPORTERS` |
| `site/kcworks/resources/serializers/bibtex/serializer.py` | Serializer wiring |
| `site/kcworks/resources/serializers/bibtex/schema.py` | `entry_mapper` |

Example API request:

```http
GET /api/records/pp4ss-8ac91 HTTP/1.1
Accept: application/x-bibtex
```

Even when a type is mapped, the serializer only selects that entry type if the
record supplies the required fields for it (for example `@inproceedings` needs
`imprint:imprint.title` as `booktitle`; `@article` needs `journal:journal.title`).
Otherwise it still falls back to `@misc`.

CSL JSON and formatted citations do **not** use this map; they resolve type from
the resource-type vocabulary’s `props.csl` value.

### Mapped KC resource types

| Resource type ID | BibTeX entry type(s) tried (in order) | Notes |
| ---------------- | ------------------------------------- | ----- |
| `textDocument-proceedingsPaper` | `inproceedings` | Stock equivalent: `publication-conferencepaper` |
| `textDocument-conferenceProceeding` | `proceedings` | Stock equivalent: `publication-conferenceproceeding` |
| `textDocument-book` | `book`, then `booklet` | Stock equivalent: `publication-book` |
| `textDocument-bookSection` | `incollection`, then `inbook` | Stock equivalent: `publication-section` |
| `textDocument-journalArticle` | `article` | Stock equivalent: `publication-article` |
| `textDocument-preprint` | `unpublished` | Stock equivalent: `publication-preprint`; requires a `note` |
| `textDocument-thesis` | `phdthesis` | Stock equivalent: `publication-thesis` |
| `textDocument-documentation` | `manual` | Stock equivalent: `publication-technicalnote` |
| `textDocument-workingPaper` | `unpublished` | Stock equivalent: `publication-workingpaper`; requires a `note` |
| `textDocument-monograph` | `book`, then `booklet` | Close equivalent to book |
| `textDocument-abstract` | `article` | Stretch; needs journal custom fields |
| `textDocument-editorial` | `article` | Stretch; needs journal custom fields |
| `textDocument-essay` | `article` | Stretch; needs journal custom fields |
| `textDocument-magazineArticle` | `article` | Stretch; needs journal custom fields |
| `textDocument-newspaperArticle` | `article` | Stretch; needs journal custom fields |
| `textDocument-review` | `article` | Stretch; needs journal custom fields |
| `software` | `software` | Same ID as stock |
| `software-3DModel` | `software` | |
| `software-application` | `software` | |
| `software-computationalModel` | `software` | |
| `software-computationalNotebook` | `software` | |
| `software-service` | `software` | |
| `software-other` | `software` | |
| `dataset` | `dataset` | Same ID as stock |

`presentation-conferencePaper` is intentionally left unmapped: `@inproceedings`
implies publication in a proceedings volume, which is the wrong signal for a
conference presentation deposit.

### Unmapped KC resource types (`@misc`)

These vocabulary IDs have no entry in `KCWorksBibTexSchema.entry_mapper` and
serialize as `@misc` (aside from any required-field fallbacks above):

- `audiovisual`
- `audiovisual-documentary`
- `audiovisual-interviewRecording`
- `audiovisual-musicalRecording`
- `audiovisual-other`
- `audiovisual-performance`
- `audiovisual-podcastEpisode`
- `audiovisual-audioRecording`
- `audiovisual-videoRecording`
- `image`
- `image-chart`
- `image-diagram`
- `image-figure`
- `image-map`
- `image-visualArt`
- `image-photograph`
- `image-other`
- `instructionalResource`
- `instructionalResource-curriculum`
- `instructionalResource-lessonPlan`
- `instructionalResource-syllabus`
- `instructionalResource-other`
- `presentation`
- `presentation-conferencePaper`
- `presentation-conferencePoster`
- `presentation-presentationText`
- `presentation-slides`
- `presentation-other`
- `textDocument`
- `textDocument-bibliography`
- `textDocument-blogPost`
- `textDocument-dataManagementPlan`
- `textDocument-interviewTranscript`
- `textDocument-journal`
- `textDocument-legalComment`
- `textDocument-legalResponse`
- `textDocument-musicalNotation`
- `textDocument-onlinePublication`
- `textDocument-other`
- `textDocument-poeticWork`
- `textDocument-proposal`
- `textDocument-report`
- `textDocument-technicalStandard`
- `textDocument-whitePaper`
- `other`
- `other-catalog`
- `other-collection`
- `other-event`
- `other-interactiveResource`
- `other-notes`
- `other-patent`
- `other-peerReview`
- `other-physicalObject`
- `other-workflow`
