import React from "react";
import { CustomField } from "@js/invenio_modular_deposit_form/field_components/CustomField";

const KeywordsComponent = ({ ...extraProps }) => (
  <CustomField
    fieldName="kcr:user_defined_tags"
    idString="KCRKeywordsField"
    label="User-defined Keywords"
    noQueryMessage={" "}
    noResultsMessage={" "}
    {...extraProps}
  />
);

export { KeywordsComponent };
