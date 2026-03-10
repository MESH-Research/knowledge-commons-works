import React from "react";
import { CustomField } from "@js/invenio_modular_deposit_form/field_components/CustomField";
import { useCustomFieldSectionName } from "@js/invenio_modular_deposit_form/hooks/useCustomFieldSectionName";

const ContentWarningComponent = ({ ...extraProps }) => {
  const uiConfigSectionName = useCustomFieldSectionName(
    "ContentWarningComponent",
    "Content warning"
  );
  return (
    <CustomField
      uiConfigSectionName={uiConfigSectionName}
      fieldName="kcr:content_warning"
      idString="ContentWarning"
      editorConfig={{
        removePlugins: [
          "Image",
          "ImageCaption",
          "ImageStyle",
          "ImageToolbar",
          "ImageUpload",
          "MediaEmbed",
          "Table",
          "TableToolbar",
          "TableProperties",
          "TableCellProperties",
        ],
      }}
      {...extraProps}
    />
  );
};

export { ContentWarningComponent };
