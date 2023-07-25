// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { ArrayField, GroupField, SelectField, TextField } from "react-invenio-forms";
import { Button, Form, Icon } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";
import _matches from "lodash/matches";
import _filter from "lodash/filter";
import _isEqual from "lodash/isEqual";
import _has from "lodash/has";
// import { emptyDate } from "./initialValues";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { sortOptions } from "@js/invenio_rdm_records";
import { FieldArray, useFormikContext } from "formik";

export const emptyDate = {
  date: "",
  description: "",
  type: "",
};


/** Top-level Dates Component */
/**
 * Returns the required option if the current value passed does match it
 * @param  {Object} currentValue The current value
 * @param  {Array} arrayOfValues The array of values for the field
 * @return {Object} The required option if any
 */
const DatesField = ({ requiredOptions=[],
                      fieldPath,
                      options,
                      label=i18next.t("Dates"),
                      addButtonLabel=i18next.t("Add another date"),
                      labelIcon="calendar",
                      placeholderDate=i18next.t("YYYY-MM-DD or YYYY-MM-DD/YYYY-MM-DD"),
                      required=false,
                      showEmptyValue=false  } ) => {
  const { values } = useFormikContext();
  const [datesLength, setDatesLength] = useState(-1);
  const [haveChangedNumber, setHaveChangedNumber] = useState(false);

  const getRequiredOption = (currentValue, arrayOfValues) => {
    for (const requiredOption of requiredOptions) {
      // If more values matched we do take the first value
      const matchingValue = _filter(arrayOfValues, _matches(requiredOption))[0];
      if (_isEqual(matchingValue, currentValue)) {
        return requiredOption;
      }
    }
    return null;
  };

  useEffect(() => {
    if ( !!haveChangedNumber ) {
      if ( datesLength < 0 ) {
        document.getElementById(`${fieldPath}.add-button`)?.focus();
      } else {
        document.getElementById(`${fieldPath}.${datesLength}.date`)?.focus();
      }
    }
  }, [datesLength]);

  const handleAddNew = (arrayHelpers, newItem) => {
    setHaveChangedNumber(true);
    arrayHelpers.push(newItem);
    setDatesLength(datesLength + 1);
  }

  const handleRemove = (arrayHelpers, index) => {
    setHaveChangedNumber(true);
    arrayHelpers.remove(index);
    setDatesLength(datesLength - 1);
  }

  return (
    <FieldArray
      name={fieldPath}
      // helpText={i18next.t(
      //   "Format: DATE or DATE/DATE where DATE is YYYY or YYYY-MM or YYYY-MM-DD."
      // )}
      // label={""}
      // labelIcon={""}
      required={required}
      requiredOptions={requiredOptions}
      showEmptyValue={showEmptyValue}
      render={arrayHelpers => (
      <>
        { values.metadata.dates.map((value, index) => {
        const fieldPathPrefix = `${fieldPath}.${index}`;
        const requiredOption = getRequiredOption(value, values.metadata.dates);
        const hasRequiredDateValue = _has(requiredOption, "date");
        const hasRequiredTypeValue = _has(requiredOption, "type");
        const hasRequiredDescriptionValue = _has(requiredOption, "description");
        return (
          <Form.Group key={index} optimized>
            <TextField
              fieldPath={`${fieldPathPrefix}.date`}
              id={`${fieldPathPrefix}.date`}
              label={index===0 ? i18next.t("Date") : ""}
              placeholder={placeholderDate}
              disabled={hasRequiredDateValue}
              required
              width={5}
            />
            <SelectField
              fieldPath={`${fieldPathPrefix}.type`}
              id={`${fieldPathPrefix}.type`}
              label={index===0 ? i18next.t("Type") : ""}
              options={sortOptions(options.type)}
              disabled={hasRequiredTypeValue}
              required
              width={5}
              optimized
            />
            <TextField
              fieldPath={`${fieldPathPrefix}.description`}
              id={`${fieldPathPrefix}.description`}
              label={index===0 ? i18next.t("Description") : ""}
              disabled={hasRequiredDescriptionValue}
              width={5}
            />
            <Form.Field>
              <Button
                aria-label={i18next.t("Remove item")}
                className="close-btn"
                disabled={!_isEmpty(requiredOption)}
                icon
                onClick={() => handleRemove(arrayHelpers, index)}
                type="button"
              >
                <Icon name="close" />
              </Button>
            </Form.Field>
          </Form.Group>
          )})}
            <Button
                type="button"
                onClick={() => handleAddNew(arrayHelpers, emptyDate)}
                icon
                className="align-self-end add-btn"
                labelPosition="left"
                id={`${fieldPath}.add-button`}
            >
                <Icon name="add" />
                {addButtonLabel}
            </Button>
        </>
      )}
    />
  )
}

DatesField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string,
  labelIcon: PropTypes.string,
  options: PropTypes.shape({
    type: PropTypes.arrayOf(
      PropTypes.shape({
        text: PropTypes.string,
        value: PropTypes.string,
      })
    ),
  }).isRequired,
  required: PropTypes.bool,
  placeholderDate: PropTypes.string,
  requiredOptions: PropTypes.array,
  showEmptyValue: PropTypes.bool,
};

export { DatesField };