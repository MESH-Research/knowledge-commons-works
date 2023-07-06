// This file is part of InvenioRDM
// Copyright (C) 2020-2022 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021-2022 Graz University of Technology.
// Copyright (C) 2022-2023 KTH Royal Institute of Technology.
//
// Invenio App RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component, createContext, createRef, Fragment,
                useEffect, useState } from "react";
import _get from "lodash/get";
import _isEmpty from "lodash/isEmpty";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { AccordionField, CustomFields, importWidget, loadWidgetsFromConfig } from "react-invenio-forms";
import {
  AccessRightField,
  DescriptionsField,
  CreatibutorsField,
  DeleteButton,
  DepositFormApp,
  DepositStatusBox,
  FileUploader,
  FormFeedback,
  IdentifiersField,
  PreviewButton,
  LanguagesField,
  LicenseField,
  PublicationDateField,
  PublishButton,
  PublisherField,
  ReferencesField,
  RelatedWorksField,
  SubjectsField,
  TitlesField,
  VersionField,
  CommunityHeader,
  SaveButton,
} from "@js/invenio_rdm_records";
import { FundingField } from "@js/invenio_vocabularies";
import {
  Button,
  Card,
  Container,
  Grid,
  Icon,
  Ref,
  Step,
  Sticky,
  Transition
} from "semantic-ui-react";
import PropTypes from "prop-types";
import Overridable from "react-overridable";
import ResourceTypeField from "../metadata_fields/ResourceTypeField";
import { PIDField } from "../metadata_fields/PIDField";
import { DatesField } from "../metadata_fields/DatesField";
import { HTML5Backend } from "react-dnd-html5-backend";
import { DndProvider } from "react-dnd";

// React Context to track the current form values.
// Will contain the Formik values object passed up from a
// form field.
const FormValuesContext = createContext();

/**
 * A React component to insert UI for a single custom fields section
 *
 * @param {string} sectionName  The label for the form section containing the
 *                              custom field(s) to be injected. Taken from the
 *                              custom field ui declaration for the field.
 * @param {string} idString  The string identifier to be used in building
 *                           the id for this field's container
 * @param {object} customFieldsUI  The whole custom fields ui declaration
 *                                 taken from the form's config
 */
const CustomFieldInjector = ({ sectionName, fieldName, idString, customFieldsUI, ...restArgs }) => {
  const [ MyWidget, setMyWidget ] = useState();
  const chosenSetConfig = new Array(customFieldsUI.find(
    item => item.section === sectionName));
  const chosenFieldConfig = chosenSetConfig[0].fields.find(item => item.field === fieldName);
  chosenFieldConfig.props = {...chosenFieldConfig.props, ...restArgs};
  const templateLoaders = [
    (widget) => import(`@templates/custom_fields/${widget}.js`),
    (widget) =>
      import(`@js/invenio_rdm_records/src/deposit/customFields`),
    (widget) => import(`react-invenio-forms`),
  ];
  const fieldPathPrefix = "custom_fields";
  useEffect(() => {
    loadWidgetsFromConfig({
      templateLoaders: templateLoaders,
      fieldPathPrefix: fieldPathPrefix,
      fields: new Array(chosenFieldConfig)
    }).then(x => setMyWidget(x[0]));
  }, []
  )

  return(
    <Overridable
      id={`InvenioAppRdm.Deposit.${idString}.container`}
      customFieldsUI={chosenSetConfig}
    >
      <>
      {MyWidget}
      {/* <CustomFields
        config={chosenSetConfig}
        templateLoaders={templateLoaders}
        fieldPathPrefix="custom_fields"
      /> */}
      </>
    </Overridable>
  )
}

const CustomFieldSectionInjector = ({sectionName, idString,
                                     customFieldsUI
                                    }) => {
  const chosenSetConfig = new Array(customFieldsUI.find(
    item => item.section === sectionName));
  const templateLoaders = [
    (widget) => import(`@templates/custom_fields/${widget}.js`),
    (widget) =>
      import(`@js/invenio_rdm_records/src/deposit/customFields`),
    (widget) => import(`react-invenio-forms`),
  ];

  return(
    <Overridable
      id={`InvenioAppRdm.Deposit.${idString}.container`}
      customFieldsUI={chosenSetConfig}
    >
      <CustomFields
        config={chosenSetConfig}
        templateLoaders={templateLoaders}
        fieldPathPrefix="custom_fields"
      />
    </Overridable>
  )
}

const AbstractComponent = ({record, vocabularies}) => {

  return(
    <Card fluid
    id={'InvenioAppRdm.Deposit.TypeTitleComponents.container'}
    >
      <Card.Content>
        <Overridable
          id="InvenioAppRdm.Deposit.DescriptionsField.container"
          record={record}
          vocabularies={vocabularies}
          fieldPath="metadata.description"
        >
          <DescriptionsField
            fieldPath="metadata.description"
            options={vocabularies.metadata.descriptions}
            recordUI={_get(record, "ui", null)}
            label="Abstract"
            editorConfig={{
              removePlugins: [
                "Image",
                "ImageCaption",
                "ImageStyle",
                "ImageToolbar",
                "ImageUpload",
                "MediaEmbed",
                "Table",
                "TableToolbar",
                "TableProperties",
                "TableCellProperties",
              ],
            }}
          />
        </Overridable>
      </Card.Content>
    </Card>
)
}

const AdditionalDatesComponent = ({vocabularies}) => {
  return(
    <Overridable
      id="InvenioAppRdm.Deposit.DateField.container"
      vocabularies={vocabularies}
      fieldPath="metadata.dates"
    >
      <DatesField
        fieldPath="metadata.dates"
        options={vocabularies.metadata.dates}
        showEmptyValue={false}
      />
    </Overridable>
  )
}

const AdditionalDescriptionComponent = ({record, vocabularies}) => {
  return(
    <Overridable
      id="InvenioAppRdm.Deposit.DescriptionsField.container"
      record={record}
      vocabularies={vocabularies}
      fieldPath="metadata.description"
    >
      <DescriptionsField
        fieldPath="metadata.description"
        options={vocabularies.metadata.descriptions}
        recordUI={_get(record, "ui", null)}
        editorConfig={{
          removePlugins: [
            "Image",
            "ImageCaption",
            "ImageStyle",
            "ImageToolbar",
            "ImageUpload",
            "MediaEmbed",
            "Table",
            "TableToolbar",
            "TableProperties",
            "TableCellProperties",
          ],
        }}
      />
    </Overridable>
)
}

const AdditionalTitlesComponent = () => {
  return(<></>)
}

const AIComponent = ({ customFieldsUI }) => {
  // const sectionConfig = customFieldsUI.find(item => item.section === "AI Usage");
  // const fieldConfig = sectionConfig.find(item => item.field === "ai_used");
  return(
    <Card fluid>
      <Card.Content>
        <CustomFieldInjector
          sectionName="AI Usage"
          fieldName="kcr:ai_usage"
          idString="AIUsageField"
          customFieldsUI={customFieldsUI}
        />
      </Card.Content>
    </Card>
  )
}

const AlternateIdentifiersComponent = ({vocabularies}) => {
  return(
    <Card fluid>
      <Card.Content>
        <Overridable
          id="InvenioAppRdm.Deposit.IdentifiersField.container"
          vocabularies={vocabularies}
          fieldPath="metadata.identifiers"
        >
          <IdentifiersField
            fieldPath="metadata.identifiers"
            label={i18next.t("Alternate identifiers")}
            labelIcon="barcode"
            schemeOptions={vocabularies.metadata.identifiers.scheme}
            showEmptyValue
          />
        </Overridable>
      </Card.Content>
    </Card>
  )
}


const CommunitiesComponent = () => {
  return(
    <Overridable id="InvenioAppRdm.Deposit.CommunityHeader.container">
      <CommunityHeader imagePlaceholderLink="/static/images/square-placeholder.png" />
    </Overridable>
)}

const ContentWarningComponent = ({ customFieldsUI }) => {
  return(
    <Card fluid>
      <Card.Content>
        <CustomFieldInjector
          fieldName="kcr:content_warning"
          sectionName="Content warning"
          idString="ContentWarning"
          customFieldsUI={customFieldsUI}
        />
      </Card.Content>
    </Card>
  )
}

const ContributorsComponent = ({config, vocabularies}) => {
  return(
    <Card fluid
      id={'InvenioAppRdm.Deposit.ContributorsField.card'}
    >
      <Card.Content>
        <Overridable
          id="InvenioAppRdm.Deposit.ContributorsField.container"
          fieldPath="metadata.contributors"
          vocabularies={vocabularies}
          config={config}
        >
          <CreatibutorsField
            addButtonLabel={i18next.t("Add contributor")}
            label={i18next.t("Contributors")}
            labelIcon="user plus"
            fieldPath="metadata.contributors"
            roleOptions={vocabularies.metadata.contributors.role}
            schema="contributors"
            autocompleteNames={config.autocomplete_names}
            modal={{
              addLabel: "Add contributor",
              editLabel: "Edit contributor",
            }}
            id="InvenioAppRdm.Deposit.ContributorsField.card"
          />
        </Overridable>
    </Card.Content>
  </Card>
)
}

const CreatorsComponent = ({config, vocabularies}) => {
  return(
    <Card fluid
      id={'InvenioAppRdm.Deposit.CreatorsField.card'}
    >
      <Card.Content>
        <Overridable
          id="InvenioAppRdm.Deposit.CreatorsField.container"
          vocabularies={vocabularies}
          config={config}
          fieldPath="metadata.creators"
        >
          <CreatibutorsField
            label={i18next.t("Creators")}
            labelIcon="user"
            fieldPath="metadata.creators"
            roleOptions={vocabularies.metadata.creators.role}
            schema="creators"
            autocompleteNames={config.autocomplete_names}
            required
            id="InvenioAppRdm.Deposit.CreatorsField.card"
          />
        </Overridable>
      </Card.Content>
    </Card>
  )
}

const DateComponent = () => {
  return(
    <Overridable
      id="InvenioAppRdm.Deposit.PublicationDateField.container"
      fieldPath="metadata.publication_date"
    >
      <PublicationDateField
        required
        fieldPath="metadata.publication_date"
      />
    </Overridable>
)
}

const DoiComponent = ({config, record}) => {
  return(
    <Card fluid
    >
      <Card.Content>
        <Overridable
          id="InvenioAppRdm.Deposit.PIDField.container"
          config={config}
          record={record}
        >
          <Fragment>
            {config.pids.map((pid) => (
              <Fragment key={pid.scheme}>
                <PIDField
                  btnLabelDiscardPID={pid.btn_label_discard_pid}
                  btnLabelGetPID={pid.btn_label_get_pid}
                  canBeManaged={pid.can_be_managed}
                  canBeUnmanaged={pid.can_be_unmanaged}
                  fieldPath={`pids.${pid.scheme}`}
                  fieldLabel={pid.field_label}
                  isEditingPublishedRecord={
                    record.is_published === true // is_published is `null` at first upload
                  }
                  managedHelpText={pid.managed_help_text}
                  pidLabel={pid.pid_label}
                  pidPlaceholder={pid.pid_placeholder}
                  pidType={pid.scheme}
                  unmanagedHelpText={pid.unmanaged_help_text}
                  required
                />
              </Fragment>
            ))}
          </Fragment>
        </Overridable>
    </Card.Content>
    </Card>
)}

const FilesUploadComponent = ({config, noFiles, record, permissions}) => {
  return(
    <Card fluid>
      <Card.Content>
    {/* <Overridable
      id="InvenioAppRdm.Deposit.AccordionFieldFiles.container"
      record={record}
      config={config}
      noFiles={noFiles}
    >
      <AccordionField
        includesPaths={["files.enabled"]}
        active
        label={i18next.t("Files")}
      > */}
        {noFiles && record.is_published && (
          <div className="text-align-center pb-10">
            <em>{i18next.t("The record has no files.")}</em>
          </div>
        )}
        <Overridable
          id="InvenioAppRdm.Deposit.FileUploader.container"
          record={record}
          config={config}
        >
          <FileUploader
            isDraftRecord={!record.is_published}
            quota={config.quota}
            decimalSizeDisplay={config.decimal_size_display}
            showMetadataOnlyToggle={permissions?.can_manage_files}
          />
        </Overridable>
      {/* </AccordionField>
    </Overridable> */}
      </Card.Content>
    </Card>
  )
}

const FundingComponent = ({}) => {
  return(
      <Card fluid
        id="InvenioAppRdm.Deposit.AccordionFieldFunding.card"
      >
        <Card.Content>
        <Overridable
          id="InvenioAppRdm.Deposit.FundingField.container"
          fieldPath="metadata.funding"
        >
          <FundingField
            fieldPath="metadata.funding"
            searchConfig={{
              searchApi: {
                axios: {
                  headers: {
                    Accept: "application/vnd.inveniordm.v1+json",
                  },
                  url: "/api/awards",
                  withCredentials: false,
                },
              },
              initialQueryState: {
                sortBy: "bestmatch",
                sortOrder: "asc",
                layout: "list",
                page: 1,
                size: 5,
              },
            }}
            label="Funding"
            labelIcon="money bill alternate outline"
            deserializeAward={(award) => {
              return {
                title: award.title_l10n,
                number: award.number,
                funder: award.funder ?? "",
                id: award.id,
                ...(award.identifiers && {
                  identifiers: award.identifiers,
                }),
                ...(award.acronym && { acronym: award.acronym }),
              };
            }}
            deserializeFunder={(funder) => {
              return {
                id: funder.id,
                name: funder.name,
                ...(funder.title_l10n && { title: funder.title_l10n }),
                ...(funder.pid && { pid: funder.pid }),
                ...(funder.country && { country: funder.country }),
                ...(funder.identifiers && {
                  identifiers: funder.identifiers,
                }),
              };
            }}
            computeFundingContents={(funding) => {
              let headerContent,
                descriptionContent,
                awardOrFunder = "";

              if (funding.funder) {
                const funderName =
                  funding.funder?.name ??
                  funding.funder?.title ??
                  funding.funder?.id ??
                  "";
                awardOrFunder = "funder";
                headerContent = funderName;
                descriptionContent = "";

                // there cannot be an award without a funder
                if (funding.award) {
                  awardOrFunder = "award";
                  descriptionContent = funderName;
                  headerContent = funding.award.title;
                }
              }

              return { headerContent, descriptionContent, awardOrFunder };
            }}
          />
        </Overridable>
      </Card.Content>
    </Card>
  )
}

const KeywordsComponent = ({ customFieldsUI }) => {
  return(
    <CustomFieldInjector
      sectionName="Tags"
      label="User-defined Keywords"
      fieldName="kcr:user_defined_tags"
      idString="KCRKeywordsField"
      customFieldsUI={customFieldsUI}
    />
  )
}

const LanguagesComponent = ({record}) => {
  return(
    <Overridable
      id="InvenioAppRdm.Deposit.LanguagesField.container"
      fieldPath="metadata.languages"
      record={record}
    >
      <LanguagesField
        fieldPath="metadata.languages"
        initialOptions={_get(record, "ui.languages", []).filter(
          (lang) => lang !== null
        )} // needed because dumped empty record from backend gives [null]
        serializeSuggestions={(suggestions) =>
          suggestions.map((item) => ({
            text: item.title_l10n,
            value: item.id,
            key: item.id,
          }))
        }
      />
    </Overridable>
  )
}

const LicensesComponent = () => {
  return(
    <Card fluid>
      <Card.Content>
        <Overridable
          id="InvenioAppRdm.Deposit.LicenseField.container"
          fieldPath="metadata.rights"
        >
          <LicenseField
            fieldPath="metadata.rights"
            searchConfig={{
              searchApi: {
                axios: {
                  headers: {
                    Accept: "application/vnd.inveniordm.v1+json",
                  },
                  url: "/api/vocabularies/licenses",
                  withCredentials: false,
                },
              },
              initialQueryState: {
                filters: [["tags", "recommended"]],
              },
            }}
            serializeLicenses={(result) => ({
              title: result.title_l10n,
              description: result.description_l10n,
              id: result.id,
              link: result.props.url,
            })}
          />
        </Overridable>
      </Card.Content>
    </Card>
)
}

const MetadataOnlyComponent = () => {
  return(<></>)
}

const PreviouslyPublishedComponent = () => {
  return(<></>)
}

const PublisherDoiComponent = () => {
  return(<></>)
}

const PublisherComponent = ({}) => {
  return(
    <Overridable
      id="InvenioAppRdm.Deposit.PublisherField.container"
      fieldPath="metadata.publisher"
    >
      <PublisherField fieldPath="metadata.publisher" />
    </Overridable>
  )
}

const PublicationLocationComponent = () => {
  return(<></>)
}


const ReferencesComponent = ({vocabularies}) => {
  return(
    <Overridable
      id="InvenioAppRdm.Deposit.AccordionFieldReferences.container"
      vocabularies={vocabularies}
    >
      <AccordionField
        includesPaths={["metadata.references"]}
        active
        label={i18next.t("References")}
      >
        <Overridable
          id="InvenioAppRdm.Deposit.ReferencesField.container"
          fieldPath="metadata.references"
          vocabularies={vocabularies}
        >
          <ReferencesField fieldPath="metadata.references" showEmptyValue />
        </Overridable>
      </AccordionField>
    </Overridable>
)}

const RelatedWorksComponent = ({vocabularies}) => {
  return(
    <Card fluid>
      <Card.Content>
        <Overridable
          id="InvenioAppRdm.Deposit.RelatedWorksField.container"
          fieldPath="metadata.related_identifiers"
          vocabularies={vocabularies}
        >
          <RelatedWorksField
            fieldPath="metadata.related_identifiers"
            options={vocabularies.metadata.identifiers}
            showEmptyValue
          />
        </Overridable>
      </Card.Content>
    </Card>
  )
}

const ResourceTypeComponent = ({vocabularies}) => {
  return(
    <Card fluid
      id={'InvenioAppRdm.Deposit.ResourceTypeComponent.container'}
    >
      <Card.Content>
        <Overridable
          id="InvenioAppRdm.Deposit.ResourceTypeField.container"
          vocabularies={vocabularies}
          fieldPath="metadata.resource_type"
        >
          <ResourceTypeField
            options={vocabularies.metadata.resource_type}
            fieldPath="metadata.resource_type"
            required
          />
        </Overridable>
      </Card.Content>
    </Card>
  )
}

const SubjectsComponent = ({record, vocabularies}) => {
  return(
    <Overridable
      id="InvenioAppRdm.Deposit.SubjectsField.container"
      vocabularies={vocabularies}
      fieldPath="metadata.subjects"
      record={record}
    >
      <SubjectsField
        fieldPath="metadata.subjects"
        label="Subjects"
        initialOptions={_get(record, "ui.subjects", null)}
        limitToOptions={vocabularies.metadata.subjects.limit_to}
      />
    </Overridable>
  )
}

const SubtitleComponent = () => {
  return(<></>)
}

const TitleComponent = ({vocabularies, record}) => {
  return(
    <Overridable
      id="InvenioAppRdm.Deposit.TitlesField.container"
      vocabularies={vocabularies}
      fieldPath="metadata.title"
      record={record}
    >
      <TitlesField
        options={vocabularies.metadata.titles}
        fieldPath="metadata.title"
        recordUI={record.ui}
        required
      />
    </Overridable>
)
}

const TotalPagesComponent = () => {
  return(<></>)
}

const SeriesTitleComponent = () => {
  return(<></>)
}

const SeriesNumberComponent = () => {
  return(<></>)
}

const TotalVolumesComponent = () => {
  return(<></>)
}

const VolumeComponent = () => {
  return(<></>)
}

const VersionComponent = () => {
  return(
    <Overridable
      id="InvenioAppRdm.Deposit.VersionField.container"
      fieldPath="metadata.version"
    >
      <VersionField fieldPath="metadata.version" />
    </Overridable>
  )
}

const AdminMetadataComponent = ({customFieldsUI}) => {
  return(
    <Card fluid>
      <Card.Content>
        <CustomFieldInjector
          sectionName="Commons admin info"
          idString="AdminMetadataFields"
          customFieldsUI={customFieldsUI}
        />
      </Card.Content>
    </Card>
)}

const BookDetailComponent = ({customFieldsUI}) => {
  return(
    <Card fluid>
      <Card.Content>
        {/* <CustomFieldInjector
          sectionName="Book information"
          idString="BookDetailFields"
          customFieldsUI={customFieldsUI}
        /> */}
        <CustomFieldInjector
          sectionName="Book / Report / Chapter"
          fieldName="imprint:imprint"
          idString="BookDetailFields"
          customFieldsUI={customFieldsUI}
        />
      </Card.Content>
    </Card>
)}

const CombinedTitlesComponent = ({vocabularies, record}) => {
  return(
    <Card fluid
      id={'InvenioAppRdm.Deposit.CombinedTitlesComponent.container'}
    >
      <Card.Content>
        <TitleComponent vocabularies={vocabularies} record={record} />
      </Card.Content>
    </Card>
  )
}

const TypeTitleComponent = ({vocabularies, record}) => {
  return(
    <Card fluid
      id={'InvenioAppRdm.Deposit.TypeTitleComponent.container'}
    >
      <Card.Content>
        <TitleComponent vocabularies={vocabularies} record={record} />
        <ResourceTypeComponent vocabularies={vocabularies} />
      </Card.Content>
    </Card>
  )
};

const SubjectKeywordsComponent = ({ record, vocabularies, customFieldsUI }) => {
  return(
    <Card fluid>
      <Card.Content>
        <SubjectsComponent record={record} vocabularies={vocabularies} />
        <KeywordsComponent customFieldsUI={customFieldsUI} />
      </Card.Content>
    </Card>
  )
}

const SubmissionComponent = () => {
  return(
    <Overridable id="InvenioAppRdm.Deposit.CardDepositStatusBox.container">
      <Card fluid>
        <Card.Content>
          <DepositStatusBox />
        </Card.Content>
        <Card.Content>
          <Grid relaxed>
            <Grid.Column
              computer={8}
              mobile={16}
              className="pb-0 left-btn-col"
            >
              <SaveButton fluid />
            </Grid.Column>

            <Grid.Column
              computer={8}
              mobile={16}
              className="pb-0 right-btn-col"
            >
              <PreviewButton fluid />
            </Grid.Column>

            <Grid.Column width={16} className="pt-10">
              <PublishButton fluid />
            </Grid.Column>
          </Grid>
        </Card.Content>
      </Card>
    </Overridable>
  )
}

const AccessRightsComponent = ({ permissions }) => {
  return(
    <Overridable
      id="InvenioAppRdm.Deposit.AccessRightField.container"
      fieldPath="access"
    >
      <AccessRightField
        label={i18next.t("Visibility")}
        labelIcon="shield"
        fieldPath="access"
        showMetadataAccess={permissions?.can_manage_record_access}
        fluid
      />
    </Overridable>
  )
}

const CombinedDatesComponent = ({ vocabularies }) => {
  return(
    <Card fluid
      id={'InvenioAppRdm.Deposit.CombinedDatesComponent.container'}
    >
      <Card.Content>
        <DateComponent />
        <AdditionalDatesComponent vocabularies={vocabularies} />
      </Card.Content>
    </Card>
  )
}

const DeleteComponent = ({ permissions, record }) => {
  return(
    <>
    {permissions?.can_delete_draft && (
      <Overridable
        id="InvenioAppRdm.Deposit.CardDeleteButton.container"
        record={record}
      >
        <Card fluid>
          <Card.Content>
            <DeleteButton fluid />
          </Card.Content>
        </Card>
      </Overridable>
    )}
    </>
  )
}


const fieldComponents = {
    abstract: AbstractComponent,
    additional_dates: AdditionalDatesComponent,
    additional_description: AdditionalDescriptionComponent,
    additional_titles: AdditionalTitlesComponent,
    ai: AIComponent,
    alternate_identifiers: AlternateIdentifiersComponent,
    communities: CommunitiesComponent,
    content_warning: ContentWarningComponent,
    contributors: ContributorsComponent,
    creators: CreatorsComponent,
    date: DateComponent,
    doi: DoiComponent,
    funding: FundingComponent,
    file_upload: FilesUploadComponent,
    keywords: KeywordsComponent,
    language: LanguagesComponent,
    licenses: LicensesComponent,
    metadata_only: MetadataOnlyComponent,
    previously_published: PreviouslyPublishedComponent,
    publisher_doi: PublisherDoiComponent,
    publisher: PublisherComponent,
    publication_location: PublicationLocationComponent,
    related_works: RelatedWorksComponent,
    resource_type: ResourceTypeComponent,
    subjects: SubjectsComponent,
    subtitle: SubtitleComponent,
    title: TitleComponent,
    total_pages: TotalPagesComponent,
    series_title: SeriesTitleComponent,
    series_number: SeriesNumberComponent,
    total_volumes: TotalVolumesComponent,
    volume: VolumeComponent,
    version: VersionComponent,
    // below are composite field components
    access_rights: AccessRightsComponent,
    admin_metadata: AdminMetadataComponent,
    book_detail: BookDetailComponent,
    combined_titles: CombinedTitlesComponent,
    combined_dates: CombinedDatesComponent,
    delete: DeleteComponent,
    subjects_keywords: SubjectKeywordsComponent,
    submission: SubmissionComponent,
    type_title: TypeTitleComponent,
}

const FormPage = ({ children, id, pageNums,
                    currentFormPage, handleFormPageChange
                  }) => {
  const currentPageIndex = pageNums.indexOf(currentFormPage);
  const nextPageIndex = currentPageIndex + 1;
  const previousPageIndex = currentPageIndex - 1;
  const nextPage = nextPageIndex < pageNums.length ? pageNums[nextPageIndex] : null;
  const previousPage = previousPageIndex >= 0 ? pageNums[previousPageIndex] : null;
  return(
    <>
    {/* // <Card fluid
    //   id={id}
    // >
    //   <Card.Content> */}

      <DndProvider backend={HTML5Backend}
        // options={{ rootElement: rootElement}}
      >
        {children}
        {!!previousPage &&
        <Button primary
          type="button"
          content={"Back"}
          floated="left"
          onClick={handleFormPageChange}
          value={previousPage}
        />}
        {!!nextPage &&
        <Button primary
          type="button"
          content={"Continue"}
          floated="right"
          onClick={handleFormPageChange}
          value={nextPage}
        />}
      </DndProvider>
      {/* </Card.Content>
    </Card> */}
  </>
  )
}

export class RDMDepositForm extends Component {
  constructor(props) {
    super(props);
    this.config = props.config || {};
    const { files, record } = this.props;
    this.state = {
      currentFormPage: "1",
    }

    // TODO: Make ALL vocabulary be generated by backend.
    // Currently, some vocabulary is generated by backend and some is
    // generated by frontend here. Iteration is faster and abstractions can be
    // discovered by generating vocabulary here. Once happy with vocabularies,
    // then we can generate it in the backend.
    this.vocabularies = {
      metadata: {
        ...this.config.vocabularies,

        creators: {
          ...this.config.vocabularies.creators,
          type: [
            { text: "Person", value: "personal" },
            { text: "Organization", value: "organizational" },
          ],
        },

        contributors: {
          ...this.config.vocabularies.contributors,
          type: [
            { text: "Person", value: "personal" },
            { text: "Organization", value: "organizational" },
          ],
        },
        identifiers: {
          ...this.config.vocabularies.identifiers,
        },
      },
    };

    // check if files are present
    this.noFiles = false;
    if (
      !Array.isArray(files.entries) ||
      (!files.entries.length && record.is_published)
    ) {
      this.noFiles = true;
    }

    this.handleFormPageChange = this.handleFormPageChange.bind(this)
    this.handleValuesChange = this.handleValuesChange.bind(this)
  }

  formFeedbackRef = createRef();
  sidebarRef = createRef();

  componentDidUpdate() {
  };
  componentWillMount() {
  };

  handleFormPageChange = (event, { value }) => {
    this.setState({currentFormPage: value});
  };

  handleValuesChange= (values) => {
    this.setState({values: values});
    console.log('changed values');
    console.log(values);
    localStorage.setItem('depositFormValues', JSON.stringify(values));
  }

  formPages = {
    '1': 'Title',
    '2': 'People',
    '3': 'Subjects',
    '4': 'Details',
    '5': 'Files',
    // '6': 'Admin',
    '7': 'Submit'
  }

  render() {
    const {
      record, files, permissions, preselectedCommunity
    } = this.props;
    const customFieldsUI = this.config.custom_fields.ui;
    const config = this.config;
    const vocabularies = this.vocabularies;
    const currentFormPage = this.state.currentFormPage;
    const currentValues = this.state.values;
    const currentResourceType = !!currentValues ? currentValues.metadata.resource_type : 'textDocument-book';
    const handleValuesChange = this.handleValuesChange;
    const currentTypeExtraFields = this.config.fields_config.extras_by_type[currentResourceType]

    return (
      <FormValuesContext.Provider
        value={{ currentValues, handleValuesChange }}
      >
      <DepositFormApp
        config={config}
        record={record}
        preselectedCommunity={preselectedCommunity}
        files={files}
        permissions={permissions}
      >
        <Overridable
          id="InvenioAppRdm.Deposit.FormFeedback.container"
          labels={config.custom_fields.error_labels}
          fieldPath="message"
        >
          <FormFeedback
            fieldPath="message"
            labels={config.custom_fields.error_labels}
          />
        </Overridable>

        <Container id="rdm-deposit-form" className="rel-mt-1">
          <Grid className="mt-25">
            <Grid.Column mobile={16} tablet={16} computer={16}>
              <h2>
                {record.id !== null ? "Updating " : "New "}
                {record.status === "draft" ? "Draft " : "Published "}Deposit
              </h2>
              <Step.Group
                widths={this.formPages.length}
                className="upload-form-pager"
                fluid={true}
                // ordered={true}
                size={"small"}
              >
                {Object.keys(this.formPages).map((pageNum, index) => (
                  <Step
                    key={index}
                    active={currentFormPage === pageNum}
                    // icon='truck'
                    link
                    onClick={this.handleFormPageChange}
                    title={this.formPages[pageNum]}
                    value={pageNum}
                    className={`upload-form-stepper-step page-${pageNum}`}
                    // description='Choose your shipping options'
                  >
                    {/* <Icon name='truck' /> */}
                    <Step.Content>
                      <Step.Title>{this.formPages[pageNum]}</Step.Title>
                      {/* <Step.Description>Choose your shipping options</Step.Description> */}
                    </Step.Content>
                  </Step>
                ))}
              </Step.Group>

              <Transition.Group
                animation="fade"
                duration={{show: 1000, hide: 20}}
              >
                {Object.keys(this.formPages).map((pageNum, index) => (
                  currentFormPage===pageNum && (
                    <div key={index}>
                      <FormPage
                        id={`InvenioAppRdm.Deposit.FormPage${pageNum}`}
                        pageNums={Object.keys(this.formPages)}
                        currentFormPage={pageNum}
                        handleFormPageChange={this.handleFormPageChange}
                        currentResourceType={currentResourceType}
                      >
                          {!!currentResourceType &&
                           !!currentTypeExtraFields[pageNum] ?
                           currentTypeExtraFields[pageNum].map((component_label, index) => {
                            const MyField = fieldComponents[component_label]
                            return (<MyField
                              key={index}
                              config={config}
                              noFiles={this.noFiles}
                              record={record}
                              vocabularies={vocabularies}
                              permissions={permissions}
                              accordionStyle={this.accordionStyle}
                              customFieldsUI={customFieldsUI}
                              currentResourceType={currentResourceType}
                            />)
                          }) : ""
                          }
                          {config.fields_config.common_fields[pageNum].map((component_label, index) => {
                            const MyField = fieldComponents[component_label]
                            return (<MyField
                              key={index}
                              config={config}
                              noFiles={this.noFiles}
                              record={record}
                              vocabularies={vocabularies}
                              permissions={permissions}
                              accordionStyle={this.accordionStyle}
                              customFieldsUI={customFieldsUI}
                              currentResourceType={currentResourceType}
                            />)
                          }
                          )}
                      </FormPage>
                    </div>
                  )
                )
                )}
                </Transition.Group>


            </Grid.Column>

          </Grid>
        </Container>
      </DepositFormApp>
    </FormValuesContext.Provider>
    );
  }
}

RDMDepositForm.propTypes = {
  config: PropTypes.object.isRequired,
  record: PropTypes.object.isRequired,
  preselectedCommunity: PropTypes.object,
  files: PropTypes.object,
  permissions: PropTypes.object,
};

RDMDepositForm.defaultProps = {
  preselectedCommunity: undefined,
  permissions: null,
  files: null,
};

export { FormValuesContext };