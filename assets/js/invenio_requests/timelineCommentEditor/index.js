// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { connect } from "react-redux";
import { submitComment, setEventContent } from "./state/actions";
import TimelineCommentEditorComponent from "./TimelineCommentEditor";

const mapDispatchToProps = (dispatch) => ({
  submitComment: (content, format) => dispatch(submitComment(content, format)),
  setCommentContent: (content) => dispatch(setEventContent(content)),
});

const mapStateToProps = (state) => ({
  isLoading: state.timelineCommentEditor.isLoading,
  error: state.timelineCommentEditor.error,
  commentContent: state.timelineCommentEditor.commentContent,
});

export const TimelineCommentEditor = connect(
  mapStateToProps,
  mapDispatchToProps
)(TimelineCommentEditorComponent);
