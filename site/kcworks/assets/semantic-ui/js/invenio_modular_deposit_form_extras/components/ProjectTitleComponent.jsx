import React from "react";
import { CustomField } from "@js/invenio_modular_deposit_form/field_components/CustomField";

const ProjectTitleComponent = ({ ...extraProps }) => {
  return (
    <CustomField
      uiConfigSectionName="Project"
      fieldName="kcr:project_title"
      idString="ProjectTitleField"
      description=""
      label="Project title"
      icon="briefcase"
      placeholder=""
      {...extraProps}
    />
  );
};

export { ProjectTitleComponent };
