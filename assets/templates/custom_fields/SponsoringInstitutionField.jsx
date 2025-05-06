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

const SponsoringInstitutionField = ({
  fieldPath,
  disabled,
  label = i18next.t("Sponsoring institution"),
  icon = "group",
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

SponsoringInstitutionField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string,
  icon: PropTypes.string,
  placeholder: PropTypes.string,
};

export { SponsoringInstitutionField };
