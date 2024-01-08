// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import PropTypes from "prop-types";

import { FieldLabel } from "react-invenio-forms";
import { AdditionalDescriptionsField } from "./AdditionalDescriptionsField";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { TextArea } from "@js/invenio_modular_deposit_form/replacement_components/TextArea";

const DescriptionsField = ({
  classnames,
  fieldPath,
  label = i18next.t("Description"),
  labelIcon = "pencil",
  options,
  editorConfig = undefined,
  recordUI = undefined,
}) => {
  return (
    <>
      <TextArea
        className={`description-field rel-mb-1 ${classnames}`}
        fieldPath={fieldPath}
        editorConfig={editorConfig}
        label={
          <FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />
        }
        optimized
      />
      <AdditionalDescriptionsField
        recordUI={recordUI}
        options={options}
        editorConfig={editorConfig}
        fieldPath="metadata.additional_descriptions"
      />
    </>
  );
};

DescriptionsField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.node,
  labelIcon: PropTypes.string,
  editorConfig: PropTypes.object,
  recordUI: PropTypes.object,
  options: PropTypes.object.isRequired,
};

export { DescriptionsField };
