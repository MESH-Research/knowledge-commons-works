import React from "react";
import { CustomField } from "@js/invenio_modular_deposit_form/field_components/CustomField";

const RemoteDataCollectionComponent = ({ ...extraProps }) => (
  <CustomField
    fieldName="kcr:remote_data_collection"
    idString="RemoteDataCollectionField"
    {...extraProps}
  />
);

export { RemoteDataCollectionComponent };
