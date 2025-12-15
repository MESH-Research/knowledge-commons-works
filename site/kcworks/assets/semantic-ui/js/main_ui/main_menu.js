import React, { useEffect, useState } from "react";
import ReactDOM from "react-dom";
import { i18next } from "@translations/kcworks/i18next";
import { Button, Label, Popup } from "semantic-ui-react";
import PropTypes from "prop-types";
import { MenuItem, IconMenuItem } from "./menu_items";

const SubMenu = ({ item, index }) => {
	return (
		<div className={`dropdown ${item.active ? " active" : ""}`}>
			<a
				role="menuitem"
				className="dropdown-toggle"
				data-toggle="dropdown"
				aria-haspopup="true"
				aria-expanded="false"
				href={item.url}
				tabIndex={index}
			>
				{/* // FIXME: safe filter??? */}
				{item.text.replace(/<[^>]*>/g, "")}
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

const PlusMenu = ({ plusMenuItems, baseTabIndex }) => {
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
				tabIndex={baseTabIndex}
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
	tabIndex,
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
				className="ui item floating dropdown computer widescreen large-monitor only"
			>
				<div
					as="a"
					role="button"
					id="user-profile-dropdown-btn"
					className=""
					aria-controls="user-settings-menu"
					aria-expanded="false"
					aria-haspopup="menu"
					aria-label={i18next.t("Settings")}
					tabIndex={tabIndex}
				>
					{/* <span> */}
					<i className="cog icon"></i>
					{/* {readableEmail} */}
					{/* </span> */}
					{/* <i className="dropdown icon"></i> */}
				</div>

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
							tabIndex={-1}
							key={index}
						>
							{item.text.replace(/<[^>]*>/g, "")}
						</a>
					))}

					<div className="ui divider"></div>

					{adminItems.map((item, index) => (
						<a
							role="menuitem"
							className="item"
							href={item.url}
							tabIndex={-1}
							key={index}
						>
							{item.text.replace(/<[^>]*>/g, "")}
						</a>
					))}
				</div>
			</div>

			<div className="sub-menu mobile tablet only" role="menu">
				<h2 className="ui small header">{i18next.t("My account")}</h2>

				{settingsItems.map((item, index) => (
					<a
						role="menuitem"
						className="item"
						href={item.url}
						key={index}
						tabIndex={0}
					>
						{item.text.replace(/<[^>]*>/g, "")}
					</a>
				))}

				<div className="ui divider"></div>

				{adminItems.map((item, index) => (
					<a
						role="menuitem"
						className="item"
						href={item.url}
						key={index}
						tabIndex={0}
					>
						{item.text.replace(/<[^>]*>/g, "")}
					</a>
				))}
				{adminItems?.length > 0 && <div className="ui divider"></div>}

				<a role="menuitem" className="item" href={logoutURL} tabIndex={0}>
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
	externalIdentifiers,
	loginURL,
	logoutURL,
	profilesEnabled,
	profilesURL,
	settingsMenuItems,
	userAdministrator,
	userAuthenticated,
	tabIndex,
}) => {
	const readableEmail =
		currentUserEmail.length >= 31
			? currentUserEmail.slice(31) + "..."
			: currentUserEmail;
	const profileURL = externalIdentifiers.external_id
		? `${profilesURL}${externalIdentifiers.external_id}`
		: undefined;

	return (
		!!accountsEnabled &&
		(!userAuthenticated ? (
			<form>
				<a href={loginURL} className="ui basic button" tabIndex={tabIndex}>
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
				tabIndex={tabIndex}
			/>
		) : (
			<>
				<div className="item">
					{/* {# <i class="user icon"></i> #} */}
					{profileURL ? (
						<>
							{/* <Popup
              content={i18next.t("My KC profile")}
              trigger={
                <a role="button" href={profileURL}>{readableEmail}</a>
              }
              className="widescreen only"
            /> */}
							<IconMenuItem
								text={i18next.t("My KC profile")}
								url={profileURL}
								icon="address card outline"
								tabIndex={tabIndex}
							/>
						</>
					) : (
						<span className="inline">{readableEmail}</span>
					)}
				</div>
			</>
		))
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
			{/* <span className="title-wrapper">
        <h1 className="ui header">
          {siteNameOverride !== "" ? "Works" : themeSitename}
        </h1>
        <span className="ui header subtitle">Knowledge Commons</span>
      </span> */}
		</a>
	) : (
		<a className="logo" href="/">
			{themeSitename}
		</a>
	);
};

const MainMenu = ({
	accountsEnabled,
	actionsMenuItems,
	adminMenuItems,
	currentUserEmail,
	externalIdentifiers,
	kcFaqUrl,
	kcWorksHelpUrl,
	kcWordpressDomain,
	loginURL,
	logoutURL,
	mainMenuItems,
	notificationsMenuItems,
	plusMenuItems,
	profilesEnabled,
	profilesURL,
	settingsMenuItems,
	themeLogoURL,
	themeSitename,
	themeSearchbarEnabled,
	userAuthenticated,
	userId,
	userAdministrator,
}) => {
	const mainItems = mainMenuItems
		.sort((a, b) => a.order - b.order)
		.filter((i) => i.visible === true);
	const actionsItems = actionsMenuItems
		.sort((a, b) => a.order - b.order)
		.filter((i) => i.visible === true);
	const notificationsItems = notificationsMenuItems
		.sort((a, b) => a.order - b.order)
		.filter((i) => i.visible === true);
	const [unreadNotifications, setUnreadNotifications] = useState([]);

	const fetchUnreadNotifications = async () => {
		const response = await fetch(
			`/api/users/${userId}/notifications/unread/list`,
		);
		const data = await response.json();
		// Store unread notifications in session storage.
		// This is to avoid fetching the same notifications in
		// independent components that can't share a context.
		sessionStorage.setItem(`unreadNotifications`, JSON.stringify(data));
		// Dispatch a storage event to update other components that are listening.
		window.dispatchEvent(new Event("storage"));
		return data;
	};

	const updateUnreadNotifications = () => {
		const unreadFromStorage = JSON.parse(
			sessionStorage.getItem(`unreadNotifications`),
		);
		setUnreadNotifications(unreadFromStorage);
	};

	useEffect(() => {
		if (![null, undefined, ""].includes(userId)) {
			fetchUnreadNotifications();
			window.addEventListener("storage", () => {
				updateUnreadNotifications();
			});
		}
		return () => {
			window.removeEventListener("storage", updateUnreadNotifications);
		};
	}, [userId]);

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

				<h2 className="ui header mobile tablet only ml-20">Menu</h2>

				{/* Searchbar not implemented yet */}
				{/* {!!themeSearchbar && (
                {%- include "invenio_app_rdm/searchbar.html" %}
            )} */}

				<div className={`item`}>
					<MenuItem
						text={i18next.t("Search")}
						url={"/search"}
						icon="search"
						tabIndex="0"
					/>
				</div>

				{/* "Main" menu, including collections */}
				{mainItems.map((item, index) =>
					!!item.children ? (
						<div className="item" key={index}>
							<SubMenu item={item} index={0} />
						</div>
					) : (
						<div
							className={`${item.active ? "item active" : " item"}`}
							key={index}
						>
							<MenuItem
								url={item.url}
								text={`${
									item.text === "Communities"
										? i18next.t("Collections")
										: item.text
								}`}
								icon={item.text === "Communities" ? "copy" : item.icon}
								key={index}
								tabIndex={0}
							/>
						</div>
					),
				)}

				{/* "Plus" menu including adding a record */}
				<PlusMenu plusMenuItems={plusMenuItems} baseTabIndex={0} />

				<div className="menu item spacer mobile tablet only"></div>

				<div className={`item`} role="menuitem">
					<IconMenuItem
						text={i18next.t("Help and support")}
						url={kcWorksHelpUrl}
						icon="question circle"
						tabIndex={0}
					/>
				</div>

				<div className={`item`} role="menuitem">
					<IconMenuItem
						text={i18next.t("Statistics")}
						url={"/stats"}
						icon="chart line"
						tabIndex={0}
					/>
				</div>

				<div className={`item`} role="menuitem">
					<IconMenuItem
						text={i18next.t("KC Home")}
						url={`https://${kcWordpressDomain}`}
						icon="home"
						tabIndex={0}
					/>
				</div>

				{/* Right-aligned menu items */}
				<div className="right menu item" role="group">
					<div className="menu item spacer mobile tablet only"></div>
					<LoginMenu
						accountsEnabled={accountsEnabled}
						adminMenuItems={adminMenuItems}
						currentUserEmail={currentUserEmail}
						externalIdentifiers={externalIdentifiers}
						loginURL={loginURL}
						logoutURL={logoutURL}
						userAuthenticated={userAuthenticated}
						profilesEnabled={profilesEnabled}
						profilesURL={profilesURL}
						settingsMenuItems={settingsMenuItems}
						userAdministrator={userAdministrator}
						tabIndex={0}
					/>

					{!!accountsEnabled &&
						!!userAuthenticated &&
						actionsItems.map((item, index) => (
							<div className={`item ${item.text}`} key={index}>
								<IconMenuItem
									text={item.text}
									url={item.url}
									icon={item.text === "My dashboard" ? "user" : item.icon}
									tabIndex={0}
								/>
							</div>
						))}

					{!!accountsEnabled &&
						!!userAuthenticated &&
						notificationsItems.map((item, index) => (
							<div className="item inbox" key={index}>
								<IconMenuItem
									text={
										item.text === "requests"
											? i18next.t("My requests")
											: item.text
									}
									url={item.url}
									icon={item.text === "requests" ? "inbox" : item.icon}
									badge={
										unreadNotifications?.length > 0
											? unreadNotifications?.length
											: undefined
									}
									tabIndex={0}
								/>
							</div>
						))}

					{!!accountsEnabled && !!userAuthenticated && (
						<div className="item">
							<IconMenuItem
								text={i18next.t("Log out")}
								url={logoutURL}
								icon="sign-out"
								tabIndex={0}
							/>
						</div>
					)}
				</div>
			</div>
		</nav>
	);
};

MainMenu.propTypes = {
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
	profilesEnabled: PropTypes.bool,
	settingsMenuItems: PropTypes.array,
	themeLogoURL: PropTypes.string,
	themeSitename: PropTypes.string,
	themeSearchbarEnabled: PropTypes.bool,
	userAuthenticated: PropTypes.bool,
	userAdministrator: PropTypes.bool,
	userId: PropTypes.string,
};

// Get the HTML element
const element = document.getElementById("main-nav-menu");

// Get the data property from the element
const accountsEnabled =
	element.dataset.accountsEnabled === "True" ? true : false;
const actionsMenuItems = JSON.parse(element.dataset.actionsMenuItems);
const adminMenuItems = JSON.parse(element.dataset.adminMenuItems);
const currentUserEmail = element.dataset.currentUserEmail;
const externalIdentifiers = JSON.parse(element.dataset.externalIdentifiers);
const kcWordpressDomain = element.dataset.kcWordpressDomain;
const kcFaqUrl = element.dataset.kcFaqUrl;
const kcWorksHelpUrl = element.dataset.kcWorksHelpUrl;
const loginURL = element.dataset.loginUrl;
const logoutURL = element.dataset.logoutUrl;
const mainMenuItems = JSON.parse(element.dataset.mainMenuItems);
const notificationsMenuItems = JSON.parse(
	element.dataset.notificationsMenuItems,
);
const plusMenuItems = JSON.parse(element.dataset.plusMenuItems);
const profilesEnabled =
	element.dataset.profilesEnabled === "True" ? true : false;
const profilesURL = element.dataset.profilesUrl;
const settingsMenuItems = JSON.parse(element.dataset.settingsMenuItems);
const themeLogoURL = element.dataset.themeLogoUrl;
const themeSitename = element.dataset.themeSitename;
const themeSearchbarEnabled =
	element.dataset.themeSearchbarEnabled === "True" ? true : false;
const userId = element.dataset.userId;
const userAuthenticated =
	element.dataset.userAuthenticated === "True" ? true : false;
const userAdministrator = JSON.parse(element.dataset.userRoles).includes(
	"administration",
)
	? true
	: false;

// Provide the data property as a prop to the MainMenu component
ReactDOM.render(
	<MainMenu
		accountsEnabled={accountsEnabled}
		actionsMenuItems={actionsMenuItems}
		adminMenuItems={adminMenuItems}
		currentUserEmail={currentUserEmail}
		externalIdentifiers={externalIdentifiers}
		kcFaqUrl={kcFaqUrl}
		kcWorksHelpUrl={kcWorksHelpUrl}
		kcWordpressDomain={kcWordpressDomain}
		loginURL={loginURL}
		logoutURL={logoutURL}
		mainMenuItems={mainMenuItems}
		notificationsMenuItems={notificationsMenuItems}
		plusMenuItems={plusMenuItems}
		profilesEnabled={profilesEnabled}
		profilesURL={profilesURL}
		settingsMenuItems={settingsMenuItems}
		themeLogoURL={themeLogoURL}
		themeSitename={themeSitename}
		themeSearchbarEnabled={themeSearchbarEnabled}
		userAuthenticated={userAuthenticated}
		userId={userId}
		userAdministrator={userAdministrator}
	/>,
	element,
);
