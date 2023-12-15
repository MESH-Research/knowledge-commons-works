// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { useEffect, useState } from "react";
import PropTypes from "prop-types";

import {
  TextField,
  GroupField,
  ArrayField,
  FieldLabel,
  SelectField,
} from "react-invenio-forms";
import { Button, Form, Grid, Icon, Segment } from "semantic-ui-react";

// import { emptyRelatedWork } from "./initialValues";
import { ResourceTypeField } from "@js/invenio_rdm_records";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { FieldArray, useFormikContext } from "formik";

export const emptyRelatedWork = {
  scheme: "",
  identifier: "",
  resource_type: "",
  relation_type: "",
};

const RelatedWorksField = ({
  fieldPath,
  label = i18next.t("Related works"),
  labelIcon = "sitemap",
  required = false,
  options,
  showEmptyValue = false,
}) => {
  const { values, setFieldValue } = useFormikContext();
  const [relatedWorksLength, setRelatedWorksLength] = useState(-1);
  const [haveChangedNumber, setHaveChangedNumber] = useState(false);

  useEffect(() => {
    if (!!haveChangedNumber) {
      if (relatedWorksLength < 0) {
        document.getElementById(`${fieldPath}.add-button`)?.focus();
      } else {
        document
          .getElementById(`${fieldPath}.${relatedWorksLength}.relation_type`)
          ?.focus();
      }
    }
  }, [relatedWorksLength]);

  const handleAddNew = (arrayHelpers, newItem) => {
    setHaveChangedNumber(true);
    arrayHelpers.push(newItem);
    setRelatedWorksLength(relatedWorksLength + 1);
  };

  const handleRemove = (arrayHelpers, index) => {
    setHaveChangedNumber(true);
    arrayHelpers.remove(index);
    setRelatedWorksLength(relatedWorksLength - 1);
  };

  return (
    <FieldArray
      addButtonLabel={i18next.t("Add related work")}
      name={fieldPath}
      label={<FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />}
      required={required}
      render={(arrayHelpers) => (
        <>
          <FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />
          {values.metadata.related_identifiers.map(
            ({ relation_type, identifier, scheme, resource_type }, index) => {
              const fieldPathPrefix = `${fieldPath}.${index}`;
              return (
                <Segment
                  key={index}
                  fluid
                  className="additional-identifiers-item-row"
                >
                  <Form.Group>
                    <SelectField
                      clearable
                      fieldPath={`${fieldPathPrefix}.relation_type`}
                      label={i18next.t("Relation")}
                      optimized
                      options={options.relations}
                      placeholder={i18next.t("Select relation...")}
                      required
                      width={6}
                    />
                    <TextField
                      fieldPath={`${fieldPathPrefix}.identifier`}
                      label={i18next.t("Identifier")}
                      required
                      width={8}
                    />
                    <Form.Field>
                      <Button
                        aria-label={i18next.t("Remove field")}
                        className="close-btn"
                        icon
                        onClick={() => handleRemove(arrayHelpers, index)}
                        width={2}
                      >
                        <Icon name="close" />
                      </Button>
                    </Form.Field>
                  </Form.Group>
                  <Form.Group>
                    <SelectField
                      clearable
                      fieldPath={`${fieldPathPrefix}.scheme`}
                      label={i18next.t("Scheme")}
                      optimized
                      options={options.scheme}
                      required
                      width={8}
                    />
                    <ResourceTypeField
                      clearable
                      fieldPath={`${fieldPathPrefix}.resource_type`}
                      labelIcon="" // Otherwise breaks alignment
                      options={options.resource_type}
                      labelclassname="small field-label-class"
                      width={8}
                    />
                  </Form.Group>
                </Segment>
              );
            }
          )}
          <Button
            type="button"
            onClick={() => handleAddNew(arrayHelpers, emptyRelatedWork)}
            icon
            className="align-self-end add-btn"
            labelPosition="left"
            id={`${fieldPath}.add-button`}
          >
            <Icon name="add" />
            Add related work
          </Button>
          <label className="helptext" style={{ marginBottom: "10px" }}>
            {/* {i18next.t(
              "Specify identifiers of related works. Supported identifiers include DOI, Handle, ARK, PURL, ISSN, ISBN, PubMed ID, PubMed Central ID, ADS Bibliographic Code, arXiv, Life Science Identifiers (LSID), EAN-13, ISTC, URNs, and URLs."
            )} */}
          </label>
        </>
      )}
    />
  );
};

RelatedWorksField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string,
  labelIcon: PropTypes.string,
  required: PropTypes.bool,
  options: PropTypes.object.isRequired,
  showEmptyValue: PropTypes.bool,
};

export { RelatedWorksField };
