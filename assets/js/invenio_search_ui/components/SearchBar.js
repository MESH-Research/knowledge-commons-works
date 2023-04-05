/*
 * This file is part of Invenio.
 * Copyright (C) 2020 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React from "react";
import { SearchBar as ReactSearchKitSearchBar } from "react-searchkit";
import ReactDOM from "react-dom";
import PropTypes from "prop-types";
import Overridable from "react-overridable";

export const SearchBar = ({ elementId, buildUID, appName }) => {
  const domElement = document.getElementById(elementId);
  if (domElement) {
    domElement.innerHTML = "";
    return ReactDOM.createPortal(<ReactSearchKitSearchBar />, domElement);
  }
  return (
    <Overridable id={buildUID("SearchApp.searchbar", "", appName)}>
      <ReactSearchKitSearchBar />
    </Overridable>
  );
};

SearchBar.propTypes = {
  elementId: PropTypes.string,
};

SearchBar.defaultProps = {
  elementId: "header-search-bar",
};
