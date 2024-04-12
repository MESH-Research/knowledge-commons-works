import React from "react";
import { CustomFieldInjector } from "@js/invenio_modular_deposit_form/field_components/CustomFieldInjector";

const EditionComponent = ({ customFieldsUI, ...extraProps }) => {
  return (
    <CustomFieldInjector
      sectionName="KCR Book information"
      fieldName="kcr:edition"
      idString="EditionField"
      customFieldsUI={customFieldsUI}
      description={""}
      label={"Edition or Version"}
      icon={"code branch"}
      placeholder={"e.g., 2nd revised"}
      {...extraProps}
    />
  );
};

export { EditionComponent };
