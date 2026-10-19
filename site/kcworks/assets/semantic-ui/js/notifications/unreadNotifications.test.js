/*
 * Part of Knowledge Commons Works
 * Copyright (C) 2024-2026 MESH Research
 *
 * KCWorks is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import axios from "axios";
import {
  UNREAD_NOTIFICATIONS_STORAGE_KEY,
  UNREAD_NOTIFICATIONS_UPDATED_EVENT,
  clearUnreadNotifications,
  getUnreadNotificationsFromStorage,
  reconcileUnreadNotifications,
  setUnreadNotificationsInSession,
} from "./unreadNotifications";

jest.mock("axios", () => {
  const get = jest.fn();
  const del = jest.fn();
  return {
    __esModule: true,
    default: {
      create: jest.fn(() => ({ get, delete: del })),
      __mockGet: get,
      __mockDelete: del,
    },
  };
});

describe("unreadNotifications helper", () => {
  beforeEach(() => {
    sessionStorage.clear();
    axios.__mockGet.mockReset();
    axios.__mockDelete.mockReset();
  });

  afterEach(() => {
    sessionStorage.clear();
    jest.restoreAllMocks();
  });

  describe("getUnreadNotificationsFromStorage", () => {
    it("returns [] when missing", () => {
      expect(getUnreadNotificationsFromStorage()).toEqual([]);
    });

    it("returns [] for invalid JSON", () => {
      const errorSpy = jest.spyOn(console, "error").mockImplementation(() => {});
      sessionStorage.setItem(UNREAD_NOTIFICATIONS_STORAGE_KEY, "{not-json");
      expect(getUnreadNotificationsFromStorage()).toEqual([]);
      errorSpy.mockRestore();
    });

    it("returns [] when stored value is not an array", () => {
      sessionStorage.setItem(
        UNREAD_NOTIFICATIONS_STORAGE_KEY,
        JSON.stringify({ request_id: "x" })
      );
      expect(getUnreadNotificationsFromStorage()).toEqual([]);
    });

    it("returns the parsed list", () => {
      const unread = [{ request_id: "1" }];
      sessionStorage.setItem(
        UNREAD_NOTIFICATIONS_STORAGE_KEY,
        JSON.stringify(unread)
      );
      expect(getUnreadNotificationsFromStorage()).toEqual(unread);
    });
  });

  describe("setUnreadNotificationsInSession", () => {
    it("writes sessionStorage and dispatches unreadNotificationsUpdated", () => {
      const listener = jest.fn();
      window.addEventListener(UNREAD_NOTIFICATIONS_UPDATED_EVENT, listener);

      const unread = [{ request_id: "1" }];
      setUnreadNotificationsInSession(unread);

      expect(sessionStorage.getItem(UNREAD_NOTIFICATIONS_STORAGE_KEY)).toBe(
        JSON.stringify(unread)
      );
      expect(listener).toHaveBeenCalledTimes(1);
      expect(listener.mock.calls[0][0].type).toBe(
        UNREAD_NOTIFICATIONS_UPDATED_EVENT
      );

      window.removeEventListener(UNREAD_NOTIFICATIONS_UPDATED_EVENT, listener);
    });
  });

  describe("clearUnreadNotifications", () => {
    it("calls clear with request_id and persists the response", async () => {
      const remaining = [{ request_id: "2" }];
      axios.__mockDelete.mockResolvedValue({ data: remaining });

      const result = await clearUnreadNotifications({ requestId: "1" });

      expect(axios.__mockDelete).toHaveBeenCalledWith(
        "/api/users/me/notifications/unread/clear",
        { params: { request_id: "1" } }
      );
      expect(result).toEqual(remaining);
      expect(sessionStorage.getItem(UNREAD_NOTIFICATIONS_STORAGE_KEY)).toBe(
        JSON.stringify(remaining)
      );
    });

    it("calls clear with no params to clear all", async () => {
      axios.__mockDelete.mockResolvedValue({ data: [] });

      await clearUnreadNotifications();

      expect(axios.__mockDelete).toHaveBeenCalledWith(
        "/api/users/me/notifications/unread/clear",
        { params: {} }
      );
    });
  });

  describe("reconcileUnreadNotifications", () => {
    it("calls reconcile and persists the response", async () => {
      const reconciled = [{ request_id: "1" }];
      axios.__mockGet.mockResolvedValue({ data: reconciled });

      const result = await reconcileUnreadNotifications();

      expect(axios.__mockGet).toHaveBeenCalledWith(
        "/api/users/me/notifications/unread/reconcile"
      );
      expect(result).toEqual(reconciled);
      expect(sessionStorage.getItem(UNREAD_NOTIFICATIONS_STORAGE_KEY)).toBe(
        JSON.stringify(reconciled)
      );
    });
  });
});
