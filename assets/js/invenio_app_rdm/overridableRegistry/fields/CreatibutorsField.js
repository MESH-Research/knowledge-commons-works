// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { useContext, useState } from "react";
import { useStore } from "react-redux";
import { getIn, FieldArray, useFormikContext } from "formik";
import { Button, Form, Icon, Label, List, TransitionGroup } from "semantic-ui-react";
import _get from "lodash/get";
import { FieldLabel } from "react-invenio-forms";
import PropTypes from "prop-types";

import { CreatibutorsFieldItem } from "./creatibutors_components/CreatibutorsFieldItem";
import { CREATIBUTOR_TYPE } from "./types";
import { FormUIStateContext } from "@js/invenio_modular_deposit_form/InnerDepositForm";
import { i18next } from "@translations/i18next";
import { getFamilyName, getGivenName } from "../../../kcworks/names";

/**
 * Sort a list of string values (options).
 * @param {list} options
 * @returns
 */
function sortOptions(options) {
  return options.sort((o1, o2) => o1.text.localeCompare(o2.text));
}

const moveCommonRolesToTop = (roleArray) => {
  let newRoleArray = [...roleArray];
  let commonRoles = [
    "projectOrTeamLeader",
    "projectOrTeamMember",
    "collaborator",
    "translator",
    "editor",
    "author",
  ];
  for (const role of commonRoles) {
    const index = newRoleArray.findIndex(({ value }) => value === role);
    newRoleArray.unshift(...newRoleArray.splice(index, 1));
  }
  newRoleArray.push(
    ...newRoleArray.splice(
      newRoleArray.findIndex(({ value }) => value === "other"),
      1
    )
  );
  return newRoleArray;
};

// FIXME: Merge creator and contributor roles vocabs to avoid merging here
// FIXME: Memoize this function
const orderOptions = (optionList, contribsOptionList) => {
  let newOptionList = optionList.concat(
    contribsOptionList.filter(
      (item) =>
        !optionList.some(
          (item2) => item2.text.toLowerCase() === item.text.toLowerCase()
        )
    )
  );
  return moveCommonRolesToTop(sortOptions(newOptionList));
};

const creatibutorNameDisplay = (value) => {
  const creatibutorType = _get(
    value,
    "person_or_org.type",
    CREATIBUTOR_TYPE.PERSON
  );
  const isPerson = creatibutorType === CREATIBUTOR_TYPE.PERSON;

  const familyName = _get(value, "person_or_org.family_name", "");
  const givenName = _get(value, "person_or_org.given_name", "");
  const affiliationName = _get(value, `affiliations[0].name`, "");
  const name = _get(value, `person_or_org.name`);

  const affiliation = affiliationName ? ` (${affiliationName})` : "";

  if (isPerson) {
    const givenNameSuffix = givenName ? `, ${givenName}` : "";
    return `${familyName}${givenNameSuffix}${affiliation}`;
  }

  return `${name}${affiliation}`;
};

const emptyCreatibutor = {
  person_or_org: {
    family_name: "",
    given_name: "",
    name: "",
    type: "personal",
    identifiers: [],
  },
  role: "author",
  affiliations: [],
};

/* *
 * Make a creatibutor object from the current user profile
 * @param {object} currentUserprofile - the current user profile
 * @returns {object} selfCreatibutor - the creatibutor object
 * */
const makeSelfCreatibutor = (currentUserprofile) => {
  const myAffiliations =
    typeof currentUserprofile.affiliations === "string" &&
    currentUserprofile.affiliations !== ""
      ? [currentUserprofile.affiliations]
      : currentUserprofile?.affiliations;

  let myNameParts = {};
  if (
    !!currentUserprofile?.name_parts_local &&
    currentUserprofile?.name_parts_local !== ""
  ) {
    myNameParts = JSON.parse(currentUserprofile.name_parts_local);
  } else if (!!currentUserprofile?.name_parts && currentUserprofile?.name_parts !== "") {
    myNameParts = JSON.parse(currentUserprofile.name_parts);
  }
  const part1 = [myNameParts?.given, myNameParts?.first, myNameParts?.middle, myNameParts?.nickname].filter(Boolean).join(" ");
  const part2 = [myNameParts?.family_prefix, myNameParts?.family_prefix_fixed, myNameParts?.spousal, myNameParts?.parental, myNameParts?.family, myNameParts?.last, ].filter(Boolean).join(" ");

  let myIdentifiers = undefined;
  const rawIdentifiers = Object.fromEntries(
    Object.entries(currentUserprofile).filter(
      ([key, value]) =>
        key.startsWith("identifier") && value !== "" && value !== null
    )
  );

  if (!!rawIdentifiers && Object.keys(rawIdentifiers).length > 0) {
    myIdentifiers = Object.entries(rawIdentifiers).map(([key, value]) => {
      return { identifier: value, scheme: key.replace("identifier_", "") };
    });
  }

  let selfCreatibutor = {
    person_or_org: {
      family_name:
        getFamilyName(myNameParts) ||
        currentUserprofile?.full_name ||
        "",
      given_name:
        getGivenName(myNameParts) ||
        myNameParts?.first ||
        "",
      name: currentUserprofile?.full_name || "",
      type: "personal",
      identifiers: myIdentifiers?.length > 0 ? myIdentifiers : [],
    },
    role: "author",
    affiliations:
      myAffiliations?.length > 0
        ? myAffiliations.map((affiliation) => ({
            text: affiliation,
            key: affiliation,
            value: affiliation,
            name: affiliation,
          }))
        : [],
  };

  return selfCreatibutor;
};

const CreatibutorsField = ({
  addButtonLabel = i18next.t("Add creator"),
  autocompleteNames = "search",
  modal={
    addLabel: i18next.t("Add creator"),
    editLabel: i18next.t("Edit creator"),
  },
  cancelButtonLabel = i18next.t("Cancel"),
  description,
  fieldPath,
  label = undefined,
  icon = undefined,
  required = true,
  roleOptions = undefined,
  schema = "creators",
  ...otherProps
}) => {
  const store = useStore();
  const config = store.getState().deposit.config;
  const [addingSelf, setAddingSelf] = useState(false);
  const [newItemIndex, setNewItemIndex] = useState(-1);
  const [showEditForms, setShowEditForms] = useState([]);
  const { errors, initialErrors, initialValues, setFieldTouched, touched, validateForm, values } = useFormikContext();

  const { currentUserprofile } = useContext(FormUIStateContext);

  const error = _get(errors, fieldPath, null);

  const initialError = getIn(initialErrors, fieldPath, null);
  const creatibutorsTouched = getIn(touched, fieldPath, null);
  const creatibutorsError =
    (!!error && !!creatibutorsTouched) ||
    (_get(values, fieldPath, []) === _get(initialValues, fieldPath, []) && initialError);

  const focusAddButtonHandler = () => {
    setTimeout(() => {
      document.getElementById(`${fieldPath}.add-button`).focus();
    }, 100);
  };

  // Add new creatibutor to the list (bottom add button)
  const handleAddNew = (pushFunc, newItem, filteredEditForms = undefined) => {
    pushFunc(newItem);

    const newIndex = getIn(values, fieldPath).length;

    setNewItemIndex(newIndex);
    const newEditForms = filteredEditForms!==undefined ? filteredEditForms : showEditForms;
    setShowEditForms([...newEditForms, newIndex]);
  };

  // Close the editing form after saving or cancelling
  const handleCloseForm = (pushFunc, index, action) => {
    setAddingSelf(false);
    const filteredEditForms = showEditForms.filter((elem) => elem !== index);

    if (action === "saveAndContinue") {
      handleAddNew(pushFunc, emptyCreatibutor, filteredEditForms);
    } else {
      setShowEditForms(filteredEditForms);
      setNewItemIndex(-1);
    }
    setFieldTouched(fieldPath, true);
  };

  // Open the editing form (edit button)
  const handleOpenForm = (index) => {
    setShowEditForms([...showEditForms, index]);
    if ( newItemIndex !== index ) {
      for (let i = 0; i < getIn(values, fieldPath).length; i++) {
        setFieldTouched(`${fieldPath}.${i}.person_or_org.name`, true);
        setFieldTouched(`${fieldPath}.${i}.person_or_org.family_name`, true);
        setFieldTouched(`${fieldPath}.${i}.person_or_org.given_name`, true);
        setFieldTouched(`${fieldPath}.${i}.role`, true);
        for (let j = 0; j < getIn(values, `${fieldPath}.${i}.affiliations`, []).length; j++) {
          setFieldTouched(`${fieldPath}.${i}.affiliations.${j}.name`, true);
        };
        for (let j = 0; j < getIn(values, `${fieldPath}.${i}.person_or_org.identifiers`, []).length; j++) {
          setFieldTouched(`${fieldPath}.${i}.person_or_org.identifiers.${j}.identifier`, true);
          setFieldTouched(`${fieldPath}.${i}.person_or_org.identifiers.${j}.scheme`, true);
        };
      };
    }
  };

  // Cancel the editing form (cancel button)
  const handleCancel = (removeFunc, index) => {
    handleCloseForm(undefined, index, "cancel");
    if ( newItemIndex === index ) {
      removeFunc(index);
    };
    setNewItemIndex(-1);
  };

  // Remove a creatibutor from the list (remove button)
  const handleRemove = (removeFunc, index) => {
    removeFunc(index);
  };

  const creatibutorUp = (moveFunc, currentIndex) => {
    if (currentIndex > 0) {
      moveFunc(currentIndex, currentIndex - 1);
    }
  };

  const creatibutorDown = (moveFunc, currentIndex) => {
    if (currentIndex < getIn(values, fieldPath).length - 1) {
      moveFunc(currentIndex, currentIndex + 1);
    }
  };

  const orderedRoleOptions = orderOptions(
    roleOptions,
    config.vocabularies.contributors.role
  );

  return (
    <Form.Field
      id={fieldPath}
      required={required}
      error={creatibutorsError}
    >
    <FieldArray
      name={fieldPath}
      className="creators"
      required={!!required}
      render={(arrayHelpers) => {
        return(
        <>
          <FieldLabel htmlFor={fieldPath} icon={icon} label={label} />

          {/* List of creatibutors with edit forms */}
          <TransitionGroup
            as={List}
            className="creators-list"
            duration={500}
            animation={"fade"}
          >
            {getIn(arrayHelpers.form.values, fieldPath, []).map((value, index) => {
              const fieldPathPrefix = `${fieldPath}.${index}`;
              const displayName = creatibutorNameDisplay(value);
              return (
                <CreatibutorsFieldItem
                  {...otherProps}
                  {...{
                    addCreatibutor: arrayHelpers.push,
                    addLabel: addButtonLabel,
                    autocompleteNames,
                    cancelLabel: cancelButtonLabel,
                    creatibutorsLength: getIn(values, fieldPath).length,
                    creatibutorDown,
                    creatibutorUp,
                    displayName,
                    editLabel: modal.editLabel,
                    fieldPath,
                    fieldPathPrefix,
                    focusAddButtonHandler,
                    handleRemove,
                    handleCancel,
                    handleCloseForm,
                    handleOpenForm,
                    index,
                    isNewItem: newItemIndex === index,
                    itemError: creatibutorsError ? error?.[index] : null,
                    key: index,
                    moveCreatibutor: arrayHelpers.move,
                    removeCreatibutor: arrayHelpers.remove,
                    replaceCreatibutor: arrayHelpers.replace,
                    roleOptions: orderedRoleOptions,
                    schema,
                    showEditForms,
                    setShowEditForms,
                    values,
                  }}
                />
              );
            })}
          </TransitionGroup>

          {/* Add buttons */}
          {!(newItemIndex > -1 && showEditForms.includes(newItemIndex)) && (
            <div>
              <Button
                type="button"
                icon
                labelPosition="left"
                id={`${fieldPath}.add-button`}
                className="add-button"
                aria-labelledby={`${fieldPath}-field-description`}
                onClick={() => {
                  setAddingSelf(false);
                  handleAddNew(arrayHelpers.push, emptyCreatibutor);
                }}
              >
                <Icon name="add" />
                {addButtonLabel}
              </Button>
              <Button
                type="button"
                icon
                labelPosition="left"
                id={`${fieldPath}.add-button`}
                className="add-button"
                aria-labelledby={`${fieldPath}-field-description`}
                onClick={() => {
                  setAddingSelf(true);
                  handleAddNew(
                    arrayHelpers.push,
                    makeSelfCreatibutor(currentUserprofile)
                  );
                }}
              >
                <Icon name="add" />
                {"Add myself"}
              </Button>
            </div>
          )}

          {/* Error message */}
          {creatibutorsError && typeof error === "string" && (
            <Label pointing="above" prompt>
              {error}
            </Label>
          )}

          {/* Field description */}
          <span id={`${fieldPath}-field-description`} className="helptext">
            {description}
          </span>
        </>
        )
      }}
    />
    </Form.Field>
  );
};

CreatibutorsField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  addButtonLabel: PropTypes.string,
  autocompleteNames: PropTypes.oneOf(["search", "search_only", "off"]),
  label: PropTypes.string,
  icon: PropTypes.string,
  modal: PropTypes.shape({
    addLabel: PropTypes.string.isRequired,
    editLabel: PropTypes.string.isRequired,
  }),
  required: PropTypes.bool,
  roleOptions: PropTypes.array,
  schema: PropTypes.oneOf(["creators", "contributors"]).isRequired,
};

export { CreatibutorsField, sortOptions };
