// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import PropTypes from "prop-types";
import Overridable from "react-overridable";
import { Button } from "semantic-ui-react";

export class RequestActionModalTrigger extends Component {
  render() {
    const {
      action,
      toggleModal,
      loading,
      modalOpen,
      requestType,
      size,
    } = this.props;
    const buttonAria = {
      "aria-expanded": !!modalOpen[action],
      "aria-haspopup": "dialog",
      "aria-controls": action,
    };
    return (
      <Overridable
        id={`RequestActionModalTrigger.${action}`}
        onClick={() => toggleModal(action, true)}
        loading={loading}
        action={action}
        requestType={requestType}
        ariaAttributes={buttonAria}
        size={size}
      >
        <Button
          onClick={() => toggleModal(action, true)}
          loading={loading}
          {...buttonAria}
        >
          {action}
        </Button>
      </Overridable>
    );
  }
}

RequestActionModalTrigger.propTypes = {
  toggleModal: PropTypes.func.isRequired,
  action: PropTypes.string.isRequired,
  loading: PropTypes.bool.isRequired,
  modalOpen: PropTypes.object.isRequired,
  requestType: PropTypes.string.isRequired,
  size: PropTypes.string,
};

export default Overridable.component(
  "InvenioRequests.RequestActionModalTrigger",
  RequestActionModalTrigger
);
