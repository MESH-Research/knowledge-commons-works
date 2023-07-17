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

import { ArrayField, GroupField, SelectField, TextField } from "react-invenio-forms";
// import { emptyAdditionalTitle } from "./initialValues";
import { LanguagesField } from "@js/invenio_rdm_records";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { FieldArray, useFormikContext } from "formik";

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

export const AdditionalTitlesField = ({fieldPath, options, recordUI}) => {
    const { values } = useFormikContext();
    const [titlesLength, setTitlesLength] = useState(-1);
    const [haveChangedNumber, setHaveChangedNumber] = useState(false);
    console.log(`titlesLength: ${titlesLength}`);

    useEffect(() => {
      if ( !!haveChangedNumber ) {
        if ( titlesLength < 0 ) {
          document.getElementById(`${fieldPath}.add-translated-button`)?.focus();
        } else {
          document.getElementById(`${fieldPath}.${titlesLength}.title`)?.focus();
        }
        console.log(document.getElementById(`${fieldPath}.${titlesLength}.title`));
        console.log(`${fieldPath}.${titlesLength}.title`);
        console.log(titlesLength);
      }
    }, [titlesLength]);

    const handleAddNew = (arrayHelpers, newItem) => {
      setHaveChangedNumber(true);
      arrayHelpers.push(newItem);
      setTitlesLength(titlesLength + 1);
    }

    const handleRemove = (arrayHelpers, index) => {
      setHaveChangedNumber(true);
      arrayHelpers.remove(index);
      setTitlesLength(titlesLength - 1);
    }

    return (
      <FieldArray
        addButtonLabel={i18next.t("Add other titles")}
        name={fieldPath}
        className="additional-titles"
        render={arrayHelpers => (
        <>
          {values.metadata.additional_titles.map(({title, type, lang}, index) => {
          const fieldPathPrefix = `${fieldPath}.${index}`;

          return (
            <Form.Group key={index} className="additional-titles-item-row">
              <TextField
                fieldPath={`${fieldPathPrefix}.title`}
                label="Additional title"
                id={`${fieldPathPrefix}.title`}
                required
                width={5}
              />
              <SelectField
                fieldPath={`${fieldPathPrefix}.type`}
                label="Type"
                id={`${fieldPathPrefix}.type`}
                optimized
                options={options.type}
                required
                width={5}
              />
              <LanguagesField
                serializeSuggestions={(suggestions) =>
                  suggestions.map((item) => ({
                    text: item.title_l10n,
                    value: item.id,
                    fieldPathPrefix: item.id,
                  }))
                }
                initialOptions={
                  recordUI?.additional_titles &&
                  recordUI.additional_titles[index]?.lang
                    ? [recordUI.additional_titles[index].lang]
                    : []
                }
                fieldPath={`${fieldPathPrefix}.lang`}
                id={`${fieldPathPrefix}.lang`}
                label="Language"
                multiple={false}
                placeholder="Select language"
                labelIcon={null}
                clearable
                selectOnBlur={false}
                width={5}
              />
              <Form.Field>
                <Button
                  aria-label={i18next.t("Remove field")}
                  className="close-btn"
                  icon
                  onClick={() => handleRemove(arrayHelpers, index)}
                >
                  <Icon name="close" />
                </Button>
              </Form.Field>
            </Form.Group>
          )})}
            <Button
                type="button"
                onClick={() => handleAddNew(arrayHelpers, emptyTranslatedTitle)}
                icon
                className="align-self-end"
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
                className="align-self-end"
                labelPosition="left"
                id={`${fieldPath}.add-alternate-button`}
            >
                <Icon name="add" />
                Add alternate title
            </Button>
      </>
    )}
    />
  )
}

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
