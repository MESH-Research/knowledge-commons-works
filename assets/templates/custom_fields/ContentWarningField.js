import React, { useState } from "react";
import { i18next } from "@translations/i18next";
import { getIn, useFormikContext } from "formik";
import { Checkbox, Form } from "semantic-ui-react";
import { FieldLabel } from "react-invenio-forms";
import { TextArea } from "@js/invenio_modular_deposit_form/replacement_components/TextArea";

const ContentWarningField = ({
  fieldPath,
  label,
  icon,
  description = undefined,
  helpText = undefined,
  ...restProps
}) => {
  const { values, setFieldValue } = useFormikContext();
  const [haveWarning, setHaveWarning] = useState(!!getIn(values, fieldPath, false));

  return (
    <Form.Field id={fieldPath} name={fieldPath}>
      <FieldLabel htmlFor={fieldPath} icon={icon} label={label} />
      <Form.Group role="radiogroup" aria-labelledby="content-warning-toggle" className="inline">
        <label id="content-warning-toggle" className="invenio-field-label content-warning-toggle-label">{i18next.t("Do you want to add a content warning to this record?")}</label>
        <Checkbox
          radio
          label='Yes'
          name='content-warning-toggle-yes'
          onChange={(e, data) => setHaveWarning(data.checked)}
          checked={haveWarning}
        />
        <Checkbox
          radio
          label='No'
          name='content-warning-toggle-no'
          checked={!haveWarning}
          onChange={(e, data) => setHaveWarning(!data.checked)}
        />
      </Form.Group>
      {!!haveWarning && (
          <TextArea
            fieldPath={fieldPath}
            // label={ai_description.label}
            description={description}
            helpText={helpText}
            required={false}
            placeholder="Enter content warning here."
            aria-describedby="content-warning-textbox-description"
          />
        )
      }
    </Form.Field>
  );
};

export default ContentWarningField;
