// This file is part of InvenioRDM
// Copyright (C) 2020-2022 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021-2022 Graz University of Technology.
// Copyright (C) 2022-2023 KTH Royal Institute of Technology.
//
// Invenio App RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component, createContext, createRef, Fragment } from "react";
import _get from "lodash/get";
import _isEmpty from "lodash/isEmpty";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { AccordionField, CustomFields } from "react-invenio-forms";
import {
  AccessRightField,
  DescriptionsField,
  CreatibutorsField,
  DatesField,
  DeleteButton,
  DepositFormApp,
  DepositStatusBox,
  FileUploader,
  FormFeedback,
  IdentifiersField,
  PIDField,
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
  Ref,
  Sticky,
  Transition
} from "semantic-ui-react";
import PropTypes from "prop-types";
import Overridable from "react-overridable";
import ResourceTypeField from "./ResourceTypeField";

const ResourceTypeContext = createContext();

const AbstractComponent = ({record, vocabularies}) => {
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
        showEmptyValue
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

const AIComponent = () => {
  return(<></>)
}

const AlternateIdentifiersComponent = ({vocabularies}) => {
  return(
    <Overridable
      id="InvenioAppRdm.Deposit.AccordionFieldAlternateIdentifiers.container"
      vocabularies={vocabularies}
    >
      <AccordionField
        includesPaths={["metadata.identifiers"]}
        active
        label={i18next.t("Alternate identifiers")}
      >
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
      </AccordionField>
    </Overridable>
  )
}


const CommunitiesComponent = () => {
  return(
    <Overridable id="InvenioAppRdm.Deposit.CommunityHeader.container">
      <CommunityHeader imagePlaceholderLink="/static/images/square-placeholder.png" />
    </Overridable>
)}

const ContentWarningComponent = () => {
  return(<></>)
}

const ContributorsComponent = ({config, vocabularies}) => {
  return(
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
      />
    </Overridable>
)
}

const CreatorsComponent = ({config, vocabularies}) => {
  return(
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
      />
    </Overridable>
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
)}

const FilesUploadComponent = ({config, noFiles, record, permissions}) => {
  return(
    <Overridable
      id="InvenioAppRdm.Deposit.AccordionFieldFiles.container"
      record={record}
      config={config}
      noFiles={noFiles}
    >
      <AccordionField
        includesPaths={["files.enabled"]}
        active
        label={i18next.t("Files")}
      >
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
      </AccordionField>
    </Overridable>
  )
}

const FundingComponent = ({accordionStyle}) => {
  return(
    <Overridable
      id="InvenioAppRdm.Deposit.AccordionFieldFunding.container"
      ui={accordionStyle}
    >
      <AccordionField
        includesPaths={["metadata.funding"]}
        active
        label="Funding"
        ui={accordionStyle}
      >
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
            label="Awards"
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
      </AccordionField>
    </Overridable>
  )
}

const KeywordsComponent = () => {
  return(<></>)
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
    <Overridable
      id="InvenioAppRdm.Deposit.AccordionFieldRelatedWorks.container"
      vocabularies={vocabularies}
    >
      <AccordionField
        includesPaths={["metadata.related_identifiers"]}
        active
        label={i18next.t("Related works")}
      >
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
      </AccordionField>
    </Overridable>
  )
}

const ResourceTypeComponent = ({vocabularies}) => {
  return(
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
    version: VersionComponent
}

const AdminMetadataComponent = ({customFieldsUI}) => {
  const kcrAdminInfoConfig = new Array(customFieldsUI.find(item => item.section === ''));
  return(
    <Overridable
      id="InvenioAppRdm.Deposit.AdminMetadataFields.container"
      customFieldsUI={kcrAdminInfoConfig}
    >
      <CustomFields
        config={kcrAdminInfoConfig}
        templateLoaders={[
          (widget) => import(`@templates/custom_fields/${widget}.js`),
          (widget) =>
            import(`@js/invenio_rdm_records/src/deposit/customFields`),
          (widget) => import(`react-invenio-forms`),
        ]}
        fieldPathPrefix="custom_fields"
      />
    </Overridable>
)}

const BookDetailComponent = ({customFieldsUI}) => {
  const bookDetailConfig = new Array(customFieldsUI.find(item => item.section === 'Book information'));
  return(
    <Overridable
      // id="InvenioAppRdm.Deposit.CustomFields.container"
      id="InvenioAppRdm.Deposit.BookDetailFields.container"
      customFieldsUI={bookDetailConfig}
    >
      <CustomFields
        config={bookDetailConfig}
        templateLoaders={[
          (widget) => import(`@templates/custom_fields/${widget}.js`),
          (widget) =>
            import(`@js/invenio_rdm_records/src/deposit/customFields`),
          (widget) => import(`react-invenio-forms`),
        ]}
        fieldPathPrefix="custom_fields"
      />
    </Overridable>
)}

const fieldSetComponents = {
  admin_metadata: AdminMetadataComponent,
  book_detail: BookDetailComponent
}

const FormPage = ({ children, id, pageNums,
                    currentFormPage, handleFormPageChange
                  }) => {
  const currentPageIndex = pageNums.indexOf(currentFormPage);
  const nextPageIndex = currentPageIndex + 1;
  const previousPageIndex = currentPageIndex - 1;
  const nextPage = nextPageIndex < pageNums.length - 1 ? pageNums[nextPageIndex] : null;
  const previousPage = previousPageIndex >= 0 ? pageNums[previousPageIndex] : null;
  return(
    <Card fluid
      id={id}
    >
      <Card.Content>
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
      </Card.Content>
    </Card>
  )
}

export class RDMDepositForm extends Component {
  constructor(props) {
    super(props);
    this.config = props.config || {};
    const { files, record } = this.props;
    this.state = {
      currentFormPage: "1",
      currentResourceType: "textDocument-book"
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
    this.handleResourceTypeChange = this.handleResourceTypeChange.bind(this)
  }

  formFeedbackRef = createRef();
  sidebarRef = createRef();

  componentDidUpdate() {
    console.log(this.config.fields_config);
    console.log(`currentFormPage: ${this.state.currentFormPage}`);
    console.log(`currentResourceType: ${this.state.currentResourceType}`);
    console.log(this.config.fields_config.extras_by_type);
  };
  componentWillMount() {
    console.log(`currentFormPage: ${this.state.currentFormPage}`);
    console.log(`currentResourceType: ${this.state.currentResourceType}`);
    console.log(this.config.fields_config.extras_by_type[this.state.currentResourceType]['1']['subsets']);
    console.log(this.state.currentFormPage==="1");
    console.log(typeof this.state.currentFormPage);
    console.log(!!this.config.fields_config.extras_by_type[this.state.currentResourceType]['1']['subsets']);
  };

  handleFormPageChange = (event) => {
    this.setState({currentFormPage: event.target.value});
    event.preventDefault();
  };

  handleResourceTypeChange = (resourceType) => {
    this.setState({currentResourceType: resourceType});
  }

  formPages = {
    '1': 'Title Information',
    '2': 'People',
    '3': 'Subjects',
    '4': 'Deposit Details',
    '5': 'File Upload',
    '6': 'Admin Metadata'
  }
  render() {
    const {
      record, files, permissions, preselectedCommunity
    } = this.props;
    const customFieldsUI = this.config.custom_fields.ui;
    const config = this.config;
    const vocabularies = this.vocabularies;
    const currentFormPage = this.state.currentFormPage;
    const currentResourceType = this.state.currentResourceType;
    const handleResourceTypeChange = this.handleResourceTypeChange;
    const currentTypeExtraFields = this.config.fields_config.extras_by_type[this.state.currentResourceType]

    return (
      <ResourceTypeContext.Provider
        value={{ currentResourceType, handleResourceTypeChange }}
      >
      <DepositFormApp
        config={config}
        record={record}
        preselectedCommunity={preselectedCommunity}
        files={files}
        permissions={permissions}
        handleResourceTypeChange={handleResourceTypeChange}
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
            <Grid.Column mobile={16} tablet={16} computer={11}>
              <h2>{currentResourceType}</h2>
              <Button.Group widths={this.formPages.length}
                className="upload-form-pager"
                fluid={true}
              >
                {Object.keys(this.formPages).map((pageNum, index) => (
                  <Button
                    key={index}
                    onClick={this.handleFormPageChange}
                    className={`upload-form-pager-button page-${pageNum}`}
                    content={this.formPages[pageNum]}
                    type="button"
                    value={pageNum}
                    // basic={pageNum<=currentFormPage ? false : true}
                    color={pageNum<=currentFormPage ? "green" : "grey"}
                  />
                ))}
              </Button.Group>

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
                          {!!currentTypeExtraFields[pageNum]['subsets'] ?
                           currentTypeExtraFields[pageNum]['subsets'].map((component_label, index) => {
                            const MyField = fieldSetComponents[component_label]
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
                          {!!currentResourceType &&
                           !!currentTypeExtraFields[pageNum]['fields'] ?
                           currentTypeExtraFields[pageNum]['fields'].map((component_label, index) => {
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
                      </FormPage>
                    </div>
                  )
                )
                )}
                </Transition.Group>


            </Grid.Column>
            <Ref innerRef={this.sidebarRef}>
              <Grid.Column
                mobile={16}
                tablet={16}
                computer={5}
                className="deposit-sidebar"
              >
                <Sticky context={this.sidebarRef} offset={20}>
                  <Overridable id="InvenioAppRdm.Deposit.CardDepositStatusBox.container">
                    <Card>
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
                  <Overridable
                    id="InvenioAppRdm.Deposit.AccessRightField.container"
                    fieldPath="access"
                  >
                    <AccessRightField
                      label={i18next.t("Visibility")}
                      labelIcon="shield"
                      fieldPath="access"
                      showMetadataAccess={permissions?.can_manage_record_access}
                    />
                  </Overridable>
                  {permissions?.can_delete_draft && (
                    <Overridable
                      id="InvenioAppRdm.Deposit.CardDeleteButton.container"
                      record={record}
                    >
                      <Card>
                        <Card.Content>
                          <DeleteButton fluid />
                        </Card.Content>
                      </Card>
                    </Overridable>
                  )}
                </Sticky>
              </Grid.Column>
            </Ref>
          </Grid>
        </Container>
      </DepositFormApp>
    </ResourceTypeContext.Provider>
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

export { ResourceTypeContext };