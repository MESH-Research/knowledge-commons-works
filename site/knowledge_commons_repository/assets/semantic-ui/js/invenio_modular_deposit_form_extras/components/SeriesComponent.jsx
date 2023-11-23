import React from "react";
import { Segment } from "semantic-ui-react";
import { CustomFieldInjector } from "@js/invenio_modular_deposit_form/field_components/CustomFieldInjector";

const SeriesComponent = ({ customFieldsUI }) => {
  return (
    <Segment as="fieldset">
      <CustomFieldInjector
        sectionName="Series"
        fieldName="kcr:book_series"
        idString="KcrBookSeries"
        icon="list"
        customFieldsUI={customFieldsUI}
      />
    </Segment>
  );
};

export { SeriesComponent };
