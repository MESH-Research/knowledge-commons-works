// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
// Copyright (C) 2022 data-futures.org.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component, createRef, useState } from "react";
import PropTypes from "prop-types";
import { Button, Divider, Form, Grid, Header, Modal } from "semantic-ui-react";
import { Formik } from "formik";
import {
  Image,
  SelectField,
  TextField,
  RadioField,
  RemoteSelectField,
} from "react-invenio-forms";
import * as Yup from "yup";
import _get from "lodash/get";
import _find from "lodash/find";
import _isEmpty from "lodash/isEmpty";
import _map from "lodash/map";
import { AffiliationsField } from "./AffiliationsField";
import { CreatibutorsIdentifiers } from "./CreatibutorsIdentifiers";
import { CREATIBUTOR_TYPE } from "./types";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { Trans } from "react-i18next";

const onPersonSearchChange = (
  { formikProps },
  selectedSuggestions,
  identifiersRef,
  affiliationsRef,
  parentFieldPath = "creators"
) => {
  if (selectedSuggestions[0].key === "manual-entry") {
    // Empty the autocomplete's selected values
    this.namesAutocompleteRef.current.setState({
      suggestions: [],
      selectedSuggestions: [],
    });
    this.setState({
      showPersonForm: true,
    });
    return;
  }

  this.setState(
    {
      showPersonForm: true,
    },
    () => {
      const identifiers = selectedSuggestions[0].extra.identifiers.map(
        (identifier) => {
          return identifier.identifier;
        }
      );
      const affiliations = selectedSuggestions[0].extra.affiliations.map(
        (affiliation) => {
          return affiliation;
        }
      );

      const personOrOrgPath = `person_or_org`;
      const familyNameFieldPath = `${personOrOrgPath}.family_name`;
      const givenNameFieldPath = `${personOrOrgPath}.given_name`;
      const identifiersFieldPath = `${personOrOrgPath}.identifiers`;
      const affiliationsFieldPath = "affiliations";

      let chosen = {
        [givenNameFieldPath]: selectedSuggestions[0].extra.given_name,
        [familyNameFieldPath]: selectedSuggestions[0].extra.family_name,
        [identifiersFieldPath]: identifiers,
        [affiliationsFieldPath]: affiliations,
      };
      Object.entries(chosen).forEach(([path, value]) => {
        formikProps.form.setFieldValue(path, value);
      });
      // Update identifiers render
      identifiersRef.current.setState({
        selectedOptions: identifiersRef.current.valuesToOptions(identifiers),
      });
      // Update affiliations render
      const affiliationsState = affiliations.map(({ name }) => ({
        text: name,
        value: name,
        key: name,
        name,
      }));
      affiliationsRef.current.setState({
        suggestions: affiliationsState,
        selectedSuggestions: affiliationsState,
        searchQuery: null,
        error: false,
        open: false,
      });
      window.setTimeout(
        () =>
          document
            .getElementById(`${parentFieldPath}.role-select`)
            .querySelectorAll("input")[0]
            .focus(),
        50
      );
    }
  );
};

const makeIdEntry = (identifier) => {
  let icon = null;
  let link = null;

  if (identifier.scheme === "orcid") {
    icon = "/static/images/orcid.svg";
    link = "https://orcid.org/" + identifier.identifier;
  } else if (identifier.scheme === "gnd") {
    icon = "/static/images/gnd-icon.svg";
    link = "https://d-nb.info/gnd/" + identifier.identifier;
  } else if (identifier.scheme === "ror") {
    icon = "/static/images/ror-icon.svg";
    link = "https://ror.org/" + identifier.identifier;
  } else {
    return (
      <>
        {identifier.scheme}: {identifier.identifier}
      </>
    );
  }

  return (
    <span key={identifier.identifier}>
      <a href={link} target="_blank" rel="noopener noreferrer">
        <Image
          src={icon}
          className="inline-id-icon ml-5 mr-5"
          verticalAlign="middle"
        />
        {identifier.identifier}
      </a>
      ;
    </span>
  );
};

const serializeSuggestions = (creatibutors, showManualEntry) => {
  let results = creatibutors.map((creatibutor) => {
    let affNames = "";
    creatibutor.affiliations.forEach((affiliation, idx) => {
      affNames += affiliation.name;
      if (idx < creatibutor.affiliations.length - 1) {
        affNames += ", ";
      }
    });

    let idString = [];
    creatibutor.identifiers.forEach((i) => {
      idString.push(makeIdEntry(i));
    });

    return {
      text: creatibutor.name,
      value: creatibutor.id,
      extra: creatibutor,
      key: creatibutor.id,
      content: (
        <Header>
          <Header.Content>
            {creatibutor.name} {idString.length ? <>({idString})</> : null}
          </Header.Content>
          <Header.Subheader>{affNames}</Header.Subheader>
        </Header>
      ),
    };
  });

  if (showManualEntry) {
    results.push({
      text: "Manual entry",
      value: "Manual entry",
      extra: "Manual entry",
      key: "manual-entry",
      content: (
        <Header textAlign="center">
          <Header.Content>
            <p>
              <Trans>
                {/* eslint-disable-next-line jsx-a11y/anchor-is-valid*/}
                Couldn't find your person? You can <a>create a new entry</a>.
              </Trans>
            </p>
          </Header.Content>
        </Header>
      ),
    });
  }
  return results;
};

/**
 * Function to transform creatibutor object
 * to formik initialValues. The function is converting
 * the array of objects fields e.g `identifiers`, `affiliations`
 * to simple arrays. This is needed as SUI dropdowns accept only
 * array of strings as values.
 */
const deserializeCreatibutor = (initialCreatibutor) => {
  const identifiersFieldPath = "person_or_org.identifiers";

  return {
    // default type to personal
    // use empty strings as defaults for name fields to keep inputs controlled
    person_or_org: {
      type: CREATIBUTOR_TYPE.PERSON,
      family_name: "",
      given_name: "",
      ...initialCreatibutor.person_or_org,
      identifiers: _get(initialCreatibutor, identifiersFieldPath, []),
    },
    affiliations: _get(initialCreatibutor, "affiliations", []),
    role: _get(initialCreatibutor, "role", ""),
  };
};

/**
 * Function to transform formik creatibutor state
 * back to the external format.
 */
const serializeCreatibutor = (submittedCreatibutor, initialCreatibutor) => {
  const findField = (arrayField, key, value) => {
    const knownField = _find(arrayField, {
      [key]: value,
    });
    return knownField ? knownField : { [key]: value };
  };
  const identifiersFieldPath = "person_or_org.identifiers";
  const affiliationsFieldPath = "affiliations";
  // The modal is saving only identifiers values, thus
  // identifiers with existing scheme are trimmed
  // Here we merge back the known scheme for the submitted identifiers
  // const initialIdentifiers = _get(
  //   initialCreatibutor,
  //   identifiersFieldPath,
  //   []
  // );
  // const submittedIdentifiers = _get(
  //   submittedCreatibutor,
  //   identifiersFieldPath,
  //   []
  // );
  // const identifiers = submittedIdentifiers.map((identifier) => {
  //   return findField(initialIdentifiers, "identifier", identifier);
  // });

  const submittedAffiliations = _get(
    submittedCreatibutor,
    affiliationsFieldPath,
    []
  );

  return {
    ...submittedCreatibutor,
    // person_or_org: {
    //   ...submittedCreatibutor.person_or_org,
    // identifiers,
    // },
    affiliations: submittedAffiliations,
  };
};

const getCreatorSchema = (isCreator = true) => {
  return Yup.object({
    person_or_org: Yup.object({
      type: Yup.string(),
      family_name: Yup.string().when("type", (type, schema) => {
        if (type === CREATIBUTOR_TYPE.PERSON && isCreator) {
          return schema.required(i18next.t("Surname is a required field."));
        }
      }),
      name: Yup.string().when("type", (type, schema) => {
        if (type === CREATIBUTOR_TYPE.ORGANIZATION && isCreator) {
          return schema.required(
            i18next.t("Organization name is a required field.")
          );
        }
      }),
      identifiers: Yup.array().of(
        Yup.object().shape({
          scheme: Yup.string().required(
            "A scheme is required for each identifier"
          ),
          identifier: Yup.string()
            .when("scheme", {
              is: "url",
              then: Yup.string()
                .url("Must be a valid URL (e.g. https://example.com)")
                .required("You must provide a URL or remove this row"),
            })
            .matches(/(?!\s).+/, {
              disallowEmptyString: true,
              message: "Identifier cannot be blank",
            })
            .required("A value is required for each identifier"),
        })
      ),
    }),
    role: Yup.string().when("_", (_, schema) => {
      if (!isCreator) {
        return schema.required(i18next.t("Role is a required field."));
      }
    }),
  });
};

const ModalActions = {
  ADD: "add",
  EDIT: "edit",
};

const NamesAutocompleteOptions = {
  SEARCH: "search",
  SEARCH_ONLY: "search_only",
  OFF: "off",
};

const CreatibutorsFormBody = ({
  autocompleteNames,
  initialCreatibutor,
  isCreator,
  parentFieldPath,
  roleOptions,
  showManualEntry,
  showPersonForm,
  values,
}) => {
  const personOrOrgPath = `person_or_org`;
  const affiliationsFieldPath = "affiliations";
  const familyNameFieldPath = `${personOrOrgPath}.family_name`;
  const givenNameFieldPath = `${personOrOrgPath}.given_name`;
  const identifiersFieldPath = `${personOrOrgPath}.identifiers`;
  const nameFieldPath = `${personOrOrgPath}.name`;
  const roleFieldPath = "role";
  const typeFieldPath = `${personOrOrgPath}.type`;

  const affiliationsRef = createRef();
  const identifiersRef = createRef();
  const inputRef = createRef();
  const namesAutocompleteRef = createRef();
  const surnameRef = createRef();

  const focusInput = () => {
    if (inputRef.current) {
      inputRef.current.focus();
    } else {
      surnameRef.current.focus();
    }
  };

  return (
    <Form>
      <Form.Group>
        <RadioField
          fieldPath={typeFieldPath}
          label={i18next.t("Person")}
          checked={_get(values, typeFieldPath) === CREATIBUTOR_TYPE.PERSON}
          value={CREATIBUTOR_TYPE.PERSON}
          onChange={({ formikProps }) => {
            formikProps.form.setFieldValue(
              typeFieldPath,
              CREATIBUTOR_TYPE.PERSON
            );
          }}
          optimized
        />
        <RadioField
          fieldPath={typeFieldPath}
          label={i18next.t("Organization")}
          checked={
            _get(values, typeFieldPath) === CREATIBUTOR_TYPE.ORGANIZATION
          }
          value={CREATIBUTOR_TYPE.ORGANIZATION}
          onChange={({ formikProps }) => {
            formikProps.form.setFieldValue(
              typeFieldPath,
              CREATIBUTOR_TYPE.ORGANIZATION
            );
            focusInput();
          }}
          optimized
        />
      </Form.Group>
      {_get(values, typeFieldPath, "") === CREATIBUTOR_TYPE.PERSON ? (
        <div>
          {autocompleteNames !== NamesAutocompleteOptions.OFF && (
            <>
              <label htmlFor={`${parentFieldPath}.person-search-select`}>
                Search our existing list by name, identifier (e.g., ORCID id),
                or affiliation; or enter a new person below.
              </label>
              <RemoteSelectField
                selectOnBlur={false}
                selectOnNavigation={false}
                searchInput={{
                  autoFocus: _isEmpty(initialCreatibutor),
                  id: `${parentFieldPath}.person-search-select`,
                }}
                fieldPath="creators"
                clearable
                multiple={false}
                allowAdditions={false}
                placeholder={i18next.t("name, identifier, or affiliation...")}
                noQueryMessage={i18next.t(
                  "name, identifier, or affiliation..."
                )}
                required={false}
                // Disable UI-side filtering of search results
                search={(options) => options}
                suggestionAPIUrl="/api/names"
                serializeSuggestions={(creatibutors) =>
                  serializeSuggestions(creatibutors, showManualEntry)
                }
                onValueChange={({ formikProps }, selectedSuggestions) =>
                  onPersonSearchChange(
                    { formikProps },
                    selectedSuggestions,
                    identifiersRef,
                    affiliationsRef
                  )
                }
                ref={namesAutocompleteRef}
              />
            </>
          )}
          {showPersonForm && (
            <>
              <Divider />
              <div>
                <Form.Group widths="equal">
                  <TextField
                    label={i18next.t("Surname(s)")}
                    placeholder={i18next.t("Surname(s)")}
                    fieldPath={familyNameFieldPath}
                    required={isCreator}
                    input={{
                      ref: surnameRef,
                      autoFocus: true,
                    }}
                  />
                  <TextField
                    label={i18next.t("First name(s)")}
                    placeholder={i18next.t("First name(s)")}
                    fieldPath={givenNameFieldPath}
                  />
                </Form.Group>
                <CreatibutorsIdentifiers
                  // initialOptions={values}
                  fieldPath={identifiersFieldPath}
                  ref={identifiersRef}
                  label={"Personal identifiers (ORCID, ISNI, or GND)"}
                  idTypes={["orcid", "isni", "gnd"]}
                />
              </div>
            </>
          )}
        </div>
      ) : (
        <>
          <Divider />
          <TextField
            label={i18next.t("Organization name")}
            placeholder={i18next.t("Organization name")}
            fieldPath={nameFieldPath}
            required={isCreator}
            // forward ref to Input component because Form.Input
            // doesn't handle it
            input={{ ref: inputRef }}
          />
          <CreatibutorsIdentifiers
            initialOptions={_get(values, identifiersFieldPath, [])}
            fieldPath={identifiersFieldPath}
            label={"Organization identifiers (ROR, ISNI, or GND)"}
            idTypes={["ror", "isni", "gnd"]}
          />
        </>
      )}
      {(_get(values, typeFieldPath) === CREATIBUTOR_TYPE.ORGANIZATION ||
        (showPersonForm &&
          _get(values, typeFieldPath) === CREATIBUTOR_TYPE.PERSON)) && (
        <div>
          <SelectField
            fieldPath={roleFieldPath}
            label={i18next.t("Role")}
            options={roleOptions}
            placeholder={i18next.t("Select role")}
            {...(isCreator && { clearable: true })}
            required={!isCreator}
            optimized
            scrolling
            search
            id={`${parentFieldPath}.role-select`}
          />
          <AffiliationsField
            fieldPath={affiliationsFieldPath}
            selectRef={affiliationsRef}
          />
        </div>
      )}
    </Form>
  );
};

const CreatibutorsFormActionButtons = ({
  action,
  autocompleteNames,
  resetForm,
  saveAndContinueLabel,
  setAction,
  setShowPersonForm,
  handleModalClose,
  handleSubmit,
}) => {
  return (
    <>
      <Button
        name="cancel"
        onClick={() => {
          resetForm();
          handleModalClose();
        }}
        icon="remove"
        content={i18next.t("Cancel")}
        floated="left"
      />
      {action === ModalActions.ADD && (
        <Button
          name="submit"
          onClick={() => {
            setAction("saveAndContinue");
            setShowPersonForm(
              autocompleteNames !== NamesAutocompleteOptions.SEARCH_ONLY
            );
            handleSubmit();
          }}
          primary
          icon="checkmark"
          content={saveAndContinueLabel}
        />
      )}
      <Button
        name="submit"
        onClick={() => {
          setAction("saveAndClose");
          setShowPersonForm(
            autocompleteNames !== NamesAutocompleteOptions.SEARCH_ONLY
          );
          handleSubmit();
        }}
        primary
        icon="checkmark"
        content={i18next.t("Save")}
      />
    </>
  );
};

const CreatibutorsItemForm = ({
  addLabel,
  autocompleteNames = "search",
  editLabel,
  handleModalClose,
  initialCreatibutor = {},
  modalAction,
  onCreatibutorChange,
  parentFieldPath,
  roleOptions = [],
  schema,
}) => {
  const [saveAndContinueLabel, setSaveAndContinueLabel] = useState(
    i18next.t("Save and add another")
  );
  const [action, setAction] = useState(modalAction);
  const [showPersonForm, setShowPersonForm] = useState(
    autocompleteNames !== NamesAutocompleteOptions.SEARCH_ONLY ||
      !_isEmpty(initialCreatibutor)
  );
  const showManualEntry =
    autocompleteNames === NamesAutocompleteOptions.SEARCH_ONLY &&
    !showPersonForm;
  const isCreator = schema === "creators";

  const CreatorSchema = getCreatorSchema(isCreator);

  const changeContent = () => {
    setSaveAndContinueLabel(i18next.t("Added"));
    // change in 2 sec
    setTimeout(() => {
      setSaveAndContinueLabel(i18next.t("Save and add another"));
    }, 2000);
  };

  const onSubmit = (values, formikBag) => {
    onCreatibutorChange(
      serializeCreatibutor(values, initialCreatibutor),
      action
    );
    formikBag.setSubmitting(false);
    formikBag.resetForm();
    switch (action) {
      case "saveAndContinue":
        // Needed to close and open the modal to reset the internal
        // state of the cmp inside the modal
        changeContent();
        break;
      case "saveAndClose":
        handleModalClose();
        break;
      default:
        break;
    }
  };

  return (
    <Formik
      initialValues={deserializeCreatibutor(initialCreatibutor)}
      onSubmit={onSubmit}
      // enableReinitialize
      validationSchema={CreatorSchema}
      validateOnChange={false}
      validateOnBlur={false}
      as="div"
    >
      {({ values, resetForm, handleSubmit }) => {
        return (
          <>
            {action === ModalActions.ADD ? (
              <Header as="h2">{addLabel}</Header>
            ) : null}
            <CreatibutorsFormBody
              {...{
                autocompleteNames,
                initialCreatibutor,
                isCreator,
                parentFieldPath,
                roleOptions,
                showManualEntry,
                showPersonForm,
                values,
              }}
            />
            <div className="creatibutors-item-form-buttons">
              <CreatibutorsFormActionButtons
                {...{
                  autocompleteNames,
                  handleModalClose,
                  handleSubmit,
                  action,
                  resetForm,
                  saveAndContinueLabel,
                  setAction,
                  setShowPersonForm,
                }}
              />
            </div>
          </>
        );
      }}
    </Formik>
  );
};

const CreatibutorsModal = ({
  addLabel,
  autocompleteNames = "search",
  editLabel,
  handleModalClose,
  handleModalOpen,
  initialCreatibutor = {},
  modalAction,
  modalOpen,
  onCreatibutorChange,
  parentFieldPath,
  roleOptions = [],
  schema,
  trigger,
}) => {
  const [saveAndContinueLabel, setSaveAndContinueLabel] = useState(
    i18next.t("Save and add another")
  );
  const [action, setAction] = useState(modalAction);
  const [showPersonForm, setShowPersonForm] = useState(
    autocompleteNames !== NamesAutocompleteOptions.SEARCH_ONLY ||
      !_isEmpty(initialCreatibutor)
  );
  const showManualEntry =
    autocompleteNames === NamesAutocompleteOptions.SEARCH_ONLY &&
    !showPersonForm;
  const isCreator = schema === "creators";

  const CreatorSchema = getCreatorSchema(isCreator);

  const changeContent = () => {
    setSaveAndContinueLabel(i18next.t("Added"));
    // change in 2 sec
    setTimeout(() => {
      setSaveAndContinueLabel(i18next.t("Save and add another"));
    }, 2000);
  };

  const onSubmit = (values, formikBag) => {
    onCreatibutorChange(serializeCreatibutor(values, initialCreatibutor));
    formikBag.setSubmitting(false);
    formikBag.resetForm();
    switch (action) {
      case "saveAndContinue":
        // Needed to close and open the modal to reset the internal
        // state of the cmp inside the modal
        // handleModalClose();
        // handleModalOpen();
        changeContent();
        break;
      case "saveAndClose":
        // handleModalClose();
        break;
      default:
        break;
    }
  };

  return (
    <Formik
      initialValues={deserializeCreatibutor(initialCreatibutor)}
      onSubmit={onSubmit}
      enableReinitialize
      validationSchema={CreatorSchema}
      validateOnChange={false}
      validateOnBlur={false}
    >
      {({ values, resetForm, handleSubmit }) => {
        return (
          <Modal
            centered={false}
            onOpen={() => handleModalOpen()}
            open={modalOpen}
            trigger={trigger}
            onClose={() => {
              handleModalClose();
              resetForm();
            }}
            closeIcon
            closeOnDimmerClick={false}
            className="deposit-creatibutor-modal"
          >
            <Modal.Header as="h6" className="pt-10 pb-10">
              <Grid>
                <Grid.Column floated="left" width={4}>
                  <Header as="h2">
                    {action === ModalActions.ADD ? addLabel : editLabel}
                  </Header>
                </Grid.Column>
              </Grid>
            </Modal.Header>
            <Modal.Content>
              <CreatibutorsFormBody
                {...{
                  autocompleteNames,
                  initialCreatibutor,
                  isCreator,
                  parentFieldPath,
                  roleOptions,
                  showManualEntry,
                  showPersonForm,
                  values,
                }}
              />
            </Modal.Content>
            <Modal.Actions>
              <CreatibutorsFormActionButtons
                {...{
                  autocompleteNames,
                  handleModalClose,
                  handleSubmit,
                  action,
                  resetForm,
                  saveAndContinueLabel,
                  setAction,
                  setShowPersonForm,
                }}
              />
            </Modal.Actions>
          </Modal>
        );
      }}
    </Formik>
  );
};

CreatibutorsModal.propTypes = {
  schema: PropTypes.oneOf(["creators", "contributors"]).isRequired,
  modalAction: PropTypes.oneOf(["add", "edit"]).isRequired,
  addLabel: PropTypes.string.isRequired,
  autocompleteNames: PropTypes.oneOf(["search", "search_only", "off"]),
  editLabel: PropTypes.string.isRequired,
  initialCreatibutor: PropTypes.shape({
    id: PropTypes.string,
    person_or_org: PropTypes.shape({
      family_name: PropTypes.string,
      given_name: PropTypes.string,
      name: PropTypes.string,
      identifiers: PropTypes.arrayOf(
        PropTypes.shape({
          scheme: PropTypes.string,
          identifier: PropTypes.string,
        })
      ),
    }),
    affiliations: PropTypes.array,
    role: PropTypes.string,
  }),
  trigger: PropTypes.object.isRequired,
  onCreatibutorChange: PropTypes.func.isRequired,
  roleOptions: PropTypes.array,
};

export { CreatibutorsModal, CreatibutorsItemForm };
