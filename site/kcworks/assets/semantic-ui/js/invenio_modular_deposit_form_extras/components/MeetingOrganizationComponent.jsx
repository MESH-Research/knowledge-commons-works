import React from "react";
import { CustomField } from "@js/invenio_modular_deposit_form/field_components/CustomField";

const MeetingOrganizationComponent = ({ ...extraProps }) => {
  return (
    <CustomField
      uiConfigSectionName="KCR Conference information"
      fieldName="kcr:meeting_organization"
      idString="MeetingOrganizationField"
      description=""
      icon="group"
      {...extraProps}
    />
  );
};

export { MeetingOrganizationComponent };
