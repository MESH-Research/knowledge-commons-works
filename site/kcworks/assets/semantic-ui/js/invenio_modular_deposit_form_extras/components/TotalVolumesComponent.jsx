import React from "react";
import { i18next } from "@translations/kcworks/i18next";
import { CustomField } from "@js/invenio_modular_deposit_form/field_components/CustomField";

const TotalVolumesComponent = ({ ...extraProps }) => (
  <CustomField
    fieldName="kcr:volumes.total_volumes"
    idString="KcrTotalVolumesField"
    label={i18next.t("Total volumes")}
    description=""
    icon="th"
    {...extraProps}
  />
);

export { TotalVolumesComponent };
