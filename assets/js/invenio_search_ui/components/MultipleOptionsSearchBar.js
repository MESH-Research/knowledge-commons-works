/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { Component } from "react";
import { withState } from "react-searchkit";
import { Search, Label, Button, Icon } from "semantic-ui-react";
import { i18next } from "@translations/invenio_search_ui/i18next";
import _isEmpty from "lodash/isEmpty";
import PropTypes from "prop-types";

const resultRenderer = ({ text }, queryString) => {
  let searchOption = "...";

  if (!_isEmpty(queryString)) {
    searchOption = queryString;
  }
  return (
    <div className="flex">
      <div className="truncated pt-5">{searchOption}</div>
      <Label className="right-floated">{text}</Label>
    </div>
  );
};

export class MultipleOptionsSearchBar extends Component {
  /** Multiple options searchbar to be used as a standalone component
   */
  constructor(props) {
    super(props);
    this.state = {
      queryString: "",
    };
  }

  handleOnSearchClick = () => {
    const { options, defaultOption } = this.props;
    const { queryString } = this.state;
    let destinationURL = options[0]?.value || defaultOption.value;

    window.location = `${destinationURL}?q=${queryString}`;
  };

  handleOnResultSelect = (e, { result }) => {
    const { queryString } = this.state;
    const { value: url } = result;
    window.location = `${url}?q=${queryString}`;
  };

  handleOnSearchChange = (e, { value }) => {
    this.setState({ queryString: value });
  };

  render() {
    const { placeholder, options } = this.props;
    const { queryString } = this.state;
    const button = (
      <Button
        icon
        className="right-floated search"
        onClick={this.handleOnSearchClick}
        aria-label={i18next.t("Search")}
      >
        <Icon name="search" />
      </Button>
    );
    return (
      <Search
        fluid
        onResultSelect={this.handleOnResultSelect}
        onSearchChange={this.handleOnSearchChange}
        resultRenderer={(props) => resultRenderer(props, queryString)}
        results={options}
        value={queryString}
        placeholder={placeholder}
        minCharacters={0}
        icon={button}
        className="right-angle-search-content"
        selectFirstResult
      />
    );
  }
}

MultipleOptionsSearchBar.propTypes = {
  options: PropTypes.array.isRequired,
  placeholder: PropTypes.string,
  defaultOption: PropTypes.shape({
    key: PropTypes.string,
    text: PropTypes.string,
    value: PropTypes.string,
  }),
};

MultipleOptionsSearchBar.defaultProps = {
  placeholder: i18next.t("Search records..."),
  defaultOption: {
    key: "records",
    text: i18next.t("All records"),
    value: "/search",
  },
};

export class MultipleOptionsSearchBarCmp extends Component {
  /** Multiple options searchbar to be wrapped with RSK context
   */
  onBtnSearchClick = (e, { result }) => {
    const { queryString, updateQueryState, currentQueryState } = this.props;
    const { defaultOption } = this.props;
    const { value: url } = result;
    const destinationURL = url || defaultOption.value;

    if (window.location.pathname === destinationURL) {
      updateQueryState({ ...currentQueryState, queryString });
    } else {
      window.location = `${destinationURL}?q=${queryString}`;
    }
  };

  handleOnSearchChange = (e, { value }) => {
    const { onInputChange } = this.props;
    onInputChange(value);
  };

  render() {
    const { placeholder, queryString, options } = this.props;
    const button = (
      <Button
        icon
        className="right-floated search"
        onClick={this.onBtnSearchClick}
        aria-label={i18next.t("Search")}
      >
        <Icon name="search" />
      </Button>
    );

    return (
      <Search
        fluid
        onResultSelect={this.onBtnSearchClick}
        onSearchChange={this.handleOnSearchChange}
        resultRenderer={(props) => resultRenderer(props, queryString)}
        results={options}
        value={queryString}
        placeholder={placeholder}
        className="right-angle-search-content"
        selectFirstResult
        icon={button}
        minCharacters={0}
      />
    );
  }
}

MultipleOptionsSearchBarCmp.propTypes = {
  options: PropTypes.array.isRequired,
  queryString: PropTypes.string.isRequired,
  updateQueryState: PropTypes.func.isRequired,
  onInputChange: PropTypes.func.isRequired,
  placeholder: PropTypes.string,
  defaultOption: PropTypes.shape({
    key: PropTypes.string,
    text: PropTypes.string,
    value: PropTypes.string,
  }),
};

MultipleOptionsSearchBarCmp.defaultProps = {
  placeholder: i18next.t("Search records..."),
  defaultOption: {
    key: "records",
    text: i18next.t("All records"),
    value: "/search",
  },
};

export const MultipleOptionsSearchBarRSK = withState(
  MultipleOptionsSearchBarCmp
);
