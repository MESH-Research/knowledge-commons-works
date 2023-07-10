// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import PropTypes from "prop-types";
import React, { Component, useState, useEffect } from "react";
import {
  ArrayField,
  FieldLabel,
  GroupField,
  SelectField,
  TextField,
} from "react-invenio-forms";
import { Button, Form, Icon } from "semantic-ui-react";
import { i18next } from "@translations/invenio_rdm_records/i18next";
// import { emptyIdentifier } from "./initialValues";
import { FieldArray, Field, useFormikContext } from "formik";

const emptyIdentifier = {
  scheme: "",
  identifier: "",
};

const emptyURL = {
  scheme: "url",
  identifier: "",
};


/** Identifiers array component */
export const IdentifiersField = ({
  fieldPath,
  label,
  labelIcon,
  required,
  schemeOptions,
  showEmptyValue,
  description,
  placeholder
  }) => {
    const { values, submitForm } = useFormikContext();
    const addButtonLabel = i18next.t("Add identifier");
    const defaultNewValue = emptyIdentifier;
    console.log(values.metadata);
    return (
      <FieldArray
        name={fieldPath}
        className="invenio-array-field"
        render={arrayHelpers => (
          <>

            <Form.Field required={required}>
              <FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />
            </Form.Field>

            {values.metadata.identifiers.map(({scheme, identifier}, index) => {
              const fieldPathPrefix = `${fieldPath}.${index}`;
              const isUrl = (scheme==='url');
              const hasText = (!!identifier || identifier!=="");
              const hasScheme = (!!scheme || scheme!=="");
              return(
              <GroupField key={index} inline>
                <TextField
                  fieldPath={`${fieldPathPrefix}.identifier`}
                  label={i18next.t(!isUrl ? "Identifier" : "URL")}
                  required={!isUrl && hasScheme}
                  width={!!isUrl ? 14 : 9}
                />
                {schemeOptions && !isUrl && (
                  <SelectField
                    fieldPath={`${fieldPathPrefix}.scheme`}
                    label={i18next.t("Scheme")}
                    options={schemeOptions}
                    optimized
                    required={!isUrl && hasText}
                    width={5}
                  />
                )}
                {!schemeOptions && (
                  <TextField
                    fieldPath={`${fieldPathPrefix}.scheme`}
                    label={i18next.t("Scheme")}
                    required
                    width={5}
                  />
                )}
                <Form.Field>
                  <Button
                    aria-label={i18next.t("Remove field")}
                    className="close-btn"
                    icon="close"
                    onClick={() => arrayHelpers.remove(index)}
                  />
                </Form.Field>
                {description && (
                  <label className="helptext mb-0">{description}</label>
                )}
              </GroupField>
            )})}
            <Button
              type="button"
              onClick={() => arrayHelpers.push(emptyURL)}
              icon
              className="align-self-end"
              labelPosition="left"
            >
              <Icon name="add" />
              Add new URL
            </Button>
            <Button
              type="button"
              onClick={() => arrayHelpers.push(emptyIdentifier)}
              icon
              className="align-self-end"
              labelPosition="left"
            >
              <Icon name="add" />
              Add another identifier
            </Button>
          </>
        )}
      />
    )
}

      // <ArrayField
      //   addButtonLabel={i18next.t("Add identifier")}
      //   defaultNewValue={emptyIdentifier}
      //   fieldPath={fieldPath}
      //   label={<FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />}
      //   required={required}
      //   showEmptyValue={showEmptyValue}
      // >
      //   {({ arrayHelpers, indexPath }) => {
      //     const fieldPathPrefix = `${fieldPath}.${indexPath}`;
      //     return (
      //       <GroupField>
      //         <SelfAwareFormFields
      //           fieldPathPrefix={fieldPathPrefix}
      //           schemeOptions={schemeOptions}
      //           fieldPath={fieldPath}
      //           indexPath={indexPath}
      //         />
      //         {!schemeOptions && (
      //           <TextField
      //             fieldPath={`${fieldPathPrefix}.scheme`}
      //             label={i18next.t("Scheme")}
      //             required
      //             width={5}
      //           />
      //         )}
      //         <Form.Field>
      //           <Button
      //             aria-label={i18next.t("Remove field")}
      //             className="close-btn"
      //             icon="close"
      //             onClick={() => arrayHelpers.remove(indexPath)}
      //           />
      //         </Form.Field>
      //       </GroupField>
      //     );
      //   }}
      // </ArrayField>
//     );
//   }
// }

IdentifiersField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string,
  labelIcon: PropTypes.string,
  required: PropTypes.bool,
  schemeOptions: PropTypes.arrayOf(
    PropTypes.shape({
      text: PropTypes.string,
      value: PropTypes.string,
    })
  ),
  showEmptyValue: PropTypes.bool,
};

IdentifiersField.defaultProps = {
  label: i18next.t("Identifiers"),
  labelIcon: "barcode",
  required: false,
  schemeOptions: undefined,
  showEmptyValue: false,
};
