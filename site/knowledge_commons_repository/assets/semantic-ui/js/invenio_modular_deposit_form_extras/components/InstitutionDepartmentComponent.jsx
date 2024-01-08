import React from "react";
import { CustomFieldInjector } from "@js/invenio_modular_deposit_form/field_components/CustomFieldInjector";

const InstitutionDepartmentComponent = ({ customFieldsUI, ...extraProps }) => {
  return (
    <CustomFieldInjector
      sectionName="KCR thesis information"
      fieldName="kcr:institution_department"
      idString="InstitutionDepartmentField"
      customFieldsUI={customFieldsUI}
      description={""}
      icon={""}
      {...extraProps}
    />
  );
};

export { InstitutionDepartmentComponent };
