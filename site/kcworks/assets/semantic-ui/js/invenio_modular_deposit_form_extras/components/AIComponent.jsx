import React from "react";
import { CustomField } from "@js/invenio_modular_deposit_form/field_components/CustomField";

const AIComponent = ({ ...extraProps }) => {
  return (
    <CustomField
      uiConfigSectionName="AI Usage"
      fieldName="kcr:ai_usage"
      idString="AIUsageField"
      {...extraProps}
    />
  );
};

export { AIComponent };
