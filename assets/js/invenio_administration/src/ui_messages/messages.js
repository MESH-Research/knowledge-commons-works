import PropTypes from "prop-types";
import React, { Component } from "react";
import { Message as SemanticMessage } from "semantic-ui-react";

export class Message extends Component {
  componentDidMount() {
    const { autoDismiss } = this.props;
    if (autoDismiss) {
      setTimeout(this.handleDismiss, autoDismiss);
    }
  }

  handleDismiss = () => {
    const { removeNotification, id } = this.props;
    removeNotification(id);
  };

  render() {
    const { id, ...props } = this.props;

    return (
      <SemanticMessage
        id={id}
        floating
        {...props}
        onDismiss={this.handleDismiss}
        role="alert"
      />
    );
  }
}

export const ErrorMessage = ({ id, header, content, removeNotification }) => (
  <Message
    negative
    icon="exclamation"
    header={header}
    content={content}
    id={id}
    removeNotification={removeNotification}
  />
);

export const SuccessMessage = ({ id, header, content, removeNotification }) => (
  <Message
    success
    icon="check"
    header={header}
    content={content}
    id={id}
    autoDismiss={5 * 1000} // in seconds
    removeNotification={removeNotification}
  />
);

Message.propTypes = {
  autoDismiss: PropTypes.number,
  removeNotification: PropTypes.func.isRequired,
  id: PropTypes.string.isRequired,
};

Message.defaultProps = {
  autoDismiss: null,
};

ErrorMessage.propTypes = {
  id: PropTypes.string.isRequired,
  header: PropTypes.string.isRequired,
  content: PropTypes.string.isRequired,
};

SuccessMessage.propTypes = ErrorMessage.propTypes;
