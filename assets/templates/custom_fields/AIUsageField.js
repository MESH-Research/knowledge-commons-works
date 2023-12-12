import React, { useContext, useEffect } from "react";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { useFormikContext } from "formik";
import { Form } from "semantic-ui-react";
import { BooleanCheckbox, FieldLabel, TextArea } from "react-invenio-forms";
// import { ResourceTypeContext } from "@js/invenio_modular_deposit_form/RDMDepositForm";
import { FormValuesContext } from "@js/invenio_modular_deposit_form";

const AIUsageField = ({
  fieldPath,
  label,
  icon,
  description,
  ai_used,
  ai_description,
  ...restProps
}) => {
  const { values, setFieldValue } = useFormikContext();
  const {
    currentValues,
    handleValuesChange,
    currentErrors,
    handleErrorsChange,
  } = useContext(FormValuesContext);

  useEffect(() => {
    setFieldValue(fieldPath, { ai_used: false, ai_description: "" });
    handleValuesChange(values);
  }, []);

  useEffect(() => {
    // console.log('changed');
    handleValuesChange(values);
    // console.log(values.custom_fields);
  }, [values]);

  return (
    <Form.Field id={fieldPath} name={fieldPath}>
      <FieldLabel htmlFor={fieldPath} icon={icon} label={label} />
      <BooleanCheckbox
        fieldPath={`${fieldPath}.ai_used`}
        // label="Did generative AI contribute to the production of this work?"
        label={ai_used.description}
        trueLabel="Yes"
        falseLabel="No"
        // icon={ai_used.icon}
        required={false}
        description=""
        value={""}
      />
      {!!values.custom_fields
        ? values.custom_fields["kcr:ai_usage"]?.ai_used === true && (
            <TextArea
              fieldPath={`${fieldPath}.ai_description`}
              // label={ai_description.label}
              description={ai_description.description}
              required={false}
              defaultNewValue={""}
            />
          )
        : ""}
    </Form.Field>
  );
};

export default AIUsageField;
