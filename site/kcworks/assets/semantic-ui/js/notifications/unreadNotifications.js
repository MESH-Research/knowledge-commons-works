/*
 * Part of Knowledge Commons Works
 * Copyright (C) 2024-2026 MESH Research
 *
 * KCWorks is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import axios from "axios";

/** sessionStorage key for the current user's unread notification list. */
export const UNREAD_NOTIFICATIONS_STORAGE_KEY = "unreadNotifications";

/** Window event name for same-tab unread list updates across React roots. */
export const UNREAD_NOTIFICATIONS_UPDATED_EVENT = "unreadNotificationsUpdated";

const unreadApiClient = axios.create({
  withCredentials: true,
  xsrfCookieName: "csrftoken",
  xsrfHeaderName: "X-CSRFToken",
  headers: {
    Accept: "application/vnd.inveniordm.v1+json",
    "Content-Type": "application/json",
  },
});

/**
 * Read the unread notification list from sessionStorage.
 *
 * @returns {Array<object>} Parsed unread items, or `[]` if missing/invalid.
 */
export function getUnreadNotificationsFromStorage() {
  try {
    const raw = sessionStorage.getItem(UNREAD_NOTIFICATIONS_STORAGE_KEY);
    if (!raw) {
      return [];
    }
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch (error) {
    console.error("Error reading unread notifications from sessionStorage:", error);
    return [];
  }
}

/**
 * Persist the unread list and notify other React roots on the page.
 *
 * Dispatches `unreadNotificationsUpdated` so same-tab listeners (header menu,
 * request list items, filters) can refresh without a shared React context.
 *
 * @param {Array<object>} unread Remaining unread notifications.
 */
export function setUnreadNotificationsInSession(unread) {
  sessionStorage.setItem(
    UNREAD_NOTIFICATIONS_STORAGE_KEY,
    JSON.stringify(unread ?? [])
  );
  window.dispatchEvent(new Event(UNREAD_NOTIFICATIONS_UPDATED_EVENT));
}

/**
 * Clear unread notifications via the API and sync sessionStorage.
 *
 * Omitting both IDs clears all unread for the authenticated user.
 *
 * @param {{ requestId?: string, commentId?: string }} [options]
 * @returns {Promise<Array<object>>} Remaining unread notifications.
 */
export async function clearUnreadNotifications(options = {}) {
  const { requestId, commentId } = options;
  const params = {};
  if (requestId) {
    params.request_id = requestId;
  }
  if (commentId) {
    params.comment_id = commentId;
  }

  const response = await unreadApiClient.delete(
    "/api/users/me/notifications/unread/clear",
    { params }
  );
  const remaining = response.data;
  setUnreadNotificationsInSession(remaining);
  return remaining;
}

/**
 * Reconcile unread against live personal requests and sync sessionStorage.
 *
 * Drops orphan / non-personal rows on the server, then updates local state
 * so Pending/Resolved badges and the header count stay accurate.
 *
 * @returns {Promise<Array<object>>} Reconciled unread notifications.
 */
export async function reconcileUnreadNotifications() {
  const response = await unreadApiClient.get(
    "/api/users/me/notifications/unread/reconcile"
  );
  const reconciled = response.data;
  setUnreadNotificationsInSession(reconciled);
  return reconciled;
}
