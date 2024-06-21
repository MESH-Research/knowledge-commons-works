import React from "react";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import MultiInput from "@js/invenio_modular_deposit_form/replacement_components/MultiInput";

const UserDefinedTags = ({
      description,
      fieldPath, // injected by the custom field loader via the `field` config property
      helpText,
      icon,
      label = undefined,
      noQueryMessage,
      placeholder,
      tag,
      ...otherProps
    }) => {

    return (
      <MultiInput
        fieldPath={`${fieldPath}`}
        label={label}
        placeholder={placeholder}
        description={description}
        helpText={helpText}
        icon={icon}
        noQueryMessage={i18next.t("Type a keyword...")}
        {...otherProps}
      ></MultiInput>
    );
}

export { UserDefinedTags };