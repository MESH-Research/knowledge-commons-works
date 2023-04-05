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

class RequestTypeLabel extends Component {
  render() {
    const { type } = this.props;
    return (
      <Overridable id={`RequestTypeLabel.layout.${type}`}>
        <Label>{type}</Label>
      </Overridable>
    );
  }
}

RequestTypeLabel.propTypes = {
  type: PropTypes.string.isRequired,
};

export default Overridable.component(
  "InvenioRequests.RequestTypeLabel",
  RequestTypeLabel
);
