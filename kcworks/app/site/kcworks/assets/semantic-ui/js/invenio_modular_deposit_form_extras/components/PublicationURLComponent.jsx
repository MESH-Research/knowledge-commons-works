import React from "react";
import { CustomFieldInjector } from "@js/invenio_modular_deposit_form/field_components/CustomFieldInjector";

const PublicationURLComponent = ({ ...extraProps }) => {
  return (
    <CustomFieldInjector
      sectionName="KCR journal information"
      fieldName="kcr:publication_url"
      idString="PublicationURLField"
      description={""}
      icon={"linkify"}
      {...extraProps}
    />
  );
};

export { PublicationURLComponent };
