import React from "react";
import { CustomField } from "@js/invenio_modular_deposit_form/field_components/CustomField";

const InstitutionDepartmentComponent = ({ ...extraProps }) => {
  return (
    <CustomField
      uiConfigSectionName="KCR thesis information"
      fieldName="kcr:institution_department"
      idString="InstitutionDepartmentField"
      description=""
      icon=""
      {...extraProps}
    />
  );
};

export { InstitutionDepartmentComponent };
