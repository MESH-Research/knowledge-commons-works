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
  Button,
  Card,
  Container,
  Divider,
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
        <FieldLabel htmlFor={"imprint:imprint"}
          icon={"book"}
          label={"Book details"}
        />
        <Divider fitted />
        <Grid padded>
          <Grid.Row>
            <Grid.Column width="8">
              <CustomFieldInjector
                sectionName="Book / Report / Chapter"
                fieldName="imprint:imprint.isbn"
                idString="ImprintISBNField"
                description=""
                customFieldsUI={customFieldsUI}
              />
            </Grid.Column>
            <Grid.Column width="8">
              <VersionComponent description=""
                label="Edition or Version"
                icon=""
              />
            </Grid.Column>
          </Grid.Row>
          <Grid.Row>
            <Grid.Column width="8">
              <PublisherComponent />
            </Grid.Column>
            <Grid.Column width="8">
              <PublicationLocationComponent customFieldsUI={customFieldsUI} />
            </Grid.Column>
          </Grid.Row>
          <Grid.Row>
            <VolumeComponent customFieldsUI={customFieldsUI} />
          </Grid.Row>
          <Grid.Row>
            <Grid.Column width="8">
              <CustomFieldInjector
                sectionName="Book / Report / Chapter"
                fieldName="imprint:imprint.pages"
                idString="ImprintPagesField"
                customFieldsUI={customFieldsUI}
                description={""}
                label="Number of Pages"
              />
            </Grid.Column>
          </Grid.Row>
      </Grid>
      </Card.Content>
    </Card>
)}

const CombinedTitlesComponent = ({vocabularies, record}) => {
  return(
    <Card fluid
      id={'InvenioAppRdm.Deposit.CombinedTitlesComponent.container'}
      as="fieldset"
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
      as="fieldset"
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

export {AdminMetadataComponent,
        BookDetailComponent,
        CombinedTitlesComponent,
        TypeTitleComponent,
        SubjectKeywordsComponent,
        SubmissionComponent,
        AccessRightsComponent,
        CombinedDatesComponent,
        DeleteComponent
};