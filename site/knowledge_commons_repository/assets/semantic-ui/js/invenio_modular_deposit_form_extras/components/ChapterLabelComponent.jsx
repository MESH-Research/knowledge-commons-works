import React from "react";
import { CustomFieldInjector } from "@js/invenio_modular_deposit_form/field_components/CustomFieldInjector";

const ChapterLabelComponent = ({ customFieldsUI, labelMods }) => {
  const moddedLabel =
    labelMods && labelMods["custom_fields.kcr:chapter_label"]
      ? labelMods["custom_fields.kcr:chapter_label"]
      : "Chapter number/label";
  return (
    <CustomFieldInjector
      sectionName="KCR Book information"
      fieldName="kcr:chapter_label"
      idString="ChapterLabelField"
      customFieldsUI={customFieldsUI}
      label={moddedLabel}
      description={""}
      icon="tag"
    />
  );
};

export { ChapterLabelComponent };
