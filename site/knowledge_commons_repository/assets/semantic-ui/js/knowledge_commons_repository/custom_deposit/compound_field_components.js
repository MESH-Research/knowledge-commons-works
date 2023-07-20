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
                useContext,
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
  Form,
  Grid,
  Segment,
} from "semantic-ui-react";
import PropTypes from "prop-types";
import Overridable from "react-overridable";
import ResourceTypeField from "../metadata_fields/ResourceTypeField";
import { PIDField } from "../metadata_fields/PIDField";
import { DatesField } from "../metadata_fields/DatesField";
import { HTML5Backend } from "react-dnd-html5-backend";
import { DndProvider } from "react-dnd";
import { CustomFieldInjector,
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
          } from "./field_components";
import { useFormikContext } from "formik";
import { FormValuesContext } from "./custom_RDMDepositForm";


const AdminMetadataComponent = ({customFieldsUI}) => {
  return(
    <Segment as="fieldset">
        <CustomFieldInjector
          sectionName="Commons admin info"
          idString="AdminMetadataFields"
          customFieldsUI={customFieldsUI}
        />
    </Segment>
)}

const PublicationDetailsComponent = ({customFieldsUI}) => {
  return(
    <Segment as="fieldset">
        {/* <FieldLabel htmlFor={"imprint:imprint"}
          icon={"book"}
          label={"Publication Details"}
        /> */}
        {/* <Divider fitted /> */}
        <Form.Group widths="equal">
            <CustomFieldInjector
              sectionName="Book / Report / Chapter"
              fieldName="imprint:imprint.isbn"
              idString="ImprintISBNField"
              description="e.g. 0-06-251587-X"
              placeholder=""
              customFieldsUI={customFieldsUI}
            />
            <VersionComponent description=""
              label="Edition or Version"
              icon=""
            />
        </Form.Group>
        <Form.Group widths="equal">
            <PublisherComponent />
            <PublicationLocationComponent customFieldsUI={customFieldsUI} />
        </Form.Group>
    </Segment>
  )
}

const BookDetailComponent = ({customFieldsUI}) => {
  return(
    <Segment as="fieldset">
      {/* <FieldLabel htmlFor={"imprint:imprint"}
        icon={"book"}
        label={"Book details"}
      />
      <Divider fitted /> */}
      <Form.Group>
          <CustomFieldInjector
          sectionName="Book / Report / Chapter"
          fieldName="imprint:imprint.isbn"
          idString="ImprintISBNField"
          description=""
          customFieldsUI={customFieldsUI}
          />
          <VersionComponent description=""
          label="Edition or Version"
          icon=""
          />
      </Form.Group>
      <Form.Group>
            <PublisherComponent />
            <PublicationLocationComponent customFieldsUI={customFieldsUI} />
      </Form.Group>
      <Form.Group>
          <VolumeComponent customFieldsUI={customFieldsUI} />
      </Form.Group>
      <Form.Group>
            <CustomFieldInjector
              sectionName="Book / Report / Chapter"
              fieldName="imprint:imprint.pages"
              idString="ImprintPagesField"
              customFieldsUI={customFieldsUI}
              description={""}
              label="Number of Pages"
            />
      </Form.Group>
      <Form.Group>
          <CustomFieldInjector
          sectionName="Series"
          fieldName="kcr:book_series"
          idString="KcrBookSeries"
          customFieldsUI={customFieldsUI}
          />
      </Form.Group>
    </Segment>
)}

const BookVolumePagesComponent = ({customFieldsUI}) => {
    return(
      <Segment as="fieldset">
        <Form.Group widths="equal">
          <VolumeComponent customFieldsUI={customFieldsUI} />
          <CustomFieldInjector
          sectionName="Book / Report / Chapter"
          fieldName="imprint:imprint.pages"
          idString="ImprintPagesField"
          customFieldsUI={customFieldsUI}
          description={""}
          label="Total pages"
          />
        </Form.Group>
      </Segment>
    )
}

const CombinedTitlesComponent = ({vocabularies, record}) => {
  return(
    <Segment
      id={'InvenioAppRdm.Deposit.CombinedTitlesComponent.container'}
      as="fieldset"
    >
      <TitleComponent vocabularies={vocabularies} record={record} />
    </Segment>
  )
}

const TypeTitleComponent = ({vocabularies, record}) => {
  return(
    <Segment
      id={'InvenioAppRdm.Deposit.TypeTitleComponent.container'}
      as="fieldset"
    >
      <TitleComponent vocabularies={vocabularies} record={record} />
      <ResourceTypeComponent vocabularies={vocabularies} />
    </Segment>
  )
};

const SubjectKeywordsComponent = ({ record, vocabularies, customFieldsUI }) => {
  return(
    <Segment as="fieldset">
      <SubjectsComponent record={record} vocabularies={vocabularies} />
      <KeywordsComponent customFieldsUI={customFieldsUI} />
    </Segment>
  )
}

const SubmissionComponent = () => {

  return(
    <Overridable id="InvenioAppRdm.Deposit.CardDepositStatusBox.container">
      <Segment as="fieldset">
          <DepositStatusBox />
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
      </Segment>
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
    <Segment
      id={'InvenioAppRdm.Deposit.CombinedDatesComponent.container'}
      as="fieldset"
      className="combined-dates-field"
    >
      <DateComponent />
      <AdditionalDatesComponent vocabularies={vocabularies} />
    </Segment>
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
        <Segment as="fieldset">
          <DeleteButton fluid />
        </Segment>
      </Overridable>
    )}
    </>
  )
}

const SubmitActionsComponent = ({permissions, record}) => {
  return(
    <Grid>
      <Grid.Column width="8">
        <SubmissionComponent />
        <DeleteComponent permissions={permissions} record={record} />
      </Grid.Column>
      <Grid.Column width="8">
        <AccessRightsComponent permissions={permissions} />
      </Grid.Column>
    </Grid>
  )
}

export {AccessRightsComponent,
        AdminMetadataComponent,
        BookDetailComponent,
        BookVolumePagesComponent,
        CombinedDatesComponent,
        CombinedTitlesComponent,
        DeleteComponent,
        PublicationDetailsComponent,
        SubjectKeywordsComponent,
        SubmissionComponent,
        SubmitActionsComponent,
        TypeTitleComponent,
};