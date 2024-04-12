import React from "react";
import ActionDropdown from "./ActionDropdown";
import { Grid, Icon, Item } from "semantic-ui-react";
import PropTypes from "prop-types";

const DropdownContent = ({ title, description, selected }) => (
  <Grid>
    <Grid.Row>
      <Grid.Column width={1} verticalAlign="middle">
        {selected && <Icon className="positive" name="checkmark" />}
      </Grid.Column>
      <Grid.Column width={14}>
        <Item.Group unstackable>
          <Item>
            <Item.Content>
              <Item.Description>
                <strong>{title}</strong>
              </Item.Description>
              <Item.Meta>{description}</Item.Meta>
            </Item.Content>
          </Item>
        </Item.Group>
      </Grid.Column>
    </Grid.Row>
  </Grid>
);

DropdownContent.propTypes = {
  title: PropTypes.string.isRequired,
  description: PropTypes.string.isRequired,
  selected: PropTypes.bool.isRequired,
};

const rolesToDropdownOptions = (roles, currentValue) =>
  roles.map((role) => ({
    key: role.name,
    text: role.title,
    value: role.name,
    content: (
      <DropdownContent
        title={role.title}
        description={role.description}
        selected={currentValue === role.name}
      />
    ),
  }));

export const RoleDropdown = ({
  roles,
  successCallback,
  action,
  disabled,
  currentValue,
  resource,
  label,
}) => {
  return (
    <ActionDropdown
      optionsSerializer={(options) => rolesToDropdownOptions(options, currentValue)}
      options={roles}
      successCallback={successCallback}
      action={action}
      disabled={disabled}
      currentValue={currentValue}
      resource={resource}
      direction="left"
      fluid
      label={label}
    />
  );
};

RoleDropdown.propTypes = {
  ...ActionDropdown.propTypes,
  roles: PropTypes.array.isRequired,
};

const visibilityTypesToDropdownOptions = (options, currentValue) => {
  return options.map((settings) => {
    return {
      key: settings.name,
      text: settings.title,
      value: settings.visible,
      content: (
        <DropdownContent
          title={settings.title}
          description={settings.description}
          selected={currentValue === settings.visible}
        />
      ),
    };
  });
};

export const VisibilityDropdown = ({
  visibilityTypes,
  successCallback,
  action,
  disabled,
  currentValue,
  resource,
  label,
}) => {
  return (
    <ActionDropdown
      optionsSerializer={(options) =>
        visibilityTypesToDropdownOptions(options, currentValue)
      }
      options={visibilityTypes}
      successCallback={successCallback}
      action={action}
      disabled={disabled}
      currentValue={currentValue}
      resource={resource}
      direction="left"
      fluid
      label={label}
    />
  );
};

VisibilityDropdown.propTypes = {
  ...ActionDropdown.propTypes,
  visibilityTypes: PropTypes.array.isRequired,
};
