import React, { Component } from "react";

import { Input, Array } from "react-invenio-forms";
import { Grid, Form, Button, Icon } from "semantic-ui-react";

const newExperiment = {
  title: "",
  program: "",
};

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
        <Input
            fieldPath={`${fieldPath}.total_volumes`}
            label={total_volumes.label}
            icon={total_volumes.icon}
            placeholder={total_volumes.placeholder}
            description={total_volumes.description}
            width={width1 || 8}
        ></Input>
        <Input
            fieldPath={`${fieldPath}.volume`}
            label={volume.label}
            icon={volume.icon}
            placeholder={volume.placeholder}
            description={volume.description}
            width={width2 || 8}
        ></Input>
      </>
    );
}}