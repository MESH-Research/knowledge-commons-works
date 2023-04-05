import React, { Component } from "react";
import Overridable from "react-overridable";
import { Loader as UILoader } from "semantic-ui-react";
import PropTypes from "prop-types";

class Loader extends Component {
  render() {
    const { isLoading, children } = this.props;
    return (
      <Overridable id="Admin.Loader.layout" {...this.props}>
        {isLoading ? (
          <UILoader active size="huge" inline="centered" />
        ) : (
          // eslint-disable-next-line react/jsx-no-useless-fragment
          <>{children}</>
        )}
      </Overridable>
    );
  }
}

Loader.propTypes = {
  isLoading: PropTypes.bool,
  children: PropTypes.node,
};

Loader.defaultProps = {
  isLoading: false,
  children: null,
};

export default Overridable.component("Loader", Loader);
