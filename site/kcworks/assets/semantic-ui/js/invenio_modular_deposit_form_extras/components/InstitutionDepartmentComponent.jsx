import React from "react";
import { CustomFieldInjector } from "@js/invenio_modular_deposit_form/field_components/CustomFieldInjector";

const InstitutionDepartmentComponent = ({ ...extraProps }) => {
  return (
    <CustomFieldInjector
      sectionName="KCR thesis information"
      fieldName="kcr:institution_department"
      idString="InstitutionDepartmentField"
      description={""}
      icon={""}
      {...extraProps}
    />
  );
};

export { InstitutionDepartmentComponent };
