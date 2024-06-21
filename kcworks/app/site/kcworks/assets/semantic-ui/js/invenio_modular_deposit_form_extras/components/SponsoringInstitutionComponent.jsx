import React from "react";
import { CustomFieldInjector } from "@js/invenio_modular_deposit_form/field_components/CustomFieldInjector";

const SponsoringInstitutionComponent = ({ ...extraProps }) => {
  return (
    <CustomFieldInjector
      sectionName="KCR Book information"
      fieldName="kcr:sponsoring_institution"
      idString="SponsoringInstitutionField"
      description={""}
      icon={"group"}
      {...extraProps}
    />
  );
};

export { SponsoringInstitutionComponent };
