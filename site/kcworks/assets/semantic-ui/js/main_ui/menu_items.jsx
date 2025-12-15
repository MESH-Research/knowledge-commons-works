import React from "react";
// import { i18next } from "@translations/kcworks/i18next";
import { Label, Popup } from "semantic-ui-react";
import PropTypes from "prop-types";

const MenuItem = ({ text, icon, url, tabIndex }) => {
	return (
		<a role="button" href={url} className="ui " tabIndex={tabIndex}>
			<i className={`${icon} icon fitted`}></i>
			<span className="inline">{text}</span>
		</a>
	);
};

MenuItem.PropTypes = {
	text: PropTypes.string,
	icon: PropTypes.string,
	url: PropTypes.string,
	tabIndex: PropTypes.number,
};

const IconMenuItem = ({ text, icon, url, badge, tabIndex }) => {
	return (
		<>
			<Popup
				content={text}
				trigger={
					<a
						role="button"
						href={url}
						className="ui computer widescreen large-monitor only"
						tabIndex={tabIndex}
						aria-label={text}
					>
						<i className={`${icon} icon fitted`}></i>
						{badge !== undefined && (
							<Label
								className="unread-notifications-badge"
								color="orange"
								floating
							>
								{badge}
							</Label>
						)}
					</a>
				}
			/>

			<a
				role="button"
				href={url}
				className="ui tablet mobile only"
				tabIndex={tabIndex}
				aria-label={text}
			>
				<i className={`${icon} icon fitted`}></i>
				<span className="inline">{text}</span>
			</a>
		</>
	);
};

IconMenuItem.PropTypes = {
	text: PropTypes.string,
	icon: PropTypes.string,
	badge: PropTypes.string,
	url: PropTypes.string,
	tabIndex: PropTypes.number,
};

const CollapsingMenuItem = ({
	text,
	icon,
	url,
	tabIndex,
	classnames,
	breakAt = "computer",
}) => {
	return (
		<>
			<Popup
				content={text}
				trigger={
					<a
						role="button"
						href={url}
						className={`ui mobile tablet only ${classnames} collapsing`}
						tabIndex={tabIndex}
					>
						<i className={`${icon} icon fitted`}></i>
					</a>
				}
			/>

			{breakAt === "computer" ? (
				<Popup
					content={text}
					trigger={
						<a
							role="button"
							href={url}
							className={`computer only ${classnames} collapsing`}
							tabIndex={tabIndex}
						>
							<i className={`${icon} icon fitted`}></i>
						</a>
					}
				/>
			) : (
				<a
					role="button"
					href={url}
					className={`computer only ${classnames} collapsing`}
					tabIndex={tabIndex}
				>
					<i className={`${icon} icon`}></i>
					<span className="inline">{text}</span>
				</a>
			)}

			<a
				role="button"
				href={url}
				className={`ui widescreen large-monitor only ${classnames} collapsing`}
				tabIndex={tabIndex}
			>
				<i className={`${icon} icon`}></i>
				<span className="inline">{text}</span>
			</a>
		</>
	);
};

CollapsingMenuItem.propTypes = {
	text: PropTypes.string,
	icon: PropTypes.string,
	url: PropTypes.string,
	tabIndex: PropTypes.number,
};

export { MenuItem, IconMenuItem, CollapsingMenuItem };
