import React from "react";
import {
  Input,
  AutocompleteDropdown,
  BooleanField,
  Dropdown,
  TextArea,
} from "react-invenio-forms";
import _capitalize from "lodash/capitalize";
import PropTypes from "prop-types";
import { Form, Segment, Header } from "semantic-ui-react";
import { AdminArrayField } from "./array";
import _isEmpty from "lodash/isEmpty";
import { sortFields } from "../components/utils";

const fieldsMap = {
  string: Input,
  integer: Input,
  uuid: Input,
  datetime: Input,
  bool: BooleanField,
};

const generateFieldProps = (
  fieldName,
  fieldSchema,
  parentField,
  isCreate,
  formFieldConfig
) => {
  let currentFieldName;

  const fieldLabel = formFieldConfig?.text || fieldSchema?.title || fieldName;
  const placeholder =
    formFieldConfig?.placeholder || fieldSchema?.metadata?.placeholder;

  if (parentField) {
    currentFieldName = `${parentField}.${fieldName}`;
  } else {
    currentFieldName = fieldName;
  }

  const htmlDescription = (
    <>
      <p />
      <div
        dangerouslySetInnerHTML={{
          __html: formFieldConfig?.description || fieldSchema?.metadata?.description,
        }}
      />
    </>
  );

  return {
    fieldPath: currentFieldName,
    key: currentFieldName,
    label: _capitalize(fieldLabel),
    description: htmlDescription,
    required: fieldSchema.required,
    disabled: fieldSchema.readOnly || (fieldSchema.createOnly && !isCreate),
    placeholder,
    options: formFieldConfig?.options || fieldSchema?.metadata?.options,
    rows: formFieldConfig?.rows || fieldSchema?.metadata?.rows,
  };
};

const mapFormFields = (obj, parentField, isCreate, formFieldsConfig, dropDumpOnly) => {
  if (!obj) {
    return null;
  }

  const sortedFields = sortFields(obj);

  const elements = Object.entries(sortedFields).map(([fieldName, fieldSchema]) => {
    if (fieldSchema.readOnly && dropDumpOnly) {
      return null;
    }

    const fieldProps = generateFieldProps(
      fieldName,
      fieldSchema,
      parentField,
      isCreate,
      formFieldsConfig[fieldName]
    );

    const showField =
      _isEmpty(formFieldsConfig) ||
      Object.prototype.hasOwnProperty.call(formFieldsConfig, fieldProps.fieldPath);

    if (!showField) {
      return null;
    }

    if (fieldSchema.type === "array") {
      return (
        <AdminArrayField
          key={fieldProps.fieldPath}
          fieldSchema={fieldSchema}
          isCreate={isCreate}
          mapFormFields={mapFormFields}
          formFields={formFieldsConfig}
          {...fieldProps}
        />
      );
    }

    if (fieldSchema.type === "bool") {
      const description = fieldProps.description;
      return (
        <>
          <BooleanField
            key={fieldProps.fieldPath}
            required={fieldSchema.required}
            {...fieldProps}
          />
          {description && <label className="helptext">{description}</label>}
        </>
      );
    }

    if (fieldSchema.type === "vocabulary") {
      return (
        <AutocompleteDropdown
          key={fieldProps.fieldPath}
          required={fieldSchema.required}
          autocompleteFrom={`/api/vocabularies/${fieldSchema.metadata.type}`}
          {...fieldProps}
        />
      );
    }

    if (fieldSchema.type === "object") {
      // nested fields
      return (
        <React.Fragment key={fieldProps.fieldPath}>
          <Header attached="top" as="h5">
            {fieldProps.label}
          </Header>
          <Segment attached="bottom">
            <Form.Group grouped>
              {mapFormFields(
                fieldSchema.properties,
                fieldProps.fieldPath,
                isCreate,
                formFieldsConfig
              )}
            </Form.Group>
          </Segment>
        </React.Fragment>
      );
    }

    const dropdownOptions =
      formFieldsConfig[fieldName]?.options || fieldSchema?.metadata?.options;
    if (fieldSchema.type === "string" && dropdownOptions) {
      return (
        <Dropdown
          key={fieldProps.fieldPath}
          required={fieldSchema.required}
          options={dropdownOptions}
          {...fieldProps}
        />
      );
    }

    const rows = formFieldsConfig[fieldName]?.rows || fieldSchema?.metadata?.rows;
    if (fieldSchema.type === "string" && rows) {
      return (
        <TextArea
          key={fieldProps.fieldPath}
          fieldPath={fieldProps.fieldPath}
          rows={rows}
          {...fieldProps}
        />
      );
    }

    const Element = fieldsMap[fieldSchema.type];
    return <Element {...fieldProps} key={fieldProps.fieldPath} />;
  });

  return elements;
};

export const GenerateForm = ({ jsonSchema, create, formFields, dropDumpOnly }) => {
  const properties = jsonSchema;
  return <>{mapFormFields(properties, undefined, create, formFields, dropDumpOnly)}</>;
};

GenerateForm.propTypes = {
  jsonSchema: PropTypes.object.isRequired,
  create: PropTypes.bool,
  formFields: PropTypes.object,
  dropDumpOnly: PropTypes.bool,
};

GenerateForm.defaultProps = {
  create: false,
  formFields: undefined,
  dropDumpOnly: false,
};
