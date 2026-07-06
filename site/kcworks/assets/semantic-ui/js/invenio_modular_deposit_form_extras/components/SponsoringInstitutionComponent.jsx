import React from "react";
import { CustomField } from "@js/invenio_modular_deposit_form/field_components/CustomField";

const SponsoringInstitutionComponent = ({ ...extraProps }) => (
  <CustomField
    fieldName="kcr:sponsoring_institution"
    idString="SponsoringInstitutionField"
    description=""
    icon="group"
    {...extraProps}
  />
);

export { SponsoringInstitutionComponent };
