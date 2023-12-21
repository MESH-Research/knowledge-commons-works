import React from "react";
import { CustomFieldInjector } from "@js/invenio_modular_deposit_form/field_components/CustomFieldInjector";

const VolumeComponent = ({ customFieldsUI, ...extraProps }) => {
  return (
    <CustomFieldInjector
      sectionName="KCR Book information"
      fieldName="kcr:volumes"
      idString="KcrVolumes"
      customFieldsUI={customFieldsUI}
      {...extraProps}
    />
  );
};

export { VolumeComponent };
