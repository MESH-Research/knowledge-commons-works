// This file is part of Knowledge Commons Works
//
// Based on a file in Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2026 MESH Research
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import { Checkbox } from "semantic-ui-react";
import { Field } from "formik";
import PropTypes from "prop-types";

class EmbargoCheckboxComponent extends Component {
  render() {
    const { fieldPath, formik, checked, classnames, disabled, label, ...restProps } =
      this.props;
    return (
      <Checkbox
        id={fieldPath}
        data-testid="embargo-checkbox-component"
        disabled={disabled}
        checked={checked}
        label={label}
        onChange={() => {
          if (formik.field.value) {
            // Reset embargo fields on uncheck so the user must refill date/reason.
            // Do not change access.files — restricted files may still be desired.
            formik.form.setFieldValue("access.embargo", {
              active: false,
            });
          } else {
            // Embargo requires restricted files; flip them if still public.
            // Use Field (not FastField) so form.values is current after
            // localStorage restore / resetForm.
            const filesEnabled = formik.form.values.files?.enabled;
            const filesPublic = formik.form.values.access?.files === "public";
            if (filesEnabled && filesPublic) {
              formik.form.setFieldValue("access.files", "restricted");
            }
            formik.form.setFieldValue(fieldPath, true);
          }
        }}
        {...restProps}
        className={`mb-12 ${classnames}`}
      />
    );
  }
}

EmbargoCheckboxComponent.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  formik: PropTypes.object.isRequired,
  checked: PropTypes.bool,
  disabled: PropTypes.bool,
};

EmbargoCheckboxComponent.defaultProps = {
  checked: false,
  disabled: true,
};

export class EmbargoCheckboxField extends Component {
  render() {
    const { fieldPath } = this.props;

    return (
      <Field name={fieldPath}>
        {(formikProps) => (
          <EmbargoCheckboxComponent formik={formikProps} {...this.props} />
        )}
      </Field>
    );
  }
}

EmbargoCheckboxField.propTypes = {
  disabled: PropTypes.bool,
  fieldPath: PropTypes.string.isRequired,
};

EmbargoCheckboxField.defaultProps = {
  disabled: false,
};
