import React from "react";
import { Segment } from "semantic-ui-react";
import { CustomFieldSectionInjector } from "@js/invenio_modular_deposit_form/field_components/CustomFieldInjector";

const AdminMetadataComponent = ({ customFieldsUI, ...extraProps }) => {
  return (
    <CustomFieldSectionInjector
      sectionName="Commons admin info"
      idString="AdminMetadataFields"
      customFieldsUI={customFieldsUI}
      {...extraProps}
    />
  );
};

export { AdminMetadataComponent };
