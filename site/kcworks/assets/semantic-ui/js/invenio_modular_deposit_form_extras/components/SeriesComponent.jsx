import React from "react";
import { CustomField } from "@js/invenio_modular_deposit_form/field_components/CustomField";

const SeriesComponent = ({ ...extraProps }) => {
  return (
    <CustomField
      uiConfigSectionName="Series"
      fieldName="kcr:book_series"
      idString="KcrBookSeries"
      icon="list"
      {...extraProps}
    />
  );
};

export { SeriesComponent };
