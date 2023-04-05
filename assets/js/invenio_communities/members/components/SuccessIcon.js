import PropTypes from "prop-types";
import React, { Component } from "react";
import { Icon } from "semantic-ui-react";

export class SuccessIcon extends Component {
  constructor(props) {
    super(props);
    const { show } = props;
    this.state = { show: show };
  }

  componentDidMount() {
    const { timeOutDelay, show } = this.props;
    // eslint-disable-next-line react/no-did-mount-set-state
    this.setState({ show: show });

    const timerAlreadySet = !!this.successTimer;

    if (show) {
      if (timerAlreadySet) {
        clearTimeout(this.successTimer);
      }

      this.successTimer = setTimeout(this.handleOnTimeOut, timeOutDelay);
    }
  }

  componentWillUnmount() {
    this.successTimer && clearTimeout(this.successTimer);
  }

  handleOnTimeOut = () => {
    this.setState({ show: false });
  };

  render() {
    const { className } = this.props;
    const { show } = this.state;
    return show && <Icon name="checkmark" className={`positive ${className}`} />;
  }
}

SuccessIcon.propTypes = {
  timeOutDelay: PropTypes.number.isRequired,
  show: PropTypes.bool,
  className: PropTypes.string,
};

SuccessIcon.defaultProps = {
  show: false,
  className: null,
};
