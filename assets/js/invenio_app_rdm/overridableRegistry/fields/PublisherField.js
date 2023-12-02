// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import PropTypes from "prop-types";
import { Field } from "formik";
import { Form, Label } from "semantic-ui-react";

import { FieldLabel } from "react-invenio-forms";
import { i18next } from "@translations/invenio_rdm_records/i18next";

import { TextField } from "@js/invenio_modular_deposit_form/replacement_components/TextField";

const PublisherField = ({
  fieldPath,
  disabled,
  label,
  labelIcon,
  placeholder,
  helpText,
  required,
}) => {
  return (
    <TextField
      fieldPath={fieldPath}
      label={label}
      labelIcon={labelIcon}
      placeholder={placeholder}
      helpText={helpText}
      required={required}
      fluid={true}
    />
  );
};

PublisherField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string,
  labelIcon: PropTypes.string,
  placeholder: PropTypes.string,
};

PublisherField.defaultProps = {
  label: i18next.t("Publisher"),
  labelIcon: "building outline",
  placeholder: i18next.t("Publisher"),
  required: true,
};

export { PublisherField };
