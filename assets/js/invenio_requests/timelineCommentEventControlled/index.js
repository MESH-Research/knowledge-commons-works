// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import EventWithStateComponent from "./TimelineCommentEventControlled";
import { connect } from "react-redux";
import { updateComment, deleteComment } from "./state/actions";

const mapDispatchToProps = (dispatch) => ({
  updateComment: async (payload) => dispatch(updateComment(payload)),
  deleteComment: async (payload) => dispatch(deleteComment(payload)),
});

export const TimelineCommentEventControlled = connect(
  null,
  mapDispatchToProps
)(EventWithStateComponent);
