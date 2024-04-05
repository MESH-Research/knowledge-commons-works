// This file is part of Invenio-Communities
// Copyright (C) 2021 CERN.
// Copyright (C) 2021 Northwestern University.
//
// Invenio-communities is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { http } from "react-invenio-forms";

/**
 * API Client for communities.
 *
 * It mostly uses the API links passed to it from responses.
 *
 */
export class CommunityApi {
  baseUrl = "/api/communities";

  /**
   * Create a new community.
   *
   * @param {object} payload - Serialized community
   * @param {object} options - Custom options
   */
  async create(payload, options) {
    options = options || {};
    return http.post(this.baseUrl, payload, {
      ...options,
    });
  }

  /**
   * Update a pre-existing community.
   *
   * @param {string} communityId - identifier
   * @param {object} payload - Serialized community
   * @param {object} options - Custom options
   */
  async update(communityId, payload, options) {
    options = options || {};
    return http.put(`${this.baseUrl}/${communityId}`, payload, {
      ...options,
    });
  }

  /**
   * Delete the community.
   *
   * @param {string} communityId - Identifier
   * @param {object} options - Custom options
   */
  async delete(communityId, options) {
    options = options || {};
    return http.delete(`${this.baseUrl}/${communityId}`, {
      ...options,
    });
  }

  /**
   * Change the identifier of a community.
   *
   * @param {string} communityId - the community identifier
   * @param {object} newSlug - the new slug
   * @param {object} options - Custom options
   */
  async renameSlug(communityId, newSlug, options) {
    options = options || {};
    return http.post(
      `${this.baseUrl}/${communityId}/rename`,
      { slug: newSlug },
      {
        ...options,
      }
    );
  }

  /**
   * Update the community logo.
   *
   * @param {string} communityId - Identifier
   * @param {object} payload - File
   * @param {object} options - Custom options
   */
  async updateLogo(communityId, payload, options) {
    options = options || {};
    const headers = {
      "Content-Type": "application/octet-stream",
    };
    return http.put(`${this.baseUrl}/${communityId}/logo`, payload, {
      headers: headers,
      ...options,
    });
  }

  /**
   * Delete the community logo.
   *
   * @param {string} communityId - Identifier
   * @param {object} options - Custom options
   */
  async deleteLogo(communityId, options) {
    options = options || {};
    const headers = {
      "Content-Type": "application/octet-stream",
    };
    return http.delete(`${this.baseUrl}/${communityId}/logo`, {
      headers: headers,
      ...options,
    });
  }
}
