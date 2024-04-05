// This file is part of Invenio-communities
// Copyright (C) 2022 CERN.
//
// Invenio-communities is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

export const errorSerializer = (error) =>
  error?.response?.data?.message || error?.message;

export const payloadSerializer = (content, format) => ({
  payload: {
    content,
    format,
  },
});

export const communityErrorSerializer = (error) => ({
  message: error?.response?.data?.message,
  errors: error?.response?.data?.errors,
  status: error?.response?.data?.status,
});

export const bulkMembersSerializer = (members) =>
  Object.entries(members).map(([memberId, memberData]) => ({
    id: memberData.id,
    type: memberData.type,
  }));
