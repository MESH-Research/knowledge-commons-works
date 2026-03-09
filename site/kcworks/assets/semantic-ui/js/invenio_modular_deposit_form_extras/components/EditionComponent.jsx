import React from "react";
import { CustomField } from "@js/invenio_modular_deposit_form/field_components/CustomField";

const EditionComponent = ({ ...extraProps }) => {
  return (
    <CustomField
      uiConfigSectionName="KCR Book information"
      fieldName="kcr:edition"
      idString="EditionField"
      description=""
      label="Edition or Version"
      icon="code branch"
      placeholder="e.g., 2nd revised"
      {...extraProps}
    />
  );
};

export { EditionComponent };
