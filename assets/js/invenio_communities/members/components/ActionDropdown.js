import PropTypes from "prop-types";
import React, { Component } from "react";
import { withCancel } from "react-invenio-forms";
import Overridable from "react-overridable";
import { Dropdown, List } from "semantic-ui-react";
import { errorSerializer } from "../../api/serializers";
import { ErrorPopup } from "./ErrorPopup";
import { SuccessIcon } from "./SuccessIcon";

const dropdownOptionsGenerator = (value) => {
  return value.map((settings) => {
    return {
      key: settings.key,
      text: settings.title,
      value: settings.key,
      content: (
        <List>
          <List.Item>
            <List.Content>
              <List.Header>{settings.title}</List.Header>
              <List.Description>{settings.description}</List.Description>
            </List.Content>
          </List.Item>
        </List>
      ),
    };
  });
};

class ActionDropdown extends Component {
  constructor(props) {
    super(props);
    this.state = { error: undefined, loading: false, actionSuccess: undefined };
  }

  componentWillUnmount() {
    this.cancellableAction && this.cancellableAction.cancel();
  }

  handleOnChange = async (e, { value }) => {
    const { successCallback, action, resource } = this.props;
    this.setState({ loading: true, actionSuccess: false });
    this.cancellableAction = withCancel(action(resource.member, value));

    try {
      const response = await this.cancellableAction.promise;
      successCallback(response, value);
      this.setState({ loading: false, actionSuccess: true, error: undefined });
    } catch (error) {
      if (error === "UNMOUNTED") return;
      this.setState({
        loading: false,
        actionSuccess: false,
        error: errorSerializer(error),
      });
    }
  };

  render() {
    const { loading, actionSuccess, error } = this.state;
    const { options, currentValue, optionsSerializer, disabled, direction, fluid } =
      this.props;

    return (
      <Overridable
        id="InvenioCommunities.ActionDropdown.layout"
        options={options}
        loading={loading}
        actionSuccess={actionSuccess}
        error={error}
        disabled={disabled}
        optionsSerializer={optionsSerializer}
      >
        <div className="flex align-items-center members-dropdown-container">
          <Dropdown
            options={optionsSerializer(options)}
            loading={loading}
            value={currentValue}
            openOnFocus={false}
            selectOnBlur={false}
            onChange={this.handleOnChange}
            disabled={disabled}
            direction={direction}
            fluid={fluid}
            floating
          />
          <div className="ml-5 action-status-container">
            {actionSuccess && <SuccessIcon timeOutDelay={3000} show={actionSuccess} />}
            {error && <ErrorPopup error={error} />}
          </div>
        </div>
      </Overridable>
    );
  }
}

ActionDropdown.propTypes = {
  options: PropTypes.array.isRequired,
  successCallback: PropTypes.func.isRequired,
  currentValue: PropTypes.oneOfType([PropTypes.string, PropTypes.bool]),
  action: PropTypes.func.isRequired,
  optionsSerializer: PropTypes.func,
  disabled: PropTypes.bool,
  direction: PropTypes.string,
  resource: PropTypes.object.isRequired,
  fluid: PropTypes.bool,
};

ActionDropdown.defaultProps = {
  currentValue: "",
  disabled: false,
  direction: "right",
  optionsSerializer: dropdownOptionsGenerator,
  fluid: false,
};

export default Overridable.component("ActionDropdown", ActionDropdown);
