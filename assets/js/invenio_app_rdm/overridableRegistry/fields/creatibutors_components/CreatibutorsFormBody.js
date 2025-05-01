import React, { createRef } from "react";
import PropTypes from "prop-types";
import { Checkbox, Divider, Form, Header } from "semantic-ui-react";
import { Field } from "formik";
import { Image } from "react-invenio-forms";
import { TextField } from "@js/invenio_modular_deposit_form/replacement_components/TextField";
import { SelectField } from "@js/invenio_modular_deposit_form/replacement_components/SelectField";
import { RemoteSelectField } from "@js/invenio_modular_deposit_form/replacement_components/RemoteSelectField";
import _get from "lodash/get";
import _find from "lodash/find";
import _isEmpty from "lodash/isEmpty";
import _map from "lodash/map";
import { AffiliationsField } from "../AffiliationsField";
import { CreatibutorsIdentifiers } from "./CreatibutorsIdentifiers";
import { CREATIBUTOR_TYPE } from "../types";
import { i18next } from "@translations/i18next";
import { Trans } from "react-i18next";
import { NamesAutocompleteOptions } from "./CreatibutorsItemForm";

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
              {/* eslint-disable jsx-a11y/anchor-is-valid*/}
              <Trans>
                Couldn't find your person? You can <a>create a new entry</a>.
              </Trans>
              {/* eslint-enable jsx-a11y/anchor-is-valid*/}
            </p>
          </Header.Content>
        </Header>
      ),
    });
  }
  return results;
};


const CreatibutorsFormBody = ({
  autocompleteNames,
  fieldPath,
  fieldPathPrefix,
  isCreator,
  isNewItem,
  roleOptions,
  showManualEntry,
  showPersonForm,
  values,
}) => {
  const personOrOrgPath = `${fieldPathPrefix}.person_or_org`;
  const affiliationsFieldPath = `${fieldPathPrefix}.affiliations`;
  const familyNameFieldPath = `${personOrOrgPath}.family_name`;
  const givenNameFieldPath = `${personOrOrgPath}.given_name`;
  const nameFieldPath = `${personOrOrgPath}.name`;
  const identifiersFieldPath = `${personOrOrgPath}.identifiers`;
  const typeFieldPath = `${personOrOrgPath}.type`;
  const roleFieldPath = `${fieldPathPrefix}.role`;

  // const affiliationsRef = createRef();
  // const identifiersRef = createRef();
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
    <>
      <Field name={typeFieldPath}>
        {({ field, form }) => {
          return(
          <Form.Group>
            <Checkbox
              radio
              label={i18next.t("Person")}
              id={CREATIBUTOR_TYPE.PERSON}
              {...field}
              checked={
                field.value === CREATIBUTOR_TYPE.PERSON
              }
              onChange={() => {
                form.setFieldValue(
                  typeFieldPath,
                  CREATIBUTOR_TYPE.PERSON
                );
                focusInput();
              }}
              value={CREATIBUTOR_TYPE.PERSON}
              optimized
            />
            <Checkbox
              radio
              label={i18next.t("Organization")}
              id={CREATIBUTOR_TYPE.ORGANIZATION}
              {...field}
              checked={
                _get(values, typeFieldPath) === CREATIBUTOR_TYPE.ORGANIZATION
              }
              value={CREATIBUTOR_TYPE.ORGANIZATION}
              onChange={() => {
                form.setFieldValue(
                  typeFieldPath,
                  CREATIBUTOR_TYPE.ORGANIZATION
                );
                focusInput();
              }}
              optimized
            />
          </Form.Group>
          )}
        }
      </Field>
      {_get(values, typeFieldPath, "") === CREATIBUTOR_TYPE.PERSON ? (
        <>
          {(autocompleteNames !== NamesAutocompleteOptions.OFF) ? (
            <>
              <label htmlFor={`${fieldPath}.person-search-select`}>
                Search our existing list by name, identifier (e.g., ORCID id),
                or affiliation; or enter a new person below.
              </label>
              <RemoteSelectField
                selectOnBlur={false}
                selectOnNavigation={false}
                searchInput={{
                  autoFocus: isNewItem,
                  id: `${fieldPath}.person-search-select`,
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
                    // identifiersRef,
                    // affiliationsRef
                  )
                }
                ref={namesAutocompleteRef}
              />
            </>
          ) : null}
          {showPersonForm && (
            <>
              <Divider />
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
                  // ref={identifiersRef}
                  label={"Personal identifiers (ORCID, KC member id, ISNI, or GND)"}
                  idTypes={["orcid", "isni", "gnd", "kc_username"]}
                />
            </>
          )}
        </>
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
            fieldPath={identifiersFieldPath}
            label={"Organization identifiers (ROR, ISNI, or GND)"}
            idTypes={["ror", "isni", "gnd"]}
          />
        </>
      )}
      {(_get(values, typeFieldPath) === CREATIBUTOR_TYPE.ORGANIZATION ||
        (showPersonForm &&
          _get(values, typeFieldPath) === CREATIBUTOR_TYPE.PERSON)) && (
            <>
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
                id={`${fieldPath}.role-select`}
              />
              <AffiliationsField
                fieldPath={affiliationsFieldPath}
                // selectRef={affiliationsRef}
              />
            </>
          )
      }
    </>
  );
};

CreatibutorsFormBody.propTypes = {
    autocompleteNames: NamesAutocompleteOptions ? PropTypes.oneOf(Object.values(NamesAutocompleteOptions)) : PropTypes.string,
    fieldPath: PropTypes.string.isRequired,
    fieldPathPrefix: PropTypes.string.isRequired,
    isCreator: PropTypes.bool,
    isNewItem: PropTypes.bool,
    roleOptions: PropTypes.array.isRequired,
    showManualEntry: PropTypes.bool,
    showPersonForm: PropTypes.bool,
    values: PropTypes.object.isRequired,
    };

export { CreatibutorsFormBody };