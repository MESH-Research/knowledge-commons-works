import React from "react";
import { CustomFieldInjector } from "@js/invenio_modular_deposit_form/field_components/CustomFieldInjector";

const DegreeComponent = ({ customFieldsUI, ...extraProps }) => {
  return (
    <CustomFieldInjector
      sectionName="KCR thesis information"
      fieldName="kcr:degree"
      idString="DegreeField"
      customFieldsUI={customFieldsUI}
      description={""}
      {...extraProps}
    />
  );
};

export { DegreeComponent };
