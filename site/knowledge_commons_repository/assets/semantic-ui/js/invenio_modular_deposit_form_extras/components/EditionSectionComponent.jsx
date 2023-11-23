import React from "react";
import { Segment } from "semantic-ui-react";
import { EditionComponent } from "./EditionComponent";
import { ChapterLabelComponent } from "./ChapterLabelComponent";

const EditionSectionComponent = ({ customFieldsUI, labelMods }) => {
  return (
    <Segment as="fieldset">
      <EditionComponent customFieldsUI={customFieldsUI} labelMods={labelMods} />
      <ChapterLabelComponent
        customFieldsUI={customFieldsUI}
        labelMods={labelMods}
      />
    </Segment>
  );
};

export { EditionSectionComponent };
