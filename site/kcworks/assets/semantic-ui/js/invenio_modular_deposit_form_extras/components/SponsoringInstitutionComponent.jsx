import React from "react";
import { CustomFieldInjector } from "@js/invenio_modular_deposit_form/field_components/CustomFieldInjector";

const SponsoringInstitutionComponent = ({ customFieldsUI, ...extraProps }) => {
  return (
    <CustomFieldInjector
      sectionName="KCR Book information"
      fieldName="kcr:sponsoring_institution"
      idString="SponsoringInstitutionField"
      customFieldsUI={customFieldsUI}
      description={""}
      icon={"group"}
      {...extraProps}
    />
  );
};

export { SponsoringInstitutionComponent };
