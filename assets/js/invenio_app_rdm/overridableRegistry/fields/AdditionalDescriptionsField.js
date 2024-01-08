// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021      Graz University of Technology.
// Copyright (C) 2022      TU Wien.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { useState, useLayoutEffect, Fragment } from "react";
import PropTypes from "prop-types";
import { Button, Form, Icon } from "semantic-ui-react";

import { SelectField } from "react-invenio-forms";
// import { emptyAdditionalDescription } from "./initialValues";
import { LanguagesField } from "@js/invenio_rdm_records";
import { i18next } from "@translations/invenio_rdm_records/i18next";
// import { sortOptions } from "../../../utils";
import { FieldArray, useFormikContext } from "formik";
import { TextArea } from "@js/invenio_modular_deposit_form/replacement_components/TextArea";

const emptyAdditionalDescription = {
  lang: "",
  description: "",
  type: "",
};

/**
 * Sort a list of string values (options).
 * @param {list} options
 * @returns
 */
function sortOptions(options) {
  return options.sort((o1, o2) => o1.text.localeCompare(o2.text));
}

const AdditionalDescriptionsField = ({
  fieldPath,
  options,
  recordUI = {},
  editorConfig = undefined,
}) => {
  const { values } = useFormikContext();
  const [descriptionsLength, setDescriptionsLength] = useState(-1);
  const [haveChangedNumber, setHaveChangedNumber] = useState(false);
  const fieldPathSanitized = fieldPath.replace(/\./g, "-");
  const textFieldRef = React.createRef();

  useLayoutEffect(() => {
    if (!!haveChangedNumber) {
      if (descriptionsLength < 0) {
        document.getElementById(`${fieldPath}.add-button`)?.focus();
      } else {
        window.setTimeout(() => {
          const nodes = document.querySelectorAll(
            ".additional-description-item-row textarea"
          );
          nodes[nodes.length - 1].focus();
        }, 100);
      }
    }
  }, [descriptionsLength]);

  const handleAddNew = (arrayHelpers, newItem) => {
    setHaveChangedNumber(true);
    arrayHelpers.push(newItem);
    setDescriptionsLength(descriptionsLength + 1);
  };

  const handleRemove = (arrayHelpers, index) => {
    setHaveChangedNumber(true);
    arrayHelpers.remove(index);
    setDescriptionsLength(descriptionsLength - 1);
  };

  return (
    <FieldArray
      addButtonLabel={i18next.t("Add another description")}
      defaultNewValue={emptyAdditionalDescription}
      name={fieldPath}
      className="additional-descriptions"
      render={(arrayHelpers) => (
        <>
          {values.metadata.additional_descriptions.map((value, index) => {
            const fieldPathPrefix = `${fieldPath}.${index}`;
            const fieldPathPrefixSanitized = `${fieldPathSanitized}-${index}`;

            return (
              <div key={index} className="additional-description-wrapper">
                <Form.Group className="additional-description-item-row sixteen wide">
                  <TextArea
                    fieldPath={`${fieldPathPrefix}.description`}
                    id={`${fieldPathPrefix}.description`}
                    label={i18next.t("Additional description")}
                    editorConfig={editorConfig}
                    optimized
                    required
                    classnames={`fourteen wide tablet sixteen wide mobile twelve wide computer ${fieldPathPrefixSanitized}-description`}
                    ref={textFieldRef}
                  />
                  <Form.Field className="mobile hidden two wide">
                    <Button
                      aria-label={i18next.t("remove field")}
                      className="close-btn"
                      floated="right"
                      icon
                      onClick={() => handleRemove(arrayHelpers, index)}
                    >
                      <Icon name="close" />
                    </Button>
                  </Form.Field>
                </Form.Group>
                <Form.Group className="sixteen wide equal widths">
                  <SelectField
                    fieldPath={`${fieldPathPrefix}.type`}
                    id={`${fieldPathPrefix}.type`}
                    label={i18next.t("Type of description")}
                    options={sortOptions(options.type)}
                    required
                    optimized
                    search={true}
                  />
                  <LanguagesField
                    serializeSuggestions={(suggestions) =>
                      suggestions.map((item) => ({
                        text: item.title_l10n,
                        value: item.id,
                        fieldPathPrefix: item.id,
                      }))
                    }
                    initialOptions={
                      recordUI?.additional_descriptions &&
                      recordUI.additional_descriptions[index]?.lang
                        ? [recordUI.additional_descriptions[index].lang]
                        : []
                    }
                    fieldPath={`${fieldPathPrefix}.lang`}
                    id={`${fieldPathPrefix}.lang`}
                    label={i18next.t("Language")}
                    multiple={false}
                    placeholder={i18next.t("select language")}
                    labelIcon=""
                    clearable
                    selectOnBlur={false}
                  />
                  <Form.Field
                    tablet={2}
                    computer={2}
                    mobile={0}
                    className="tablet computer only two wide"
                  />
                  <Form.Field
                    tablet={0}
                    computer={0}
                    mobile={2}
                    className="mobile only two wide"
                  >
                    <Button
                      aria-label={i18next.t("remove field")}
                      className="close-btn"
                      floated="right"
                      icon
                      onClick={() => handleRemove(arrayHelpers, index)}
                    >
                      <Icon name="close" />
                    </Button>
                  </Form.Field>
                </Form.Group>
              </div>
            );
          })}
          <Button
            type="button"
            onClick={() =>
              handleAddNew(arrayHelpers, emptyAdditionalDescription)
            }
            icon
            className="align-self-end add-btn"
            labelPosition="left"
            id={`${fieldPath}.add-button`}
          >
            <Icon name="add" />
            Add another description
          </Button>
        </>
      )}
    />
  );
};

AdditionalDescriptionsField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  options: PropTypes.shape({
    type: PropTypes.arrayOf(
      PropTypes.shape({
        icon: PropTypes.string,
        text: PropTypes.string,
        value: PropTypes.string,
      })
    ),
    lang: PropTypes.arrayOf(
      PropTypes.shape({
        text: PropTypes.string,
        value: PropTypes.string,
      })
    ),
  }).isRequired,
  recordUI: PropTypes.object,
  editorConfig: PropTypes.object,
};

export { AdditionalDescriptionsField };
