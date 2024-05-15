import React from "react";
import { CustomFieldInjector } from "@js/invenio_modular_deposit_form/field_components/CustomFieldInjector";

const VolumeComponent = ({ ...extraProps }) => {
  return (
    <CustomFieldInjector
      sectionName="KCR Book information"
      fieldName="kcr:volumes"
      idString="KcrVolumes"
      {...extraProps}
    />
  );
};

export { VolumeComponent };
