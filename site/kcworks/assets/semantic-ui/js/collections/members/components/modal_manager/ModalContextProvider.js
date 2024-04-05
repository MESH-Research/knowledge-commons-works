/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { Component } from "react";
import { ModalContext } from "./index";
import PropTypes from "prop-types";

export class ModalContextProvider extends Component {
  constructor(props) {
    super(props);

    this.state = {
      modalMode: null,
      modalAction: null,
      modalOpen: false,
    };
  }

  openModal = ({ modalAction, modalMode }) => {
    this.setState({ modalOpen: true, modalAction, modalMode });
  };

  closeModal = () => {
    this.setState({ modalOpen: false });
  };

  render() {
    const { children } = this.props;
    const { modalMode, modalAction, modalOpen } = this.state;

    return (
      <ModalContext.Provider
        value={{
          closeModal: this.closeModal,
          openModal: this.openModal,
          modalMode,
          modalAction,
          modalOpen,
        }}
      >
        {children}
      </ModalContext.Provider>
    );
  }
}

ModalContextProvider.propTypes = {
  children: PropTypes.node.isRequired,
};
