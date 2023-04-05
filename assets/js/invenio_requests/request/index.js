// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { connect } from "react-redux";
import RequestComponent from "./Request";
import { initRequest, updateRequestAfterAction } from "./state/actions";

const mapDispatchToProps = (dispatch) => ({
  initRequest: () => dispatch(initRequest()),
  updateRequestAfterAction: (request) =>
    dispatch(updateRequestAfterAction(request)),
});

const mapStateToProps = (state) => ({
  request: state.request.data,
});

export const Request = connect(
  mapStateToProps,
  mapDispatchToProps
)(RequestComponent);

export * from "./Status";
export * from "./StatusLabel";
export * from "./TypeLabel";
