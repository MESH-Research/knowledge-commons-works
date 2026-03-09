import React from "react";
import { CustomField } from "@js/invenio_modular_deposit_form/field_components/CustomField";

const VolumeComponent = ({ ...extraProps }) => {
  return (
    <CustomField
      uiConfigSectionName="KCR Book information"
      fieldName="kcr:volumes"
      idString="KcrVolumes"
      {...extraProps}
    />
  );
};

export { VolumeComponent };
