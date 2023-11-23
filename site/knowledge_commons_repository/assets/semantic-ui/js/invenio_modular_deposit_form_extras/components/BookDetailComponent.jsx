import React from "react";
import { Form, Segment } from "semantic-ui-react";
import { CustomFieldInjector } from "@js/invenio_form/components";
import {
  BookTitleComponent,
  PublisherComponent,
  PublicationLocationComponent,
  TotalPagesComponent,
} from "@js/invenio_modular_deposit_form/field_components/field_components";
import { SeriesComponent } from "./SeriesComponent";

const BookDetailComponent = ({ customFieldsUI }) => {
  return (
    <Segment as="fieldset">
      {/* <FieldLabel htmlFor={"imprint:imprint"}
        icon={"book"}
        label={"Book details"}
      />
      <Divider fitted /> */}
      <Form.Group>
        <BookTitleComponent customFieldsUI={customFieldsUI} />
      </Form.Group>
      <Form.Group>
        <CustomFieldInjector
          sectionName="Book / Report / Chapter"
          fieldName="imprint:imprint.isbn"
          idString="ImprintISBNField"
          description=""
          customFieldsUI={customFieldsUI}
        />
        <VersionComponent description="" label="Edition or Version" icon="" />
      </Form.Group>
      <Form.Group>
        <PublisherComponent />
        <PublicationLocationComponent customFieldsUI={customFieldsUI} />
      </Form.Group>
      <Form.Group>
        <VolumeComponent customFieldsUI={customFieldsUI} />
      </Form.Group>
      <Form.Group>
        <TotalPagesComponent
          customFieldsUI={customFieldsUI}
          description={""}
          label="Number of Pages"
          icon="file outline"
        />
      </Form.Group>
      <Form.Group>
        <SeriesComponent customFieldsUI={customFieldsUI} />
      </Form.Group>
    </Segment>
  );
};

export { BookDetailComponent };
