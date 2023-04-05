// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { connect } from "react-redux";
import {
  getTimelineWithRefresh,
  setPage,
  clearTimelineInterval,
} from "./state/actions";
import TimelineFeedComponent from "./TimelineFeed";

const mapDispatchToProps = (dispatch) => ({
  getTimelineWithRefresh: () => dispatch(getTimelineWithRefresh()),
  timelineStopRefresh: () => dispatch(clearTimelineInterval()),
  setPage: (page) => dispatch(setPage(page)),
});

const mapStateToProps = (state) => ({
  loading: state.timeline.loading,
  refreshing: state.timeline.refreshing,
  timeline: state.timeline.data,
  error: state.timeline.error,
  isSubmitting: state.timelineCommentEditor.isLoading,
  size: state.timeline.size,
  page: state.timeline.page,
});

export const Timeline = connect(
  mapStateToProps,
  mapDispatchToProps
)(TimelineFeedComponent);
