// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";

import { TextField } from "@js/invenio_modular_deposit_form/replacement_components/TextField";

import PropTypes from "prop-types";

export class ImprintPagesField extends Component {
  render() {
    const {
      fieldPath, // injected by the custom field loader via the `field` config property
      title,
      pages,
      label,
      icon,
      placeholder,
      description,
      helpText,
    } = this.props;
    return (
      <TextField
          fieldPath={fieldPath}
          label={label}
          placeholder={placeholder}
          icon={icon}
          description={description}
          helpText={helpText}
      />
    );
  }
}

ImprintPagesField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  pages: PropTypes.object,
  icon: PropTypes.string,
  label: PropTypes.string,
  placeholder: PropTypes.string,
  description: PropTypes.string
};

ImprintPagesField.defaultProps = {
  icon: "file outline",
  label: undefined,
  placeholder: undefined,
  description: undefined,
};
