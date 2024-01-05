import React from "react";
import { CustomFieldInjector } from "@js/invenio_modular_deposit_form/field_components/CustomFieldInjector";

const CourseTitleComponent = ({ customFieldsUI, ...extraProps }) => {
  return (
    <CustomFieldInjector
      sectionName="Course"
      fieldName="kcr:course_title"
      idString="CourseTitleField"
      customFieldsUI={customFieldsUI}
      description={""}
      {...extraProps}
    />
  );
};

export { CourseTitleComponent };
