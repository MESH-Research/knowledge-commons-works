// Part of Knowledge Commons Works
// Copyright (C) 2023-2026, MESH Research
//
// Knowledge Commons Works is an instance of InvenioRDM, which is
// Copyright (c) 2019-2026, CERN
//
// Knowledge Commons Works and InvenioRDM are both free software;
// You can redistribute and/or modify them under the terms of the
// MIT License; see LICENSE file for more details.

const EDITING_STEP = /** @type {const} */ ({
  HOST: "host",
  MAPPED: "mapped",
  GUEST: "guest",
  NONE: null,
});

/** Fallback Globus Web App base URL when a server has no configured domain. */
const GLOBUS_APP_BASE_URL = "https://app.globus.org";

const kcworksAuthStartURL = (next_url = "/") => {
  return `/globus/login/start?next=${encodeURIComponent(next_url)}`;
};

/**
 * Normalize a Globus app base URL (configured domain or fallback).
 *
 * @param {string} [domain] Optional configured domain (may include a trailing slash).
 * @returns {string} Base URL with no trailing slash.
 */
const resolveGlobusAppBaseUrl = (domain) => (domain || GLOBUS_APP_BASE_URL).replace(/\/+$/, "");

/**
 * Console overview URL for a Globus Connect Server host endpoint.
 *
 * @param {string} endpointId Host endpoint UUID.
 * @param {string} [domain] Configured Globus app domain for the server.
 * @returns {string}
 */
const globusConsoleEndpointUrl = (endpointId, domain) =>
  `${resolveGlobusAppBaseUrl(domain)}/console/endpoints/${endpointId}`;

/**
 * Collection overview URL in the Globus Web App.
 *
 * @param {string} collectionId Mapped or guest collection UUID.
 * @param {string} [domain] Configured Globus app domain for the server.
 * @returns {string}
 */
const globusCollectionOverviewUrl = (collectionId, domain) =>
  `${resolveGlobusAppBaseUrl(domain)}/file-manager/collections/${collectionId}/overview`;

/**
 * File Manager URL for a collection, optionally at a path.
 *
 * @param {string} collectionId Collection UUID.
 * @param {string} [path] Absolute path within the collection.
 * @param {string} [domain] Configured Globus app domain for the server.
 * @returns {string}
 */
const globusFileManagerUrl = (collectionId, path, domain) => {
  const url = `${resolveGlobusAppBaseUrl(domain)}/file-manager?origin_id=${collectionId}`;
  if (!path) {
    return url;
  }
  return `${url}&origin_path=${encodeURIComponent(path)}`;
};

export {
  EDITING_STEP,
  GLOBUS_APP_BASE_URL,
  globusCollectionOverviewUrl,
  globusConsoleEndpointUrl,
  globusFileManagerUrl,
  kcworksAuthStartURL,
  resolveGlobusAppBaseUrl,
};
