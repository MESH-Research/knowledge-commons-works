// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { REQUEST_INIT } from './actions';

export const initialState = {
  loading: false,
  data: {  },
  error: null,
};

export const requestReducer = (state = initialState, action) => {
  switch (action.type) {
    case REQUEST_INIT:
      return {
        ...state,
        loading: false,
        data: action.payload,
        error: null,
      };
    default:
      return state;
  }
};

