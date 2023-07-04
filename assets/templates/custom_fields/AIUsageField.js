import React, {useState} from "react";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { FastField } from "formik";
import { Form, Icon, Radio, } from "semantic-ui-react";
import { BooleanCheckbox, TextArea, BooleanField, FieldLabel } from "react-invenio-forms";

const AIUsageField = ({fieldPath,
                       label,
                       icon,
                       description,
                       ai_used,
                       ai_description,
                       ...restProps
                      }) => {
  const [ aiWasUsed, setAiWasUsed ] = useState(false);

  const handleChange = (e, value) => {
      console.log(`ai used? ${value}`);
      setAiWasUsed(value === "yes");
  };

  return (
    <>
    <BooleanCheckbox
      fieldPath={`${fieldPath}.ai_used`}
      // label="Did generative AI contribute to the production of this work?"
      label={ai_used.description}
      trueLabel="probably"
      falseLabel="no"
      // icon={ai_used.icon}
      required={false}
      description=""
      icon={ai_used.icon}
    />
    <TextArea
      fieldPath={`${fieldPath}.ai_description`}
      label={ai_description.label}
      description={ai_description.description}
      required={false}
    />
    </>
  );
}

export default AIUsageField;