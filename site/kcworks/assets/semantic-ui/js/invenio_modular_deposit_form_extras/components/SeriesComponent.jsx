import React from "react";
import { CustomField } from "@js/invenio_modular_deposit_form/field_components/CustomField";
import { useCustomFieldSectionName } from "@js/invenio_modular_deposit_form/hooks/useCustomFieldSectionName";

const SeriesComponent = ({ ...extraProps }) => {
  const uiConfigSectionName = useCustomFieldSectionName("SeriesComponent", "Series");
  return (
    <CustomField
      uiConfigSectionName={uiConfigSectionName}
      fieldName="kcr:book_series"
      idString="KcrBookSeries"
      icon="list"
      {...extraProps}
    />
  );
};

export { SeriesComponent };
