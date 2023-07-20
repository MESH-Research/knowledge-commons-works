// Part of the Knowledge Commons Repository
// Copyright (C) 2023 MESH Research
//
// based on portions of InvenioRDM
// Copyright (C) 2020-2022 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021-2022 Graz University of Technology.
// Copyright (C) 2022-2023 KTH Royal Institute of Technology.
//
// The Knowledge Commons Repository and Invenio App RDM are both free software;
// you can redistribute them and/or modify them
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component, createContext, createRef, forwardRef, Fragment,
                useEffect, useLayoutEffect, useRef, useState } from "react";
import _get from "lodash/get";
import _isEmpty from "lodash/isEmpty";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { AccordionField, CustomFields, FieldLabel, loadWidgetsFromConfig } from "react-invenio-forms";
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
  Card,
  Container,
  Divider,
  Segment,
} from "semantic-ui-react";
// import PropTypes from "prop-types";
import Overridable from "react-overridable";
import ResourceTypeField from "../metadata_fields/ResourceTypeField";
import { PIDField } from "../metadata_fields/PIDField";
import { DatesField } from "../metadata_fields/DatesField";
import { HTML5Backend } from "react-dnd-html5-backend";
import { DndProvider } from "react-dnd";


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
    <Segment
      id={'InvenioAppRdm.Deposit.AbstractComponent.container'}
      as="fieldset"
    >
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
    </Segment>
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
    <Segment
      as="fieldset"
    >
      <CustomFieldInjector
        sectionName="AI Usage"
        fieldName="kcr:ai_usage"
        idString="AIUsageField"
        customFieldsUI={customFieldsUI}
      />
    </Segment>
  )
}

const AlternateIdentifiersComponent = ({vocabularies}) => {
  return(
    <Segment as="fieldset">
      <Overridable
        id="InvenioAppRdm.Deposit.IdentifiersField.container"
        vocabularies={vocabularies}
        fieldPath="metadata.identifiers"
      >
        <IdentifiersField
          fieldPath="metadata.identifiers"
          label={i18next.t("URL or Alternate Identifiers")}
          labelIcon="barcode"
          schemeOptions={vocabularies.metadata.identifiers.scheme}
          showEmptyValue
        />
      </Overridable>
    </Segment>
  )
}

const BookTitleComponent = ({customFieldsUI}) => {
  return(
    <CustomFieldInjector
      sectionName="Book / Report / Chapter"
      fieldName="imprint:imprint.title"
      idString="ImprintTitleField"
      customFieldsUI={customFieldsUI}
      description={""}
    />
  )
}

const CommunitiesComponent = () => {
  return(
    <Segment as="fieldset" className="communities-field">
      <Overridable id="InvenioAppRdm.Deposit.CommunityHeader.container">
        <CommunityHeader imagePlaceholderLink="/static/images/square-placeholder.png" />
      </Overridable>
    </Segment>
)}

const ContentWarningComponent = ({ customFieldsUI }) => {
  return(
    <Segment as="fieldset">
      <CustomFieldInjector
        fieldName="kcr:content_warning"
        sectionName="Content warning"
        idString="ContentWarning"
        customFieldsUI={customFieldsUI}
      />
    </Segment>
  )
}

const ContributorsComponent = ({config, vocabularies}) => {
  return(
    <Segment
      id={'InvenioAppRdm.Deposit.ContributorsField.card'}
      as="fieldset"
    >
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
    </Segment>
)
}

const CreatorsComponent = ({config, vocabularies}) => {
  return(
    <Segment
      id={'InvenioAppRdm.Deposit.CreatorsField.card'}
      as="fieldset"
    >
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
    </Segment>
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
    <Segment as="fieldset" className="pid-field">
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
    </Segment>
)}

const FilesUploadComponent = ({config, noFiles, record, permissions}) => {
  return(
    <Segment as="fieldset">
    {/* <Overridable
      id="InvenioAppRdm.Deposit.AccordionFieldFiles.container"
      record={record}
      config={config}
      noFiles={noFiles}
    >*/}
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
    {/*</Overridable> */}
    </Segment>
  )
}

const FundingComponent = ({}) => {
  return(
    <Segment
      id="InvenioAppRdm.Deposit.AccordionFieldFunding.card"
      as="fieldset"
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
    </Segment>
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
    <Segment as="fieldset">
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
    </Segment>
  )
}

const LicensesComponent = () => {
  return(
    <Segment as="fieldset">
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
    </Segment>
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
      <PublisherField
        fieldPath="metadata.publisher"
        description=""
        labelIcon=""
        helpText=""
      />
    </Overridable>
  )
}

const PublicationLocationComponent = ({customFieldsUI}) => {
  return(
    <CustomFieldInjector
      sectionName="Book / Report / Chapter"
      fieldName="imprint:imprint.place"
      idString="ImprintPlaceField"
      customFieldsUI={customFieldsUI}
      label={"Place of Publication"}
      description={""}
    />
  )
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
    <Segment as="fieldset">
      <Overridable
        id="InvenioAppRdm.Deposit.RelatedWorksField.container"
        fieldPath="metadata.related_identifiers"
        vocabularies={vocabularies}
      >
        <RelatedWorksField
          fieldPath="metadata.related_identifiers"
          options={vocabularies.metadata.identifiers}
          showEmptyValue={false}
        />
      </Overridable>
    </Segment>
  )
}

const ResourceTypeComponent = ({vocabularies}) => {
  return(
    <Segment
      id={'InvenioAppRdm.Deposit.ResourceTypeComponent.container'}
      as="fieldset"
      className="resource-type-field"
    >
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
    </Segment>
  )
}

const SeriesComponent = ({ customFieldsUI }) => {
  return(
    <Segment as="fieldset">
      <CustomFieldInjector
        sectionName="Series"
        fieldName="kcr:book_series"
        idString="KcrBookSeries"
        icon="list"
        customFieldsUI={customFieldsUI}
      />
    </Segment>
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
  const required = true;
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
        label={"Title"}
        required={required}
      />
    </Overridable>
)
}

const TotalPagesComponent = () => {
  return(<></>)
}

const VolumeComponent = ({ customFieldsUI }) => {
  return(
    <CustomFieldInjector
      sectionName="KCR Book information"
      fieldName="kcr:volumes"
      idString="KcrVolumes"
      customFieldsUI={customFieldsUI}
    />
  )
}

const VersionComponent = ({description, label, icon}) => {
  return(
    <Overridable
      id="InvenioAppRdm.Deposit.VersionField.container"
      fieldPath="metadata.version"
    >
      <VersionField fieldPath="metadata.version"
        description={description}
        label={label}
        labelIcon={icon}
        helpText=""
      />
    </Overridable>
  )
}

export { CustomFieldInjector,
         CustomFieldSectionInjector,
         AbstractComponent,
         AdditionalDatesComponent,
         AdditionalDescriptionComponent,
         AdditionalTitlesComponent,
         AIComponent,
         AlternateIdentifiersComponent,
         BookTitleComponent,
         CommunitiesComponent,
         ContentWarningComponent,
         ContributorsComponent,
         CreatorsComponent,
         DateComponent,
         DoiComponent,
         FilesUploadComponent,
         FundingComponent,
         KeywordsComponent,
         LanguagesComponent,
         LicensesComponent,
         MetadataOnlyComponent,
         PreviouslyPublishedComponent,
         PublisherDoiComponent,
         PublisherComponent,
         PublicationLocationComponent,
         ReferencesComponent,
         RelatedWorksComponent,
         ResourceTypeComponent,
         SubjectsComponent,
         SubtitleComponent,
         TitleComponent,
         TotalPagesComponent,
         SeriesComponent,
         VolumeComponent,
         VersionComponent
        };