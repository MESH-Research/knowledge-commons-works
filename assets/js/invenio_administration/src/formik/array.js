import React from "react";
import { Array } from "react-invenio-forms";
import { Form, Button, Icon } from "semantic-ui-react";
import { i18next } from "@translations/invenio_administration/i18next";
import PropTypes from "prop-types";

const createEmptyArrayRowObject = (properties) => {
  const emptyRow = {};
  for (let [key, schema] of Object.entries(properties)) {
    if (schema.type === "object" || schema.type === "vocabulary") {
      emptyRow[key] = createEmptyArrayRowObject(schema.properties);
    } else if (schema.type === "array") {
      emptyRow[key] = [createEmptyArrayRowObject(schema.items.properties)];
    } else {
      emptyRow[key] = "";
    }
  }
  return emptyRow;
};

export const AdminArrayField = ({
  fieldSchema,
  mapFormFields,
  isCreate,
  formFields,
  ...fieldProps
}) => {
  const newRow = createEmptyArrayRowObject(fieldSchema.items.properties);
  return (
    <Array
      defaultNewValue={newRow}
      className="array-widget"
      addButtonLabel={i18next.t("Add")}
      {...fieldProps}
    >
      {({ arrayHelpers, indexPath }) => {
        const fieldPathPrefix = `${fieldProps.fieldPath}.${indexPath}`;
        return (
          <Form.Group grouped widths="equal" className="group">
            {mapFormFields(
              fieldSchema.items.properties,
              fieldPathPrefix,
              isCreate,
              formFields
            )}
            <Form.Field>
              <Button
                aria-label={i18next.t("Remove field")}
                className="close-btn"
                icon
                onClick={() => arrayHelpers.remove(indexPath)}
              >
                <Icon name="close" />
              </Button>
            </Form.Field>
          </Form.Group>
        );
      }}
    </Array>
  );
};

AdminArrayField.propTypes = {
  fieldSchema: PropTypes.object.isRequired,
  mapFormFields: PropTypes.func.isRequired,
  isCreate: PropTypes.bool,
  formFields: PropTypes.object,
};

AdminArrayField.defaultProps = {
  isCreate: false,
  formFields: undefined,
};
