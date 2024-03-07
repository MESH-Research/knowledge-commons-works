/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import PropTypes from "prop-types";
import React, { Component } from "react";
import { Icon, Label } from "semantic-ui-react";
import { Filters } from "../Filters";

class FilterLabel extends Component {
  render() {
    const { filter, currentQueryState, updateQueryState } = this.props;
    const currentFilters = currentQueryState.filters;
    const filtersClass = new Filters();
    const displayValue = filtersClass.getDisplayValue(filter);
    return (
      <Label className="rel-mr-1 rel-mt-1">
        {displayValue}
        <Icon
          onClick={() => {
            const start = currentFilters.indexOf(filter);
            currentFilters.splice(start, 1);
            updateQueryState(currentQueryState);
          }}
          name="delete"
        />
      </Label>
    );
  }
}

FilterLabel.propTypes = {
  updateQueryState: PropTypes.func.isRequired,
  currentQueryState: PropTypes.object.isRequired,
  filter: PropTypes.array.isRequired,
};

export default FilterLabel;
