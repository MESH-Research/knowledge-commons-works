import React from "react";
import { CustomField } from "@js/invenio_modular_deposit_form/field_components/CustomField";

const InstitutionDepartmentComponent = ({ ...extraProps }) => (
  <CustomField
    fieldName="kcr:institution_department"
    idString="InstitutionDepartmentField"
    description=""
    icon=""
    {...extraProps}
  />
);

export { InstitutionDepartmentComponent };
