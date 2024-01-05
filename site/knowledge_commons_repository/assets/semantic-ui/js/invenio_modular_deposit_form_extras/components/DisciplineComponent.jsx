import React from "react";
import { CustomFieldInjector } from "@js/invenio_modular_deposit_form/field_components/CustomFieldInjector";

const DisciplineComponent = ({ customFieldsUI, ...extraProps }) => {
  return (
    <CustomFieldInjector
      sectionName="KCR thesis information"
      fieldName="kcr:discipline"
      idString="DisciplineField"
      customFieldsUI={customFieldsUI}
      description={""}
      {...extraProps}
    />
  );
};

export { DisciplineComponent };
