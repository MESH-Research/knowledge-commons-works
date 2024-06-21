import React from "react";
import { CustomFieldInjector } from "@js/invenio_modular_deposit_form/field_components/CustomFieldInjector";

const MeetingOrganizationComponent = ({ ...extraProps }) => {
  return (
    <CustomFieldInjector
      sectionName="KCR Conference information"
      fieldName="kcr:meeting_organization"
      idString="MeetingOrganizationField"
      description={""}
      icon={"group"}
      {...extraProps}
    />
  );
};

export { MeetingOrganizationComponent };
