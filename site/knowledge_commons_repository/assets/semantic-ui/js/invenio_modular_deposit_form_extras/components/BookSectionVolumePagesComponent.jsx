import React from "react";
import { Segment, Form } from "semantic-ui-react";
import {
  SectionPagesComponent,
  TotalPagesComponent,
} from "@js/invenio_modular_deposit_form/field_components/field_components";
import { ChapterLabelComponent } from "./ChapterLabelComponent";

const BookSectionVolumePagesComponent = ({ customFieldsUI, labelMods }) => {
  return (
    <Segment as="fieldset">
      <Form.Group widths="equal">
        <SectionPagesComponent
          customFieldsUI={customFieldsUI}
          labelMods={labelMods}
        />
        <TotalPagesComponent
          customFieldsUI={customFieldsUI}
          description={""}
          labelMods={labelMods}
        />
        <ChapterLabelComponent
          customFieldsUI={customFieldsUI}
          labelMods={labelMods}
        />
      </Form.Group>
      <Form.Group widths="equal">
        <VolumeComponent customFieldsUI={customFieldsUI} />
      </Form.Group>
    </Segment>
  );
};

export { BookSectionVolumePagesComponent };
