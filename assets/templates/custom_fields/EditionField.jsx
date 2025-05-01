// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import PropTypes from "prop-types";
import { i18next } from "@translations/i18next";
import { TextField } from "@js/invenio_modular_deposit_form/replacement_components/TextField";

const EditionField = ({
  fieldPath,
  disabled,
  label = i18next.t("Edition or version"),
  icon = "code branch",
  placeholder,
  helpText,
  required = false,
  ...extraProps
}) => {
  return (
    <TextField
      fieldPath={fieldPath}
      label={label}
      icon={icon}
      placeholder={placeholder}
      helpText={helpText}
      required={required}
      fluid={true}
      {...extraProps}
    />
  );
};

EditionField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string,
  icon: PropTypes.string,
  placeholder: PropTypes.string,
};

export default EditionField;
