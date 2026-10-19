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
import React from "react";
import { Label, Popup } from "semantic-ui-react";
import PropTypes from "prop-types";

const NavItem = ({ text, icon, url, tabIndex, className = "" }) => {
  return (
    <a href={url} className={`ui pl-15 pr-15 ${className}`} tabIndex={tabIndex}>
      <i className={`${icon} icon fitted`}></i>
      <span className="inline">{text}</span>
    </a>
  );
};

NavItem.propTypes = {
  text: PropTypes.string,
  icon: PropTypes.string,
  url: PropTypes.string,
  tabIndex: PropTypes.number,
  className: PropTypes.string,
};

const IconNavItem = ({ text, icon, url, badge, tabIndex, className = "" }) => {
  return (
    <>
      <Popup
        content={text}
        trigger={
          <a
            href={url}
            className={`ui pl-15 pr-15 computer widescreen large screen only ${className}`}
            tabIndex={tabIndex}
            aria-label={text}
          >
            <i className={`${icon} icon fitted`}></i>
            {badge !== undefined && (
              <Label className="unread-notifications-badge" color="orange" floating>
                {badge}
              </Label>
            )}
          </a>
        }
      />

      <a
        href={url}
        className={`ui pl-15 pr-15 tablet mobile only ${className}`}
        tabIndex={tabIndex}
      >
        <i className={`${icon} icon fitted`}></i>
        <span className="inline">{text}</span>
      </a>
    </>
  );
};

IconNavItem.propTypes = {
  text: PropTypes.string,
  icon: PropTypes.string,
  badge: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  url: PropTypes.string,
  tabIndex: PropTypes.number,
  className: PropTypes.string,
};

const CollapsingNavItem = ({ text, icon, url, tabIndex, classnames, breakAt = "computer" }) => {
  return (
    <>
      <Popup
        content={text}
        trigger={
          <a
            href={url}
            className={`ui mobile tablet only ${classnames} collapsing`}
            tabIndex={tabIndex}
            aria-label={text}
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
              href={url}
              className={`computer only ${classnames} collapsing`}
              tabIndex={tabIndex}
              aria-label={text}
            >
              <i className={`${icon} icon fitted`}></i>
            </a>
          }
        />
      ) : (
        <a href={url} className={`computer only ${classnames} collapsing`} tabIndex={tabIndex}>
          <i className={`${icon} icon`}></i>
          <span className="inline">{text}</span>
        </a>
      )}

      <a
        href={url}
        className={`ui widescreen large screen only ${classnames} collapsing`}
        tabIndex={tabIndex}
      >
        <i className={`${icon} icon`}></i>
        <span className="inline">{text}</span>
      </a>
    </>
  );
};

CollapsingNavItem.propTypes = {
  text: PropTypes.string,
  icon: PropTypes.string,
  url: PropTypes.string,
  tabIndex: PropTypes.number,
  classnames: PropTypes.string,
  breakAt: PropTypes.string,
};

export { NavItem, IconNavItem, CollapsingNavItem };
