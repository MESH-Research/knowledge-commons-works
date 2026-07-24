import React, { useEffect, useState } from "react";
import { i18next } from "@translations/i18next";
import { getIn, useFormikContext } from "formik";
import { Checkbox, Form } from "semantic-ui-react";
import { FieldLabel } from "react-invenio-forms";
import { TextArea } from "@js/invenio_modular_deposit_form/replacement_components/input_controls/TextArea";

const ContentWarningField = ({
  fieldPath,
  label,
  icon,
  description = undefined,
  helpText = undefined,
  ...restProps
}) => {
  const { values, setFieldValue } = useFormikContext();
  const warningValue = getIn(values, fieldPath, false);
  const [haveWarning, setHaveWarning] = useState(!!warningValue);

  // After localStorage recovery, Formik is reset with a restored string while
  // this component may already be mounted with haveWarning=false. Sync only
  // when a truthy value appears so "Yes" + empty textarea still works.
  useEffect(() => {
    if (warningValue) {
      setHaveWarning(true);
    }
  }, [warningValue]);

  return (
    <Form.Field id={fieldPath} name={fieldPath} {...restProps}>
      <FieldLabel htmlFor={fieldPath} icon={icon} label={label} />
      <Form.Group role="radiogroup" aria-labelledby="content-warning-toggle" className="inline">
        <label
          id="content-warning-toggle"
          className="invenio-field-label content-warning-toggle-label"
        >
          {i18next.t("Do you want to add a content warning to this record?")}
        </label>
        <Checkbox
          radio
          label="Yes"
          name="content-warning-toggle-yes"
          onChange={(_, data) => setHaveWarning(data.checked)}
          checked={haveWarning}
          className="rel-ml-2"
        />
        <Checkbox
          radio
          label="No"
          name="content-warning-toggle-no"
          checked={!haveWarning}
          onChange={(_, data) => {
            if (data.checked) {
              setHaveWarning(false);
              setFieldValue(fieldPath, "");
            }
          }}
          className="rel-ml-2"
        />
      </Form.Group>
      {!!haveWarning && (
        <TextArea
          fieldPath={fieldPath}
          description={description}
          helpText={helpText}
          required={false}
          placeholder="Enter content warning here."
          aria-describedby="content-warning-textbox-description"
        />
      )}
    </Form.Field>
  );
};

export default ContentWarningField;
