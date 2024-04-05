import React from "react";
import { CustomFieldInjector } from "@js/invenio_modular_deposit_form/field_components/CustomFieldInjector";

const ProjectTitleComponent = ({ customFieldsUI, ...extraProps }) => {
  return (
    <CustomFieldInjector
      sectionName="Project"
      fieldName="kcr:project_title"
      idString="ProjectTitleField"
      customFieldsUI={customFieldsUI}
      description={""}
      label={"Project title"}
      icon={"briefcase"}
      placeholder={""}
      {...extraProps}
    />
  );
};

export { ProjectTitleComponent };
