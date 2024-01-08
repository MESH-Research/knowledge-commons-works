import React, { useContext, useEffect } from "react";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { getIn, useFormikContext } from "formik";
import { Form } from "semantic-ui-react";
import { BooleanCheckbox, FieldLabel } from "react-invenio-forms";
import { FormValuesContext } from "@js/invenio_modular_deposit_form";
import { TextArea } from "@js/invenio_modular_deposit_form/replacement_components/TextArea";

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

  // useEffect(() => {
  //   // setFieldValue(fieldPath, { ai_used: false, ai_description: "" });
  // }, []);

  // useEffect(() => {
  //   // console.log('changed');
  //   handleValuesChange(values);
  //   // console.log(values.custom_fields);
  // }, [values]);
  console.log("AI field", getIn(values, `${fieldPath}`, undefined));

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
        // value={values.custom_fields?.["kcr:ai_usage"]?.ai_used}
        value={getIn(values, `${fieldPath}.ai_used`, false)}
        initialValue={getIn(values, `${fieldPath}.ai_used`, false)}
      />
      {!!values.custom_fields
        ? values.custom_fields["kcr:ai_usage"]?.ai_used === true && (
            <TextArea
              fieldPath={`${fieldPath}.ai_description`}
              // label={ai_description.label}
              description={ai_description.description}
              required={false}
            />
          )
        : ""}
    </Form.Field>
  );
};

export default AIUsageField;
