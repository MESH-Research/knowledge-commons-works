// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.
export const payloadSerializer = (content, format) => ({
  payload: {
    content,
    format,
  },
});

export const errorSerializer = (error) =>
  error?.response?.data?.message || error?.message;
