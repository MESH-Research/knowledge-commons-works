import React, { Component } from "react";
import PropTypes from "prop-types";
import { Form, Radio, Item } from "semantic-ui-react";

export class RadioSelection extends Component {
  constructor(props) {
    super(props);
    this.state = { selected: undefined };
  }

  handleOnChange = (e, { value }) => {
    const { onOptionChangeCallback } = this.props;
    this.setState({ selected: value });
    onOptionChangeCallback(value);
  };

  render() {
    const { options, label } = this.props;
    const { selected } = this.state;

    return (
      <Form.Field required>
        <label>{label}</label>
        <Item.Group className="mt-10">
          {options.map((option) => (
            <Item key={option.name}>
              <Item.Content>
                <Item.Header>
                  <Form.Field>
                    <Radio
                      onClick={this.handleOnChange}
                      label={option.title}
                      aria-label={option.title}
                      value={option.name}
                      checked={selected === option.name}
                      name="membersRoles"
                      key={option.name}
                    />
                  </Form.Field>
                </Item.Header>
                <Item.Meta className="ml-25 mt-0">{option.description}</Item.Meta>
              </Item.Content>
            </Item>
          ))}
        </Item.Group>
      </Form.Field>
    );
  }
}

RadioSelection.propTypes = {
  options: PropTypes.array.isRequired,
  label: PropTypes.string.isRequired,
  onOptionChangeCallback: PropTypes.func.isRequired,
};
