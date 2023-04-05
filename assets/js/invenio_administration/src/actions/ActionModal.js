// This file is part of InvenioAdministration
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import PropTypes from "prop-types";
import React, { Component } from "react";
import { Modal } from "semantic-ui-react";
import Overridable from "react-overridable";

class ActionModal extends Component {
  render() {
    const { children, modalOpen, resource } = this.props;

    return (
      <Overridable
        id="InvenioAdministration.ActionModal.layout"
        modalOpen={modalOpen}
        // eslint-disable-next-line react/no-children-prop
        children={children}
        resource={resource}
      >
        <Modal role="dialog" open={modalOpen}>
          {children}
        </Modal>
      </Overridable>
    );
  }
}

ActionModal.propTypes = {
  children: PropTypes.object,
  modalOpen: PropTypes.bool,
  resource: PropTypes.object.isRequired,
};

ActionModal.defaultProps = {
  modalOpen: false,
  children: null,
};

export default Overridable.component("InvenioAdministration.ActionModal", ActionModal);
