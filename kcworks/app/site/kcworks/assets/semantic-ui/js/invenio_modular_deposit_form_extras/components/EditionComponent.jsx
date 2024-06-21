import React from "react";
import { CustomFieldInjector } from "@js/invenio_modular_deposit_form/field_components/CustomFieldInjector";

const EditionComponent = ({ ...extraProps }) => {
  return (
    <CustomFieldInjector
      sectionName="KCR Book information"
      fieldName="kcr:edition"
      idString="EditionField"
      description={""}
      label={"Edition or Version"}
      icon={"code branch"}
      placeholder={"e.g., 2nd revised"}
      {...extraProps}
    />
  );
};

export { EditionComponent };
