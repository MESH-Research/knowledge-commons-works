/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { Component } from "react";
import { Dropdown, Icon } from "semantic-ui-react";
import PropTypes from "prop-types";
import _find from "lodash/find";

export class DropdownSort extends Component {
  parsedOptions = () => {
    const {
      options,
      currentSortBy,
      onValueChange,
      ariaLabel,
      selectOnNavigation,
      ...uiProps
    } = this.props;

    return options.map((option) => {

      const selected = currentSortBy === option.sortBy;

      return {
        key: option.value,
        text: option.text,
        value: option.value,
        disabled: selected,
        selected: selected
      };
    });
  };

  getCurrentlySelectedOption = (options) => {
    return options.find(option => {
      return option.selected === true;
    })
  }

  render() {
    const {
      options,
      currentSortBy,
      onValueChange,
      ariaLabel,
      selectOnNavigation,
      ...uiProps
    } = this.props;

    const parsedOptions = this.parsedOptions()
    return (
      <Dropdown
        icon="sort"
        button
        labeled
        item
        trigger={
          <span>
            {this.getCurrentlySelectedOption(parsedOptions).text}
            <Icon name="dropdown" />
          </span>
        }
        options={parsedOptions}
        value={currentSortBy}
        onChange={(_, { value }) => onValueChange(value)}
        aria-label={ariaLabel}
        selectOnNavigation={selectOnNavigation}
        selectOnBlur={false}
        size="large"
        className="icon fluid-responsive"
      />
    );
  }
}

DropdownSort.propTypes = {
  options: PropTypes.array.isRequired,
  currentSortBy: PropTypes.string,
  overridableId: PropTypes.string,
  ariaLabel: PropTypes.string,
  selectOnNavigation: PropTypes.bool,
  onValueChange: PropTypes.func.isRequired,
};

export class DropdownFilter extends Component {
  onChangeFilter = (e, data) => {
    const { updateQueryState, currentQueryState } = this.props;
    currentQueryState.filters.push(JSON.parse(data.value));
    updateQueryState(currentQueryState);
  };

  render() {
    const {
      filterKey,
      filterValues,
      filterLabel,
      currentQueryState,
      updateQueryState,
      loading,
      ...uiProps
    } = this.props;
    const options = filterValues.map((filterValue) => {
      const value = [filterKey, filterValue.key];
      const disabled = currentQueryState.filters.some(
        (filter) => JSON.stringify(value) === JSON.stringify(filter)
      );
      return {
        key: filterValue.key,
        text: filterValue.label,
        value: JSON.stringify(value),
        disabled: disabled,
      };
    });

    return (
      <Dropdown
        icon="filter"
        labeled
        item
        button
        trigger={
          <span>
            {filterLabel}
            <Icon name="dropdown" />
          </span>
        }
        options={options}
        onChange={this.onChangeFilter}
        selectOnBlur={false}
        value={null}
        loading={loading}
        className="icon fluid-responsive"
        {...uiProps}
      />
    );
  }
}

DropdownFilter.propTypes = {
  updateQueryState: PropTypes.func.isRequired,
  currentQueryState: PropTypes.object.isRequired,
  filterKey: PropTypes.string.isRequired,
  filterValues: PropTypes.array.isRequired,
  filterLabel: PropTypes.string.isRequired,
};

DropdownFilter.defaultProps = {
  filterLabel: "",
};
