import React from "react";
import { CustomFieldInjector } from "@js/invenio_modular_deposit_form/field_components/CustomFieldInjector";

const ContentWarningComponent = ({ ...extraProps }) => {
  return (
    <CustomFieldInjector
      fieldName="kcr:content_warning"
      sectionName="Content warning"
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
