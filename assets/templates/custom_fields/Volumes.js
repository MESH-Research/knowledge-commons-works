import React, { Component } from "react";

import { TextField } from "@js/invenio_modular_deposit_form/replacement_components/TextField";

export class Volumes extends Component {
  render() {
    const {
      fieldPath, // injected by the custom field loader via the `field` config property
      total_volumes,
      volume,
      icon,
      description,
      label,
      width1,
      width2
    } = this.props;

    return (
      <>
        <TextField
            fieldPath={`${fieldPath}.total_volumes`}
            label={total_volumes.label}
            icon={total_volumes.icon}
            placeholder={total_volumes.placeholder}
            description={total_volumes.description}
            helpText={total_volumes.helptext}
            width={width1 || 8}
        ></TextField>
        <TextField
            fieldPath={`${fieldPath}.volume`}
            label={volume.label}
            icon={volume.icon}
            placeholder={volume.placeholder}
            description={volume.description}
            helpText={volume.helptext}
            width={width2 || 8}
        ></TextField>
      </>
    );
}}