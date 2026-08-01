import React from "react";
import { i18next } from "@translations/kcworks/i18next";
import { CustomField } from "@js/invenio_modular_deposit_form/field_components/CustomField";

const VolumeComponent = ({ ...extraProps }) => (
  <CustomField
    fieldName="kcr:volumes.volume"
    idString="KcrVolumeField"
    label={i18next.t("Volume")}
    description=""
    icon="book"
    {...extraProps}
  />
);

export { VolumeComponent };
