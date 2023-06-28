// This file is part of the Knowledge Commons Repository
// a customized deployment of InvenioRDM
// Copyright (C) 2023 MESH Research.
// InvenioRDM Copyright (C) 2023 CERN.
//
// Invenio App RDM and the Knowledge Commons Repository are free software;
// you can redistribute them and/or modify them
// under the terms of the MIT License; see LICENSE file for more details.

import React, { useContext, useEffect } from "react";
import PropTypes from "prop-types";
import _get from "lodash/get";
import { FieldLabel, SelectField } from "react-invenio-forms";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { useFormikContext } from "formik";
import { ResourceTypeContext } from "./custom_RDMDepositForm";

const ResourceTypeField = ({fieldPath,
                            label=i18next.t("Resource type"),
                            labelIcon="tag",
                            options,
                            labelclassname="field-label-class",
                            required=false,
                            ...restProps}) => {

  const { values, submitForm } = useFormikContext();
  const { currentResourceType, handleResourceTypeChange } = useContext(ResourceTypeContext);
  console.log(values.metadata.resource_type);
  console.log(currentResourceType);

  useEffect(() => {
    if ( currentResourceType !== values.metadata.resource_type ) {
      handleResourceTypeChange(values.metadata.resource_type)
    }
  }, [values]
  );

  const groupErrors = (errors, fieldPath) => {
    const fieldErrors = _get(errors, fieldPath);
    if (fieldErrors) {
      return { content: fieldErrors };
    }
    return null;
  };

  /**
   * Generate label value
   *
   * @param {object} option - back-end option
   * @returns {string} label
   */
  const _label = (option) => {
    return option.type_name + (option.subtype_name ? " / " + option.subtype_name : "");
  };

  /**
   * Convert back-end options to front-end options.
   *
   * @param {array} propsOptions - back-end options
   * @returns {array} front-end options
   */
  const createOptions = (propsOptions) => {
    return propsOptions
      .map((o) => ({ ...o, label: _label(o) }))
      .sort((o1, o2) => o1.label.localeCompare(o2.label))
      .map((o) => {
        return {
          value: o.id,
          icon: o.icon,
          text: o.label,
        };
      });
  };
  const frontEndOptions = createOptions(options);

  return (
    <SelectField
        fieldPath={fieldPath}
        label={(
            <FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />
        )}
        optimized
        options={frontEndOptions}
        selectOnBlur={false}
        {...restProps}
    />
);
}

ResourceTypeField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string,
  labelIcon: PropTypes.string,
  labelclassname: PropTypes.string,
  options: PropTypes.arrayOf(
    PropTypes.shape({
      icon: PropTypes.string,
      type_name: PropTypes.string,
      subtype_name: PropTypes.string,
      id: PropTypes.string,
    })
  ).isRequired,
  required: PropTypes.bool,
};

export default ResourceTypeField;