/*
* This file is part of Knowledge Commons Works.
* Copyright (C) 2024 Mesh Research.
*
* Knowledge Commons Works is based on InvenioRDM, and
* this file is based on code from InvenioRDM. InvenioRDM is
* Copyright (C) 2020-2024 CERN.
* Copyright (C) 2020-2022 Northwestern University.
*
* InvenioRDM and Knowledge Commons Works are both free software;
* you can redistribute and/or modify them under the terms of the
* MIT License; see LICENSE file for more details.
*/

import PropTypes from "prop-types";
import React, { useState, useEffect } from "react";
import { FieldLabel } from "react-invenio-forms";
import { Button, Form, Icon } from "semantic-ui-react";
import { i18next } from "@translations/invenio_rdm_records/i18next";
// import { emptyIdentifier } from "./initialValues";
import { FieldArray, useFormikContext } from "formik";
import { TextField } from "@js/invenio_modular_deposit_form/replacement_components/TextField";
import { SelectField } from "@js/invenio_modular_deposit_form/replacement_components/SelectField";

const emptyIdentifier = {
  scheme: "",
  identifier: "",
};

const emptyURL = {
  scheme: "url",
  identifier: "",
};

/** Identifiers array component */
export const IdentifiersField = ({
  fieldPath,
  description,
  placeholder,
  label = i18next.t("Identifiers"),
  icon = "barcode",
  required = false,
  schemeOptions = undefined,
  showEmptyValue = false,
}) => {
  const { values, setFieldValue } = useFormikContext();
  const [identifiersLength, setIdentifiersLength] = useState(0);
  const [haveChangedNumber, setHaveChangedNumber] = useState(false);
  const addButtonLabel = i18next.t("Add identifier");

  useEffect(() => {
    if (!!haveChangedNumber) {
      if (identifiersLength < 0) {
        document.getElementById(`${fieldPath}.add-url-button`)?.focus();
      } else {
        document
          .getElementById(`${fieldPath}.${identifiersLength}.identifier`)
          ?.focus();
      }
    }
  }, [identifiersLength]);

  // useEffect(() => {
  //   if (values.metadata.identifiers.length < 1) {
  //     setFieldValue(fieldPath, [emptyURL]);
  //   }
  // }, []);

  const handleAddNew = (arrayHelpers, newItem) => {
    setHaveChangedNumber(true);
    arrayHelpers.push(newItem);
    setIdentifiersLength(identifiersLength + 1);
  };

  const handleRemove = (arrayHelpers, index) => {
    setHaveChangedNumber(true);
    arrayHelpers.remove(index);
    setIdentifiersLength(identifiersLength - 1);
  };

  const filterEmptyIdentifiers = (e) => {
    // Get the parent element
    const parentElement = e.target.closest(".fields");

    // Get all sibling elements
    const siblingElements = Array.from(parentElement.querySelectorAll("*"));

    // Check if any sibling elements have focus
    // wait for the focus to reach the sibling element
    setTimeout(() => {
      const siblingHasFocus = siblingElements.some(
        (element) =>
          element.firstElementChild === document.activeElement ||
          (document.activeElement.id &&
            element.id.includes(document.activeElement.id))
      );
      if (values.metadata.identifiers.length && !siblingHasFocus) {
        let filteredIdentifiers = values.metadata.identifiers.reduce(
          (newList, item) => {
            if (item.identifier !== "" && item.scheme !== "")
              newList.push(item);
            return newList;
          },
          []
        );
        setIdentifiersLength(filteredIdentifiers.length - 1);
        setFieldValue("metadata.identifiers", filteredIdentifiers);
      }
    }, 10);
  };

  return (
    <FieldArray
      name={fieldPath}
      id={fieldPath}
      className="invenio-array-field"
      showEmptyValue={showEmptyValue}
      render={(arrayHelpers) => (
        <>
          <Form.Field required={required}>
            <FieldLabel htmlFor={fieldPath} icon={icon} label={label} />
          </Form.Field>

          {values.metadata.identifiers.map(({ scheme, identifier }, index) => {
            const fieldPathPrefix = `${fieldPath}.${index}`;
            const isUrl = scheme === "url";
            const hasText = !!identifier || identifier !== "";
            const hasScheme = !!scheme || scheme !== "";

            return (
              <Form.Group
                id={`${fieldPath}.${index}`}
                key={index}
                className="identifier-item-row"
                onBlur={(e) => {
                  filterEmptyIdentifiers(e);
                }}
              >
                {/* <GroupField key={index} inline> */}
                <TextField
                  fieldPath={`${fieldPathPrefix}.identifier`}
                  label={i18next.t(!isUrl ? "Identifier" : "URL")}
                  required={!isUrl && hasScheme}
                  id={`${fieldPathPrefix}.identifier`}
                  width={!!isUrl ? 14 : 9}
                  fluid={false}
                  onBlur={(e) => {
                    filterEmptyIdentifiers(e);
                  }}
                />
                {schemeOptions && !isUrl && (
                  <SelectField
                    fieldPath={`${fieldPathPrefix}.scheme`}
                    id={`${fieldPathPrefix}.scheme`}
                    label={i18next.t("Scheme")}
                    options={schemeOptions}
                    optimized
                    required={!isUrl && hasText}
                    width={5}
                  />
                )}
                {!schemeOptions && (
                  <TextField
                    fieldPath={`${fieldPathPrefix}.scheme`}
                    id={`${fieldPathPrefix}.scheme`}
                    label={i18next.t("Scheme")}
                    required
                    width={5}
                    fluid={false}
                  />
                )}
                <Form.Field width={2}>
                  <Button
                    aria-label={i18next.t("Remove field")}
                    className="close-btn"
                    icon="close"
                    onClick={() => handleRemove(arrayHelpers, index)}
                  />
                </Form.Field>
                {description && (
                  <label className="helptext mb-0">{description}</label>
                )}
              </Form.Group>
            );
          })}
          <Button
            type="button"
            onClick={() => handleAddNew(arrayHelpers, emptyURL)}
            icon
            className="align-self-end add-button"
            labelPosition="left"
            id={`${fieldPath}.add-url-button`}
          >
            <Icon name="add" />
            Add URL
          </Button>
          <Button
            type="button"
            onClick={() => handleAddNew(arrayHelpers, emptyIdentifier)}
            icon
            className="align-self-end add-button"
            labelPosition="left"
            id={`${fieldPath}.add-id-button`}
          >
            <Icon name="add" />
            Add another identifier
          </Button>
        </>
      )}
    />
  );
};

IdentifiersField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string,
  icon: PropTypes.string,
  required: PropTypes.bool,
  schemeOptions: PropTypes.arrayOf(
    PropTypes.shape({
      text: PropTypes.string,
      value: PropTypes.string,
    })
  ),
  showEmptyValue: PropTypes.bool,
};
