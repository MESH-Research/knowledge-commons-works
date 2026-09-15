/*
 * Part of Knowledge Commons Works
 * Copyright (C) 2024-2026 MESH Research
 *
 * KCWorks is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React from "react";
import { act, cleanup, render, screen, waitFor } from "@testing-library/react";
import {
  UNREAD_NOTIFICATIONS_STORAGE_KEY,
  UNREAD_NOTIFICATIONS_UPDATED_EVENT,
  setUnreadNotificationsInSession,
} from "@js/kcworks/notifications/unreadNotifications";
import { MainMenu } from "./main_menu";

jest.mock("@translations/kcworks/i18next", () => ({
  i18next: {
    t: (key) => key,
  },
}));

const unreadFixture = [
  {
    request_id: "req-1",
    request_type: "community-submission",
    request_status: "submitted",
    is_new_request: true,
    unread_comments: [],
  },
  {
    request_id: "req-2",
    request_type: "user-access-request",
    request_status: "submitted",
    is_new_request: false,
    unread_comments: ["c1"],
  },
];

const baseProps = {
  accountsEnabled: true,
  actionsMenuItems: [],
  adminMenuItems: [],
  externalIdentifiers: {},
  kcWorksHelpUrl: "/help",
  kcWordpressDomain: "example.org",
  loginURL: "/login",
  logoutURL: "/logout",
  mainMenuItems: [],
  notificationsMenuItems: [
    {
      text: "requests",
      url: "/me/requests",
      icon: "inbox",
      order: 1,
      visible: true,
    },
  ],
  plusMenuItems: [],
  profilesURL: "/profiles",
  settingsMenuItems: [],
  themeLogoURL: "",
  themeSitename: "KCWorks",
  themeSearchbarEnabled: false,
  userAuthenticated: true,
  userDisplayName: "Test User",
  userId: "42",
  userAdministrator: false,
};

/**
 * @param {string} pathname
 */
function setPathname(pathname) {
  window.history.pushState({}, "", pathname);
}

describe("MainMenu unread notifications", () => {
  beforeEach(() => {
    sessionStorage.clear();
    setPathname("/");
    global.fetch = jest.fn();
  });

  afterEach(() => {
    cleanup();
    jest.restoreAllMocks();
    sessionStorage.clear();
  });

  it("fetches unread list off the requests dashboard and shows the badge count", async () => {
    global.fetch.mockResolvedValue({
      json: async () => unreadFixture,
    });

    render(<MainMenu {...baseProps} />);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        "/api/users/me/notifications/unread/list"
      );
    });

    await waitFor(() => {
      expect(sessionStorage.getItem(UNREAD_NOTIFICATIONS_STORAGE_KEY)).toBe(
        JSON.stringify(unreadFixture)
      );
    });

    const badges = await screen.findAllByText("2");
    expect(badges.length).toBeGreaterThan(0);
    expect(
      document.querySelector(".unread-notifications-badge")
    ).toBeInTheDocument();
  });

  it("skips list fetch on /me/requests and seeds the badge from sessionStorage", async () => {
    setPathname("/me/requests");
    sessionStorage.setItem(
      UNREAD_NOTIFICATIONS_STORAGE_KEY,
      JSON.stringify(unreadFixture)
    );

    render(<MainMenu {...baseProps} />);

    await waitFor(() => {
      expect(screen.getAllByText("2").length).toBeGreaterThan(0);
    });
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it("treats /me/requests/ like the requests dashboard (no list fetch)", async () => {
    setPathname("/me/requests/");
    sessionStorage.setItem(
      UNREAD_NOTIFICATIONS_STORAGE_KEY,
      JSON.stringify([unreadFixture[0]])
    );

    render(<MainMenu {...baseProps} />);

    await waitFor(() => {
      expect(screen.getAllByText("1").length).toBeGreaterThan(0);
    });
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it("does not fetch or show a badge when userId is missing", async () => {
    render(<MainMenu {...baseProps} userId="" />);

    await act(async () => {
      await Promise.resolve();
    });

    expect(global.fetch).not.toHaveBeenCalled();
    expect(
      document.querySelector(".unread-notifications-badge")
    ).not.toBeInTheDocument();
  });

  it("updates the badge when unreadNotificationsUpdated is dispatched", async () => {
    setPathname("/me/requests");
    sessionStorage.setItem(UNREAD_NOTIFICATIONS_STORAGE_KEY, JSON.stringify([]));

    render(<MainMenu {...baseProps} />);

    await act(async () => {
      await Promise.resolve();
    });
    expect(
      document.querySelector(".unread-notifications-badge")
    ).not.toBeInTheDocument();

    act(() => {
      setUnreadNotificationsInSession(unreadFixture);
    });

    await waitFor(() => {
      expect(screen.getAllByText("2").length).toBeGreaterThan(0);
    });
  });

  it("removes the unread listener on unmount", async () => {
    setPathname("/me/requests");
    const { unmount } = render(<MainMenu {...baseProps} />);

    await act(async () => {
      await Promise.resolve();
    });

    const removeSpy = jest.spyOn(window, "removeEventListener");
    unmount();

    expect(removeSpy).toHaveBeenCalledWith(
      UNREAD_NOTIFICATIONS_UPDATED_EVENT,
      expect.any(Function)
    );
  });

  it("omits the badge when unread count is zero after fetch", async () => {
    global.fetch.mockResolvedValue({
      json: async () => [],
    });

    render(<MainMenu {...baseProps} />);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
    });

    await waitFor(() => {
      expect(sessionStorage.getItem(UNREAD_NOTIFICATIONS_STORAGE_KEY)).toBe(
        "[]"
      );
    });

    expect(
      document.querySelector(".unread-notifications-badge")
    ).not.toBeInTheDocument();
  });
});
