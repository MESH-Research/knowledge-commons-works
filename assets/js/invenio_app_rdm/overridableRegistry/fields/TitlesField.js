// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import PropTypes from "prop-types";

import { AdditionalTitlesField } from "./AdditionalTitlesField";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { Form } from "semantic-ui-react";
import { Field } from "formik";

import { TextField } from "@js/invenio_modular_deposit_form/replacement_components/TextField";

const TitlesField = ({
  fieldPath = "metadata.title",
  options,
  label = i18next.t("Title"),
  required = false,
  recordUI = undefined,
  disabled = false,
  ...extraProps
}) => {
  return (
    <>
      <TextField
        fieldPath={fieldPath}
        label={label}
        required={required}
        classnames="title-field"
        showLabel={true}
        labelIcon="book"
        disabled={disabled}
        {...extraProps}
      />
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
