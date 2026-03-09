import React from "react";
import { i18next } from "@translations/kcworks/i18next";
import { CustomField } from "@js/invenio_modular_deposit_form/field_components/CustomField";

const ChapterLabelComponent = ({ ...extraProps }) => {
  return (
    <CustomField
      uiConfigSectionName="KCR Book information"
      fieldName="kcr:chapter_label"
      idString="ChapterLabelField"
      label={i18next.t("Chapter number/label")}
      description=""
      icon="tag"
      {...extraProps}
    />
  );
};

export { ChapterLabelComponent };
