import React from "react";

import { TextField } from "@js/invenio_modular_deposit_form/replacement_components/input_controls/TextField";

const Volumes = ({
  classnames,
  fieldPath, // injected by the custom field loader via the `field` config property
  total_volumes,
  volume,
  icon1,
  icon2,
  description,
  helpText,
  label1,
  label2,
  width1,
  width2,
}) => {
  return (
    <>
      {description && <div className="description">{description}</div>}
      <TextField
        fieldPath={`${fieldPath}.total_volumes`}
        label={label1 || total_volumes.label}
        icon={icon1 || total_volumes.icon}
        placeholder={total_volumes.placeholder}
        description={total_volumes.description}
        helpText={total_volumes.helptext}
        width={width1 || 8}
        classnames={`${classnames} pl-0`}
      ></TextField>
      <TextField
        fieldPath={`${fieldPath}.volume`}
        label={label2 || volume.label}
        icon={icon2 || volume.icon}
        placeholder={volume.placeholder}
        description={volume.description}
        helpText={volume.helptext}
        width={width2 || 8}
        classnames={`${classnames} pr-0`}
      ></TextField>
      {helpText && <div className="helptext">{helpText}</div>}
    </>
  );
};

export { Volumes };
