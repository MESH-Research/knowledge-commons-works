import React from "react";
import { CustomField } from "@js/invenio_modular_deposit_form/field_components/CustomField";
import { useCustomFieldSectionName } from "@js/invenio_modular_deposit_form/hooks/useCustomFieldSectionName";

const CourseTitleComponent = ({ ...extraProps }) => {
  const uiConfigSectionName = useCustomFieldSectionName("CourseTitleComponent", "Course");
  return (
    <CustomField
      uiConfigSectionName={uiConfigSectionName}
      fieldName="kcr:course_title"
      idString="CourseTitleField"
      description=""
      {...extraProps}
    />
  );
};

export { CourseTitleComponent };
