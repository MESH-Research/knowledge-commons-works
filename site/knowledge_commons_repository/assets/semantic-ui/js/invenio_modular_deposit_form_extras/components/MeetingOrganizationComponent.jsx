import React from "react";
import { CustomFieldInjector } from "@js/invenio_modular_deposit_form/field_components/CustomFieldInjector";

const MeetingOrganizationComponent = ({ customFieldsUI, ...extraProps }) => {
  return (
    <CustomFieldInjector
      sectionName="KCR Conference information"
      fieldName="kcr:meeting_organization"
      idString="MeetingOrganizationField"
      customFieldsUI={customFieldsUI}
      description={""}
      icon={"group"}
      {...extraProps}
    />
  );
};

export { MeetingOrganizationComponent };
