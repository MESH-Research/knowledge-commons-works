import React, { Component } from "react";
import PropTypes from "prop-types";
import { Message } from "semantic-ui-react";
import { communityErrorSerializer } from "../../api/serializers";

export class ErrorMessage extends Component {
  render() {
    const { error } = this.props;
    let { errors, message } = communityErrorSerializer(error);

    if (!message) {
      message = error.message;
    }
    return (
      <Message className="ml-20 mr-20" negative>
        <Message.Header>{message}</Message.Header>
        {errors && (
          <Message.List>
            {errors.map((error) => {
              return (
                <Message.Item key={error}>
                  {/* when there is no field Marshmallow returns _schema */}
                  {error.field !== "_schema" && <strong>{error.field}: </strong>}
                  {error.messages.length === 1 ? (
                    error.messages[0]
                  ) : (
                    <Message.List>
                      {error.messages.map((message) => (
                        <Message.Item key={message}>{message}</Message.Item>
                      ))}
                    </Message.List>
                  )}
                </Message.Item>
              );
            })}
          </Message.List>
        )}
      </Message>
    );
  }
}

ErrorMessage.propTypes = {
  error: PropTypes.object.isRequired,
};
