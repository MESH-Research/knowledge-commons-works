// This file is part of the Knowledge Commons Repository
// a customized deployment of InvenioRDM
// Copyright (C) 2023 MESH Research.
// InvenioRDM Copyright (C) 2023 CERN.
//
// Invenio App RDM and the Knowledge Commons Repository are free software;
// you can redistribute them and/or modify them
// under the terms of the MIT License; see LICENSE file for more details.

import React, { useState } from "react";
import PropTypes from "prop-types";
import _get from "lodash/get";
import { Form } from "semantic-ui-react";
import { FieldLabel, SelectField } from "react-invenio-forms";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { useFormikContext } from "formik";
// import { FormValuesContext } from "../custom_deposit/custom_RDMDepositForm";
import { Button, Icon, Menu } from "semantic-ui-react";

const ResourceTypeSelectorField = ({fieldPath,
                            label=i18next.t("Resource type"),
                            labelIcon="tag",
                            options,
                            labelclassname="field-label-class",
                            required=false,
                            ...restProps}) => {

  const [ otherToggleActive, setOtherToggleActive ] = useState(false);
  const { values, errors, setFieldValue, initialValues } = useFormikContext();

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

  const handleItemClick = (event) => {
    setFieldValue("metadata.resource_type",
                  event.target.closest('button').name);
    setOtherToggleActive(false);
  }

  const handleOtherToggleClick = () => {
    setFieldValue("metadata.resource_type", null);
    setOtherToggleActive(true);
    document.querySelectorAll(".resource-type-field .invenio-select-field input")[0].focus();
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
      <div
        className="ui compact fluid icon labeled six item menu"
      >
      {buttonTypes.map((buttonType, index) => (
        // <Menu.Item
        //   key={index}
        //   name={buttonType.id}
        //   as={Button}
        //   active={values.metadata.resource_type === buttonType.id}
        //   onClick={handleItemClick}
        //   formnovalidate
        // >
        //   <Icon name={buttonType.icon} />
        //   {buttonType.label}
        // </Menu.Item>
        <button
          key={index}
          id={buttonType.id}
          name={buttonType.id}
          onClick={handleItemClick}
          className={`ui button item ${values.metadata.resource_type === buttonType.id ? "active" : ""}`}
          formNoValidate
          type="button"
        >
          <Icon name={buttonType.icon} />
          {buttonType.label}
        </button>
        )
      )}
        <button
          id={'otherToggle'}
          name={'otherToggle'}
          onClick={handleOtherToggleClick}
          className={`ui button item ${otherToggleActive === true ? "active" : ""}`}
          formNoValidate
          type="button"
        >
          <Icon name="asterisk" />
          Other...
        </button>
        {/* <Menu.Item
          name='otherToggle'
          active={otherToggleActive === true}
          onClick={handleOtherToggleClick}
          as={Button}
        >
          <Icon name='asterisk' />
          Other...
        </Menu.Item>*/}
      </div>
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

ResourceTypeSelectorField.propTypes = {
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

export default ResourceTypeSelectorField;