import React from "react";
import { CustomFieldInjector } from "@js/invenio_modular_deposit_form/field_components/CustomFieldInjector"; 

export const RemoteDataCollectionComponent = ({ ...extraProps }) => {
  return (
    <CustomFieldInjector
      sectionName="Remote Data"
      fieldName="kcr:remote_data_collection"
      idString="RemoteDataCollectionField"
      {...extraProps}
    />
  );
};