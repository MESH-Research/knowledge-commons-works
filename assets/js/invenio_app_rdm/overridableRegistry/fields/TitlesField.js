// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import PropTypes from "prop-types";

import { FieldLabel, TextField } from "react-invenio-forms";
import { AdditionalTitlesField } from "./AdditionalTitlesField";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { Form } from "semantic-ui-react";
import { Field } from "formik";

const TitlesField = ({
  fieldPath = "metadata.title",
  options,
  label = i18next.t("Title"),
  required = false,
  recordUI = undefined,
  disabled = false,
}) => {
  return (
    <>
      <Field id={"metadata.title"} name={"metadata.title"}>
        {({
          field, // { name, value, onChange, onBlur }
          form: { touched, errors }, // also values, setXXXX, handleXXXX, dirty, isValid, status, etc.
          meta,
        }) => (
          <Form.Field
            required={!!required}
            error={!!meta.error && !!meta.touched}
            // (!!meta.touched && !!meta.errors) ||
            // (!meta.touched && meta.initialError)
            className="invenio-text-input-field title-field"
          >
            <FieldLabel htmlFor={fieldPath} icon="book" label={label} />
            <Form.Input
              error={meta.error && meta.touched ? meta.error : undefined}
              disabled={disabled}
              fluid
              id={fieldPath}
              name={fieldPath}
              {...field}
            />
          </Form.Field>
        )}
      </Field>
      <AdditionalTitlesField
        options={options}
        recordUI={recordUI}
        fieldPath="metadata.additional_titles"
      />
    </>
  );
};

TitlesField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string,
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
  }).isRequired,
  required: PropTypes.bool,
  recordUI: PropTypes.object,
};

export { TitlesField };
