import React from "react";
import { CustomField } from "@js/invenio_modular_deposit_form/field_components/CustomField";

const DisciplineComponent = ({ ...extraProps }) => {
  return (
    <CustomField
      uiConfigSectionName="KCR thesis information"
      fieldName="kcr:discipline"
      idString="DisciplineField"
      description=""
      {...extraProps}
    />
  );
};

export { DisciplineComponent };
