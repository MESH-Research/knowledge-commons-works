import React from "react";
import { CustomField } from "@js/invenio_modular_deposit_form/field_components/CustomField";
import { useCustomFieldSectionName } from "@js/invenio_modular_deposit_form/hooks/useCustomFieldSectionName";

const ProjectTitleComponent = ({ ...extraProps }) => {
  const uiConfigSectionName = useCustomFieldSectionName(
    "ProjectTitleComponent",
    "Project"
  );
  return (
    <CustomField
      uiConfigSectionName={uiConfigSectionName}
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
