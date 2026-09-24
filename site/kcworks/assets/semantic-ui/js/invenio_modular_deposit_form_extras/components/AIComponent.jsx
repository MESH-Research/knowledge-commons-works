import React from "react";
import { CustomField } from "@js/invenio_modular_deposit_form/field_components/CustomField";

const AIComponent = ({ ...extraProps }) => (
  <CustomField
    fieldName="kcr:ai_usage"
    idString="AIUsageField"
    {...extraProps}
  />
);

export { AIComponent };
