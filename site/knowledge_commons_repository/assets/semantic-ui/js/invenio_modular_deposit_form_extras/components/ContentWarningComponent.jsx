import React from "react";
import { Segment } from "semantic-ui-react";
import { CustomFieldInjector } from "@js/invenio_modular_deposit_form/field_components/CustomFieldInjector";

const ContentWarningComponent = ({ customFieldsUI }) => {
  return (
    <Segment as="fieldset">
      <CustomFieldInjector
        fieldName="kcr:content_warning"
        sectionName="Content warning"
        idString="ContentWarning"
        customFieldsUI={customFieldsUI}
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
      />
    </Segment>
  );
};

export { ContentWarningComponent };
