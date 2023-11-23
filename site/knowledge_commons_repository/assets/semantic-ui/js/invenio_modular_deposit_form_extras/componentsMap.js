
import { AdminMetadataComponent } from './components/AdminMetadataComponent';
import { AIComponent } from './components/AIComponent';
import { BookDetailComponent } from './components/BookDetailComponent';
import { BookSectionVolumePagesComponent } from './components/BookSectionVolumePagesComponent';
import { BookVolumePagesComponent } from './components/BookVolumePagesComponent';
import { ChapterLabelComponent } from './components/ChapterLabelComponent';
import { CommonsLegacyInfoComponent } from './components/CommonsLegacyInfoComponent';
import { ContentWarningComponent } from './components/ContentWarningComponent';
import { EditionComponent } from './components/EditionComponent';
import { EditionSectionComponent } from './components/EditionSectionComponent';
import { KeywordsComponent } from './components/KeywordsComponent';
import { OrganizationDetailsComponent } from './components/OrganizationDetailsComponent';
import { PreviouslyPublishedComponent } from './components/PreviouslyPublishedComponent';
import { SeriesComponent } from './components/SeriesComponent';
import { SponsoringInstitutionComponent } from './components/SponsoringInstitutionComponent';
import { SubjectsKeywordsComponent } from './components/SubjectsKeywordsComponent';
import { VolumeComponent } from './components/VolumeComponent';

const componentsMap = {
  AdminMetadataComponent: [AdminMetadataComponent,
    [
    "kcr:commons_domain",
    "kcr:submitter_email",
    "kcr:submitter_username",
    ]
  ],
  AIComponent: [AIComponent, ["custom_fields.kcr:ai_usage"]],
  BookDetailComponent: [
    BookDetailComponent,
    [
      "custom_fields.imprint:imprint.isbn",
      "metadata.version",
      "metadata.publisher",
      "custom_fields.imprint:imprint.place",
      "custom_fields.kcr:book_series"
    ],
  ],
  BookSectionVolumePagesComponent: [
    BookSectionVolumePagesComponent,
    [
      "custom_fields.journal:journal.pages",
      "custom_fields.kcr:volume",
      "custom_fields.imprint:imprint.pages",
    ],
  ],
  BookVolumePagesComponent: [
    BookVolumePagesComponent,
    ["custom_fields.kcr:volume", "custom_fields.imprint:imprint.pages"],
  ],
  ChapterLabelComponent: [ChapterLabelComponent, ["custom_fields.kcr:chapter_label"]],
  CommonsLegacyInfoComponent: [CommonsLegacyInfoComponent, [
    "hclegacy:groups_for_deposit",
    "hclegacy:collection",
    "hclegacy:committee_deposit",
    "hclegacy:file_location",
    "hclegacy:file_pid",
    "hclegacy:groups_for_deposit",
    "hclegacy:previously_published",
    "hclegacy:publication_type",
    "hclegacy:record_change_date",
    "hclegacy:record_creation_date",
    "hclegacy:record_identifier",
    "hclegacy:society",
    "hclegacy:submitter_org_memberships",
    "hclegacy:submitter_affiliation",
    "hclegacy:submitter_id",
  ]],
  ContentWarningComponent: [
    ContentWarningComponent,
    ["custom_fields.kcr:content_warning"],
  ],
  EditionComponent: [
    EditionComponent,
    ["custom_fields.kcr:edition"],
  ],
  EditionSectionComponent: [
    EditionSectionComponent,
    ["custom_fields.kcr:edition", "custom_fields.kcr:chapter_label"],
  ],
  KeywordsComponent: [KeywordsComponent, ["custom_fields.kcr:user_defined_tags"]],
  OrganizationDetailsComponent: [
    OrganizationDetailsComponent,
    [
      "custom_fields.kcr:sponsoring_institution",
      "custom_fields.imprint:imprint.place",
    ],
  ],
  PreviouslyPublishedComponent: [PreviouslyPublishedComponent, []],
  SeriesComponent: [SeriesComponent, ["custom_fields.kcr:book_series"]],
  SponsoringInstitutionComponent: [SponsoringInstitutionComponent, ["custom_fields.kcr:sponsoring_institution"]],
  SubjectsKeywordsComponent: [
    SubjectsKeywordsComponent,
    ["metadata.subjects", "custom_fields.kcr:user_defined_tags"],
  ],
  VolumeComponent: [VolumeComponent, ["custom_fields.kcr:volumes"]],
};

export {componentsMap};