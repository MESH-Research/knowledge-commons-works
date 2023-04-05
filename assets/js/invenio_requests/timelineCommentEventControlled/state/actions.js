// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import {
  clearTimelineInterval,
  IS_REFRESHING,
  setTimelineInterval,
  SUCCESS,
} from "../../timeline/state/actions";
import { payloadSerializer } from "../../api/serializers";
import _cloneDeep from "lodash/cloneDeep";
import { i18next } from "../../../../translations/invenio_requests/i18next";

export const updateComment = ({ content, format, event }) => {
  return async (dispatch, getState, config) => {
    dispatch(clearTimelineInterval());
    const commentsApi = config.requestEventsApi(event.links);

    const payload = payloadSerializer(content, format);

    dispatch({ type: IS_REFRESHING });

    const response = await commentsApi.updateComment(payload);

    dispatch({
      type: SUCCESS,
      payload: _newStateWithUpdate(response.data, getState().timeline.data),
    });

    dispatch(setTimelineInterval());

    return response.data;
  };
};

export const deleteComment = ({ event }) => {
  return async (dispatch, getState, config) => {
    dispatch(clearTimelineInterval());
    const commentsApi = config.requestEventsApi(event.links);

    dispatch({ type: IS_REFRESHING });

    const response = await commentsApi.deleteComment();

    dispatch({
      type: SUCCESS,
      payload: _newStateWithDelete(event.id, getState),
    });

    dispatch(setTimelineInterval());

    return response.data;
  };
};

const _newStateWithUpdate = (updatedComment, currentState) => {
  // return timeline with the updated comment
  const timelineState = _cloneDeep(currentState);
  const currentHits = timelineState.hits.hits;
  const currentCommentKey = currentHits.findIndex(
    (comment) => comment.id === updatedComment.id
  );

  currentHits[currentCommentKey] = updatedComment;

  return timelineState;
};

const _newStateWithDelete = (eventId, currentState) => {
  // return timeline with the deleted comment replaced by the deletion event
  const timelineState = _cloneDeep(currentState().timeline.data);
  const currentHits = timelineState.hits.hits;

  const indexCommentToDelete = currentHits.findIndex(
    (comment) => comment.id === eventId
  );

  const currentComment = currentHits[indexCommentToDelete];

  const deletionPayload = {
    content: i18next.t("deleted a comment"),
    event: "comment_deleted",
    format: "html",
  };

  currentHits[indexCommentToDelete] = {
    ...currentComment,
    type: "L",
    payload: deletionPayload,
  };

  return timelineState;
};
