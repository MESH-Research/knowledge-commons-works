/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { i18next } from "@translations/invenio_communities/i18next";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { withState } from "react-searchkit";
import { Button } from "semantic-ui-react";
import FilterLabel from "./FilterLabel";

export class FilterLabelsComponent extends Component {
  filterCurrentFilters = (filters) => {
    const { ignoreFilters } = this.props;
    return filters.filter((element) => !ignoreFilters.includes(element[0]));
  };

  onClearAllFilters = (currentQueryState, updateCurrentFilters) => {
    const { ignoreFilters } = this.props;
    currentQueryState.filters = currentQueryState.filters.filter((element) =>
      ignoreFilters.includes(element[0])
    );
    updateCurrentFilters(currentQueryState);
  };

  render() {
    const { currentQueryState, updateQueryState } = this.props;
    const currentFilters = this.filterCurrentFilters(currentQueryState.filters);

    return (
      <>
        {currentFilters.map((filter) => {
          return (
            <FilterLabel
              key={filter[0]}
              filter={filter}
              currentQueryState={currentQueryState}
              updateQueryState={updateQueryState}
            />
          );
        })}
        {currentFilters.length > 0 && (
          <Button
            primary
            compact
            size="mini"
            onClick={() => {
              this.onClearAllFilters(currentQueryState, updateQueryState);
            }}
            className="rel-mr-1 rel-mt-1"
          >
            {i18next.t("Clear all filters")}
          </Button>
        )}
      </>
    );
  }
}

FilterLabelsComponent.propTypes = {
  updateQueryState: PropTypes.func.isRequired,
  currentQueryState: PropTypes.object.isRequired,
  ignoreFilters: PropTypes.array,
};

FilterLabelsComponent.defaultProps = {
  ignoreFilters: [],
};

export const FilterLabels = withState(FilterLabelsComponent);
