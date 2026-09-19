import React, { useEffect, useState } from "react";
import { i18next } from "@translations/i18next";
import { getIn, useFormikContext } from "formik";
import { Checkbox, Form } from "semantic-ui-react";
import { FieldLabel } from "@js/invenio_modular_deposit_form/replacement_components/input_controls/FieldLabel";
import { TextArea } from "@js/invenio_modular_deposit_form/replacement_components/input_controls/TextArea";
import PropTypes from "prop-types";

const AIUsageField = ({
  fieldPath,
  label,
  icon,
  description,
  helpText,
  ai_used,
}) => {
  const { values, setFieldValue } = useFormikContext();
  const usedValue = getIn(values, `${fieldPath}.ai_used`, false);
  const [usedAI, setUsedAI] = useState(!!usedValue);

  useEffect(() => {
    setUsedAI(!!usedValue);
  }, [usedValue]);

  return (
    <Form.Field id={fieldPath}>
      <FieldLabel htmlFor={fieldPath} icon={icon} label={label} />
      <Form.Group role="radiogroup" aria-labelledby="ai-usage-toggle" className="inline mt-10">
        <label id="ai-usage-toggle" className="invenio-field-label ai-usage-toggle-label">
          {i18next.t(ai_used.description)}
        </label>
        <Checkbox
          radio
          label="Yes"
          name="ai-usage-toggle-yes"
          checked={usedAI}
          className="rel-ml-2"
          onChange={(_, data) => {
            if (data.checked) {
              setUsedAI(true);
              setFieldValue(`${fieldPath}.ai_used`, true);
              setFieldValue(
                `${fieldPath}.ai_description`,
                getIn(values, `${fieldPath}.ai_description`) ?? ""
              );
            }
          }}
        />
        <Checkbox
          radio
          label="No"
          name="ai-usage-toggle-no"
          checked={!usedAI}
          className="rel-ml-2"
          onChange={(_, data) => {
            if (data.checked) {
              setUsedAI(false);
              setFieldValue(`${fieldPath}.ai_used`, false);
              setFieldValue(`${fieldPath}.ai_description`, "");
            }
          }}
        />
      </Form.Group>
      {usedAI ? (
        <TextArea
          classnames="rel-mt-1"
          fieldPath={`${fieldPath}.ai_description`}
          description={description}
          helpText={helpText}
          required={false}
          placeholder="Describe your use of AI here."
          aria-describedby="ai-usage-textbox-description"
        />
      ) : null}
    </Form.Field>
  );
};

AIUsageField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string,
  icon: PropTypes.string,
  description: PropTypes.string,
  helpText: PropTypes.string,
  ai_used: PropTypes.object,
  ai_description: PropTypes.object,
};

export default AIUsageField;
