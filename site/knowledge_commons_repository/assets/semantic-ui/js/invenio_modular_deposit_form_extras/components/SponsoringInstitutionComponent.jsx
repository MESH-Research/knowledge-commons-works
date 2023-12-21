import React from "react";
import { CustomFieldInjector } from "@js/invenio_modular_deposit_form/field_components/CustomFieldInjector";

const SponsoringInstitutionComponent = ({ customFieldsUI, ...extraProps }) => {
  return (
    <CustomFieldInjector
      sectionName="KCR Conference information"
      fieldName="kcr:sponsoring_institution"
      idString="SponsoringInstitutionField"
      customFieldsUI={customFieldsUI}
      description={""}
      {...extraProps}
    />
  );
};

export { SponsoringInstitutionComponent };
