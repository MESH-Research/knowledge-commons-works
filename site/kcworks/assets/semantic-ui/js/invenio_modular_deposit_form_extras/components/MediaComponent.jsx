import React from "react";
import { CustomField } from "@js/invenio_modular_deposit_form/field_components/CustomField";

const MediaComponent = ({ ...extraProps }) => {
  return (
    <CustomField
      uiConfigSectionName="Media"
      fieldName="kcr:media"
      idString="KCRMediaField"
      label="Media and materials"
      icon="paint brush"
      placeholder="e.g., oil on canvas (press 'enter' to add each medium/material)"
      helpText=""
      description=""
      {...extraProps}
    />
  );
};

export { MediaComponent };
