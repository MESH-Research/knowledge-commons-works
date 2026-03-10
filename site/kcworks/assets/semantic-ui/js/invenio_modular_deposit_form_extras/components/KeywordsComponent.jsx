import React from "react";
import { CustomField } from "@js/invenio_modular_deposit_form/field_components/CustomField";
import { useCustomFieldSectionName } from "@js/invenio_modular_deposit_form/hooks/useCustomFieldSectionName";

const KeywordsComponent = ({ ...extraProps }) => {
  const uiConfigSectionName = useCustomFieldSectionName("KeywordsComponent", "Tags");
  return (
    <CustomField
      uiConfigSectionName={uiConfigSectionName}
      fieldName="kcr:user_defined_tags"
      idString="KCRKeywordsField"
      label="User-defined Keywords"
      noQueryMessage={" "}
      noResultsMessage={" "}
      {...extraProps}
    />
  );
};

export { KeywordsComponent };
