import React from "react";
import { CustomField } from "@js/invenio_modular_deposit_form/field_components/CustomField";

const MeetingOrganizationComponent = ({ ...extraProps }) => (
  <CustomField
    fieldName="kcr:meeting_organization"
    idString="MeetingOrganizationField"
    description=""
    icon="group"
    {...extraProps}
  />
);

export { MeetingOrganizationComponent };
