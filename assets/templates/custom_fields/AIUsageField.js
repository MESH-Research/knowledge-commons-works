import React, { useEffect, useState } from "react";
import { i18next } from "@translations/i18next";
import { getIn, useFormikContext } from "formik";
import { Form } from "semantic-ui-react";
import { RadioField } from "react-invenio-forms";
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
  ai_description,
  ...restProps
}) => {
  const { values, setFieldValue } = useFormikContext();
  const usedValue = getIn(values, `${fieldPath}.ai_used`, false);
  const [usedAI, setUsedAI] = useState(usedValue);

  useEffect(() => {
    setFieldValue(`${fieldPath}.ai_used`, usedAI);
  }, [usedAI]);

  return (
    <Form.Field id={fieldPath} {...restProps}>
      <FieldLabel htmlFor={fieldPath} icon={icon} label={label} />
      <Form.Group role="radiogroup" aria-labelledby="ai-usage-toggle" className="inline mt-10">
        <label id="ai-usage-toggle" className="invenio-field-label ai-usage-toggle-label">
          {i18next.t(ai_used.description)}
        </label>
        <RadioField
          fieldPath={`${fieldPath}.ai_used`}
          checked={!!usedAI}
          className="rel-ml-2"
          label="Yes"
          name="ai-usage-toggle-yes"
          onChange={({ _, data }) => {
            setUsedAI(data.checked);
            {
              /* If we don't set ai_description to an empty value it can stay absent and miss validation. */
            }
            setFieldValue(
              `${fieldPath}.ai_description`,
              getIn(values, `${fieldPath}.ai_description`) ?? ""
            );
          }}
          value={true}
        />
        <RadioField
          fieldPath={`${fieldPath}.ai_used`}
          checked={!usedAI}
          className="rel-ml-2"
          label="No"
          name="ai-usage-toggle-no"
          onChange={({ _, data }) => {
            if (data.checked) {
              setUsedAI(false);
              setFieldValue(`${fieldPath}.ai_description`, "");
            }
          }}
          value={false}
        />
      </Form.Group>
      {!!usedAI ? (
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
  ai_used: PropTypes.object,
  ai_description: PropTypes.object,
};

export default AIUsageField;
