import React from "react";
import { CustomField } from "@js/invenio_modular_deposit_form/field_components/CustomField";

const KeywordsComponent = ({ ...extraProps }) => {
  return (
    <CustomField
      uiConfigSectionName="Tags"
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
