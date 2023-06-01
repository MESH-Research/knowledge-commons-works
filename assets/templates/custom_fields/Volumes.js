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
    } = this.props;

    return (
        <Grid>
            <Grid.Column width="7">
            <Input
                fieldPath={`${fieldPath}.total_volumes`}
                label={total_volumes.label}
                placeholder={total_volumes.placeholder}
                description={total_volumes.description}
            ></Input>
            </Grid.Column>
            <Grid.Column width="5">
            <Input
                fieldPath={`${fieldPath}.volume`}
                label={volume.label}
                icon={"building"}
                placeholder={volume.placeholder}
                description={volume.description}
            ></Input>
            </Grid.Column>
        </Grid>
    );
}}