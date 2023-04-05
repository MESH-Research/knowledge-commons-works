// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.
import { http } from "react-invenio-forms";

export class RequestEventsLinksExtractor {
  #links;

  constructor(links) {
    this.#links = links;
  }

  get eventUrl() {
    if (!this.#links.self) {
      throw TypeError("Self link missing from resource.");
    }
    return this.#links.self;
  }
}

export class InvenioRequestEventsApi {
  #links;

  constructor(links) {
    this.#links = links;
  }

  getComment = async () => {
    return await http.get(this.#links.eventUrl, { params: { expand: 1 } });
  };

  updateComment = async (payload) => {
    return http.put(this.#links.eventUrl, payload, { params: { expand: 1 } });
  };

  deleteComment = async () => {
    return await http.delete(this.#links.eventUrl);
  };
}
