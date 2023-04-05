// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import {
  CHANGE_PAGE,
  HAS_ERROR,
  IS_LOADING,
  IS_REFRESHING,
  SUCCESS,
} from "./actions";

export const initialState = {
  loading: false,
  refreshing: false,
  data: {},
  error: null,
  size: 15,
  page: 1,
};

export const timelineReducer = (state = initialState, action) => {
  switch (action.type) {
    case IS_LOADING:
      return { ...state, loading: true };
    case IS_REFRESHING:
      return { ...state, refreshing: true };
    case SUCCESS:
      return {
        ...state,
        refreshing: false,
        loading: false,
        data: action.payload,
        error: null,
      };
    case HAS_ERROR:
      return {
        ...state,
        refreshing: false,
        loading: false,
        error: action.payload,
      };
    case CHANGE_PAGE:
      return {
        ...state,
        page: action.payload,
      };

    default:
      return state;
  }
};
