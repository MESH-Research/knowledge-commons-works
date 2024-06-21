import React from "react";
import { CustomFieldInjector } from "@js/invenio_modular_deposit_form/field_components/CustomFieldInjector";

const DegreeComponent = ({ ...extraProps }) => {
  return (
    <CustomFieldInjector
      sectionName="KCR thesis information"
      fieldName="kcr:degree"
      idString="DegreeField"
      description={""}
      {...extraProps}
    />
  );
};

export { DegreeComponent };
