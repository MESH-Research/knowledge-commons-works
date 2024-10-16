import React from "react";
import { Segment } from "semantic-ui-react";
import { CustomFieldInjector } from "@js/invenio_modular_deposit_form/field_components/CustomFieldInjector";

const SeriesComponent = ({ ...extraProps }) => {
  return (
    <CustomFieldInjector
      sectionName="Series"
      fieldName="kcr:book_series"
      idString="KcrBookSeries"
      icon="list"
      {...extraProps}
    />
  );
};

export { SeriesComponent };
