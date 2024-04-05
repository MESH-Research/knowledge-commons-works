import React from "react";
import ReactDOM from "react-dom";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { Popup } from "semantic-ui-react";
import PropTypes from "prop-types";

const PlusMenu = ({ plusMenuItems }) => {
  return (
    //   {# {%- if plus_menu_items %}
    //     <div role="menuitem" class="rdm-plus-menu rdm-plus-menu-responsive ui dropdown floating pr-15 computer only" aria-label="{{ _("Quick create") }}">
    //         <i class="fitted plus icon"></i>
    //         <i class="fitted dropdown icon"></i>
    //         <div class="menu">
    //             {%- for item in plus_menu_items if item.visible %}
    //             {%- if item.text != "New community" or (current_user.roles | selectattr("name", "equalto", "administrator") | list) %}
    //               <a class="item" href="{{ item.url }}">{{ item.text|safe }} </a>
    //             {%- endif %}
    //             {%- endfor %}
    //         </div>
    //     </div>
    // )

    //     <div class="sub-menu mobile tablet only">
    //       <h2 class="ui small header">{{ _("Actions") }}</h2>

    //       {%- for item in plus_menu_items if item.visible %}
    //       {%- if item.text != "New community" or (current_user.roles | selectattr("name", "equalto", "administrator") | list) %}
    //         <a role="menuitem" class="item" href="{{ item.url }}">
    //           <i class="plus icon"></i>
    //           {{ item.text|safe }}
    //         </a>
    //       {%- endif %}
    //       {%- endfor %}
    //     </div>
    //   {% endif %} #}

    <div className="item plus">
      <a
        role="menuitem"
        aria-label={i18next.t("Quick create")}
        href={plusMenuItems[0].url}
      >
        <i className="fitted upload icon"></i>
        <span className="inline">{i18next.t("Add a work")}</span>
      </a>
    </div>
  );
};

const UserMenu = ({
  adminMenuItems,
  logoutURL,
  readableEmail,
  settingsMenuItems,
}) => {
  const settingsItems = settingsMenuItems
    .sort((a, b) => a.order - b.order)
    .filter((item) => item.visible === true);
  const adminItems = adminMenuItems
    .sort((a, b) => a.order - b.order)
    .filter((item) => item.visible === true);

  return (
    <>
      <div
        role="menuitem"
        id="user-profile-dropdown"
        className="ui floating dropdown computer only"
      >
        <button
          id="user-profile-dropdown-btn"
          className="ui right labeled right floated icon button text"
          aria-controls="user-profile-menu"
          aria-expanded="false"
          aria-haspopup="menu"
          aria-label="{i18next.t('My account')}"
        >
          <span>
            {/* {#  <i class="user icon"></i> #} */}
            {readableEmail}
          </span>
          <i className="dropdown icon"></i>
        </button>

        <div
          id="user-profile-menu"
          className="ui menu"
          role="menu"
          aria-labelledby="user-profile-dropdown-btn"
        >
          {settingsItems.map((item, index) => (
            <a
              role="menuitem"
              className="item"
              href={item.url}
              tabindex="-1"
              key={index}
            >
              {item.text}
            </a>
          ))}

          <div className="ui divider"></div>

          {adminItems.map((item, index) => (
            <a
              role="menuitem"
              className="item"
              href={item.url}
              tabindex="-1"
              key={index}
            >
              {item.text}
            </a>
          ))}

          {adminItems.length > 0 && <div className="ui divider"></div>}

          <a role="menuitem" className="item" href={logoutURL} tabindex="-1">
            <i className="fitted sign-out icon"></i>
            <span className="mobile tablet only inline">
              {i18next.t("Log out")}
            </span>
            <span className="widescreen only inline">
              {i18next.t("Log out")}
            </span>
          </a>
        </div>
      </div>

      <div className="sub-menu mobile tablet only">
        <h2 className="ui small header">{i18next.t("My account")}</h2>

        {settingsItems.map((item, index) => (
          <a role="menuitem" className="item" href={item.url} key={index}>
            {item.text}
          </a>
        ))}

        <div className="ui divider"></div>

        {adminItems.map((item, index) => (
          <a role="menuitem" className="item" href={item.url} key={index}>
            {item.text}
          </a>
        ))}
        {adminItems.length > 0 && <div className="ui divider"></div>}

        <a role="menuitem" className="item" href={logoutURL}>
          <i className="fitted sign-out icon"></i>
          {i18next.t("Log out")}
        </a>
      </div>
    </>
  );
};

const LoginMenu = ({
  accountsEnabled,
  adminMenuItems,
  currentUserEmail,
  currentUserProfile,
  loginURL,
  logoutURL,
  profilesEnabled,
  settingsMenuItems,
  userAdministrator,
  userAuthenticated,
}) => {
  const readableEmail =
    currentUserEmail.length >= 31
      ? currentUserEmail.slice(31) + "..."
      : currentUserEmail;

  return (
    !!accountsEnabled &&
    (!userAuthenticated ? (
      <form>
        <a href={loginURL} className="ui basic button">
          <i className="fitted sign-in icon"></i>
          {i18next.t("Log in")}
        </a>
        {/* // {% if security.registerable %}
            //     <a href="{{ url_for_security('register') }}" class="ui button signup">
            //         <i class="edit outline icon"></i>
            //         {{ _('Sign up') }}
            //     </a>
            // {% endif %} */}
      </form>
    ) : !!profilesEnabled && !!userAdministrator ? (
      <UserMenu
        adminMenuItems={adminMenuItems}
        logoutURL={logoutURL}
        readableEmail={readableEmail}
        settingsMenuItems={settingsMenuItems}
      />
    ) : (
      <>
        <div className="item">
          {/* {# <i class="user icon"></i> #} */}
          <span className="inline" href={currentUserProfile}>
            {readableEmail}
          </span>
        </div>
      </>
    ))
  );
};

const MenuItem = ({ text, icon, url }) => {
  return (
    <a role="button" href={url} className="ui ">
      <i className={`${icon} icon fitted`}></i>
      <span className="inline">{i18next.t(text)}</span>
    </a>
  );
};

const CollapsingMenuItem = ({ text, icon, url }) => {
  return (
    <>
      <Popup
        content={i18next.t(text)}
        trigger={
          <a role="button" href={url} className="ui computer only">
            <i className={`${icon} icon fitted`}></i>
          </a>
        }
      />

      <a role="button" href={url} className="ui widescreen only">
        <i className={`${icon} icon fitted`}></i>
        <span className="inline">{i18next.t(text)}</span>
      </a>

      <a role="button" href={url} className="ui mobile tablet only">
        <i className={`${icon} icon fitted`}></i>
        <span className="inline">{i18next.t(text)}</span>
      </a>

    </>
  );
};

const SubMenu = ({ item }) => {
  return (
    <div className={`dropdown ${item.active ? " active" : ""}`}>
      <a
        role="menuitem"
        className="dropdown-toggle"
        data-toggle="dropdown"
        aria-haspopup="true"
        aria-expanded="false"
        href={item.url}
      >
        {/* // FIXME: safe filter??? */}
        {item.text}
        <b className="caret"></b>
      </a>
      <ul className="dropdown-menu">
        {item.children
          .sort((a, b) => a.order - b.order)
          .map((childItem, indexInner) => (
            <li
              className={`${childItem.active ? "active" : ""}`}
              key={indexInner}
            >
              <MenuItem {...childItem} />
            </li>
          ))}
      </ul>
    </div>
  );
};

const Brand = ({ themeLogoURL, themeSitename }) => {
  const siteNameOverride = "Works";
  return themeLogoURL !== "" ? (
    <a className="logo-link" href="/">
      <img
        className="ui image rdm-logo"
        src={`${themeLogoURL}`}
        alt={i18next.t(siteNameOverride ? siteNameOverride : themeSitename)}
      />
      <span className="title-wrapper">
        <h1 className="ui header">
          {siteNameOverride !== "" ? "Works" : themeSitename}
        </h1>
        <span className="ui header subtitle">Knowledge Commons</span>
      </span>
    </a>
  ) : (
    <a className="logo" href="/">
      {i18next.t(themeSitename)}
    </a>
  );
};

const MainMenu = ({
  accountsEnabled,
  actionsMenuItems,
  adminMenuItems,
  currentUserEmail,
  currentUserProfile,
  kcWordpressDomain,
  loginURL,
  logoutURL,
  mainMenuItems,
  notificationsMenuItems,
  plusMenuItems,
  profilesEnabled,
  settingsMenuItems,
  themeLogoURL,
  themeSitename,
  themeSearchbarEnabled,
  userAuthenticated,
  userAdministrator,
}) => {
  console.log("mainMenuItems: ", mainMenuItems);

  const mainItems = mainMenuItems
    .sort((a, b) => a.order - b.order)
    .filter((i) => i.visible === true);
  const actionsItems = actionsMenuItems
    .sort((a, b) => a.order - b.order)
    .filter((i) => i.visible === true);
  const notificationsItems = notificationsMenuItems
    .sort((a, b) => a.order - b.order)
    .filter((i) => i.visible === true);

  return (
    <nav id="invenio-nav" className="ui menu borderless stackable p-0">
      <div className="item logo p-0">
        <Brand themeLogoURL={themeLogoURL} themeSitename={themeSitename} />
      </div>

      <div id="rdm-burger-toggle">
        <button
          id="rdm-burger-menu-icon"
          className="ui button transparent"
          aria-label={i18next.t("Menu")}
          aria-haspopup="menu"
          aria-expanded="false"
          aria-controls="invenio-menu"
        >
          <span className="navicon"></span>
        </button>
      </div>

      <div
        role="menu"
        id="invenio-menu"
        aria-labelledby="rdm-burger-menu-icon"
        className="ui fluid menu borderless mobile-hidden"
      >
        <button
          id="rdm-close-burger-menu-icon"
          className="ui button transparent"
          aria-label="{{ _('Close menu') }}"
        >
          <span className="navicon"></span>
        </button>

        {/* Searchbar not implemented yet */}
        {/* {!!themeSearchbar && (
                {%- include "invenio_app_rdm/searchbar.html" %}
            )} */}

        {/* "Main" menu, including collections */}
        {mainItems.map((item, index) =>
          !!item.children ? (
            <div className="item" key={index}>
              <SubMenu item={item} />
            </div>
          ) : (
            <div
              className={`${item.active ? "item active" : " item"}`}
              key={index}
            >
              <MenuItem
                url={item.url}
                text={`${
                  item.text === "Communities" ? "Collections" : item.text
                }`}
                icon={item.text === "Communities" ? "copy" : item.icon}
                key={index}
              />
            </div>
          )
        )}

        <div className={`item`}>
          <MenuItem text="Search" url={"/records?search="} icon="search" />
        </div>

        {/* "Plus" menu including adding a record */}
        <PlusMenu plusMenuItems={plusMenuItems} />

        <div className={`item`}>
          <CollapsingMenuItem text="Help and support" url={`https://support.${kcWordpressDomain}`} icon="question circle" />
        </div>

        {/* Right-aligned menu items */}
        <div className="right menu item">

          <LoginMenu
            accountsEnabled={accountsEnabled}
            adminMenuItems={adminMenuItems}
            currentUserEmail={currentUserEmail}
            currentUserProfile={currentUserProfile}
            loginURL={loginURL}
            logoutURL={logoutURL}
            userAuthenticated={userAuthenticated}
            profilesEnabled={profilesEnabled}
            settingsMenuItems={settingsMenuItems}
            userAdministrator={userAdministrator}
          />


          {!!accountsEnabled && !!userAuthenticated && actionsItems.map((item, index) => (
              <div className={`item ${item.text}`} key={index}>
                <CollapsingMenuItem text={item.text} url={item.url} icon={item.text === "My dashboard" ? "user" : item.icon} />
              </div>
            )
            )}

          {!!accountsEnabled && !!userAuthenticated && notificationsItems.map((item, index) => (
                  <div className="item inbox" key={index}>
                    <CollapsingMenuItem text={item.text==="requests" ? "My inbox" : item.text} url={item.url} icon={item.text==="requests" ? "inbox" : item.icon} />
                  </div>
                ))}

          {!!accountsEnabled && !!userAuthenticated && (<CollapsingMenuItem text="Log out" url={logoutURL} icon="sign-out" />)}

        </div>
      </div>
    </nav>
  );
};

MainMenu.propTypes = {
  accountsEnabled: PropTypes.bool,
  actionsMenuItems: PropTypes.array,
  adminMenuItems: PropTypes.array,
  currentUserEmail: PropTypes.string,
  loginURL: PropTypes.string,
  logoutURL: PropTypes.string,
  mainMenuItems: PropTypes.array,
  notificationsMenuItems: PropTypes.array,
  plusMenuItems: PropTypes.array,
  profilesEnabled: PropTypes.bool,
  settingsMenuItems: PropTypes.array,
  themeLogoURL: PropTypes.string,
  themeSitename: PropTypes.string,
  themeSearchbarEnabled: PropTypes.bool,
  userAuthenticated: PropTypes.bool,
  userAdministrator: PropTypes.bool,
};

// Get the HTML element
const element = document.getElementById("main-nav-menu");

// Get the data property from the element
const accountsEnabled =
  element.dataset.accountsEnabled === "True" ? true : false;
const actionsMenuItems = JSON.parse(element.dataset.actionsMenuItems);
const adminMenuItems = JSON.parse(element.dataset.adminMenuItems);
const currentUserEmail = element.dataset.currentUserEmail;
const kcWordpressDomain = element.dataset.kcWordpressDomain;
const loginURL = element.dataset.loginUrl;
const logoutURL = element.dataset.logoutUrl;
const mainMenuItems = JSON.parse(element.dataset.mainMenuItems);
const notificationsMenuItems = JSON.parse(
  element.dataset.notificationsMenuItems
);
const plusMenuItems = JSON.parse(element.dataset.plusMenuItems);
const profilesEnabled =
  element.dataset.profilesEnabled === "True" ? true : false;
const settingsMenuItems = JSON.parse(element.dataset.settingsMenuItems);
const themeLogoURL = element.dataset.themeLogoUrl;
const themeSitename = element.dataset.themeSitename;
const themeSearchbarEnabled =
  element.dataset.themeSearchbarEnabled === "True" ? true : false;
const userAuthenticated =
  element.dataset.userAuthenticated === "True" ? true : false;
const userAdministrator =
  element.dataset.userAdministrator === "True" ? true : false;

// Provide the data property as a prop to the MainMenu component
ReactDOM.render(
  <MainMenu
    accountsEnabled={accountsEnabled}
    actionsMenuItems={actionsMenuItems}
    adminMenuItems={adminMenuItems}
    currentUserEmail={currentUserEmail}
    kcWordpressDomain={kcWordpressDomain}
    loginURL={loginURL}
    logoutURL={logoutURL}
    mainMenuItems={mainMenuItems}
    notificationsMenuItems={notificationsMenuItems}
    plusMenuItems={plusMenuItems}
    profilesEnabled={profilesEnabled}
    settingsMenuItems={settingsMenuItems}
    themeLogoURL={themeLogoURL}
    themeSitename={themeSitename}
    themeSearchbarEnabled={themeSearchbarEnabled}
    userAuthenticated={userAuthenticated}
    userAdministrator={userAdministrator}
  />,
  element
);
