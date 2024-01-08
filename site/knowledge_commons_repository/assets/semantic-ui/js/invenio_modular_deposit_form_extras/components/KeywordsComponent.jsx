import React from "react";
import { CustomFieldInjector } from "@js/invenio_modular_deposit_form/field_components/CustomFieldInjector";

const KeywordsComponent = ({ customFieldsUI, ...extraProps }) => {
  return (
    <CustomFieldInjector
      sectionName="Tags"
      label="User-defined Keywords"
      fieldName="kcr:user_defined_tags"
      idString="KCRKeywordsField"
      customFieldsUI={customFieldsUI}
      {...extraProps}
    />
  );
};

export { KeywordsComponent };
