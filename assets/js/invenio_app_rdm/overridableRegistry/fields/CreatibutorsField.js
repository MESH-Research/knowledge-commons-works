// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { useEffect, useState } from "react";
import PropTypes from "prop-types";
import { getIn, FieldArray, useFormikContext } from "formik";
import { Button, Form, Label, List, Icon } from "semantic-ui-react";
import _get from "lodash/get";
import { FieldLabel } from "react-invenio-forms";
// import { HTML5Backend } from "react-dnd-html5-backend";
// import { DndProvider } from "react-dnd";

import { CreatibutorsItemForm } from "./CreatibutorsModal";
import { CreatibutorsFieldItem } from "./CreatibutorsFieldItem";
import { CREATIBUTOR_TYPE } from "./types";
// import { GlobalDndContext } from "./GlobalDndContext";
// import { sortOptions } from "../../utils";
import { i18next } from "@translations/invenio_rdm_records/i18next";

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

const CreatibutorsFieldForm = ({
  addButtonLabel = i18next.t("Add creator"),
  addingSelf,
  setAddingSelf,
  autocompleteNames = "search",
  config,
  currentUserprofile,
  description,
  id,
  form: { values, errors, initialErrors, initialValues, touched },
  label = i18next.t("Creators"),
  labelIcon = "user",
  modal = {
    addLabel: i18next.t("Add creator"),
    editLabel: i18next.t("Edit creator"),
  },
  modalOpen,
  move: formikArrayMove,
  name: fieldPath,
  push: formikArrayPush,
  remove: formikArrayRemove,
  replace: formikArrayReplace,
  roleOptions,
  schema,
  setCreatibutorsTouched,
  setModalOpen,
  showEditForms,
  setShowEditForms,
}) => {
  const creatibutorsList = getIn(values, fieldPath, []);
  const formikInitialValues = getIn(initialValues, fieldPath, []);

  const error = getIn(errors, fieldPath, null);
  const initialError = getIn(initialErrors, fieldPath, null);
  const creatibutorsTouched = getIn(touched, fieldPath, null);
  const creatibutorsError =
    (error && creatibutorsTouched) ||
    (creatibutorsList === formikInitialValues && initialError);
  const orderedRoleOptions = orderOptions(
    roleOptions,
    config.vocabularies.contributors.role
  );

  const handleModalOpen = () => {
    setModalOpen(true);
    setCreatibutorsTouched(true);
  };

  const handleModalClose = () => {
    setCreatibutorsTouched(true);
    setModalOpen(false);
    setAddingSelf(false);
    focusAddButtonHandler();
  };

  const handleOnContributorChange = (selectedCreatibutor, action) => {
    console.log("handleOnContributorChange");
    setAddingSelf(false);
    formikArrayPush(selectedCreatibutor);
    setModalOpen(action === "saveAndContinue" ? true : false);
  };

  const focusAddButtonHandler = () => {
    setTimeout(() => {
      document.getElementById(`${fieldPath}.add-button`).focus();
    }, 100);
  };

  const creatibutorUp = (currentIndex) => {
    if (currentIndex > 0) {
      formikArrayMove(currentIndex, currentIndex - 1);
    }
  };

  const creatibutorDown = (currentIndex) => {
    if (currentIndex < creatibutorsList.length - 1) {
      formikArrayMove(currentIndex, currentIndex + 1);
    }
  };

  const myAffiliations =
    typeof currentUserprofile.affiliations === "string" &&
    currentUserprofile.affiliations !== ""
      ? [currentUserprofile.affiliations]
      : currentUserprofile?.affiliations;
  const selfCreatibutor = {
    person_or_org: {
      family_name: addingSelf
        ? currentUserprofile?.family_name ||
          currentUserprofile?.full_name ||
          ""
        : "",
      given_name: addingSelf ? currentUserprofile?.given_name || "" : "",
      name: addingSelf ? currentUserprofile?.full_name || "" : "",
      type: "personal",
    },
    role: "author",
    affiliations:
      addingSelf && myAffiliations?.length > 0
        ? myAffiliations.map((affiliation) => ({
            text: affiliation,
            key: affiliation,
            value: affiliation,
            name: affiliation,
          }))
        : [],
  };

  return (
    <Form.Field
      required={schema === "creators"}
      className={creatibutorsError ? "error" : ""}
    >
      <FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />
      <List>
        {creatibutorsList.map((value, index) => {
          const key = `${fieldPath}.${index}`;
          // const key = `${fieldPath}.${value.person_or_org.name}`;
          const displayName = creatibutorNameDisplay(value);
          console.log("key is", key);

          return (
            <CreatibutorsFieldItem
              key={key}
              creatibutorsLength={creatibutorsList.length}
              creatibutorDown={creatibutorDown}
              creatibutorUp={creatibutorUp}
              itemError={creatibutorsError ? error[index] : null}
              {...{
                displayName,
                index,
                roleOptions: orderedRoleOptions,
                schema,
                compKey: key,
                initialCreatibutor: value,
                removeCreatibutor: formikArrayRemove,
                replaceCreatibutor: formikArrayReplace,
                moveCreatibutor: formikArrayMove,
                addLabel: modal.addLabel,
                editLabel: modal.editLabel,
                autocompleteNames: autocompleteNames,
              }}
              focusAddButtonHandler={focusAddButtonHandler}
              modalOpen={modalOpen}
              handleModalClose={handleModalClose}
              handleModalOpen={handleModalOpen}
              parentFieldPath={fieldPath}
              setModalOpen={setModalOpen}
              showEditForms={showEditForms}
              setShowEditForms={setShowEditForms}
            />
          );
        })}
      </List>
      {!modalOpen && (
        <div>
          <Button
            type="button"
            icon
            labelPosition="left"
            id={`${fieldPath}.add-button`}
            className="add-button"
            aria-labelledby={`${fieldPath}-field-description`}
            onClick={() => setModalOpen(true)}
            //  ref={this.adderRef}
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
              setTimeout(() => {
                setModalOpen(true);
              }, 100);
            }}
          >
            <Icon name="add" />
            {"Add myself"}
          </Button>
        </div>
      )}

      {(modalOpen ||
        (creatibutorsError && typeof creatibutorsError == "string")) && (
        <CreatibutorsItemForm
          onCreatibutorChange={handleOnContributorChange}
          addLabel={modal.addLabel}
          editLabel={modal.editLabel}
          roleOptions={orderedRoleOptions}
          schema={schema}
          autocompleteNames={autocompleteNames}
          focusAddButtonHandler={focusAddButtonHandler}
          parentFieldPath={fieldPath}
          modalOpen={modalOpen}
          handleModalClose={handleModalClose}
          handleModalOpen={handleModalOpen}
          initialCreatibutor={selfCreatibutor}
          modalAction="add"
        />
      )}
      {creatibutorsError && typeof error === "string" && (
        <Label pointing="above" prompt>
          {error}
        </Label>
      )}
      <span id={`${fieldPath}-field-description`} className="helptext">
        {description}
      </span>
    </Form.Field>
  );
};

const CreatibutorsField = ({
  addButtonLabel = i18next.t("Add creator"),
  autocompleteNames = "search",
  currentUserprofile,
  fieldPath,
  label = undefined,
  labelIcon = undefined,
  modal = {
    addLabel: i18next.t("Add creator"),
    editLabel: i18next.t("Edit creator"),
  },
  roleOptions = undefined,
  schema = "creators",
  ...otherProps
}) => {
  console.log(
    "CreatibutorsField called",
    fieldPath,
    label,
    labelIcon,
    modal,
    roleOptions,
    schema,
    otherProps
  );
  // FIXME: This state has to be managed here because the whole fieldarray is reredered and loses state on any state change; seems related to react-dnd
  const [modalOpen, setModalOpen] = useState(false);
  const [addingSelf, setAddingSelf] = useState(false);
  const [showEditForms, setShowEditForms] = useState([]);
  const [creatibutorsTouched, setCreatibutorsTouched] = useState(false);
  const { setFieldTouched } = useFormikContext();

  useEffect(() => {
    console.log("useEffect creatibutorsTouched", creatibutorsTouched);
    // if (creatibutorsTouched) {
    //   setFieldTouched("metadata.creators", true);
    // }
  }, [creatibutorsTouched]);

  return (
    <FieldArray
      name={fieldPath}
      component={(formikProps) => (
        <CreatibutorsFieldForm
          {...formikProps}
          {...otherProps}
          {...{
            addButtonLabel,
            addingSelf,
            autocompleteNames,
            currentUserprofile,
            fieldPath,
            label,
            labelIcon,
            modalOpen,
            roleOptions,
            modal,
            schema,
            setAddingSelf,
            setCreatibutorsTouched,
            setModalOpen,
            showEditForms,
            setShowEditForms,
          }}
        />
      )}
    />
  );
};

CreatibutorsFieldForm.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  addButtonLabel: PropTypes.string,
  modal: PropTypes.shape({
    addLabel: PropTypes.string.isRequired,
    editLabel: PropTypes.string.isRequired,
  }),
  schema: PropTypes.oneOf(["creators", "contributors"]).isRequired,
  autocompleteNames: PropTypes.oneOf(["search", "search_only", "off"]),
  label: PropTypes.string,
  labelIcon: PropTypes.string,
  roleOptions: PropTypes.array.isRequired,
  form: PropTypes.object.isRequired,
  remove: PropTypes.func.isRequired,
  replace: PropTypes.func.isRequired,
  move: PropTypes.func.isRequired,
  push: PropTypes.func.isRequired,
  name: PropTypes.string.isRequired,
};

CreatibutorsField.propTypes = {
  addButtonLabel: PropTypes.string,
  autocompleteNames: PropTypes.oneOf(["search", "search_only", "off"]),
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string,
  labelIcon: PropTypes.string,
  modal: PropTypes.shape({
    addLabel: PropTypes.string.isRequired,
    editLabel: PropTypes.string.isRequired,
  }),
  roleOptions: PropTypes.array,
  schema: PropTypes.oneOf(["creators", "contributors"]).isRequired,
};

CreatibutorsField.defaultProps = {};

export { CreatibutorsField, CreatibutorsFieldForm, sortOptions };
