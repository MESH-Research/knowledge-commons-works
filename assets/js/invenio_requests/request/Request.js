// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import Overridable from "react-overridable";
import Loader from "../components/Loader";
import RequestActionsPortal from "./actions";
import RequestDetails from "./RequestDetails";
import React, { Component } from "react";
import PropTypes from "prop-types";
import isEmpty from "lodash/isEmpty";

export class Request extends Component {
  componentDidMount() {
    const { initRequest } = this.props;
    initRequest();
  }

  render() {
    const { request, updateRequestAfterAction, userAvatar } = this.props;

    return (
      <Overridable id="InvenioRequest.Request.layout">
        <Loader isLoading={isEmpty(request)}>
          <RequestActionsPortal
            request={request}
            actionSuccessCallback={updateRequestAfterAction}
          />
          <RequestDetails request={request} userAvatar={userAvatar} />
        </Loader>
      </Overridable>
    );
  }
}

Request.propTypes = {
  request: PropTypes.object.isRequired,
  initRequest: PropTypes.func.isRequired,
  updateRequestAfterAction: PropTypes.func.isRequired,
  userAvatar: PropTypes.string,
};

Request.defaultProps = {
  userAvatar: "",
};

export default Overridable.component("InvenioRequests.Request", Request);
