import React, { Component } from "react";

import { Input, Array } from "react-invenio-forms";
import { Grid, Form, Button, Icon } from "semantic-ui-react";

const newNote = {
  note_text: "",
  note_description: "",
};

export class Experiments extends Component {
  render() {
    const {
      fieldPath, // injected by the custom field loader via the `field` config property
      note_text,
      note_description,
      icon,
      addButtonLabel,
      description,
      label,
    } = this.props;
    return (
      <Array
        fieldPath={fieldPath}
        label={label}
        icon={icon}
        addButtonLabel={addButtonLabel}
        defaultNewValue={newNote}
        description={description}
      >
        {({ arrayHelpers, indexPath }) => {
          const fieldPathPrefix = `${fieldPath}.${indexPath}`;
          return (
            <Grid>
              <Grid.Column width="12">
                <Input
                  fieldPath={`${fieldPathPrefix}.note_text`}
                  label={note_text.label}
                  placeholder={note_text.placeholder}
                  description={note_text.description}
                ></Input>
              </Grid.Column>
              <Grid.Column width="12">
                <Input
                  fieldPath={`${fieldPathPrefix}.note_description`}
                  label={note_description.label}
                  icon={"pencil"}
                  placeholder={note_description.placeholder}
                  description={note_description.description}
                ></Input>
              </Grid.Column>
              <Grid.Column width="1">
                <Form.Field style={{ marginTop: "1.75rem", float: "right" }}>
                  <Button
                    aria-label={"Remove field"}
                    className="close-btn"
                    icon
                    onClick={() => arrayHelpers.remove(indexPath)}
                    type="button"
                  >
                    <Icon name="close" />
                  </Button>
                </Form.Field>
              </Grid.Column>
            </Grid>
          );
        }}
      </Array>
    );
  }
}