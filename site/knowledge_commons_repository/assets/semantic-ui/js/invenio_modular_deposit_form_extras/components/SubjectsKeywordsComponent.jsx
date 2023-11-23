import React from "react";
import { Segment } from "semantic-ui-react";
import { SubjectsComponent } from "@js/invenio_modular_deposit_form_extras/field_components/field_components";
import { KeywordsComponent } from "./KeywordsComponent";

const SubjectsKeywordsComponent = ({
  record,
  vocabularies,
  customFieldsUI,
}) => {
  return (
    <Segment as="fieldset" className="subject-keywords-fields">
      <SubjectsComponent record={record} vocabularies={vocabularies} />
      <KeywordsComponent customFieldsUI={customFieldsUI} />
    </Segment>
  );
};

export { SubjectsKeywordsComponent };
