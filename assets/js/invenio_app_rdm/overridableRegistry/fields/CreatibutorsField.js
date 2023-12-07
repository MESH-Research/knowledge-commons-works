// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { useEffect, useState } from "react";
import PropTypes from "prop-types";
import { getIn, FieldArray } from "formik";
import { Button, Form, Label, List, Icon } from "semantic-ui-react";
import _get from "lodash/get";
import { FieldLabel } from "react-invenio-forms";
// import { HTML5Backend } from "react-dnd-html5-backend";
// import { DndProvider } from "react-dnd";

import { CreatibutorsModal, CreatibutorsItemForm } from "./CreatibutorsModal";
import { CreatibutorsFieldItem } from "./CreatibutorsFieldItem";
import { CREATIBUTOR_TYPE } from "./types";
// import { GlobalDndContext } from "./GlobalDndContext";
// import { sortOptions } from "../../utils";
import { i18next } from "@translations/invenio_rdm_records/i18next";

let renderCount = 0;

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
  push: formikArrayPush,
  form: { values, errors, initialErrors, initialValues },
  remove: formikArrayRemove,
  replace: formikArrayReplace,
  move: formikArrayMove,
  name: fieldPath,
  addButtonLabel = i18next.t("Add creator"),
  autocompleteNames = "search",
  config,
  id,
  description,
  label = i18next.t("Creators"),
  labelIcon = "user",
  modal = {
    addLabel: i18next.t("Add creator"),
    editLabel: i18next.t("Edit creator"),
  },
  roleOptions,
  schema,
}) => {
  const [modalOpen, setModalOpen] = useState(false);

  const creatibutorsList = getIn(values, fieldPath, []);
  const formikInitialValues = getIn(initialValues, fieldPath, []);

  const error = getIn(errors, fieldPath, null);
  const initialError = getIn(initialErrors, fieldPath, null);
  const creatibutorsError =
    error || (creatibutorsList === formikInitialValues && initialError);
  const orderedRoleOptions = orderOptions(
    roleOptions,
    config.vocabularies.contributors.role
  );

  const handleModalOpen = () => {
    setModalOpen(true);
  };

  const handleModalClose = () => {
    focusAddButtonHandler();
    setModalOpen(false);
  };

  const handleOnContributorChange = (selectedCreatibutor) => {
    formikArrayPush(selectedCreatibutor);
    setModalOpen(true);
  };

  const focusAddButtonHandler = () => {
    document.getElementById(`${fieldPath}.add-button`).focus();
  };

  return (
    <Form.Field
      required={schema === "creators"}
      className={creatibutorsError ? "error" : ""}
    >
      <FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />
      <List>
        {creatibutorsList.map((value, index) => {
          // const key = `${fieldPath}.${index}`;
          const key = `${fieldPath}.${value.person_or_org.name}`;
          const identifiersError =
            creatibutorsError &&
            creatibutorsError[index]?.person_or_org?.identifiers;
          const displayName = creatibutorNameDisplay(value);
          console.log("CreatibutorsFieldForm initialCreatibutor", value);

          return (
            <CreatibutorsFieldItem
              key={key}
              identifiersError={identifiersError}
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
            />
          );
        })}
      </List>
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
        onClick={() => setModalOpen(true)}
      >
        <Icon name="add" />
        {"Add myself"}
      </Button>
      {modalOpen && (
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
          modalAction="add"
        />
      )}
      {/* <CreatibutorsNonModalForm
        onCreatibutorChange={handleOnContributorChange}
        addLabel={modal.addLabel}
        editLabel={modal.editLabel}
        roleOptions={orderedRoleOptions}
        schema={schema}
        autocompleteNames={autocompleteNames}
        trigger={
          <Button
            type="button"
            icon
            labelPosition="left"
            id={`${fieldPath}.add-button`}
            className="add-button"
            aria-labelledby={`${fieldPath}-field-description`}
            //  ref={this.adderRef}
          >
            <Icon name="add" />
            {addButtonLabel}
          </Button>
        }
        focusAddButtonHandler={focusAddButtonHandler}
        parentFieldPath={fieldPath}
        modalOpen={modalOpen}
        handleModalClose={handleModalClose}
        handleModalOpen={handleModalOpen}
        modalAction="add"
      /> */}
      {creatibutorsError && typeof creatibutorsError == "string" && (
        <Label pointing="left" prompt>
          {creatibutorsError}
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
  return (
    <FieldArray
      name={fieldPath}
      component={(formikProps) => (
        <CreatibutorsFieldForm
          {...formikProps}
          {...otherProps}
          {...{
            fieldPath,
            autocompleteNames,
            label,
            labelIcon,
            roleOptions,
            modal,
            schema,
            addButtonLabel,
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
  roleOptions: PropTypes.array,
};

CreatibutorsField.defaultProps = {};

export { CreatibutorsField, CreatibutorsFieldForm, sortOptions };
