// Part of Knowledge Commons Works
// Copyright (C) 2023-2026, MESH Research
//
// Knowledge Commons Works is an instance of InvenioRDM, which is
// Copyright (c) 2019-2026, CERN
//
// Knowledge Commons Works and InvenioRDM are both free software;
// You can redistribute and/or modify them under the terms of the
// MIT License; see LICENSE file for more details.

// biome-ignore lint/correctness/noUnusedImports: classic JSX
import React, { useCallback, useEffect, useState } from "react";
import ReactDOM from "react-dom";
import { i18next } from "@translations/kcworks/i18next";
import {
  setUnreadNotificationsInSession,
  UNREAD_NOTIFICATIONS_UPDATED_EVENT,
} from "@js/kcworks/notifications/unreadNotifications";
import PropTypes from "prop-types";
import { NavItem, IconNavItem } from "./nav_items";

const SubMenu = ({ item, index }) => {
  return (
    <div className={`dropdown ${item.active ? " active" : ""}`}>
      <button
        type="button"
        className="dropdown-toggle unstyled"
        data-toggle="dropdown"
        aria-haspopup="true"
        aria-expanded="false"
        tabIndex={index}
      >
        {/* // FIXME: safe filter??? */}
        {item.text.replace(/<[^>]*>/g, "")}
        <b className="caret"></b>
      </button>
      <ul className="dropdown-menu">
        {item.children
          .sort((a, b) => a.order - b.order)
          .map((childItem) => (
            <li className={`${childItem.active ? "active" : ""}`} key={childItem.text}>
              <NavItem {...childItem} />
            </li>
          ))}
      </ul>
    </div>
  );
};

const NON_ADMIN_SETTINGS_MENU_NAMES = ["security", "applications"];

const stripHtml = (text) => (text || "").replace(/<[^>]*>/g, "");

const UserNav = ({
  adminMenuItems,
  externalIdentifiers,
  profilesURL,
  settingsMenuItems,
  tabIndex,
  userAdministrator,
  userDisplayName,
}) => {
  const nonAdminSettingsItems = settingsMenuItems
    .sort((a, b) => a.order - b.order)
    .filter((item) => item.visible === true)
    .filter((item) => NON_ADMIN_SETTINGS_MENU_NAMES.includes(item.name));

  const adminSettingsItems = settingsMenuItems
    .sort((a, b) => a.order - b.order)
    .filter((item) => item.visible === true)
    .filter((item) => !NON_ADMIN_SETTINGS_MENU_NAMES.includes(item.name));
  const adminItems = adminMenuItems
    .sort((a, b) => a.order - b.order)
    .filter((item) => item.visible === true);
  const adminItemsCombined = adminSettingsItems.concat(adminItems);
  const truncatedDisplayName =
    userDisplayName && userDisplayName.length >= 31
      ? `${userDisplayName.slice(0, 31)}...`
      : userDisplayName;
  const profileURL = externalIdentifiers?.external_id
    ? `${profilesURL}${externalIdentifiers.external_id}`
    : undefined;

  return (
    <>
      <div
        id="user-profile-dropdown"
        className="ui item floating dropdown computer widescreen large screen only"
      >
        <button
          type="button"
          id="user-profile-dropdown-btn"
          className="unstyled pl-15 pr-5"
          aria-controls="user-profile-nav"
          aria-expanded="false"
          aria-label={truncatedDisplayName || i18next.t("Settings")}
          tabIndex={tabIndex}
        >
          <span className="pr-5">{truncatedDisplayName}</span>
          <i className="dropdown icon"></i>
        </button>

        <div id="user-profile-nav" className="ui menu">
          {profileURL && (
            <a className="item" href={profileURL} tabIndex={-1}>
              {i18next.t("KC profile")}
            </a>
          )}
          {nonAdminSettingsItems.map((item) => (
            <a className="item" href={item.url} tabIndex={-1} key={item.text}>
              {stripHtml(item.text)}
            </a>
          ))}
          {userAdministrator
            ? adminItemsCombined?.map((item) => (
                <a className="item restricted" href={item.url} tabIndex={-1} key={item.text}>
                  {stripHtml(item.text)}
                </a>
              ))
            : null}
        </div>
      </div>

      <div className="item spacer mobile tablet only mt-10"></div>

      <h2 className="ui small header mobile tablet only ml-25">
        {truncatedDisplayName || i18next.t("My account")}
      </h2>

      {profileURL && (
        <a className="ui mobile tablet only" href={profileURL} tabIndex={0}>
          {i18next.t("KC profile")}
        </a>
      )}
      {nonAdminSettingsItems.map((item) => (
        <a className="ui mobile tablet only" href={item.url} key={item.text} tabIndex={0}>
          {stripHtml(item.text)}
        </a>
      ))}

      {userAdministrator && <div className="item spacer mobile tablet only restricted mt-10"></div>}
      {adminItemsCombined.map((item) => (
        <a
          className="ui mobile tablet only restricted"
          href={item.url}
          key={item.text}
          tabIndex={0}
        >
          {stripHtml(item.text)}
        </a>
      ))}
      {userAdministrator && <div className="item spacer mobile tablet only restricted mb-10"></div>}
    </>
  );
};

const Brand = ({ themeLogoURL, themeSitename }) => {
  const siteNameOverride = "Works";
  return themeLogoURL !== "" ? (
    <a
      className="logo-link"
      href="/"
      aria-label={siteNameOverride ? siteNameOverride : themeSitename}
      tabIndex="0"
    >
      <img
        className="ui image rdm-logo"
        src={`${themeLogoURL}`}
        alt={siteNameOverride ? siteNameOverride : themeSitename}
      />
    </a>
  ) : (
    <a className="logo" href="/">
      {themeSitename}
    </a>
  );
};

const MainNav = ({
  accountsEnabled,
  actionsMenuItems,
  adminMenuItems,
  externalIdentifiers,
  kcWorksHelpUrl,
  kcWordpressDomain,
  loginURL,
  logoutURL,
  mainMenuItems,
  notificationsMenuItems,
  plusMenuItems,
  profilesURL,
  settingsMenuItems,
  themeLogoURL,
  themeSitename,
  // themeSearchbarEnabled,
  userAuthenticated,
  userDisplayName,
  userId,
  userAdministrator,
}) => {
  let mainItems = mainMenuItems.sort((a, b) => a.order - b.order).filter((i) => i.visible === true);
  mainItems.unshift({
    url: "/search",
    text: "Search",
    icon: "search",
    active: true,
  });
  const plusItems = plusMenuItems
    .filter((plusItem) => plusItem.url === "/uploads/new")
    .map((item) => ({ ...item, icon: "upload", text: i18next.t("Add a work") }));
  mainItems = mainItems.concat(plusItems);
  const actionsItems = actionsMenuItems
    .sort((a, b) => a.order - b.order)
    .filter((i) => i.visible === true);
  const notificationsItems = notificationsMenuItems
    .sort((a, b) => a.order - b.order)
    .filter((i) => i.visible === true);
  const [unreadNotifications, setUnreadNotifications] = useState([]);

  const fetchUnreadNotifications = useCallback(async () => {
    const response = await fetch(`/api/users/me/notifications/unread/list`);
    const data = await response.json();
    // Store unread notifications in session storage
    // to avoid fetching the same notifications in
    // independent components that can't share a context.
    setUnreadNotificationsInSession(data);
    return data;
  }, []);

  const updateUnreadFromStorage = useCallback(() => {
    const unreadFromStorage = JSON.parse(sessionStorage.getItem(`unreadNotifications`));
    setUnreadNotifications(unreadFromStorage);
  }, []);

  useEffect(() => {
    if (![null, undefined, ""].includes(userId)) {
      // On My requests search, the dashboard layout runs reconcile (fetches
      // from the API and writes sessionStorage). Skip this here to avoid
      // duplicating the fetch and potential race condition.
      const path = window.location.pathname.replace(/\/$/, "") || "/";
      const isMyRequestsDashboard = path === "/me/requests";
      if (!isMyRequestsDashboard) {
        fetchUnreadNotifications();
      } else {
        updateUnreadFromStorage();
      }
      window.addEventListener(UNREAD_NOTIFICATIONS_UPDATED_EVENT, updateUnreadFromStorage);
    }
    return () => {
      window.removeEventListener(UNREAD_NOTIFICATIONS_UPDATED_EVENT, updateUnreadFromStorage);
    };
  }, [userId, fetchUnreadNotifications, updateUnreadFromStorage]);

  return (
    <nav id="invenio-nav" className="ui menu borderless stackable pr-0 pl-0">
      <div className="item logo p-0">
        <Brand themeLogoURL={themeLogoURL} themeSitename={themeSitename} />
      </div>

      <div id="rdm-burger-toggle">
        <button
          id="rdm-burger-menu-icon"
          className="ui button transparent borderless borderless-hover"
          type="button"
          aria-label={i18next.t("Menu")}
          aria-expanded="false"
          aria-controls="invenio-menu"
        >
          <span className="navicon"></span>
        </button>
      </div>

      <div id="invenio-menu" className="ui fluid menu borderless mobile-hidden">
        <button
          id="rdm-close-burger-menu-icon"
          className="ui button transparent borderless borderless-hover"
          type="button"
          aria-label={i18next.t("Close menu")}
        >
          <span className="navicon"></span>
        </button>

        <h2 className="ui header mobile tablet only ml-20">Menu</h2>

        {/* Searchbar not implemented yet */}
        {/* {!!themeSearchbar && (
                {%- include "invenio_app_rdm/searchbar.html" %}
            )} */}

        {/* "Main" menu, including search and collections */}
        <h3 className="ui small header mobile tablet only ml-25 mb-10 secondary">
          {i18next.t("Explore")}
        </h3>
        {mainItems.map((item) =>
          item.children ? (
            <div className="item" key={item.text}>
              <SubMenu item={item} index={0} />
            </div>
          ) : (
            <div className="item" key={item.text}>
              <NavItem
                url={item.url}
                text={item.text}
                icon={["Communities", "Collections"].includes(item.text) ? "copy" : item.icon}
                tabIndex={0}
              />
            </div>
          )
        )}

        {/* "Plus" menu including adding a record */}
        {/*<PlusMenu plusMenuItems={plusMenuItems} baseTabIndex={0} />*/}

        <div className="item spacer mobile tablet only"></div>
        <h3 className="ui small header mobile tablet only ml-25 mb-10 secondary">
          {i18next.t("Info")}
        </h3>

        <div className="item">
          <IconNavItem
            text={i18next.t("Help and support")}
            url={kcWorksHelpUrl}
            icon="question circle"
            tabIndex={0}
          />
        </div>

        <div className="item">
          <IconNavItem
            text={i18next.t("Statistics")}
            url={"/stats"}
            icon="chart line"
            tabIndex={0}
          />
        </div>

        <div className="item">
          <IconNavItem
            text={i18next.t("KC Home")}
            url={`https://${kcWordpressDomain}`}
            icon="home"
            tabIndex={0}
          />
        </div>

        <div className="item spacer mobile tablet only mt-20"></div>
        {/* Invenio expects .item.right.menu here — not a nested .right.menu */}
        <div className={`right menu item pr-10 pl-10 ${userAuthenticated ? "" : "logged-out"}`}>
          {!!accountsEnabled && !userAuthenticated ? (
            <NavItem url={loginURL} text={i18next.t("Log in")} icon="sign-in" tabIndex={0} />
          ) : (
            <UserNav
              adminMenuItems={adminMenuItems}
              externalIdentifiers={externalIdentifiers}
              profilesURL={profilesURL}
              settingsMenuItems={settingsMenuItems}
              userAdministrator={userAdministrator}
              userDisplayName={userDisplayName}
              tabIndex={0}
            />
          )}

          {!!accountsEnabled &&
            !!userAuthenticated &&
            actionsItems.map((item) => (
              <IconNavItem
                className={item.text}
                key={item.text}
                text={item.text}
                url={item.url}
                icon={item.text === "My dashboard" ? "user" : item.icon}
                tabIndex={0}
              />
            ))}

          {!!accountsEnabled &&
            !!userAuthenticated &&
            notificationsItems.map((item) => (
              <IconNavItem
                className="inbox"
                key={item.text}
                text={item.text === "requests" ? i18next.t("My requests") : item.text}
                url={item.url}
                icon={item.text === "requests" ? "inbox" : item.icon}
                badge={unreadNotifications?.length > 0 ? unreadNotifications?.length : undefined}
                tabIndex={0}
              />
            ))}

          {!!accountsEnabled && !!userAuthenticated && (
            <IconNavItem
              className="logout"
              text={i18next.t("Log out")}
              url={logoutURL}
              icon="sign-out"
              tabIndex={0}
            />
          )}
          <div className="item spacer mobile tablet only mb-10"></div>
        </div>
      </div>
    </nav>
  );
};

MainNav.propTypes = {
  accountsEnabled: PropTypes.bool,
  actionsMenuItems: PropTypes.array,
  adminMenuItems: PropTypes.array,
  externalIdentifiers: PropTypes.object,
  loginURL: PropTypes.string,
  logoutURL: PropTypes.string,
  kcWorksHelpUrl: PropTypes.string,
  mainMenuItems: PropTypes.array,
  notificationsMenuItems: PropTypes.array,
  plusMenuItems: PropTypes.array,
  settingsMenuItems: PropTypes.array,
  themeLogoURL: PropTypes.string,
  themeSitename: PropTypes.string,
  themeSearchbarEnabled: PropTypes.bool,
  userAuthenticated: PropTypes.bool,
  userAdministrator: PropTypes.bool,
  userDisplayName: PropTypes.string,
  userId: PropTypes.string,
};

// Provide props from the template mount point when it exists (skip in Jest).
const element = document.getElementById("main-nav-menu");

if (element) {
  const accountsEnabled = element.dataset.accountsEnabled === "True";
  const actionsMenuItems = JSON.parse(element.dataset.actionsMenuItems);
  const adminMenuItems = JSON.parse(element.dataset.adminMenuItems);
  const externalIdentifiers = JSON.parse(element.dataset.externalIdentifiers);
  const kcWordpressDomain = element.dataset.kcWordpressDomain;
  const kcFaqUrl = element.dataset.kcFaqUrl;
  const kcWorksHelpUrl = element.dataset.kcWorksHelpUrl;
  const loginURL = element.dataset.loginUrl;
  const logoutURL = element.dataset.logoutUrl;
  const mainMenuItems = JSON.parse(element.dataset.mainMenuItems);
  const notificationsMenuItems = JSON.parse(element.dataset.notificationsMenuItems);
  const plusMenuItems = JSON.parse(element.dataset.plusMenuItems);
  const profilesURL = element.dataset.profilesUrl;
  const settingsMenuItems = JSON.parse(element.dataset.settingsMenuItems);
  const themeLogoURL = element.dataset.themeLogoUrl;
  const themeSitename = element.dataset.themeSitename;
  const themeSearchbarEnabled = element.dataset.themeSearchbarEnabled === "True";
  const userDisplayName = element.dataset.userDisplayName || "";
  const userId = element.dataset.userId;
  const userAuthenticated = element.dataset.userAuthenticated === "True";
  const userAdministrator = JSON.parse(element.dataset.userRoles).includes("administration");

  ReactDOM.render(
    <MainNav
      accountsEnabled={accountsEnabled}
      actionsMenuItems={actionsMenuItems}
      adminMenuItems={adminMenuItems}
      externalIdentifiers={externalIdentifiers}
      kcFaqUrl={kcFaqUrl}
      kcWorksHelpUrl={kcWorksHelpUrl}
      kcWordpressDomain={kcWordpressDomain}
      loginURL={loginURL}
      logoutURL={logoutURL}
      mainMenuItems={mainMenuItems}
      notificationsMenuItems={notificationsMenuItems}
      plusMenuItems={plusMenuItems}
      profilesURL={profilesURL}
      settingsMenuItems={settingsMenuItems}
      themeLogoURL={themeLogoURL}
      themeSitename={themeSitename}
      themeSearchbarEnabled={themeSearchbarEnabled}
      userAuthenticated={userAuthenticated}
      userDisplayName={userDisplayName}
      userId={userId}
      userAdministrator={userAdministrator}
    />,
    element
  );
}

export { MainNav };
