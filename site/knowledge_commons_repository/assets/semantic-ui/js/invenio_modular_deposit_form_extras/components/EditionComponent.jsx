import React from "react";
import { CustomFieldInjector } from "@js/invenio_modular_deposit_form/field_components/CustomFieldInjector";

const EditionComponent = ({ customFieldsUI }) => {
  return (
    <CustomFieldInjector
      sectionName="KCR Book info"
      fieldName="kcr:edition"
      idString="EditionField"
      customFieldsUI={customFieldsUI}
      description={""}
    />
  );
};

export { EditionComponent };
