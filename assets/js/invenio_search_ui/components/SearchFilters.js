/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { DropdownFilter } from "@js/invenio_search_ui/components";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { withState } from "react-searchkit";

export class SearchFiltersComponent extends Component {
  render() {
    const {
      currentQueryState,
      updateQueryState,
      currentResultsState,
      customFilters,
    } = this.props;
    const filters = customFilters
      ? customFilters
      : currentResultsState.data.aggregations;
    return (
      <>
        {Object.entries(filters).map((filter) => (
          <DropdownFilter
            key={filter[0]}
            filterKey={filter[0]}
            filterLabel={filter[1].label}
            filterValues={filter[1].buckets}
            currentQueryState={currentQueryState}
            updateQueryState={updateQueryState}
            loading={currentResultsState.loading}
            size="large"
          />
        ))}
      </>
    );
  }
}

SearchFiltersComponent.propTypes = {
  updateQueryState: PropTypes.func.isRequired,
  currentQueryState: PropTypes.object.isRequired,
  customFilters: PropTypes.object,
};

SearchFiltersComponent.defaultProps = {
  customFilters: undefined,
};

export const SearchFilters = withState(SearchFiltersComponent);
