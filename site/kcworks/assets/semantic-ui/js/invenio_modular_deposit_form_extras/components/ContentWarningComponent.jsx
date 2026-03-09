import React from "react";
import { CustomField } from "@js/invenio_modular_deposit_form/field_components/CustomField";

const ContentWarningComponent = ({ ...extraProps }) => {
  return (
    <CustomField
      uiConfigSectionName="Content warning"
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
