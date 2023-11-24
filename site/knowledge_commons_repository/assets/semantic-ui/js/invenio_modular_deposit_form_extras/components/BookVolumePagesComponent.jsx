import React from "react";
import { Segment, Form } from "semantic-ui-react";
import { CustomFieldInjector } from "@js/invenio_modular_deposit_form/field_components/CustomFieldInjector";
import { VolumeComponent } from "./VolumeComponent";

const BookVolumePagesComponent = ({ customFieldsUI }) => {
  return (
    <Form.Group>
      <VolumeComponent customFieldsUI={customFieldsUI} />
      <CustomFieldInjector
        sectionName="Book / Report / Chapter"
        fieldName="imprint:imprint.pages"
        idString="ImprintPagesField"
        customFieldsUI={customFieldsUI}
        description={""}
        label="Total pages"
        icon="file outline"
      />
    </Form.Group>
  );
};

export { BookVolumePagesComponent };
