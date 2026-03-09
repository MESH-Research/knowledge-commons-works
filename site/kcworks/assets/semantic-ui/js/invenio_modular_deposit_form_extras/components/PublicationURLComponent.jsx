import React from "react";
import { CustomField } from "@js/invenio_modular_deposit_form/field_components/CustomField";

const PublicationURLComponent = ({ ...extraProps }) => {
  return (
    <CustomField
      uiConfigSectionName="KCR journal information"
      fieldName="kcr:publication_url"
      idString="PublicationURLField"
      description=""
      icon="linkify"
      {...extraProps}
    />
  );
};

export { PublicationURLComponent };
