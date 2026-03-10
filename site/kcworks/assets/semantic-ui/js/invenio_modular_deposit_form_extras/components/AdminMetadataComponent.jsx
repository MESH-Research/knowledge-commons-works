import React from "react";
import { CustomField } from "@js/invenio_modular_deposit_form/field_components/CustomField";
import { useCustomFieldSectionName } from "@js/invenio_modular_deposit_form/hooks/useCustomFieldSectionName";

/**
 * Renders the Commons admin info custom fields (commons domain, submitter email,
 * submitter username). Uses CustomField so widget and props come from
 * custom_fields.ui (Commons admin info section).
 */
const AdminMetadataComponent = ({ ...extraProps }) => {
  const uiConfigSectionName = useCustomFieldSectionName(
    "AdminMetadataComponent",
    "Commons admin info"
  );
  return (
    <>
      <CustomField
        uiConfigSectionName={uiConfigSectionName}
        fieldName="kcr:commons_domain"
        idString="CommonsDomainField"
        description=""
        {...extraProps}
      />
      <CustomField
        uiConfigSectionName={uiConfigSectionName}
        fieldName="kcr:submitter_email"
        idString="SubmitterEmailField"
        description=""
        {...extraProps}
      />
      <CustomField
        uiConfigSectionName={uiConfigSectionName}
        fieldName="kcr:submitter_username"
        idString="SubmitterUsernameField"
        description=""
        {...extraProps}
      />
    </>
  );
};

export { AdminMetadataComponent };
