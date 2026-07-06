// This file is part of Knowledge Commons Works
// Copyright (C) 2024 MESH Research.
//
// Knowledge Commons Works is free software; you can redistribute it
// and/or modify it under the terms of the MIT License; see LICENSE
// file for more details.

/**
 * @module IdentifiersComponent
 * Replacement for the modular deposit form's AlternateIdentifiersComponent.
 * Provides two separate add buttons ("Add URL" / "Add identifier"), URL-specific
 * row layout (wider input, no scheme dropdown), and on-blur cleanup of empty rows.
 */

import React, { useEffect, useState } from "react";
import { useStore } from "react-redux";
import { FieldArray, useFormikContext } from "formik";
import { Button, Form, Icon } from "semantic-ui-react";
import { FieldLabel } from "react-invenio-forms";
import { i18next } from "@translations/i18next";
import { FieldComponentWrapper } from "@js/invenio_modular_deposit_form/field_components/FieldComponentWrapper";
import { SelectField } from "@js/invenio_modular_deposit_form/replacement_components/input_controls/SelectField";
import { TextField } from "@js/invenio_modular_deposit_form/replacement_components/input_controls/TextField";

const emptyIdentifier = { scheme: "", identifier: "" };
const emptyURL = { scheme: "url", identifier: "" };

/** Resolve a dot-separated path against an object. */
const getIn = (obj, path) =>
  path.split(".").reduce((o, key) => o?.[key], obj);

/**
 * Inner identifiers array field.
 * `fieldPath`, `label`, `labelIcon`, and `required` are injected by
 * `FieldComponentWrapper` via `React.cloneElement`; defaults are provided
 * for standalone use.
 *
 * @param {string}   fieldPath       - Formik path, e.g. "metadata.identifiers".
 * @param {string}   [label]         - Field label text.
 * @param {string}   [labelIcon]     - Semantic UI icon name for the label.
 * @param {boolean}  [required]      - Whether the field is required.
 * @param {Object[]} [schemeOptions] - Options for the scheme dropdown.
 * @param {boolean}  [showEmptyValue] - Whether to show an empty initial row.
 */
const IdentifiersField = ({
  fieldPath = "metadata.identifiers",
  label = i18next.t("Identifiers"),
  labelIcon = "barcode",
  required = false,
  schemeOptions = undefined,
  showEmptyValue = false,
}) => {
  const { values, setFieldValue } = useFormikContext();
  const [identifiersLength, setIdentifiersLength] = useState(0);
  const [haveChangedNumber, setHaveChangedNumber] = useState(false);

  useEffect(() => {
    if (!haveChangedNumber) return;
    if (identifiersLength < 0) {
      document.getElementById(`${fieldPath}.add-url-button`)?.focus();
    } else {
      document
        .getElementById(`${fieldPath}.${identifiersLength}.identifier`)
        ?.focus();
    }
  }, [identifiersLength, haveChangedNumber, fieldPath]);

  const handleAddNew = (arrayHelpers, newItem) => {
    setHaveChangedNumber(true);
    arrayHelpers.push(newItem);
    setIdentifiersLength((n) => n + 1);
  };

  const handleRemove = (arrayHelpers, index) => {
    setHaveChangedNumber(true);
    arrayHelpers.remove(index);
    setIdentifiersLength((n) => n - 1);
  };

  /**
   * Remove incomplete rows once focus leaves the row group.
   * A short timeout lets focus settle on a sibling before deciding the row
   * is truly abandoned.
   */
  const filterEmptyIdentifiers = (e) => {
    const parentElement = e.target.closest(".fields");
    const siblingElements = parentElement
      ? Array.from(parentElement.querySelectorAll("*"))
      : [];

    setTimeout(() => {
      const siblingHasFocus = siblingElements.some(
        (el) =>
          el.firstElementChild === document.activeElement ||
          (document.activeElement.id &&
            el.id.includes(document.activeElement.id))
      );
      const current = getIn(values, fieldPath) ?? [];
      if (current.length && !siblingHasFocus) {
        const filtered = current.filter(
          ({ identifier, scheme }) => identifier !== "" || scheme !== ""
        );
        setIdentifiersLength(filtered.length - 1);
        setFieldValue(fieldPath, filtered);
      }
    }, 10);
  };

  const currentIdentifiers = getIn(values, fieldPath) ?? [];

  return (
    <FieldArray
      name={fieldPath}
      id={fieldPath}
      className="invenio-array-field"
      showEmptyValue={showEmptyValue}
      render={(arrayHelpers) => (
        <>
          <Form.Field required={required}>
            <FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />
          </Form.Field>

          {currentIdentifiers.map(({ scheme, identifier }, index) => {
            const fieldPathPrefix = `${fieldPath}.${index}`;
            const isUrl = scheme === "url";
            const hasText = identifier !== "";
            const hasScheme = scheme !== "";

            return (
              <Form.Group
                id={`${fieldPath}.${index}`}
                key={index}
                className="identifier-item-row"
                onBlur={(e) => filterEmptyIdentifiers(e)}
              >
                <TextField
                  fieldPath={`${fieldPathPrefix}.identifier`}
                  label={isUrl ? i18next.t("URL") : i18next.t("Identifier")}
                  required={!isUrl && hasScheme}
                  id={`${fieldPathPrefix}.identifier`}
                  width={isUrl ? 14 : 9}
                  fluid={false}
                  onBlur={(e) => filterEmptyIdentifiers(e)}
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
                {!schemeOptions && !isUrl && (
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
            {i18next.t("Add URL")}
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
            {i18next.t("Add identifier")}
          </Button>
        </>
      )}
    />
  );
};

/**
 * Deposit form section component for alternate identifiers / URLs.
 * Registered as `AlternateIdentifiersComponent` in the extras componentsRegistry,
 * overriding the modular form's default to provide the KCWorks dual-button UX.
 * `fieldPath`, `label`, and `labelIcon` are injected into `IdentifiersField` by
 * `FieldComponentWrapper` via `React.cloneElement`.
 */
const IdentifiersComponent = ({ ...extraProps }) => {
  const vocabularies =
    useStore().getState().deposit?.config?.vocabularies ?? { metadata: {} };

  return (
    <FieldComponentWrapper
      componentName="IdentifiersField"
      fieldPath="metadata.identifiers"
      label={i18next.t("URLs and Other Identifiers")}
      labelIcon="barcode"
      {...extraProps}
    >
      <IdentifiersField
        schemeOptions={vocabularies.metadata?.identifiers?.scheme}
        showEmptyValue={false}
      />
    </FieldComponentWrapper>
  );
};

export { IdentifiersComponent };
