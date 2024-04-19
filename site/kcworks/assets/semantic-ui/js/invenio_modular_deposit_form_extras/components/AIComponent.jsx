import React from "react";
import { CustomFieldInjector } from "@js/invenio_modular_deposit_form/field_components/CustomFieldInjector";

const AIComponent = ({ ...extraProps }) => {
  return (
    <CustomFieldInjector
      sectionName="AI Usage"
      fieldName="kcr:ai_usage"
      idString="AIUsageField"
      {...extraProps}
    />
  );
};

export { AIComponent };
