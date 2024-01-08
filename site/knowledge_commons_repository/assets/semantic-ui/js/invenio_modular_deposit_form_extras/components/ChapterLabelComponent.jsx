import React from "react";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { CustomFieldInjector } from "@js/invenio_modular_deposit_form/field_components/CustomFieldInjector";

const ChapterLabelComponent = ({ customFieldsUI, ...extraProps }) => {
  return (
    <CustomFieldInjector
      sectionName="KCR Book information"
      fieldName="kcr:chapter_label"
      idString="ChapterLabelField"
      customFieldsUI={customFieldsUI}
      label={i18next.t("Chapter number/label")}
      description={""}
      icon="tag"
      {...extraProps}
    />
  );
};

export { ChapterLabelComponent };
