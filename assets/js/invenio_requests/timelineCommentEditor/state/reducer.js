// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { IS_LOADING, HAS_ERROR, SUCCESS, SETTING_CONTENT } from "./actions";

const initial_state = {
  error: null,
  isLoading: false,
  commentContent: "",
};

export const commentEditorReducer = (state = initial_state, action) => {
  switch (action.type) {
    case SETTING_CONTENT:
      return { ...state, commentContent: action.payload };
    case IS_LOADING:
      return { ...state, isLoading: true };
    case HAS_ERROR:
      return { ...state, error: action.payload, isLoading: false };
    case SUCCESS:
      return {
        ...state,
        isLoading: false,
        error: null,
        commentContent: "",
      };
    default:
      return state;
  }
};
