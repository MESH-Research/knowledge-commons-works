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
import {AccessRightsComponent,
        AdminMetadataComponent,
        BookDetailComponent,
        BookVolumePagesComponent,
        CombinedDatesComponent,
        CombinedTitlesComponent,
        DeleteComponent,
        PublicationDetailsComponent,
        SubjectKeywordsComponent,
        SubmissionComponent,
        TypeTitleComponent,
} from "./compound_field_components";


// React Context to track the current form values.
// Will contain the Formik values object passed up from a
// form field.
const FormValuesContext = createContext();


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
    series: SeriesComponent,
    subjects: SubjectsComponent,
    subtitle: SubtitleComponent,
    title: TitleComponent,
    total_pages: TotalPagesComponent,
    volume: VolumeComponent,
    version: VersionComponent,
    // below are composite field components
    access_rights: AccessRightsComponent,
    admin_metadata: AdminMetadataComponent,
    book_detail: BookDetailComponent,
    book_volume_pages: BookVolumePagesComponent,
    combined_titles: CombinedTitlesComponent,
    combined_dates: CombinedDatesComponent,
    delete: DeleteComponent,
    publication_detail: PublicationDetailsComponent,
    subjects_keywords: SubjectKeywordsComponent,
    submission: SubmissionComponent,
    type_title: TypeTitleComponent,
}

const FormPage = forwardRef(({ children, id, pageNums,
                    currentFormPage, handleFormPageChange
                  }, ref) => {
  const currentPageIndex = pageNums.indexOf(currentFormPage);
  const nextPageIndex = currentPageIndex + 1;
  const previousPageIndex = currentPageIndex - 1;
  const nextPage = nextPageIndex < pageNums.length ? pageNums[nextPageIndex] : null;
  const previousPage = previousPageIndex >= 0 ? pageNums[previousPageIndex] : null;
  return(
    <div className="formPageWrapper" id={id} ref={ref}>
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
    </div>
  )
});

export const RDMDepositForm = ({ config, files, record, permissions, preselectedCommunity}) => {
    config = config || {};
    const [currentFormPage, setCurrentFormPage] = useState("1");
    console.log(`current form page at top: ${currentFormPage}`);
    const [formValues, setFormValues] = useState({});
    const [currentResourceType, setCurrentResourceType] = useState('textDocument-journalArticle');
    const [currentTypeExtraFields, setCurrentTypeExtraFields] = useState(config.fields_config.extras_by_type[currentResourceType]);
    const ref1 = useRef(null);
    const ref2 = useRef(null);
    const formPages = {
      '1': ['Title', ref1],
      '2': ['People', ref2],
      '3': ['Subjects', useRef(null)],
      '4': ['Details', useRef(null)],
      '5': ['Files', useRef(null)],
      // '6': 'Admin',
      '7': ['Submit', useRef(null)],
    }
    const customFieldsUI = config.custom_fields.ui;

    const setFormPageInHistory = (value) => {
      if ( value === undefined ) {
        value = currentFormPage;
      }
      console.log(`setting page in history to ${value}`);
      console.log(window.history.length);
      let urlParams = new URLSearchParams(window.location.search);
      console.log(urlParams.toString());
      if ( !urlParams.has('depositFormPage') ) {
        urlParams.append('depositFormPage', value);
      } else if ( !urlParams.depositFormPage !== value) {
        urlParams.set("depositFormPage", value);
      }
      console.log(urlParams.toString());
      const currentBaseURL = window.location.origin;
      const currentPath = window.location.pathname;
      const currentParams = urlParams.toString();
      const newCurrentURL = `${currentBaseURL}${currentPath}?${currentParams}`;
      window.history.pushState('fake-route', document.title, newCurrentURL);
    }

    const handleFormPageParam = () => {
      console.log(`setting current page based on param`);
      const urlParams = new URLSearchParams(window.location.search);
      const urlFormPage = urlParams.get('depositFormPage');
      console.log(`urlFormPage is ${urlFormPage}`);
      console.log(`currentFormPage is ${currentFormPage}`);
      // if ( !!urlFormPage && urlFormPage !== currentFormPage ) {
      if ( !!urlFormPage ) {
        console.log(`changing current to ${urlFormPage}`);
        setCurrentFormPage(urlFormPage);
      }
    }

    // useEffect(() => {
    //   setFormPageInHistory();
    // }, [currentFormPage]
    // )

    useEffect(() => {
      console.log('initial setup');
      // Add a fake history event so that the back button does nothing if pressed once
      // console.log(window.history.state);
      // console.log(window.history.href);
      // const currentBaseURL = window.location.origin;
      // const currentPath = window.location.pathname;
      // const currentParams = window.location.search || "?";
      // const newCurrentURL = `${currentBaseURL}${currentPath}${currentParams}depositFormPage=${currentFormPage}`;

      handleFormPageParam();
      setFormPageInHistory();
      // window.history.pushState('fake-route', document.title, window.history.href);
      // console.log(window.history.state);
      // console.log(window.history.href);
      window.addEventListener('popstate', handleFormPageParam);

      // // Here is the cleanup when this component unmounts
      return () => {
        window.removeEventListener('popstate', handleFormPageParam);
        // If we left without using the back button, aka by using a button on the page, we need to clear out that fake history event
        if (window.history.state === 'fake-route') {
          window.history.back();
        }
      }
    //   console.log("");
    }, []);

    let formFeedbackRef = useRef(0);
    let sidebarRef = useRef(0);

    // TODO: Make ALL vocabulary be generated by backend.
    // Currently, some vocabulary is generated by backend and some is
    // generated by frontend here. Iteration is faster and abstractions can be
    // discovered by generating vocabulary here. Once happy with vocabularies,
    // then we can generate it in the backend.
    const vocabularies = {
      metadata: {
        ...config.vocabularies,

        creators: {
          ...config.vocabularies.creators,
          type: [
            { text: "Person", value: "personal" },
            { text: "Organization", value: "organizational" },
          ],
        },

        contributors: {
          ...config.vocabularies.contributors,
          type: [
            { text: "Person", value: "personal" },
            { text: "Organization", value: "organizational" },
          ],
        },
        identifiers: {
          ...config.vocabularies.identifiers,
        },
      },
    };

    // check if files are present
    let noFiles = false;
    if (
      !Array.isArray(files.entries) ||
      (!files.entries.length && record.is_published)
    ) {
      noFiles = true;
    }

    useLayoutEffect(() => {
      const newPageWrapper = document.getElementById(`InvenioAppRdm.Deposit.FormPage${currentFormPage}`);
      const newFirstInput = newPageWrapper.querySelectorAll('button, input')[0];
      newFirstInput.focus();
    }, [currentFormPage]
    );

    const handleFormPageChange = (event, { value }) => {
      setCurrentFormPage(value);
      setFormPageInHistory(value);
    };

    const handleValuesChange= (values) => {
      setFormValues(values);
      // console.log('changed values');
      // console.log(values);
      localStorage.setItem('depositFormValues', JSON.stringify(values));
      setCurrentResourceType(values.metadata.resource_type);
      setCurrentTypeExtraFields(config.fields_config.extras_by_type[values.metadata.resource_type]);
    }

    return (
      <FormValuesContext.Provider
        value={{ formValues, handleValuesChange }}
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
                widths={formPages.length}
                className="upload-form-pager"
                fluid={true}
                // ordered={true}
                size={"small"}
              >
                {Object.keys(formPages).map(([pageNum, pageRef], index) => (
                  <Step
                    key={index}
                    as={Button}
                    active={currentFormPage === pageNum}
                    // icon='truck'
                    link
                    onClick={handleFormPageChange}
                    value={pageNum}
                    className={`upload-form-stepper-step page-${pageNum}`}
                    // description='Choose your shipping options'
                  >
                    {/* <Icon name='truck' /> */}
                    <Step.Content>
                      <Step.Title>{formPages[pageNum][0]}</Step.Title>
                      {/* <Step.Description>Choose your shipping options</Step.Description> */}
                    </Step.Content>
                  </Step>
                ))}
              </Step.Group>

              <Transition.Group
                animation="fade"
                duration={{show: 1000, hide: 20}}
              >
                {Object.keys(formPages).map(([pageNum, pageRef], index) => (
                  currentFormPage===pageNum && (
                    <div key={index}>
                      <FormPage
                        id={`InvenioAppRdm.Deposit.FormPage${pageNum}`}
                        pageNums={Object.keys(formPages)}
                        currentFormPage={pageNum}
                        handleFormPageChange={handleFormPageChange}
                        currentResourceType={currentResourceType}
                        ref={pageRef}
                      >
                          {!!currentResourceType &&
                           !!currentTypeExtraFields[pageNum] ?
                           currentTypeExtraFields[pageNum].map((component_label, index) => {
                            const MyField = fieldComponents[component_label]
                            return (<MyField
                              key={index}
                              config={config}
                              noFiles={noFiles}
                              record={record}
                              vocabularies={vocabularies}
                              permissions={permissions}
                              // accordionStyle={accordionStyle}
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
                              noFiles={noFiles}
                              record={record}
                              vocabularies={vocabularies}
                              permissions={permissions}
                              // accordionStyle={accordionStyle}
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