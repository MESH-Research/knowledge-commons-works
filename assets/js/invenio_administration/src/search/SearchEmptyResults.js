/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { Component } from "react";
import { Button, Header, Icon, Segment } from "semantic-ui-react";
import { withState } from "react-searchkit";
import { i18next } from "@translations/invenio_administration/i18next";
import PropTypes from "prop-types";

class SearchEmptyResults extends Component {
  render() {
    const {
      resetQuery,
      extraContent,
      queryString,
      currentQueryState,
      currentResultsState,
    } = this.props;

    const isEmptyPageAfterSearch = currentQueryState.page < 0;
    const isEmptyPage =
      currentQueryState.page === 1 && currentResultsState.data.total === 0;

    return (
      <Segment placeholder textAlign="center">
        <Header icon>
          <Icon name="search" />
          {isEmptyPage && i18next.t("There is no resources in this category.")}
          {isEmptyPageAfterSearch && i18next.t("No matching resources found.")}
        </Header>
        {queryString && <em>Current search "{queryString}"</em>}
        <br />
        {isEmptyPageAfterSearch && (
          <Button primary onClick={() => resetQuery()}>
            {i18next.t("Clear query")}
          </Button>
        )}
        {extraContent}
      </Segment>
    );
  }
}

SearchEmptyResults.propTypes = {
  resetQuery: PropTypes.func.isRequired,
  extraContent: PropTypes.node,
  queryString: PropTypes.string,
  currentQueryState: PropTypes.object.isRequired,
  currentResultsState: PropTypes.object.isRequired,
};

SearchEmptyResults.defaultProps = {
  extraContent: undefined,
  queryString: undefined,
};

export default withState(SearchEmptyResults);
