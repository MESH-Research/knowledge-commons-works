import React from "react";
import { Segment } from "semantic-ui-react";
import { SubjectsComponent } from "@js/invenio_modular_deposit_form/field_components/field_components";
import { KeywordsComponent } from "./KeywordsComponent";

const SubjectsKeywordsComponent = ({
  record,
  vocabularies,
  customFieldsUI,
}) => {
  return (
    <>
      <SubjectsComponent
        record={record}
        vocabularies={vocabularies}
        description=""
      />
      <KeywordsComponent customFieldsUI={customFieldsUI} />
    </>
  );
};

export { SubjectsKeywordsComponent };
