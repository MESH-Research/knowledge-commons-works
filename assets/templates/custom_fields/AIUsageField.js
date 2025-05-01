import React, { useContext, useEffect } from "react";
import { i18next } from "@translations/i18next";
import { getIn, useFormikContext } from "formik";
import { Form } from "semantic-ui-react";
import { BooleanCheckbox, FieldLabel } from "react-invenio-forms";
import { TextArea } from "@js/invenio_modular_deposit_form/replacement_components/TextArea";
import PropTypes from "prop-types";

const AIUsageField = ({
  fieldPath,
  label,
  icon,
  description,
  helpText,
  ai_used,
  ai_description,
  ...restProps
}) => {
  const { values } = useFormikContext();

  return (
    <Form.Field id={fieldPath} name={fieldPath}>
      <FieldLabel htmlFor={fieldPath} icon={icon} label={label} />
      <BooleanCheckbox
        fieldPath={`${fieldPath}.ai_used`}
        label={ai_used.description}
        trueLabel="Yes"
        falseLabel="No"
        // icon={ai_used.icon}
        required={false}
        description=""
        value={getIn(values, `${fieldPath}.ai_used`, false)}
        initialValue={getIn(values, `${fieldPath}.ai_used`, false)}
      />
      {!!values.custom_fields
        ? values.custom_fields["kcr:ai_usage"]?.ai_used === true && (
            <TextArea
              fieldPath={`${fieldPath}.ai_description`}
              // label={ai_description.label}
              description={description}
              helpText={helpText}
              required={false}
              aria-describedby="ai-usage-textbox-description"
            />
          )
        : ""}
    </Form.Field>
  );
};

AIUsageField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string,
  icon: PropTypes.string,
  description: PropTypes.string,
  ai_used: PropTypes.object,
  ai_description: PropTypes.object,
};

export default AIUsageField;
