// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import _isEmpty from "lodash/isEmpty";
import { http } from "react-invenio-forms";

export class RequestLinksExtractor {
  #urls;

  constructor(request) {
    if (!request?.links) {
      throw TypeError("Request resource links are undefined");
    }
    this.#urls = request.links;
  }

  get self() {
    return this.#urls.self;
  }

  get timeline() {
    if (!this.#urls.timeline) {
      throw TypeError("Timeline link missing from resource.");
    }
    return this.#urls.timeline;
  }

  get comments() {
    if (!this.#urls.comments) {
      throw TypeError("Comments link missing from resource.");
    }
    return this.#urls.comments;
  }

  get actions() {
    if (!this.#urls.actions) {
      throw TypeError("Actions link missing from resource.");
    }
    return this.#urls.actions;
  }
}

export class InvenioRequestsAPI {
  #urls;

  constructor(requestLinksExtractor) {
    this.#urls = requestLinksExtractor;
  }

  get availableRequestStatuses() {
    return ["accepted", "declined", "expired", "cancelled"];
  }

  getTimeline = async (params) => {
    return await http.get(this.#urls.timeline, {
      params: {
        expand: 1,
        ...params,
      },
    });
  };

  getRequest = async () => {
    return await http.get(this.#urls.self, { params: { expand: 1 } });
  };

  submitComment = async (payload) => {
    return await http.post(this.#urls.comments, payload, {
      params: { expand: 1 },
    });
  };

  performAction = async (action, commentContent = null) => {
    let payload = {};
    if (!_isEmpty(commentContent)) {
      payload = {
        payload: {
          content: commentContent,
          format: "html",
        },
      };
    }
    return await http.post(this.#urls.actions[action], payload, {
      params: { expand: 1 },
    });
  };
}
