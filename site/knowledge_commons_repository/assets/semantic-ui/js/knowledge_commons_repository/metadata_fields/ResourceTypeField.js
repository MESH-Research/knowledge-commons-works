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
import { FieldLabel, SelectField } from "react-invenio-forms";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { useFormikContext } from "formik";
import { FormValuesContext } from "../custom_deposit/custom_RDMDepositForm";
import { Icon, Menu } from "semantic-ui-react";

const ResourceTypeField = ({fieldPath,
                            label=i18next.t("Resource type"),
                            labelIcon="tag",
                            options,
                            labelclassname="field-label-class",
                            required=false,
                            ...restProps}) => {

  const [ otherToggleActive, setOtherToggleActive ] = useState(false);
  const { values, setFieldValue, initialValues } = useFormikContext();
  const selectedType = values[fieldPath];
  const { currentResourceType, handleValuesChange } = useContext(FormValuesContext);


  useEffect(() => {

  }, []);

  useEffect(() => {
    if ( currentResourceType !== values.metadata.resource_type ) {
      handleValuesChange(values);
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

  const handleItemClick = (event, { name }) => {
    setFieldValue("metadata.resource_type", name);
    setOtherToggleActive(false);
  }

  const handleOtherToggleClick = () => {
    setFieldValue("metadata.resource_type", null);
    setOtherToggleActive(true);
  }

  return (
    <>
      <FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} /><br />
      <Menu compact icon='labeled'>
        <Menu.Item
          name='textDocument-journalArticle'
          active={values.metadata.resource_type === 'textDocument-journalArticle'}
          onClick={handleItemClick}
        >
          <Icon name='file text' />
          Journal Article
        </Menu.Item>

        <Menu.Item
          name='textDocument-review'
          active={values.metadata.resource_type === 'textDocument-review'}
          onClick={handleItemClick}
        >
          <Icon name='thumbs up' />
          Review
        </Menu.Item>

        <Menu.Item
          name='textDocument-book'
          active={values.metadata.resource_type === 'textDocument-book'}
          onClick={handleItemClick}
        >
          <Icon name='book' />
          Book
        </Menu.Item>
        <Menu.Item
          name='textDocument-bookSection'
          active={values.metadata.resource_type === 'textDocument-bookSection'}
          onClick={handleItemClick}
        >
          <Icon name='book' />
          Book Section
        </Menu.Item>
        <Menu.Item
          name='instructionalResource-syllabus'
          active={values.metadata.resource_type === 'instructionalResource-syllabus'}
          onClick={handleItemClick}
        >
          <Icon name='graduation' />
          Syllabus
        </Menu.Item>
        <Menu.Item
          name='otherToggle'
          active={otherToggleActive === true}
          onClick={handleOtherToggleClick}
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