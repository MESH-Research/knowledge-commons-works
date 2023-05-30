import React, { Component } from "react";

import { MultiInput, Array } from "react-invenio-forms";
import { Grid, Form, Button, Icon } from "semantic-ui-react";

export class UserDefinedTags extends Component {
  render() {
    const {
      fieldPath, // injected by the custom field loader via the `field` config property
      label,
      tag,
      icon,
      description
    } = this.props;
    return (
        <Grid>
            <Grid.Column width="12">
            <MultiInput
                fieldPath={`${fieldPath}.tag`}
                label={tag.tag_label.label}
                placeholder={tag.tag_label.placeholder}
                description={description}
                icon={icon}
            ></MultiInput>
            </Grid.Column>
        </Grid>
    );
  }
}
