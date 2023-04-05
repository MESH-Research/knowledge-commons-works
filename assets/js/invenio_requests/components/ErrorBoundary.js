// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.
import React, { Component } from "react";
import Overridable from "react-overridable";
import PropTypes from "prop-types";
import Error from "./Error";

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { error: null, errorInfo: null };
  }

  componentDidCatch(error, errorInfo) {
    // Catch errors in any components below and re-render with error message
    this.setState({
      error: error,
      errorInfo: errorInfo,
    });
    // You can also log error messages to an error reporting service here
  }

  render() {
    const { children } = this.props;
    const { error, errorInfo } = this.state;

    return (
      <Error error={error} errorInfo={errorInfo.componentStack}>
        {children}
      </Error>
    );
  }
}

ErrorBoundary.propTypes = {
  error: PropTypes.bool,
  children: PropTypes.node,
};

ErrorBoundary.defaultProps = {
  error: null,
  children: null,
};

export default Overridable.component("ErrorBoundary", ErrorBoundary);
