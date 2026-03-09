import React from "react";
import { CustomField } from "@js/invenio_modular_deposit_form/field_components/CustomField";

const SponsoringInstitutionComponent = ({ ...extraProps }) => {
  return (
    <CustomField
      uiConfigSectionName="KCR Book information"
      fieldName="kcr:sponsoring_institution"
      idString="SponsoringInstitutionField"
      description=""
      icon="group"
      {...extraProps}
    />
  );
};

export { SponsoringInstitutionComponent };
