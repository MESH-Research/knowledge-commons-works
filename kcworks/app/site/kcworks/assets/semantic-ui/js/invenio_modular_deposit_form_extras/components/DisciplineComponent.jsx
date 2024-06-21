import React from "react";
import { CustomFieldInjector } from "@js/invenio_modular_deposit_form/field_components/CustomFieldInjector";

const DisciplineComponent = ({ ...extraProps }) => {
  return (
    <CustomFieldInjector
      sectionName="KCR thesis information"
      fieldName="kcr:discipline"
      idString="DisciplineField"
      description={""}
      {...extraProps}
    />
  );
};

export { DisciplineComponent };
