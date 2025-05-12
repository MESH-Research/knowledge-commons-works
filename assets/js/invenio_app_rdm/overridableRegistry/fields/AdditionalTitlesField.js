// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { useEffect, useState } from "react";
import PropTypes from "prop-types";
import { Button, Form, Icon } from "semantic-ui-react";

import {
  SelectField,
  TextField,
} from "react-invenio-forms";
import { i18next } from "@translations/i18next";
import { FieldArray, useFormikContext } from "formik";
import { SingleLanguageSelector } from "./shared_components/SingleLanguageSelector";

const emptyAlternateTitle = {
  lang: "",
  title: "",
  type: "alternative-title",
};

const emptyTranslatedTitle = {
  lang: "",
  title: "",
  type: "translated-title",
};

/**
 * Form field component for additional titles for the RDM deposit form.
 *
 * NOTE: The language subfield uses a custom implementation of the LanguagesField
 * component. It does not use a simple string value for the language, but an object
 * with the following shape:
 *
 * {
 *   id: string,
 *   title_l10n: string,
 * }
 *
 * This is necessary in order to preserve the readable language name in the dropdown
 * menu when the component re-renders from the client-side form values.
 *
 * @param {Object} props - The component props.
 * @param {string} props.fieldPath - The path to the field in the form values.
 * @param {Object} props.options - The options for the field.
 * @param {Object} props.recordUI - The record.ui property from the redux store.
 * @returns {React.ReactNode} The component.
 */
const AdditionalTitlesField = ({ fieldPath, options, recordUI }) => {
  const { values } = useFormikContext();
  const [titlesLength, setTitlesLength] = useState(-1);
  const [haveChangedNumber, setHaveChangedNumber] = useState(false);

  useEffect(() => {
    if (!!haveChangedNumber) {
      if (titlesLength < 0) {
        document.getElementById(`${fieldPath}.add-translated-button`)?.focus();
      } else {
        document.getElementById(`${fieldPath}.${titlesLength}.title`)?.focus();
      }
    }
  }, [titlesLength]);

  const handleAddNew = (arrayHelpers, newItem) => {
    setHaveChangedNumber(true);
    arrayHelpers.push(newItem);
    setTitlesLength(titlesLength + 1);
  };

  const handleRemove = (arrayHelpers, index) => {
    setHaveChangedNumber(true);
    arrayHelpers.remove(index);
    setTitlesLength(titlesLength - 1);
  };

  return (
    <FieldArray
      addButtonLabel={i18next.t("Add other titles")}
      name={fieldPath}
      className="additional-titles"
      render={(arrayHelpers) => (
        <>
          {values.metadata.additional_titles.map((value, index) => {
            const fieldPathPrefix = `${fieldPath}.${index}`;
            let titleWord =
              value.type === "translated-title" ? "Translated" : "Additional";
            titleWord =
              value.type === "alternative-title" ? "Alternative" : titleWord;

            return (
              <Form.Group key={index} className="additional-titles-item-row">
                <TextField
                  fieldPath={`${fieldPathPrefix}.title`}
                  label={`${titleWord} title`}
                  id={`${fieldPathPrefix}.title`}
                  required
                  width={7}
                />
                <SelectField
                  fieldPath={`${fieldPathPrefix}.type`}
                  label="Type"
                  id={`${fieldPathPrefix}.type`}
                  optimized
                  options={options.type}
                  required
                  width={4}
                />
                <SingleLanguageSelector
                  fieldPath={fieldPathPrefix}
                  value={value}
                  index={index}
                  recordUI={recordUI}
                  fieldName="additional_titles"
                  clearable={true}
                />
                <Form.Field>
                  <Button
                    aria-label={i18next.t("Remove item")}
                    className="close-btn no-label"
                    icon
                    onClick={() => handleRemove(arrayHelpers, index)}
                  >
                    <Icon name="close" />
                  </Button>
                </Form.Field>
              </Form.Group>
            );
          })}
          <Button
            type="button"
            onClick={() => handleAddNew(arrayHelpers, emptyTranslatedTitle)}
            icon
            className="align-self-end add-btn"
            labelPosition="left"
            id={`${fieldPath}.add-translated-button`}
          >
            <Icon name="add" />
            Add translated title
          </Button>
          <Button
            type="button"
            onClick={() => handleAddNew(arrayHelpers, emptyAlternateTitle)}
            icon
            className="align-self-end add-btn"
            labelPosition="left"
            id={`${fieldPath}.add-alternate-button`}
          >
            <Icon name="add" />
            Add alternative title
          </Button>
        </>
      )}
    />
  );
};

AdditionalTitlesField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  options: PropTypes.shape({
    type: PropTypes.arrayOf(
      PropTypes.shape({
        icon: PropTypes.string,
        text: PropTypes.string,
        value: PropTypes.string,
      })
    ),
    lang: PropTypes.arrayOf(
      PropTypes.shape({
        text: PropTypes.string,
        value: PropTypes.string,
      })
    ),
  }),
  recordUI: PropTypes.object,
};

AdditionalTitlesField.defaultProps = {
  options: undefined,
  recordUI: undefined,
};

export { AdditionalTitlesField };
