// This file is part of the Knowledge Commons Repository
// a customized deployment of InvenioRDM
// Copyright (C) 2023 MESH Research.
// InvenioRDM Copyright (C) 2023 CERN.
//
// Invenio App RDM and the Knowledge Commons Repository are free software;
// you can redistribute them and/or modify them
// under the terms of the MIT License; see LICENSE file for more details.

import React, { useContext, useEffect, useState } from "react";
import PropTypes from "prop-types";
import _get from "lodash/get";
import { Form } from "semantic-ui-react";
import { FieldLabel, SelectField } from "react-invenio-forms";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { useFormikContext } from "formik";
import { FormValuesContext } from "../custom_deposit/custom_RDMDepositForm";
import { Button, Icon, Menu } from "semantic-ui-react";

const ResourceTypeField = ({fieldPath,
                            label=i18next.t("Resource type"),
                            labelIcon="tag",
                            options,
                            labelclassname="field-label-class",
                            required=false,
                            ...restProps}) => {

  const [ otherToggleActive, setOtherToggleActive ] = useState(false);
  const { values, errors, setFieldValue, initialValues } = useFormikContext();
  const selectedType = values[fieldPath];
  const { uiValues, handleValuesChange,
          uiErrors, handleErrorsChange } = useContext(FormValuesContext);

  useEffect(() => {

  }, []);

  useEffect(() => {
    if ( !!uiValues &&
      uiValues.metadata.resource_type !== values.metadata.resource_type ) {
      handleValuesChange(values);
    }
  }, [values]
  );

  useEffect(() => {
    if ( uiErrors !== errors ) {
      handleErrorsChange(errors);
    }
  }, [errors]
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

  const handleItemClick = (event, { name }) => {
    setFieldValue("metadata.resource_type", name);
    setOtherToggleActive(false);
  }

  const handleOtherToggleClick = () => {
    setFieldValue("metadata.resource_type", null);
    setOtherToggleActive(true);
  }

  const buttonTypes = [
    {id: 'textDocument-journalArticle',
     label: 'Journal Article',
     icon: 'file text'
    },
    {id: 'textDocument-review',
     label: 'Review',
     icon: 'thumbs up'
    },
    {id: 'textDocument-book',
     label: 'Book',
     icon: 'book'
    },
    {id: 'textDocument-bookSection',
     label: 'Book Section',
     icon: 'book'
    },
    {id: 'instructionalResource-syllabus',
     label: 'Syllabus',
     icon: 'graduation'
    },
  ]

  return (
    <>
      <Form.Field required={required}>
        <FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />
      </Form.Field>
      <Menu compact icon='labeled' fluid widths={6}>
      {buttonTypes.map((buttonType, index) => (
        <Menu.Item
          key={index}
          name={buttonType.id}
          as={Button}
          active={values.metadata.resource_type === buttonType.id}
          onClick={handleItemClick}
        >
          <Icon name={buttonType.icon} />
          {buttonType.label}
        </Menu.Item>
        )
      )}
        <Menu.Item
          name='otherToggle'
          active={otherToggleActive === true}
          onClick={handleOtherToggleClick}
          as={Button}
        >
          <Icon name='asterisk' />
          Other...
        </Menu.Item>
      </Menu>
      {!!otherToggleActive &&
        <SelectField
            fieldPath={fieldPath}
            label={""}
            optimized
            options={frontEndOptions}
            selectOnBlur={false}
            search={true}
            placeholder={"choose another resource type..."}
            {...restProps}
        />
      }
    </>
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