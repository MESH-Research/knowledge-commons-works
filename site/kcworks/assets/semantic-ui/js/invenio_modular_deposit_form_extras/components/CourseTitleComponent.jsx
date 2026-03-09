import React from "react";
import { CustomField } from "@js/invenio_modular_deposit_form/field_components/CustomField";

const CourseTitleComponent = ({ ...extraProps }) => {
  return (
    <CustomField
      uiConfigSectionName="Course"
      fieldName="kcr:course_title"
      idString="CourseTitleField"
      description=""
      {...extraProps}
    />
  );
};

export { CourseTitleComponent };
