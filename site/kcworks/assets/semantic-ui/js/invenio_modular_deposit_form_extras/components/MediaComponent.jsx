import React from "react";
import { CustomFieldInjector } from "@js/invenio_modular_deposit_form/field_components/CustomFieldInjector";

const MediaComponent = ({ customFieldsUI, ...extraProps }) => {
  return (
    <CustomFieldInjector
      sectionName="Media"
      label="Media and materials"
      fieldName="kcr:media"
      idString="KCRMediaField"
      customFieldsUI={customFieldsUI}
      icon={"paint brush"}
      placeholder={
        "e.g., oil on canvas (press 'enter' to add each medium/material)"
      }
      helpText={""}
      description={""}
      {...extraProps}
    />
  );
};

export { MediaComponent };
