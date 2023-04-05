import React, { Component } from "react";
import PropTypes from "prop-types";
import { ErrorMessage, SuccessMessage } from "./messages";

export const NotificationContext = React.createContext({
  notifications: {},
  addNotification: () => {},
  removeNotification: () => {},
});

export class NotificationController extends Component {
  constructor(props) {
    super(props);
    this.state = { nextNotificationID: 1, notifications: {} };
  }

  addNotification = (notification) => {
    const { notifications: prevNotifications, nextNotificationID } = this.state;

    this.setState({
      notifications: {
        ...prevNotifications,
        [nextNotificationID]: notification,
      },
    });
    this.setState({ nextNotificationID: nextNotificationID + 1 });
  };

  removeNotification = (notificationID) => {
    const { notifications: prevNotifications } = this.state;
    delete prevNotifications[notificationID];
    this.setState({ notifications: { ...prevNotifications } });
  };

  renderNotification(id, notification) {
    let MessageComponent = ErrorMessage;
    if (notification.type === "success") {
      MessageComponent = SuccessMessage;
    }

    return (
      <MessageComponent
        id={id}
        key={id}
        header={notification.title}
        content={notification.content}
        removeNotification={this.removeNotification}
      />
    );
  }

  render() {
    const { children } = this.props;
    const { notifications } = this.state;
    return (
      <NotificationContext.Provider
        value={{
          notifications: notifications,
          addNotification: this.addNotification,
          removeNotification: this.removeNotification,
        }}
      >
        <div id="admin-notifications" className="compact">
          {Object.entries(notifications).map(([messageID, message]) =>
            this.renderNotification(messageID, message)
          )}
        </div>
        {children}
      </NotificationContext.Provider>
    );
  }
}

NotificationController.propTypes = {
  children: PropTypes.element.isRequired,
};
