// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { useState, useEffect } from "react";
import { Button, Form, Icon } from "semantic-ui-react";
import PropTypes, { array } from "prop-types";
import { FieldLabel, SelectField } from "react-invenio-forms";
import _unickBy from "lodash/unionBy";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { TextField } from "@js/invenio_modular_deposit_form/replacement_components/TextField";
import { FieldArray, useFormikContext } from "formik";

const newIdentifier = { scheme: "", identifier: "" };

const idTypeData = {
  orcid: { text: "ORCID", value: "orcid", key: "orcid" },
  isni: { text: "ISNI", value: "isni", key: "isni" },
  gnd: { text: "GND", value: "gnd", key: "gnd" },
  ror: { text: "ROR", value: "ror", key: "ror" },
};

const CreatibutorsIdentifiers = ({
  fieldPath,
  label = i18next.t("Name identifiers"),
  placeholder = "",
  idTypes = ["orcid", "isni", "gnd", "ror"],
}) => {
  // const [selectedOptions, setSelectedOptions] = useState(initialOptions);

  const [identifiersLength, setIdentifiersLength] = useState(-1);
  const [haveChangedNumber, setHaveChangedNumber] = useState(false);

  // const { values, formikProps } = useFormikContext();
  // console.log("formikProps", formikProps);

  const handleAddNew = (arrayHelpers, newItem) => {
    setHaveChangedNumber(true);
    arrayHelpers.push(newItem);
    setIdentifiersLength(identifiersLength + 1);
  };

  const handleRemove = (arrayHelpers, index) => {
    setHaveChangedNumber(true);
    arrayHelpers.remove(index);
    setIdentifiersLength(identifiersLength - 1);
  };

  // const handleChange = ({ data, formikProps, index }) => {
  //   console.log("handleChange", { data, formikProps, index });
  // console.log("handleChange formikProps", formikProps);
  // const subField = formikProps.fieldPath.split(".")[2];
  // const newOptions = selectedOptions.map((option, i) =>
  //   i === index ? { ...option, [subField]: data.value } : option
  // );
  // console.log("newOptions", newOptions);
  // setSelectedOptions(newOptions);
  // formikProps.form.setFieldValue(formikProps.fieldPath, data.value);
  // };

  return (
    <>
      <FieldLabel htmlFor={`${fieldPath}`} label={label} />
      <FieldArray
        addButtonLabel={i18next.t("Add other titles")}
        name={fieldPath}
        className="creator-identifiers"
        render={(arrayHelpers) => (
          <>
            {arrayHelpers.form.values.person_or_org.identifiers?.map(
              (option, index) => {
                console.log("option", option);
                console.log("arrayHelpers", arrayHelpers);
                const fieldPathPrefix = `${fieldPath}.${index}`;
                console.log("fieldPathPrefix", fieldPathPrefix);
                return (
                  <Form.Group
                    key={index}
                    inline
                    className={`creatibutors-identifiers-item-row`}
                  >
                    <TextField
                      fieldPath={`${fieldPathPrefix}.identifier`}
                      name={`${fieldPathPrefix}.identifier`}
                      id={`${fieldPathPrefix}.identifier`}
                      label={""}
                      width={10}
                    />
                    <SelectField
                      fieldPath={`${fieldPathPrefix}.scheme`}
                      name={`${fieldPathPrefix}.scheme`}
                      id={`${fieldPathPrefix}.scheme`}
                      label={"Scheme"}
                      options={idTypes.map((option) => idTypeData[option])}
                      selection
                      selectOnBlur
                      optimized
                      width={4}
                    />
                    <Form.Field>
                      <Button
                        aria-label={i18next.t("Remove item")}
                        className="close-btn"
                        icon
                        onClick={() => handleRemove(arrayHelpers, index)}
                      >
                        <Icon name="close" />
                      </Button>
                    </Form.Field>
                  </Form.Group>
                );
              }
            )}

            <Button
              type="button"
              onClick={() => handleAddNew(arrayHelpers, newIdentifier)}
              icon
              className="align-self-end add-btn creatibutors-identifiers-add-button"
              labelPosition="left"
              id={`${fieldPath}.add-identifier-button`}
            >
              <Icon name="add" />
              Add identifier
            </Button>
          </>
        )}
      />
    </>
  );
};

CreatibutorsIdentifiers.propTypes = {
  initialOptions: PropTypes.arrayOf(
    PropTypes.shape({
      key: PropTypes.string.isRequired,
      text: PropTypes.string.isRequired,
      value: PropTypes.string.isRequired,
    })
  ).isRequired,
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string,
  placeholder: PropTypes.string,
};

export { CreatibutorsIdentifiers };
