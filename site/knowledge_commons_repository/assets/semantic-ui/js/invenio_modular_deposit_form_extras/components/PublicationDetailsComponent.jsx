import React from "react";
import { Form, Segment } from "semantic-ui-react";
import { CustomFieldInjector } from "@js/invenio_modular_deposit_form/field_components/CustomFieldInjector";
import {
  PublisherComponent,
  PublicationLocationComponent,
} from "@js/invenio_modular_deposit_form/field_components/field_components";
import { EditionComponent } from "./EditionComponent";

const PublicationDetailsComponent = ({ customFieldsUI }) => {
  return (
    <>
      {/* <FieldLabel htmlFor={"imprint:imprint"}
          icon={"book"}
          label={"Publication Details"}
        /> */}
      {/* <Divider fitted /> */}
      <Form.Group widths="equal">
        <CustomFieldInjector
          sectionName="Book / Report / Chapter"
          fieldName="imprint:imprint.isbn"
          idString="ImprintISBNField"
          description="e.g. 0-06-251587-X"
          placeholder=""
          customFieldsUI={customFieldsUI}
        />
        <EditionComponent
          customFieldsUI={customFieldsUI}
          label="Edition or Version"
          icon="copy outline"
        />
        {/* <VersionComponent description="" */}
        {/* /> */}
      </Form.Group>
      <Form.Group widths="equal">
        <PublisherComponent />
        <PublicationLocationComponent customFieldsUI={customFieldsUI} />
      </Form.Group>
    </>
  );
};

export { PublicationDetailsComponent };
