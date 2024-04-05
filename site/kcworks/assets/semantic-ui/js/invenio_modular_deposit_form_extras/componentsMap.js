import { AdminMetadataComponent } from "./components/AdminMetadataComponent";
import { AIComponent } from "./components/AIComponent";
import { ChapterLabelComponent } from "./components/ChapterLabelComponent";
import { CommonsLegacyInfoComponent } from "./components/CommonsLegacyInfoComponent";
import { ContentWarningComponent } from "./components/ContentWarningComponent";
import { CourseTitleComponent } from "./components/CourseTitleComponent";
import { DegreeComponent } from "./components/DegreeComponent";
import { DisciplineComponent } from "./components/DisciplineComponent";
import { EditionComponent } from "./components/EditionComponent";
import { EditionSectionComponent } from "./components/EditionSectionComponent";
import { InstitutionDepartmentComponent } from "./components/InstitutionDepartmentComponent";
import { KeywordsComponent } from "./components/KeywordsComponent";
import { MediaComponent } from "./components/MediaComponent";
import { MeetingOrganizationComponent } from "./components/MeetingOrganizationComponent";
import { ProjectTitleComponent } from "./components/ProjectTitleComponent";
import { PublicationURLComponent } from "./components/PublicationURLComponent";
import { SeriesComponent } from "./components/SeriesComponent";
import { SponsoringInstitutionComponent } from "./components/SponsoringInstitutionComponent";
import { SubjectsKeywordsComponent } from "./components/SubjectsKeywordsComponent";
import { VolumeComponent } from "./components/VolumeComponent";

const componentsMap = {
  AdminMetadataComponent: [
    AdminMetadataComponent,
    ["kcr:commons_domain", "kcr:submitter_email", "kcr:submitter_username"],
  ],
  AIComponent: [AIComponent, ["custom_fields.kcr:ai_usage"]],
  ChapterLabelComponent: [
    ChapterLabelComponent,
    ["custom_fields.kcr:chapter_label"],
  ],
  CommonsLegacyInfoComponent: [
    CommonsLegacyInfoComponent,
    [
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
    ],
  ],
  ContentWarningComponent: [
    ContentWarningComponent,
    ["custom_fields.kcr:content_warning"],
  ],
  CourseTitleComponent: [
    CourseTitleComponent,
    ["custom_fields.kcr:course_title"],
  ],
  DegreeComponent: [DegreeComponent, ["custom_fields.kcr:degree"]],
  DisciplineComponent: [DisciplineComponent, ["custom_fields.kcr:discipline"]],
  EditionComponent: [EditionComponent, ["custom_fields.kcr:edition"]],
  EditionSectionComponent: [
    EditionSectionComponent,
    ["custom_fields.kcr:edition", "custom_fields.kcr:chapter_label"],
  ],
  InstitutionDepartmentComponent: [
    InstitutionDepartmentComponent,
    ["custom_fields.kcr:institution_department"],
  ],
  KeywordsComponent: [
    KeywordsComponent,
    ["custom_fields.kcr:user_defined_tags"],
  ],
  MediaComponent: [MediaComponent, ["custom_fields.kcr:media"]],
  MeetingOrganizationComponent: [
    MeetingOrganizationComponent,
    ["custom_fields.kcr:meeting_organization"],
  ],
  ProjectTitleComponent: [
    ProjectTitleComponent,
    ["custom_fields.kcr:project_title"],
  ],
  PublicationURLComponent: [
    PublicationURLComponent,
    ["custom_fields.kcr:publication_url"],
  ],
  SeriesComponent: [SeriesComponent, ["custom_fields.kcr:book_series"]],
  SponsoringInstitutionComponent: [
    SponsoringInstitutionComponent,
    ["custom_fields.kcr:sponsoring_institution"],
  ],
  SubjectsKeywordsComponent: [
    SubjectsKeywordsComponent,
    ["metadata.subjects", "custom_fields.kcr:user_defined_tags"],
  ],
  VolumeComponent: [VolumeComponent, ["custom_fields.kcr:volumes"]],
};

export { componentsMap };
