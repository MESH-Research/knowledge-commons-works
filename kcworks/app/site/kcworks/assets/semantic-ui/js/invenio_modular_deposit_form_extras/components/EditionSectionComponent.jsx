import React from "react";
import { Segment } from "semantic-ui-react";
import { EditionComponent } from "./EditionComponent";
import { ChapterLabelComponent } from "./ChapterLabelComponent";

const EditionSectionComponent = () => {
  return (
    <>
      <EditionComponent />
      <ChapterLabelComponent />
    </>
  );
};

export { EditionSectionComponent };
