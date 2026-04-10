import React from "react";
import { CustomField } from "@js/invenio_modular_deposit_form/field_components/CustomField";

const DegreeComponent = ({ ...extraProps }) => (
  <CustomField
    fieldName="kcr:degree"
    idString="DegreeField"
    description=""
    {...extraProps}
  />
);

export { DegreeComponent };
