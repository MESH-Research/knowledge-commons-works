import React from "react";
import { CustomFieldInjector } from "@js/invenio_modular_deposit_form/field_components/CustomFieldInjector";

const AIComponent = ({ customFieldsUI, ...extraProps }) => {
  // const sectionConfig = customFieldsUI.find(item => item.section === "AI Usage");
  // const fieldConfig = sectionConfig.find(item => item.field === "ai_used");
  return (
    <CustomFieldInjector
      sectionName="AI Usage"
      fieldName="kcr:ai_usage"
      idString="AIUsageField"
      customFieldsUI={customFieldsUI}
      {...extraProps}
    />
  );
};

export { AIComponent };
