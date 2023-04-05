// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.
// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import PropTypes from "prop-types";
import Overridable from "react-overridable";
import { Label } from "semantic-ui-react";

class RequestStatusLabel extends Component {
  render() {
    const { status } = this.props;
    return (
      <Overridable id={`RequestStatusLabel.layout.${status}`}>
        <Label>{status}</Label>
      </Overridable>
    );
  }
}

RequestStatusLabel.propTypes = {
  status: PropTypes.string.isRequired,
};

export default Overridable.component(
  "InvenioRequests.RequestStatusLabel",
  RequestStatusLabel
);
