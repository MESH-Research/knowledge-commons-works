// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import PropTypes from "prop-types";
import { TextField } from "@js/invenio_modular_deposit_form/replacement_components/TextField";

const ImprintPlaceField = ({
  fieldPath, // injected by the custom field loader via the `field` config property
  place,
  label,
  labelIcon = "map marker alternate",
  placeholder,
  description,
  ...extraProps
}) => {
  return (
    <>
      <TextField
        fieldPath={fieldPath}
        label={label}
        labelIcon={labelIcon}
        placeholder={placeholder}
        type={"text"}
        {...extraProps}
      />
      {description && <label className="helptext mb-0">{description}</label>}
    </>
  );
};

ImprintPlaceField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  place: PropTypes.object,
  icon: PropTypes.string,
  label: PropTypes.string,
  placeholder: PropTypes.string,
  description: PropTypes.string,
};

export { ImprintPlaceField };
